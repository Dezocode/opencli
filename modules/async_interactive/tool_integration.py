"""
Tool execution integration for async interactive mode
Connects async_interactive tools with permission system and streaming display
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from .tools import execute_tool_async, TOOLS
from .streaming import StreamHandler


class ToolExecutor:
    """Handles tool execution with permission integration and streaming"""
    
    def __init__(self, app=None, session=None, permission_manager=None):
        self.app = app
        self.session = session
        self.permission_manager = permission_manager
        self.stream_handler = StreamHandler()
    
    async def execute_tool_call(
        self, 
        tool_call: Dict[str, Any], 
        stream_display=None
    ) -> Dict[str, Any]:
        """
        Execute a tool call with permission checking and streaming output
        
        Args:
            tool_call: Tool call data with name and arguments
            stream_display: Optional streaming display widget
            
        Returns:
            Tool execution result
        """
        try:
            tool_name = tool_call.get("name", "")
            tool_args = tool_call.get("arguments", {})
            
            # Parse arguments if they're a string
            if isinstance(tool_args, str):
                try:
                    tool_args = json.loads(tool_args)
                except json.JSONDecodeError:
                    return {
                        "status": "error", 
                        "error": f"Invalid tool arguments: {tool_args}"
                    }
            
            # Show tool execution indicator
            if stream_display and hasattr(stream_display, 'write_stream'):
                stream_display.write_stream(f"\\n🔧 Executing {tool_name}...")
            elif self.app:
                self.app.write(f"\\n🔧 Executing {tool_name}...\\n")
            
            # Check if tool requires permission
            tool_registration = self._find_tool_registration(tool_name)
            if tool_registration and self.permission_manager:
                # TODO: Integrate with permission system
                # For now, execute directly for safe tools
                pass
            
            # Execute the tool
            result = await execute_tool_async(
                tool_name, 
                tool_args, 
                permission_manager=self.permission_manager,
                current_dir=getattr(self.session, 'cwd', None),
                app=self.app
            )
            
            # Show result
            if result.get("status") == "success":
                if stream_display and hasattr(stream_display, 'write_stream'):
                    stream_display.write_stream(f" ✓\\n")
                elif self.app:
                    self.app.write("✓\\n")
                    
                # Show tool output if available
                if "content" in result:
                    content = result["content"][:1000]  # Limit output length
                    if len(result["content"]) > 1000:
                        content += "... (truncated)"
                    
                    if stream_display and hasattr(stream_display, 'write_stream'):
                        stream_display.write_stream(f"\\n```\\n{content}\\n```\\n")
                    elif self.app:
                        self.app.write(f"\\n```\\n{content}\\n```\\n")
                        
            else:
                error_msg = result.get("error", "Unknown error")
                if stream_display and hasattr(stream_display, 'write_stream'):
                    stream_display.write_stream(f" ✗ Error: {error_msg}\\n")
                elif self.app:
                    self.app.write(f"✗ Error: {error_msg}\\n")
            
            return result
            
        except Exception as e:
            error_result = {"status": "error", "error": str(e)}
            
            if stream_display and hasattr(stream_display, 'write_stream'):
                stream_display.write_stream(f" ✗ Exception: {str(e)}\\n")
            elif self.app:
                self.app.write(f"✗ Exception: {str(e)}\\n")
                
            return error_result
    
    def _find_tool_registration(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Find tool registration by name"""
        for tool in TOOLS:
            if tool.get("function", {}).get("name") == tool_name:
                return tool
        return None
    
    async def execute_multiple_tools(
        self, 
        tool_calls: List[Dict[str, Any]], 
        stream_display=None
    ) -> List[Dict[str, Any]]:
        """Execute multiple tool calls in sequence"""
        results = []
        
        for i, tool_call in enumerate(tool_calls):
            if stream_display and hasattr(stream_display, 'write_stream'):
                stream_display.write_stream(f"\\n[{i+1}/{len(tool_calls)}] ")
            elif self.app:
                self.app.write(f"\\n[{i+1}/{len(tool_calls)}] ")
                
            result = await self.execute_tool_call(tool_call, stream_display)
            results.append(result)
            
            # Short delay between tools
            await asyncio.sleep(0.1)
        
        return results
    
    def set_context(self, app=None, session=None, permission_manager=None):
        """Update execution context"""
        if app is not None:
            self.app = app
        if session is not None:
            self.session = session
        if permission_manager is not None:
            self.permission_manager = permission_manager


# Global tool executor instance
_tool_executor = None

def get_tool_executor(app=None, session=None, permission_manager=None) -> ToolExecutor:
    """Get or create global tool executor instance"""
    global _tool_executor
    
    if _tool_executor is None:
        _tool_executor = ToolExecutor(app, session, permission_manager)
    else:
        # Update context if provided
        _tool_executor.set_context(app, session, permission_manager)
    
    return _tool_executor