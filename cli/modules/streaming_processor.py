"""
CLI Streaming Processor
Handles streaming responses and tool call processing
"""

import json
from typing import Dict, Any, Tuple
from types import SimpleNamespace


class StreamingProcessor:
    """Processes streaming API responses and tool calls"""
    
    def __init__(self, session, component_init):
        """Initialize streaming processor
        
        Args:
            session: Current session
            component_init: Component initializer
        """
        self.session = session
        self.component_init = component_init
    
    def process_stream_response(self, stream) -> Tuple[str, Dict]:
        """Process streaming response from API
        
        Args:
            stream: Stream object from API
            
        Returns:
            Tuple of (full_content, tool_calls_dict)
        """
        full_content = ""
        tool_calls_dict = {}
        
        print()
        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if not delta:
                continue
            
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_dict:
                        tool_calls_dict[idx] = {"id": tc.id or "", "name": "", "arguments": ""}
                    if tc.function:
                        if tc.function.name:
                            tool_calls_dict[idx]["name"] = tc.function.name
                        if tc.function.arguments:
                            tool_calls_dict[idx]["arguments"] += tc.function.arguments
            
            if delta.content:
                full_content += delta.content
                print(delta.content, end='', flush=True)
        
        return full_content, tool_calls_dict
    
    def extract_tool_calls_from_text(self, full_content: str) -> Tuple[list, str]:
        """Extract tool calls from text if no direct tool calls
        
        Args:
            full_content: Full content from API response
            
        Returns:
            Tuple of (parsed_calls, cleaned_content)
        """
        tool_utils = self.component_init.get_component('tool_utils')
        extract_func = tool_utils['extract_tool_calls_from_text']
        return extract_func(full_content)
    
    def execute_tool_calls(self, tool_calls_dict: Dict, full_content: str) -> bool:
        """Execute tool calls and update session
        
        Args:
            tool_calls_dict: Dictionary of tool calls
            full_content: Full content from response
            
        Returns:
            True if tool calls were executed, False otherwise
        """
        if not tool_calls_dict:
            parsed_calls, cleaned_content = self.extract_tool_calls_from_text(full_content)
            if parsed_calls:
                for idx, call in enumerate(parsed_calls):
                    try:
                        arguments_json = json.dumps(call.get("arguments", {}))
                    except TypeError:
                        arguments_json = json.dumps({})
                    tool_calls_dict[idx] = {
                        "id": call.get("id", f"text_{idx}"),
                        "name": call.get("name", ""),
                        "arguments": arguments_json,
                        "type": "function"
                    }
                full_content = cleaned_content
        
        if tool_calls_dict:
            print()
            
            # Convert to tool call objects
            tool_calls = []
            for idx, tc_data in tool_calls_dict.items():
                tc_obj = SimpleNamespace(
                    id=tc_data["id"],
                    function=SimpleNamespace(name=tc_data["name"], arguments=tc_data["arguments"])
                )
                tool_calls.append(tc_obj)
            
            # Add assistant message with tool calls
            self.session.messages.append({
                "role": "assistant",
                "content": "",
                "tool_calls": [{
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in tool_calls]
            })
            
            # Execute each tool call with permission checking
            from ..tools import execute_tool
            for tc in tool_calls:
                print(f"\033[2m⚙ {tc.function.name}\033[0m")
                permission_manager = getattr(self.session, 'permission_manager', None)

                # Check permissions for non-safe tools
                if permission_manager and hasattr(permission_manager, 'should_prompt'):
                    try:
                        args_dict = json.loads(tc.function.arguments)
                        should_prompt, reason, risk_data = permission_manager.should_prompt(
                            tc.function.name,
                            {"name": tc.function.name, "args": args_dict},
                            self.session.cwd
                        )
                        if should_prompt:
                            print(f"⚠️  Permission required for {tc.function.name}: {reason}")
                            # For CLI, we'll auto-deny risky operations unless explicitly allowed
                            if risk_data and risk_data.get('risk_level') in ['HIGH', 'CRITICAL']:
                                print(f"❌ Denied: {tc.function.name} (high risk operation)")
                                continue
                            else:
                                print(f"✓ Allowed: {tc.function.name}")
                    except Exception as e:
                        print(f"⚠️  Permission check failed: {e}")

                result = execute_tool(tc.function.name, json.loads(tc.function.arguments), permission_manager, self.session.cwd)
                self.session.messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
            
            return True
        
        return False


def create_streaming_processor(session, component_init) -> StreamingProcessor:
    """Factory function to create streaming processor
    
    Args:
        session: Current session
        component_init: Component initializer
        
    Returns:
        StreamingProcessor instance
    """
    return StreamingProcessor(session, component_init)