"""
Message handling and preparation for async interactive mode
"""

import json
from typing import Dict, List, Tuple, Optional, Callable
from copy import deepcopy


def normalize_tool_call_messages(messages):
    """
    Normalize tool call messages to handle different formats
    Some models return tool calls as JSON strings, others as objects
    """
    normalized = []
    
    for message in messages:
        msg_copy = deepcopy(message)
        
        # Handle tool_calls normalization
        if 'tool_calls' in msg_copy and msg_copy['tool_calls']:
            for tool_call in msg_copy['tool_calls']:
                if 'function' in tool_call and 'arguments' in tool_call['function']:
                    args = tool_call['function']['arguments']
                    # If arguments is a string, try to parse as JSON
                    if isinstance(args, str):
                        try:
                            tool_call['function']['arguments'] = json.loads(args)
                        except json.JSONDecodeError:
                            # Keep as string if not valid JSON
                            pass
        
        normalized.append(msg_copy)
    
    return normalized


def _flatten_message_content(content) -> str:
    """Flatten message content to plain text"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Handle structured content (images, text blocks, etc.)
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
                elif item.get('type') == 'image_url':
                    text_parts.append('[Image]')
            elif isinstance(item, str):
                text_parts.append(item)
        return ' '.join(text_parts)
    else:
        return str(content)


def convert_messages_for_anthropic(messages: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    Convert OpenAI format messages to Anthropic format
    Returns (system_prompt, messages)
    """
    system_prompt = ""
    converted_messages = []
    
    for message in messages:
        role = message.get('role')
        content = message.get('content', '')
        
        if role == 'system':
            # Anthropic uses separate system parameter
            system_prompt += _flatten_message_content(content) + "\n"
        elif role in ['user', 'assistant']:
            converted_messages.append({
                'role': role,
                'content': _flatten_message_content(content)
            })
        # Skip tool calls and other roles for now
    
    return system_prompt.strip(), converted_messages


def extract_openrouter_policy_error(error: Exception) -> Optional[str]:
    """Extract policy violation details from OpenRouter errors"""
    error_str = str(error)
    
    if "content_policy_violation" in error_str.lower():
        return "Content policy violation detected"
    elif "rate_limit" in error_str.lower():
        return "Rate limit exceeded"
    elif "insufficient_quota" in error_str.lower():
        return "Insufficient quota/credits"
    elif "model_not_found" in error_str.lower():
        return "Model not available"
    
    return None


async def prepare_messages_with_context(messages, session, config):
    """Prepare messages with full context (dev6 pattern)

    Adds:
    - Constitution principles (if available)
    - AGENTS.md content (if agent active)
    - Spec/goal context (if available)
    - Working directory info
    - Tool definitions

    Args:
        messages: Raw message list from session
        session: Session object
        config: Config dict

    Returns:
        Prepared messages with system context prepended
    """
    import asyncio
    import os
    from pathlib import Path

    prepared = []

    # Remove any existing system messages (we'll add fresh ones)
    for msg in messages:
        if msg.get('role') != 'system':
            prepared.append(msg)

    # Build system context
    system_parts = []

    # 1. Constitution (if available)
    try:
        constitution_path = Path.home() / ".opencli" / "CONSTITUTION.md"
        if constitution_path.exists():
            async def read_constitution():
                with open(constitution_path) as f:
                    return f.read()

            constitution = await asyncio.to_thread(read_constitution)
            system_parts.append("# OpenCLI Constitution\n\n" + constitution)
    except:
        pass

    # 2. AGENTS.md (if agent active)
    if hasattr(session, 'current_agent') and session.current_agent:
        try:
            agents_path = Path.cwd() / "AGENTS.md"
            if agents_path.exists():
                async def read_agents():
                    with open(agents_path) as f:
                        return f.read()

                agents_content = await asyncio.to_thread(read_agents)
                system_parts.append(f"# Active Agent: {session.current_agent}\n\n{agents_content}")
        except:
            pass

    # 3. Working directory
    cwd = os.getcwd()
    system_parts.append(f"# Working Directory\n\n{cwd}")

    # 4. Tool definitions
    try:
        from .tools import TOOLS
        tool_names = [t.get('name', 'unknown') for t in TOOLS]
        system_parts.append(f"# Available Tools\n\n{', '.join(tool_names)}")
    except:
        pass

    # Prepend system message
    if system_parts:
        system_content = "\n\n---\n\n".join(system_parts)
        prepared.insert(0, {
            'role': 'system',
            'content': system_content
        })

    return prepared


# REMOVED: create_message_handler() - now handled by ExecutionFlowManager.handle_user_prompt
# See cli/modules/execution_flow.py for the new implementation