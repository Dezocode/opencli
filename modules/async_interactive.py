"""
Async Interactive Mode for OpenCLI
Fully async architecture with Textual TUI integration
"""

import os
import json
import asyncio
import subprocess
import queue
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import httpx
from openai import AsyncOpenAI
from simple_tui import OpenCLITUI
from stream_buffer import StreamBuffer, BufferStatusDisplay

# Inline normalization function to avoid import issues
import uuid
from copy import deepcopy


# CRITICAL: Async wrapper for app.write() to prevent UI blocking
async def async_write(app, text, end="\n"):
    """Write to app - direct queue + ALWAYS yield for responsiveness"""
    # app.write() already queues writes in background thread (simple_tui.py:756)
    # Call directly - no extra threading needed
    app.write(text, end=end)

    # CRITICAL: ALWAYS yield to keep UI responsive during fast streaming
    # The queue batching (simple_tui.py:660) handles write efficiency
    # This yield ensures UI can update between chunks
    await asyncio.sleep(0)


async def write_markdown_response(app, markdown_text):
    """Write a complete markdown response (replaces plain text streaming)"""
    # Get the content widget and use its markdown renderer
    content = app._resolve_content_widget()
    if content and hasattr(content, '_markdown_renderer'):
        # Render markdown ONCE (not incrementally)
        rendered = content._markdown_renderer.render(markdown_text)

        # Add to content display
        if hasattr(content, '_lines'):
            content._lines.append(rendered)

            # Rebuild display with all lines
            from rich.text import Text
            display_text = Text()
            for line in content._lines:
                if isinstance(line, Text):
                    display_text.append_text(line)
                else:
                    display_text.append(str(line))

                # Add newline if not present
                if isinstance(line, Text):
                    if not line.plain.endswith("\n"):
                        display_text.append("\n")
                elif not line.endswith("\n"):
                    display_text.append("\n")

            content.update(display_text)
    else:
        # Fallback: write as plain text
        await async_write(app, markdown_text)

    await asyncio.sleep(0)  # Yield for UI update

def normalize_tool_call_messages(messages):
    """Return a sanitized copy of messages with well-formed tool call payloads."""
    normalized = []

    for original in messages:
        msg = deepcopy(original)

        if msg.get("role") == "assistant" and "tool_calls" in msg:
            # Providers expect an explicit string, not None
            if msg.get("content") is None:
                msg["content"] = ""

            tool_calls = []
            for call in msg.get("tool_calls") or []:
                if not isinstance(call, dict):
                    continue

                call_copy = deepcopy(call)
                call_copy.setdefault("type", "function")
                if not call_copy.get("type"):
                    call_copy["type"] = "function"

                call_copy.setdefault("id", f"call_{uuid.uuid4().hex[:8]}")

                function_payload = call_copy.get("function")
                if not isinstance(function_payload, dict):
                    function_payload = {}

                function_payload.setdefault("name", "")
                function_payload.setdefault("arguments", "")
                call_copy["function"] = function_payload

                tool_calls.append(call_copy)

            msg["tool_calls"] = tool_calls

        # Normalize tool result payloads as well
        if "tool_call_id" in msg:
            if msg.get("role") != "tool":
                msg["role"] = "tool"
            if msg.get("content") is None:
                msg["content"] = ""
            if not msg.get("tool_call_id") and msg.get("id"):
                msg["tool_call_id"] = msg["id"]

        normalized.append(msg)

    return normalized

# Debug function loaded (print statement removed - use /debug to enable debug mode)


def _flatten_message_content(content) -> str:
    """Convert message content into plain text for provider formats."""
    if content is None:
        return ""

    if isinstance(content, list):
        parts = []
        for segment in content:
            if isinstance(segment, dict):
                if segment.get("type") == "text":
                    parts.append(segment.get("text", ""))
                else:
                    parts.append(json.dumps(segment))
            else:
                parts.append(str(segment))
        return "\n".join(p for p in parts if p)

    return str(content)


def convert_messages_for_anthropic(messages: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    Convert OpenAI-style messages into Anthropic's Messages format.

    Returns:
        system_prompt: Unified system prompt string (or empty)
        conversation: List of message dicts for Anthropic API
    """
    system_segments: List[str] = []
    conversation: List[Dict] = []

    for msg in messages:
        role = msg.get("role")
        text = _flatten_message_content(msg.get("content"))

        if role == "system":
            if text:
                system_segments.append(text)
            continue

        if role == "tool":
            tool_id = msg.get("tool_call_id")
            prefix = f"Tool result ({tool_id}):" if tool_id else "Tool result:"
            text = f"{prefix}\n{text}" if text else prefix
            role = "user"

        tool_calls = msg.get("tool_calls") if isinstance(msg, dict) else None
        if role == "assistant" and tool_calls and not text:
            call_lines = []
            for tc in tool_calls:
                if isinstance(tc, dict):
                    func = tc.get("function", {})
                    name = func.get("name", "tool")
                    arguments = func.get("arguments", "")
                    args_text = arguments if isinstance(arguments, str) else json.dumps(arguments)
                    call_lines.append(f"[Tool call] {name}({args_text})")
            if call_lines:
                text = "\n".join(call_lines)

        if role not in ("user", "assistant"):
            role = "user"

        conversation.append({
            "role": role,
            "content": [{"type": "text", "text": text}]
        })

    system_prompt = "\n\n".join(system_segments).strip()
    return system_prompt, conversation


def extract_openrouter_policy_error(error: Exception) -> Optional[str]:
    """Check if exception indicates an OpenRouter data policy mismatch."""
    text = str(error)
    if not text:
        return None

    normalized = text.replace("\n", " ")
    marker = "No endpoints found matching your data"
    if marker in normalized:
        return normalized

    # Try to inspect response payload if available
    payload = getattr(error, "response", None)
    if payload:
        try:
            error_json = payload.json()
            message = error_json.get("error", {}).get("message")
            if message:
                normalized_msg = message.replace("\n", " ")
                if marker in normalized_msg:
                    return normalized_msg
        except Exception:
            pass

    return None


async def perform_anthropic_request(
    messages: List[Dict],
    session,
    config: Dict,
    *,
    timeout: Optional[float] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Execute a request against the Anthropic Messages API.

    Returns:
        (success, response_text, error_message)
    """
    system_prompt, conversation = convert_messages_for_anthropic(messages)

    if not conversation:
        return False, None, "No conversation messages available for Anthropic request"

    api_key = config.get("apiKey")
    if not api_key:
        return False, None, "Anthropic API key missing from configuration"

    # Derive sensible token limit
    max_tokens = config.get("anthropicMaxTokens")
    if not isinstance(max_tokens, int) or max_tokens <= 0:
        max_tokens = min(4096, max(config.get("contextWindow", 128000) // 4, 1024))

    payload: Dict = {
        "model": session.model or config.get("model"),
        "messages": conversation,
        "max_tokens": max_tokens,
    }

    if system_prompt:
        payload["system"] = system_prompt

    base_url = (config.get("baseURL") or "").rstrip("/")
    if not base_url:
        return False, None, "Anthropic base URL missing from configuration"

    default_headers = config.get("defaultHeaders") or {}
    headers = {
        "x-api-key": api_key,
        "anthropic-version": default_headers.get("anthropic-version", "2023-06-01"),
    }

    # Allow additional user-defined headers
    for key, value in default_headers.items():
        headers.setdefault(key, value)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}/messages",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as e:
        return False, None, f"Anthropic API error: {e.response.status_code} {e.response.text}"
    except Exception as e:
        return False, None, f"Anthropic request failed: {e}"

    text_parts: List[str] = []
    for block in data.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            text_parts.append(block.get("text", ""))

    reply_text = "\n".join(part for part in text_parts if part).strip()
    return True, reply_text, None

try:
    from .frontier_colors import FRONTIER_COLORS
except (ImportError, ValueError):
    try:
        from frontier_colors import FRONTIER_COLORS
    except ImportError:
        FRONTIER_COLORS = {}


# Tool execution functions (from opencli.py)
def execute_read(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {file_path}: {str(e)}"

def execute_write(file_path, content):
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"✓ Written to {file_path}"
    except Exception as e:
        return f"Error writing to {file_path}: {str(e)}"

def execute_edit(file_path, old_string, new_string):
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        if old_string not in content:
            return f"Error: old_string not found in {file_path}"

        new_content = content.replace(old_string, new_string, 1)

        with open(file_path, 'w') as f:
            f.write(new_content)

        return f"✓ Edited {file_path}"
    except Exception as e:
        return f"Error editing {file_path}: {str(e)}"

async def execute_bash_async(command, description=None, timeout=30, current_dir=None, debug=False):
    """Non-blocking async bash execution"""
    try:
        # Set working directory if provided
        cwd = current_dir if current_dir else os.getcwd()

        if debug:
            print(f"[BASH ASYNC] Creating subprocess for: {command} in {cwd}")

        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )

        if debug:
            print(f"[BASH ASYNC] Subprocess created, waiting for output (timeout={timeout}s)...")

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            if debug:
                print(f"[BASH ASYNC] Got output: stdout={len(stdout)} bytes, stderr={len(stderr)} bytes")
            output = stdout.decode() + stderr.decode()
            return output if output else f"✓ Command executed: {command}"
        except asyncio.TimeoutError:
            if debug:
                print(f"[BASH ASYNC] TIMEOUT after {timeout}s")
            proc.kill()
            await proc.wait()
            return f"⏱ Command timed out after {timeout}s"

    except Exception as e:
        if debug:
            print(f"[BASH ASYNC] EXCEPTION: {e}")
        return f"Error executing command: {str(e)}"

def execute_bash(command, description=None):
    """Sync wrapper for bash - kept for compatibility"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return output if output else f"✓ Command executed: {command}"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after 30s"
    except Exception as e:
        return f"Error executing command: {str(e)}"

def execute_glob(pattern):
    from glob import glob
    files = glob(pattern, recursive=True)
    return "\n".join(files) if files else f"No files match pattern: {pattern}"

async def execute_grep_async(pattern, timeout=10):
    """Non-blocking async grep execution"""
    try:
        proc = await asyncio.create_subprocess_shell(
            f'grep -r "{pattern}" .',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            output = stdout.decode()
            return output if output else f"No matches for: {pattern}"
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return f"⏱ Grep timed out after {timeout}s"

    except Exception as e:
        return f"Error: {str(e)}"

def execute_grep(pattern):
    """Sync wrapper for grep - kept for compatibility"""
    try:
        result = subprocess.run(
            f'grep -r "{pattern}" .',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout if result.stdout else f"No matches for: {pattern}"
    except Exception as e:
        return f"Error: {str(e)}"

async def execute_tool_async(name, args, permission_manager=None, current_dir=None, app=None):
    """
    Execute a tool asynchronously without blocking the event loop

    Uses asyncio.to_thread for file I/O and subprocess for Bash/Grep

    NOTE: Permission checks should be done BEFORE calling this function
    """
    debug_mode = hasattr(app, 'session') and hasattr(app.session, 'debug_mode') and app.session.debug_mode if app else False

    try:
        if debug_mode and app:
            app.write(f"[dim]🐛 TOOL EXEC: Entering execute_tool_async for {name}[/dim]\n")

        if name == "Read":
            # Run file I/O in thread pool to avoid blocking
            if debug_mode and app:
                app.write(f"[dim]🐛 TOOL EXEC: About to read file {args['file_path']}[/dim]\n")
            return await asyncio.to_thread(execute_read, args["file_path"])

        elif name == "Write":
            return await asyncio.to_thread(execute_write, args["file_path"], args["content"])

        elif name == "Edit":
            return await asyncio.to_thread(execute_edit, args["file_path"], args["old_string"], args["new_string"])

        elif name == "Bash":
            # Use async subprocess for bash commands
            if debug_mode and app:
                app.write(f"[dim]🐛 TOOL EXEC: About to run bash command: {args['command']}[/dim]\n")
            result = await execute_bash_async(args["command"], args.get("description"), current_dir=current_dir)
            if debug_mode and app:
                app.write(f"[dim]🐛 TOOL EXEC: Bash command returned[/dim]\n")
            return result

        elif name == "Glob":
            # Glob is fast, run in thread pool
            return await asyncio.to_thread(execute_glob, args["pattern"])

        elif name == "Grep":
            # Use async subprocess for grep
            return await execute_grep_async(args["pattern"])

        else:
            return f"Unknown tool: {name}"

    except Exception as e:
        return f"Error executing {name}: {str(e)}"

def execute_tool(name, args, permission_manager=None, current_dir=None, app=None):
    """Synchronous tool execution - kept for non-async contexts"""

    # CRITICAL DEBUG - This should NOT be called in TUI mode!
    import sys
    sys.stderr.write(f"\n⚠️⚠️⚠️ SYNC execute_tool CALLED (WRONG!): {name}\n")
    sys.stderr.write(f"This is the OLD synchronous version - TUI should use execute_tool_async!\n")
    sys.stderr.flush()

    if app:
        app.write(f"[red]⚠️ SYNC execute_tool called for {name} - should use async version![/red]\n")

    # Execute the tool (no permission checks in sync version - TUI should use async!)
    tools = {
        "Read": lambda: execute_read(args["file_path"]),
        "Write": lambda: execute_write(args["file_path"], args["content"]),
        "Edit": lambda: execute_edit(args["file_path"], args["old_string"], args["new_string"]),
        "Bash": lambda: execute_bash(args["command"], args.get("description")),
        "Glob": lambda: execute_glob(args["pattern"]),
        "Grep": lambda: execute_grep(args["pattern"])
    }

    return tools.get(name, lambda: f"Unknown tool: {name}")()


async def prepare_messages_with_context(messages, config, spec_memory=None, goal_tracker=None):
    """
    Prepare messages with system context (constitution + AGENTS.md + cwd + GOAL CONTEXT)
    ALWAYS adds fresh system message - removes old one if exists

    NOW ASYNC - Uses asyncio.to_thread for all file I/O to prevent blocking!
    """
    # Remove any existing system messages (we'll add a fresh one)
    messages_without_system = [m for m in messages if m.get('role') != 'system']

    # Load essential context
    config_dir = Path.home() / '.opencli'
    constitution_file = config_dir / 'agents' / 'system_prompts' / 'base' / 'constitution.md'
    agents_template = config_dir / 'agents' / 'system_prompts' / 'base' / 'AGENTS.md'

    # Build system message
    system_parts = []

    # Add constitution (tool guides) - ASYNC FILE READ
    if constitution_file.exists():
        constitution_content = await asyncio.to_thread(constitution_file.read_text)
        system_parts.append(constitution_content)

    # Add AGENTS.md (project context or template)
    # First try to find project-specific AGENTS.md
    cwd = os.getcwd()
    current = Path(cwd)
    agents_md_content = None

    for parent in [current] + list(current.parents):
        agents_file = parent / 'AGENTS.md'
        if agents_file.exists():
            agents_md_content = await asyncio.to_thread(agents_file.read_text)
            break

    # If no project AGENTS.md, use template - ASYNC FILE READ
    if not agents_md_content and agents_template.exists():
        agents_md_content = await asyncio.to_thread(agents_template.read_text)

    if agents_md_content:
        system_parts.append(f"\n## Project Context\n{agents_md_content}")

    # Add Spec-Kit context (constitution, goals, plans)
    if spec_memory:
        spec_context = spec_memory.format_context_for_system_message()
        if spec_context:
            system_parts.append(f"\n## Spec-Kit Context\n{spec_context}")

    # Add current goal context
    if goal_tracker and goal_tracker.current_goal:
        goal_context = goal_tracker.get_context_for_system_message()
        system_parts.append(goal_context)

    # Add working directory
    system_parts.append(f"\nWorking directory: {cwd}")

    # Add available tools as context (prevents OpenRouter provider routing)
    import json
    tools_json = json.dumps(TOOLS, indent=2)
    system_parts.append(f"\n## Available Tools\nYou have access to these tools. Respond with tool_calls in your message when you want to use them:\n```json\n{tools_json}\n```")

    # Create system message
    system_message = {
        'role': 'system',
        'content': '\n'.join(system_parts)
    }

    # Normalize tool call payloads to match provider expectations
    normalized_messages = normalize_tool_call_messages(messages_without_system)

    # Return messages with system message first (always fresh)
    return [system_message] + normalized_messages


async def interactive_async(config, session=None, initial_prompt=None):
    """
    Async interactive mode with Textual TUI

    Args:
        config: OpenCLI configuration dict
        session: Session object (created if None)
        initial_prompt: Optional initial prompt string
    """
    # Create session if not provided (same as fallback mode)
    if not session:
        # Create a minimal Session object inline
        import uuid

        class Session:
            def __init__(self, model=None):
                self.session_id = str(uuid.uuid4())
                self.messages = []
                self.model = model
                self.cwd = os.getcwd()
                self.current_agent = 'assistant'
                self.permission_manager = None
                self.debug_mode = False

            def add(self, role, content):
                self.messages.append({"role": role, "content": content})

            def save(self):
                # Save to sessions directory
                sessions_dir = Path.home() / '.opencli' / 'sessions'
                sessions_dir.mkdir(parents=True, exist_ok=True)
                with open(sessions_dir / f"{self.session_id}.json", 'w') as f:
                    json.dump({
                        "session_id": self.session_id,
                        "model": self.model,
                        "messages": self.messages,
                        "cwd": self.cwd,
                        "debug_mode": getattr(self, 'debug_mode', False),
                        "timestamp": datetime.now().isoformat()
                    }, f)

        session = Session(model=config["model"])

    # Tool definitions - MUST match opencli.py exactly
    TOOLS = [
        {"type": "function", "function": {"name": "Read", "description": "Read file contents. Safe tool, auto-executes.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}}},
        {"type": "function", "function": {"name": "Write", "description": "Write to file. [REQUIRES PERMISSION] User will be prompted to approve this operation.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["file_path", "content"]}}},
        {"type": "function", "function": {"name": "Edit", "description": "Edit file by replacing text. [REQUIRES PERMISSION] User will be prompted to approve this operation.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}, "old_string": {"type": "string"}, "new_string": {"type": "string"}}, "required": ["file_path", "old_string", "new_string"]}}},
        {"type": "function", "function": {"name": "Bash", "description": "Execute bash command. [REQUIRES PERMISSION] User will be prompted to approve this command before execution.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}, "description": {"type": "string"}}, "required": ["command"]}}},
        {"type": "function", "function": {"name": "Glob", "description": "Find files by pattern. Safe tool, auto-executes.", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]}}},
        {"type": "function", "function": {"name": "Grep", "description": "Search files for pattern. Safe tool, auto-executes.", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]}}},
    ]

    def create_async_client(current_config):
        """Factory to create AsyncOpenAI client with provider defaults."""
        headers = current_config.get("defaultHeaders") or None
        return AsyncOpenAI(
            base_url=current_config["baseURL"],
            api_key=current_config["apiKey"],
            default_headers=headers
        )

    # Create async client with provider-specific headers
    client = create_async_client(config)

    # Initialize permission manager (same as fallback mode)
    TOOL_PERMISSIONS = False
    try:
        from .tool_permissions import ToolPermissionManager
        from .async_permissions import AsyncPermissionHandler, set_global_handler
        TOOL_PERMISSIONS = True
    except (ImportError, ValueError):
        try:
            from tool_permissions import ToolPermissionManager
            from async_permissions import AsyncPermissionHandler, set_global_handler
            TOOL_PERMISSIONS = True
        except ImportError:
            pass

    if TOOL_PERMISSIONS and (not hasattr(session, 'permission_manager') or session.permission_manager is None):
        config_dir = Path.home() / '.opencli'
        session.permission_manager = ToolPermissionManager(config_dir)

    # Store flag on session for use in tool execution loop
    session.tool_permissions_enabled = TOOL_PERMISSIONS

    # Initialize agent manager for context management (same as fallback mode)
    agent_manager = None
    try:
        from .agent_manager import AgentManager
    except (ImportError, ValueError):
        try:
            from agent_manager import AgentManager
        except ImportError:
            pass

    if AgentManager:
        try:
            config_dir = Path.home() / '.opencli'
            agent_manager = AgentManager(config_dir)
            if not hasattr(session, 'current_agent') or not session.current_agent:
                session.current_agent = 'assistant'
        except Exception as e:
            print(f"Warning: Agent manager initialization failed: {e}")

    # Initialize Spec-Kit goal tracking system
    spec_memory = None
    goal_tracker = None
    try:
        from .spec_memory import SpecMemory
        from .goal_tracker import GoalTracker
    except (ImportError, ValueError):
        try:
            from spec_memory import SpecMemory
            from goal_tracker import GoalTracker
        except ImportError:
            pass

    if SpecMemory and GoalTracker:
        try:
            spec_memory = SpecMemory(project_root=Path(session.cwd if hasattr(session, 'cwd') else os.getcwd()))
            goal_tracker = GoalTracker(
                session_id=session.session_id,
                spec_memory=spec_memory,
                verbose=getattr(session, 'debug_mode', False)
            )
            session.spec_memory = spec_memory
            session.goal_tracker = goal_tracker
        except Exception as e:
            print(f"Warning: Goal tracking initialization failed: {e}")

    # Create TUI - color mode is configured automatically in __init__
    app = OpenCLITUI(session=session, config=config)

    # Initialize async permission handler for TUI (AFTER app is created)
    try:
        from .async_permissions import AsyncPermissionHandler, set_global_handler
    except (ImportError, ValueError):
        from async_permissions import AsyncPermissionHandler, set_global_handler

    permission_handler = AsyncPermissionHandler(session.permission_manager, app)
    set_global_handler(permission_handler)
    app.permission_handler = permission_handler

    # Store initial prompt for processing after TUI starts
    app.initial_prompt = initial_prompt

    # Auto-initialize models if API key exists but no models registered
    try:
        from .model_manager import ModelManager
    except (ImportError, ValueError):
        from model_manager import ModelManager

    model_mgr = ModelManager()
    keys = model_mgr.get_configured_keys()
    models = model_mgr.list_available_models()

    # If we have an OpenRouter key but no models, fetch them
    if "openrouter" in keys and not models:
        async def auto_init_models():
            """Auto-fetch models on first run"""
            await asyncio.sleep(0.5)  # Let TUI mount first
            app.write("[dim]Detecting API key... fetching available models...[/dim]\n")

            result = await model_mgr.fetch_models_from_openrouter(keys["openrouter"])

            if result["success"]:
                model_mgr.add_api_key("openrouter", keys["openrouter"])
                model_mgr.register_models("openrouter", result["models"])
                app.write(f"[green]✓ Registered {result['count']} models from OpenRouter[/green]\n\n")
                app.write("Use [cyan]/model[/cyan] to see available models\n\n")
            else:
                app.write(f"[yellow]⚠ Could not fetch models: {result['error']}[/yellow]\n\n")

        # Schedule auto-init after TUI mounts
        asyncio.create_task(auto_init_models())

    # Setup message handler
    async def handle_user_input(user_input: str):
        """Handle user input and generate response"""
        nonlocal client

        # Handle pending provider header prompts before other logic
        if hasattr(session, '_pending_header_update') and session._pending_header_update:
            pending = session._pending_header_update
            fields = pending.get("fields", [])
            index = pending.get("index", 0)
            if index < len(fields):
                field = fields[index]
                value = user_input.strip()
                current_headers = pending.get("current", {}) or {}

                if not value and field in current_headers:
                    value = current_headers[field]

                pending.setdefault("collected", {})[field] = value
                pending["index"] = index + 1

                if hasattr(app, 'stream_display'):
                    app.stream_display.remove_permission_prompt()

                if pending["index"] < len(fields):
                    next_field = fields[pending["index"]]
                    current_value = pending.get("current", {}).get(next_field, "")
                    if hasattr(app, 'stream_display'):
                        app.stream_display.add_permission_prompt({
                            "title": "Configure Provider Headers",
                            "message": f"Enter value for {next_field}. Leave blank to keep existing value.",
                            "details": {
                                "current": current_value or "[unset]"
                            },
                            "options": []
                        })
                    else:
                        app.write(f"[cyan]Enter value for {next_field} (leave blank to keep existing):[/cyan]\n")
                else:
                    provider_id = pending.get("provider", "openrouter")
                    collected = {k: v for k, v in pending.get("collected", {}).items() if v}

                    try:
                        # Create local ModelManager instance
                        try:
                            from .model_manager import ModelManager
                        except (ImportError, ValueError):
                            from model_manager import ModelManager

                        local_mgr = ModelManager()
                        local_mgr.update_provider_headers(provider_id, collected, None)
                        config.update(local_mgr.config)
                        app.config = config
                        client = create_async_client(config)
                        if collected:
                            app.write(f"[green]✓ Updated {provider_id} headers.[/green]\n")
                        else:
                            app.write(f"[yellow]⚠️ No header changes applied.[/yellow]\n")
                        app.write("[dim]Re-run your last message to continue streaming.[/dim]\n\n")
                    except Exception as e:
                        app.write(f"[red]Failed to update headers: {e}[/red]\n\n")

                    session._pending_header_update = None

            return

        # Handle exit commands
        if user_input.lower() in ['exit', 'quit', '/exit', '/quit']:
            app.should_exit = True
            app.exit()
            return

        # Check if awaiting model confirmation (y/n)
        if hasattr(session, '_awaiting_model_confirm') and session._awaiting_model_confirm:
            model_id = session._awaiting_model_confirm
            response = user_input.strip().lower()

            # Clear flag
            session._awaiting_model_confirm = None

            if response in ['y', 'yes']:
                try:
                    from .model_manager import ModelManager
                except (ImportError, ValueError):
                    from model_manager import ModelManager

                local_model_mgr = ModelManager()
                result = local_model_mgr.switch_model(session, model_id)

                if result["success"]:
                    app.write(f"[green]✓ Switched to {result['model']}[/green]\n\n")

                    # Refresh runtime config from model manager
                    config.update(local_model_mgr.config)
                    app.config = config

                    # Show pricing info
                    if "pricing" in result:
                        pricing = result["pricing"]
                        prompt_cost = pricing.get("prompt", "?")
                        completion_cost = pricing.get("completion", "?")

                        # Build pricing message
                        pricing_parts = []

                        if prompt_cost == "0":
                            pricing_parts.append("FREE (prompt)")
                        elif prompt_cost != "?":
                            prompt_per_1m = float(prompt_cost) * 1_000_000
                            pricing_parts.append(f"${prompt_per_1m:.2f}/1M prompt tokens")

                        if completion_cost == "0":
                            pricing_parts.append("FREE (completion)")
                        elif completion_cost != "?":
                            completion_per_1m = float(completion_cost) * 1_000_000
                            pricing_parts.append(f"${completion_per_1m:.2f}/1M completion tokens")

                        if pricing_parts:
                            app.write(f"[dim]💰 Pricing: {', '.join(pricing_parts)}[/dim]\n\n")

                    # Recreate client with new provider headers
                    client = create_async_client(config)
                    app.update_status()
                else:
                    app.write(f"[red]✗ {result['error']}[/red]\n\n")
            else:
                app.write("[dim]Model switch cancelled.[/dim]\n\n")

            return

        # Check if awaiting API key input
        if hasattr(session, '_awaiting_api_key') and session._awaiting_api_key:
            try:
                from .model_manager import ModelManager
            except (ImportError, ValueError):
                from model_manager import ModelManager

            local_model_mgr = ModelManager()
            api_key = user_input.strip()

            # Clear flag
            session._awaiting_api_key = False

            app.write("[dim]Validating key and fetching models...[/dim]\n")

            # Fetch models from OpenRouter
            result = await local_model_mgr.fetch_models_from_openrouter(api_key)

            if result["success"]:
                # Register models
                local_model_mgr.add_api_key("openrouter", api_key)
                local_model_mgr.register_models("openrouter", result["models"])

                app.write(f"[green]✓ API key added![/green]\n")
                app.write(f"[green]✓ Registered {result['count']} models[/green]\n\n")
                app.write("Use [cyan]/model[/cyan] to see available models\n\n")
            else:
                app.write(f"[red]✗ Failed: {result['error']}[/red]\n\n")

            return

        # Check if awaiting provider key input
        if hasattr(session, '_awaiting_provider_key') and session._awaiting_provider_key:
            try:
                from .model_manager import ModelManager
            except (ImportError, ValueError):
                from model_manager import ModelManager

            local_model_mgr = ModelManager()
            api_key = user_input.strip()

            # Clear flag
            session._awaiting_provider_key = False

            # Auto-detect provider
            provider = local_model_mgr.detect_provider(api_key)

            if not provider:
                app.write("[red]✗ Could not detect provider from API key format[/red]\n\n")
                app.write("Supported key formats:\n")
                app.write("  • OpenRouter: sk-or-...\n")
                app.write("  • Anthropic: sk-ant-...\n")
                app.write("  • OpenAI: sk-proj-... or sk-...\n")
                app.write("  • DeepSeek: sk-...\n")
                app.write("  • Google AI: AIza...\n\n")
                return

            provider_info = local_model_mgr.models_db.get("providers", {}).get(provider, {})
            provider_name = provider_info.get("name", provider)

            app.write(f"[green]✓ Detected provider: {provider_name}[/green]\n")
            app.write("[dim]Fetching models...[/dim]\n\n")

            # Fetch models from provider
            result = await local_model_mgr.fetch_models_from_provider(provider, api_key)

            if result["success"]:
                local_model_mgr.add_api_key(provider, api_key)
                local_model_mgr.register_models(provider, result["models"])

                app.write(f"[green]✓ Added {provider_name}![/green]\n")
                app.write(f"[green]✓ Registered {result['count']} models[/green]\n\n")
                app.write("Use [cyan]/model[/cyan] to see and switch to these models\n\n")
            else:
                app.write(f"[red]✗ Failed to fetch models: {result['error']}[/red]\n\n")

            return

        # Handle slash commands
        if user_input.startswith('/'):
            # Handle /debug command - toggle debug mode
            if user_input.startswith('/debug'):
                session.debug_mode = not session.debug_mode
                status = "enabled" if session.debug_mode else "disabled"
                color = "green" if session.debug_mode else "yellow"
                app.write(f"[{color}]🐛 Debug mode {status}[/{color}]\n\n")
                if session.debug_mode:
                    app.write("[dim]Debug logs will show:\n")
                    app.write("  • 🐛 STALL DEBUG - Async operation boundaries\n")
                    app.write("  • 🔍 DEBUG - Message structure and API calls\n")
                    app.write("  • 🚨 EXTREME DEBUG - Full JSON payloads\n\n")
                return

            # Handle /performance command - toggle performance monitoring
            if user_input.startswith('/performance'):
                try:
                    from .performance_monitor import get_monitor
                except (ImportError, ValueError):
                    from performance_monitor import get_monitor

                perf_monitor = get_monitor()

                # Parse subcommand
                parts = user_input.split(maxsplit=1)
                subcommand = parts[1] if len(parts) > 1 else None

                if subcommand == "report":
                    # Show detailed report
                    app.write(perf_monitor.get_detailed_report())
                    return

                if subcommand == "fast":
                    # Toggle fast mode (skip markdown rendering for speed)
                    if not hasattr(session, 'fast_mode'):
                        session.fast_mode = False

                    session.fast_mode = not session.fast_mode
                    status = "enabled" if session.fast_mode else "disabled"
                    color = "green" if session.fast_mode else "yellow"

                    app.write(f"[{color}]⚡ Fast mode {status}[/{color}]\n\n")
                    if session.fast_mode:
                        app.write("[dim]Optimizations enabled:\n")
                        app.write("  • Skipped markdown post-processing\n")
                        app.write("  • Raw text rendering only\n")
                        app.write("  • Maximum token throughput\n\n")
                        app.write("⚠️ Note: Markdown formatting will not render\n\n")
                    else:
                        app.write("[dim]Markdown rendering restored\n\n")
                    return

                # Toggle monitoring via statusline widget
                try:
                    from .simple_tui import PerformanceStatusLine
                except (ImportError, ValueError):
                    from simple_tui import PerformanceStatusLine

                try:
                    perf_statusline = app.query_one(PerformanceStatusLine)
                    is_enabled = perf_statusline.toggle()

                    if is_enabled:
                        app.write("[green]📊 Performance monitoring enabled[/green]\n\n")
                        app.write("[dim]Live statusline active beneath prompt showing:\n")
                        app.write("  • 🟢 CPU usage and trend (↗️↘️→)\n")
                        app.write("  • 💾 Memory usage (MB)\n")
                        app.write("  • 🧵 Thread count\n")
                        app.write("  • ⚡ Token streaming speed (tok/s)\n")
                        app.write("  • 🔴 Current bottlenecks (if any)\n\n")
                        app.write("Use [cyan]/performance report[/cyan] for detailed analysis\n")
                        app.write("Use [cyan]/performance fast[/cyan] to toggle fast mode\n\n")
                    else:
                        app.write("[yellow]📊 Performance monitoring disabled[/yellow]\n\n")
                except Exception as e:
                    app.write(f"[red]Error: Could not toggle performance monitor: {e}[/red]\n\n")

                return

            # Handle /model command locally
            if user_input.startswith('/model'):
                try:
                    from .model_manager import ModelManager
                except (ImportError, ValueError):
                    from model_manager import ModelManager

                local_model_mgr = ModelManager()

                # Parse args
                parts = user_input.split(maxsplit=1)
                args = parts[1] if len(parts) > 1 else None

                if not args:
                    # Refresh models from OpenRouter to get latest rankings/pricing
                    keys = local_model_mgr.get_configured_keys()
                    if "openrouter" in keys:
                        app.write("[dim]Refreshing models from OpenRouter...[/dim]\n")
                        result = await local_model_mgr.fetch_models_from_openrouter(keys["openrouter"])
                        if result["success"]:
                            local_model_mgr.register_models("openrouter", result["models"])
                            app.write("[dim]✓ Updated {count} models[/dim]\n\n".format(count=result["count"]))

                    # Show available models (only those with keys)
                    current = local_model_mgr.get_current_model(session)
                    models = local_model_mgr.list_available_models()
                    recent = local_model_mgr.get_recent_models()

                    if not models:
                        app.write("[yellow]⚠ No models available[/yellow]\n\n")
                        app.write("Add an API key first:\n")
                        app.write("  [cyan]/model add[/cyan]\n\n")
                        return

                    # Get provider info
                    providers = local_model_mgr.get_providers()
                    provider_names = {p["id"]: p["name"] for p in providers}

                    # Show recently used models first
                    if recent:
                        app.write("[bold magenta]⭐ Recently Used:[/bold magenta]\n\n")

                        for idx, model in enumerate(recent[:5], 1):  # Top 5 recent
                            marker = "→" if model["id"] == current else " "
                            context = f"{model['context']//1000}K" if model['context'] else "?"
                            provider = model.get("provider", "unknown")
                            provider_name = provider_names.get(provider, provider)

                            # Check if free
                            pricing = model.get("pricing", {})
                            is_free = ":free" in model["id"] or pricing.get("prompt") == "0"
                            free_badge = " [green]FREE[/green]" if is_free else ""

                            app.write(f"{marker} [bold]r{idx}.[/bold] {model['name']}{free_badge}\n")
                            app.write(f"     ID: [dim]{model['id']}[/dim]\n")
                            app.write(f"     Provider: [cyan]{provider_name}[/cyan] | Context: {context}\n\n")

                        app.write("\n")

                    app.write("[bold cyan]📋 All Available Models:[/bold cyan]\n\n")

                    for idx, model in enumerate(models, 1):
                        marker = "→" if model["id"] == current else " "
                        context = f"{model['context']//1000}K" if model['context'] else "?"
                        provider = model.get("provider", "unknown")
                        provider_name = provider_names.get(provider, provider)

                        # Check if free
                        pricing = model.get("pricing", {})
                        is_free = ":free" in model["id"] or pricing.get("prompt") == "0"
                        free_badge = " [green]FREE[/green]" if is_free else ""

                        app.write(f"{marker} [bold]{idx}.[/bold] {model['name']}{free_badge}\n")
                        app.write(f"     ID: [dim]{model['id']}[/dim]\n")
                        app.write(f"     Provider: [cyan]{provider_name}[/cyan] | Context: {context}\n\n")

                    app.write("\n[dim]Usage: /model <number> or /model r<number> (recent)  or  /model add[/dim]\n\n")

                elif args == "add":
                    # Interactive API key setup
                    app.write("[bold]🔑 Add API Key[/bold]\n\n")
                    app.write("Enter your OpenRouter API key:\n")
                    app.write("[dim](Get one at https://openrouter.ai/keys)[/dim]\n\n")

                    # Prompt for key on next input - set a flag
                    app.write("[yellow]Type your key and press Enter:[/yellow]\n")
                    session._awaiting_api_key = True

                else:
                    # Switch model by number or ID
                    models = local_model_mgr.list_available_models()
                    recent = local_model_mgr.get_recent_models()

                    if not models:
                        app.write("[red]No models available. Use /model add first.[/red]\n\n")
                        return

                    # Check if recent model selection (r1, r2, etc.)
                    if args.lower().startswith('r') and args[1:].isdigit():
                        idx = int(args[1:]) - 1
                        if 0 <= idx < len(recent):
                            model_id = recent[idx]["id"]
                            selected_model = recent[idx]
                        else:
                            app.write(f"[red]✗ Invalid recent model number: {args}[/red]\n\n")
                            return
                    # Check if numeric selection from all models
                    elif args.isdigit():
                        idx = int(args) - 1
                        if 0 <= idx < len(models):
                            model_id = models[idx]["id"]
                            selected_model = models[idx]
                        else:
                            app.write(f"[red]✗ Invalid model number: {args}[/red]\n\n")
                            return
                    # Model ID directly
                    else:
                        model_id = args
                        # Find in models list for pricing check
                        selected_model = None
                        for m in models:
                            if m["id"] == model_id:
                                selected_model = m
                                break

                    # Check if paid model - show confirmation
                    if selected_model:
                        pricing = selected_model.get("pricing", {})
                        is_free = ":free" in selected_model["id"] or pricing.get("prompt") == "0"

                        if not is_free:
                            # Calculate readable pricing
                            prompt_cost = pricing.get("prompt", "?")
                            completion_cost = pricing.get("completion", "?")

                            app.write(f"[yellow]⚠️  PAID MODEL WARNING[/yellow]\n\n")
                            app.write(f"Model: [bold]{selected_model['name']}[/bold]\n")

                            if prompt_cost != "?":
                                prompt_per_1m = float(prompt_cost) * 1_000_000
                                app.write(f"Prompt: [yellow]${prompt_per_1m:.2f}/1M tokens[/yellow]\n")
                            if completion_cost != "?":
                                completion_per_1m = float(completion_cost) * 1_000_000
                                app.write(f"Completion: [yellow]${completion_per_1m:.2f}/1M tokens[/yellow]\n\n")

                            app.write("[yellow]Switch to this paid model? (y/n):[/yellow]\n")

                            # Set flag to await y/n response
                            session._awaiting_model_confirm = model_id
                            return

                    result = local_model_mgr.switch_model(session, model_id)

                    if result["success"]:
                        app.write(f"[green]✓ Switched to {result['model']}[/green]\n\n")

                        # Refresh runtime config
                        config.update(local_model_mgr.config)
                        app.config = config

                        # Show pricing info if available
                        if "pricing" in result:
                            pricing = result["pricing"]
                            prompt_cost = pricing.get("prompt", "?")
                            completion_cost = pricing.get("completion", "?")

                            # Build pricing message
                            pricing_parts = []

                            # Prompt pricing
                            if prompt_cost == "0":
                                pricing_parts.append("FREE (prompt)")
                            elif prompt_cost != "?":
                                prompt_per_1m = float(prompt_cost) * 1_000_000
                                pricing_parts.append(f"${prompt_per_1m:.2f}/1M prompt tokens")

                            # Completion pricing
                            if completion_cost == "0":
                                pricing_parts.append("FREE (completion)")
                            elif completion_cost != "?":
                                completion_per_1m = float(completion_cost) * 1_000_000
                                pricing_parts.append(f"${completion_per_1m:.2f}/1M completion tokens")

                            if pricing_parts:
                                app.write(f"[dim]💰 Pricing: {', '.join(pricing_parts)}[/dim]\n\n")

                        # Recreate client with new provider headers
                        client = create_async_client(config)
                        app.update_status()
                    else:
                        app.write(f"[red]✗ {result['error']}[/red]\n\n")

                return

            # Handle /providers command locally
            if user_input.startswith('/providers'):
                try:
                    from .model_manager import ModelManager
                except (ImportError, ValueError):
                    from model_manager import ModelManager

                providers_mgr = ModelManager()

                # Parse args
                parts = user_input.split(maxsplit=2)
                subcommand = parts[1] if len(parts) > 1 else None
                args = parts[2] if len(parts) > 2 else None

                if not subcommand or subcommand == "list":
                    # List all providers with status
                    providers = providers_mgr.get_providers()

                    app.write("[bold cyan]🔌 API Providers[/bold cyan]\n\n")

                    for provider in providers:
                        status = "[green]✓ Configured[/green]" if provider["has_key"] else "[dim]Not configured[/dim]"
                        model_count = provider.get("model_count", 0)
                        models_text = f"({model_count} models)" if provider["has_key"] else ""

                        app.write(f"[bold]{provider['name']}[/bold] {status} {models_text}\n")
                        app.write(f"  ID: [dim]{provider['id']}[/dim]\n\n")

                    app.write("\n[dim]Usage:[/dim]\n")
                    app.write("  [cyan]/providers add[/cyan]          Add new provider key\n")
                    app.write("  [cyan]/providers add <key>[/cyan]   Add specific key (auto-detects provider)\n")
                    app.write("  [cyan]/providers remove <id>[/cyan] Remove provider key\n\n")

                elif subcommand == "add":
                    if not args:
                        # Interactive mode - prompt for key
                        app.write("[bold]🔑 Add Provider API Key[/bold]\n\n")
                        app.write("Paste your API key and I'll auto-detect the provider:\n")
                        app.write("[dim](Supports: OpenRouter, Anthropic, OpenAI, DeepSeek, Google AI)[/dim]\n\n")
                        app.write("[yellow]Type your key and press Enter:[/yellow]\n")

                        # Set flag to await provider key
                        session._awaiting_provider_key = True
                    else:
                        # Direct key provided - detect and add
                        api_key = args.strip()
                        provider = providers_mgr.detect_provider(api_key)

                        if not provider:
                            app.write("[red]✗ Could not detect provider from API key format[/red]\n\n")
                            app.write("Supported key formats:\n")
                            app.write("  • OpenRouter: sk-or-...\n")
                            app.write("  • Anthropic: sk-ant-...\n")
                            app.write("  • OpenAI: sk-proj-... or sk-...\n")
                            app.write("  • DeepSeek: sk-...\n")
                            app.write("  • Google AI: AIza...\n\n")
                            return

                        provider_info = providers_mgr.models_db.get("providers", {}).get(provider, {})
                        provider_name = provider_info.get("name", provider)

                        app.write(f"[green]✓ Detected provider: {provider_name}[/green]\n")
                        app.write("[dim]Fetching models...[/dim]\n\n")

                        # Fetch models from provider
                        result = await providers_mgr.fetch_models_from_provider(provider, api_key)

                        if result["success"]:
                            providers_mgr.add_api_key(provider, api_key)
                            providers_mgr.register_models(provider, result["models"])

                            app.write(f"[green]✓ Added {provider_name}![/green]\n")
                            app.write(f"[green]✓ Registered {result['count']} models[/green]\n\n")
                            app.write("Use [cyan]/model[/cyan] to see and switch to these models\n\n")
                        else:
                            app.write(f"[red]✗ Failed to fetch models: {result['error']}[/red]\n\n")

                elif subcommand == "remove":
                    if not args:
                        app.write("[red]✗ Specify provider ID to remove[/red]\n\n")
                        app.write("Example: [cyan]/providers remove openrouter[/cyan]\n\n")
                        return

                    provider_id = args.strip()
                    providers = providers_mgr.models_db.get("providers", {})

                    if provider_id not in providers:
                        app.write(f"[red]✗ Unknown provider: {provider_id}[/red]\n\n")
                        return

                    # Remove the key
                    if provider_id in providers_mgr.models_db.get("api_keys", {}):
                        del providers_mgr.models_db["api_keys"][provider_id]
                        providers_mgr._save_models()
                        app.write(f"[green]✓ Removed {provider_id} API key[/green]\n\n")
                    else:
                        app.write(f"[yellow]⚠ {provider_id} was not configured[/yellow]\n\n")

                else:
                    app.write(f"[red]✗ Unknown subcommand: {subcommand}[/red]\n\n")
                    app.write("Usage: [cyan]/providers [list|add|remove][/cyan]\n\n")

                return

            # Handle /restart command (restart OpenCLI while keeping IPC alive)
            if user_input.startswith('/restart'):
                app.write("[cyan]🔄 Restarting OpenCLI...[/cyan]\n\n")

                try:
                    import sys
                    import os

                    # Keep IPC server alive by enabling persistence
                    if hasattr(session, 'ipc_server') and session.ipc_server and session.ipc_server.running:
                        # Enable persistence mode (20 min timeout)
                        async def persist_server():
                            await session.ipc_server.stop(persist=True)

                        try:
                            asyncio.create_task(persist_server())
                            app.write("[dim]✓ IPC server will remain active for 20 minutes[/dim]\n")
                        except Exception:
                            pass

                    # Save current session (non-blocking)
                    await asyncio.to_thread(session.save)
                    app.write("[dim]✓ Session saved[/dim]\n\n")

                    # Get the OpenCLI command path
                    opencli_path = os.path.expanduser("~/bin/opencli")

                    # Prepare restart command that will resume this session
                    restart_cmd = f"{opencli_path} --resume {session.session_id}"

                    app.write(f"[green]Restarting with session {session.session_id[:8]}...[/green]\n\n")

                    # Use os.execv to replace the current process
                    # This maintains the shell and restarts OpenCLI
                    os.execv(sys.executable, [sys.executable, opencli_path, '--resume', session.session_id])

                except Exception as e:
                    app.write(f"[red]✗ Restart failed: {e}[/red]\n\n")
                    import traceback
                    app.write(f"[dim]{traceback.format_exc()}[/dim]\n\n")

                return

            # Handle /upgrade command (reload modules)
            if user_input.startswith('/upgrade'):
                app.write("[cyan]🔄 Reloading modules...[/cyan]\n\n")

                try:
                    import importlib
                    import sys

                    # List of modules to reload
                    modules_to_reload = [
                        'simple_tui',
                        'streaming_display',
                        'frontier_colors',
                        'markdown_renderer',
                        'async_interactive',
                        'opencli_ipc',
                        'model_manager'
                    ]

                    reloaded_count = 0
                    for module_name in modules_to_reload:
                        if module_name in sys.modules:
                            try:
                                importlib.reload(sys.modules[module_name])
                                reloaded_count += 1
                                app.write(f"[dim]✓ Reloaded {module_name}[/dim]\n")
                            except Exception as e:
                                app.write(f"[yellow]⚠ Could not reload {module_name}: {e}[/yellow]\n")

                    app.write(f"\n[green]✓ Reloaded {reloaded_count} modules[/green]\n\n")

                    # Refresh laser colors on the running app instance
                    try:
                        # Try relative import first
                        try:
                            from .frontier_colors import FRONTIER_LASER_COLORS
                        except (ImportError, ValueError):
                            from frontier_colors import FRONTIER_LASER_COLORS

                        # Update main app colors
                        app._laser_colors = FRONTIER_LASER_COLORS

                        # Update streaming display widget colors
                        try:
                            stream_display = app.query_one("#stream-display")
                            stream_display.set_laser_colors(FRONTIER_LASER_COLORS)
                            app.write(f"[dim]✓ Refreshed laser colors: {FRONTIER_LASER_COLORS[:3]}...[/dim]\n\n")
                        except Exception:
                            # Fallback if query fails
                            if hasattr(app, '_content_widget') and app._content_widget:
                                app._content_widget.set_laser_colors(FRONTIER_LASER_COLORS)
                                app.write(f"[dim]✓ Refreshed laser colors: {FRONTIER_LASER_COLORS[:3]}...[/dim]\n\n")
                            else:
                                app.write(f"[dim]✓ Refreshed app laser colors (restart may be needed for full effect)[/dim]\n\n")
                    except Exception as e:
                        app.write(f"[yellow]⚠ Could not refresh laser colors: {e}[/yellow]\n\n")

                    app.write("[dim]Note: Some changes may require restarting OpenCLI[/dim]\n\n")

                except Exception as e:
                    app.write(f"[red]✗ Module reload failed: {e}[/red]\n\n")
                    import traceback
                    app.write(f"[dim]{traceback.format_exc()}[/dim]\n\n")

                return

            # Handle /api command (IPC server control)
            if user_input.startswith('/api'):
                parts = user_input.split(maxsplit=1)
                subcommand = parts[1] if len(parts) > 1 else "status"

                if subcommand == "start":
                    # Start IPC server
                    try:
                        if hasattr(session, 'ipc_server') and session.ipc_server:
                            if session.ipc_server.running:
                                app.write("[yellow]⚠ IPC server is already running[/yellow]\n\n")
                            else:
                                await session.ipc_server.start()

                                # Initialize shell injector
                                try:
                                    from .shell_injector import get_shell_injector
                                except (ImportError, ValueError):
                                    from shell_injector import get_shell_injector

                                session.shell_injector = get_shell_injector(session.ipc_server)
                                await session.shell_injector.start()

                                # Register response handler for command results
                                try:
                                    from .opencli_ipc import MessageType
                                except (ImportError, ValueError):
                                    from opencli_ipc import MessageType

                                async def handle_response(message):
                                    """Handle responses from subagents"""
                                    result = message.payload.get('result', {})
                                    if result.get('success'):
                                        app.write(f"\n[green]📥 Response from {message.sender_id[:8]}...[/green]\n")
                                        if 'stdout' in result:
                                            app.write(f"[dim]{result['stdout']}[/dim]\n")
                                    else:
                                        app.write(f"\n[red]📥 Error from {message.sender_id[:8]}...[/red]\n")
                                        app.write(f"[dim]{result.get('error', 'Unknown error')}[/dim]\n")
                                    app.write("\n")

                                async def handle_message(message):
                                    """Handle messages from subagents - send to AI or handle commands"""
                                    payload = message.payload
                                    content = payload.get('content', '')

                                    # Display in chat
                                    app.write(f"\n[dim]📨 {content}[/dim]\n\n")

                                    # Route to handle_user_input which will detect if it's a command
                                    await handle_user_input(content)

                                session.ipc_server.register_handler(MessageType.RESPONSE.value, handle_response)
                                session.ipc_server.register_handler(MessageType.MESSAGE.value, handle_message)

                                app.write("[green]✓ IPC server started[/green]\n\n")
                                app.write(f"Socket: /tmp/opencli/opencli_{session.session_id}.sock\n\n")
                                app.write(f"[dim]Shell injection enabled - Messages logged to ~/.opencli/ipc_logs/[/dim]\n\n")
                        else:
                            # Create and start IPC server
                            try:
                                from .opencli_ipc import IPCServer
                            except (ImportError, ValueError):
                                from opencli_ipc import IPCServer

                            session.ipc_server = IPCServer(session.session_id)
                            await session.ipc_server.start()

                            # Initialize shell injector
                            try:
                                from .shell_injector import get_shell_injector
                            except (ImportError, ValueError):
                                from shell_injector import get_shell_injector

                            session.shell_injector = get_shell_injector(session.ipc_server)
                            await session.shell_injector.start()

                            # Register response handler for command results
                            try:
                                from .opencli_ipc import MessageType
                            except (ImportError, ValueError):
                                from opencli_ipc import MessageType

                            async def handle_response(message):
                                """Handle responses from subagents"""
                                result = message.payload.get('result', {})
                                if result.get('success'):
                                    app.write(f"\n[green]📥 Response from {message.sender_id[:8]}...[/green]\n")
                                    if 'stdout' in result:
                                        app.write(f"[dim]{result['stdout']}[/dim]\n")
                                else:
                                    app.write(f"\n[red]📥 Error from {message.sender_id[:8]}...[/red]\n")
                                    app.write(f"[dim]{result.get('error', 'Unknown error')}[/dim]\n")
                                app.write("\n")

                            async def handle_message(message):
                                """Handle messages from subagents - send to AI or handle commands"""
                                payload = message.payload
                                content = payload.get('content', '')

                                # Display in chat
                                app.write(f"\n[dim]📨 {content}[/dim]\n\n")

                                # Route to handle_user_input which will detect if it's a command
                                await handle_user_input(content)

                            session.ipc_server.register_handler(MessageType.RESPONSE.value, handle_response)
                            session.ipc_server.register_handler(MessageType.MESSAGE.value, handle_message)

                            app.write("[green]✓ IPC server started[/green]\n\n")
                            app.write(f"Socket: /tmp/opencli/opencli_{session.session_id}.sock\n\n")
                            app.write(f"[dim]Shell injection enabled - Messages logged to ~/.opencli/ipc_logs/[/dim]\n\n")
                    except Exception as e:
                        app.write(f"[red]✗ Failed to start IPC server: {e}[/red]\n\n")
                        import traceback
                        app.write(f"[dim]{traceback.format_exc()}[/dim]\n\n")

                elif subcommand == "stop":
                    # Stop IPC server
                    if hasattr(session, 'ipc_server') and session.ipc_server:
                        # Stop shell injector first
                        if hasattr(session, 'shell_injector') and session.shell_injector:
                            await session.shell_injector.stop()

                        await session.ipc_server.stop()
                        app.write("[green]✓ IPC server stopped[/green]\n\n")
                    else:
                        app.write("[yellow]⚠ IPC server is not running[/yellow]\n\n")

                elif subcommand == "status":
                    # Show IPC server status
                    if hasattr(session, 'ipc_server') and session.ipc_server:
                        if session.ipc_server.running:
                            subagent_count = session.ipc_server.get_subagent_count()
                            app.write("[green]✓ IPC server is running[/green]\n")
                            app.write(f"Socket: /tmp/opencli/opencli_{session.session_id}.sock\n")
                            app.write(f"Session ID: {session.session_id}\n")
                            app.write(f"Subagents: {subagent_count}\n\n")
                        else:
                            app.write("[yellow]⚠ IPC server is not running[/yellow]\n\n")
                    else:
                        app.write("[yellow]⚠ IPC server is not initialized[/yellow]\n\n")
                        app.write("Use [cyan]/api start[/cyan] to start the server\n\n")

                elif subcommand == "logs":
                    # Show injection logs summary
                    if hasattr(session, 'shell_injector') and session.shell_injector:
                        summary = session.shell_injector.get_log_summary()
                        app.write("[cyan]📊 Shell Injection Logs[/cyan]\n\n")
                        app.write(f"Total Messages: {summary['total_messages']}\n")
                        app.write(f"Log File: {summary['log_file']}\n\n")

                        if summary['by_type']:
                            app.write("By Type:\n")
                            for msg_type, count in summary['by_type'].items():
                                app.write(f"  • {msg_type}: {count}\n")
                            app.write("\n")

                        if summary['by_agent']:
                            app.write("By Agent:\n")
                            for agent, count in summary['by_agent'].items():
                                app.write(f"  • {agent}: {count}\n")
                            app.write("\n")
                    else:
                        app.write("[yellow]⚠ Shell injector not running[/yellow]\n\n")
                        app.write("Start IPC server first: [cyan]/api start[/cyan]\n\n")

                else:
                    app.write(f"[red]✗ Unknown subcommand: {subcommand}[/red]\n\n")
                    app.write("Usage:\n")
                    app.write("  [cyan]/api status[/cyan]  - Show server status\n")
                    app.write("  [cyan]/api start[/cyan]   - Start IPC server\n")
                    app.write("  [cyan]/api stop[/cyan]    - Stop IPC server\n")
                    app.write("  [cyan]/api logs[/cyan]    - Show injection logs\n\n")

                return

            # Handle /inject command - Send commands to subagents
            if user_input.startswith('/inject'):
                parts = user_input.split(maxsplit=2)

                if len(parts) < 3:
                    app.write("[yellow]Usage: /inject <agent-id|all> <command>[/yellow]\n\n")
                    app.write("Examples:\n")
                    app.write("  [cyan]/inject all ls -la[/cyan]           - Run command on all agents\n")
                    app.write("  [cyan]/inject <agent-id> pwd[/cyan]       - Run command on specific agent\n")
                    app.write("  [cyan]/inject all read /path/to/file[/cyan] - Read file on all agents\n\n")

                    if hasattr(session, 'ipc_server') and session.ipc_server:
                        subagents = session.ipc_server.get_subagents()
                        if subagents:
                            app.write("Connected agents:\n")
                            for agent in subagents:
                                app.write(f"  • {agent.name} ({agent.agent_id[:8]}...)\n")
                            app.write("\n")
                    return

                target = parts[1]
                command = parts[2]

                if not hasattr(session, 'ipc_server') or not session.ipc_server or not session.ipc_server.running:
                    app.write("[red]✗ IPC server is not running[/red]\n\n")
                    app.write("Start it with: [cyan]/api start[/cyan]\n\n")
                    return

                # Get subagents
                subagents = session.ipc_server.get_subagents()

                if not subagents:
                    app.write("[yellow]⚠ No subagents connected[/yellow]\n\n")
                    return

                # Determine targets
                if target.lower() == 'all':
                    targets = [agent.agent_id for agent in subagents]
                    app.write(f"[cyan]📤 Sending command to {len(targets)} agent(s)...[/cyan]\n\n")
                else:
                    # Try to match by ID prefix or name
                    matched = None
                    for agent in subagents:
                        if agent.agent_id.startswith(target) or agent.name.lower() == target.lower():
                            matched = agent
                            break

                    if not matched:
                        app.write(f"[red]✗ Agent not found: {target}[/red]\n\n")
                        app.write("Connected agents:\n")
                        for agent in subagents:
                            app.write(f"  • {agent.name} ({agent.agent_id[:8]}...)\n")
                        app.write("\n")
                        return

                    targets = [matched.agent_id]
                    app.write(f"[cyan]📤 Sending command to {matched.name}...[/cyan]\n\n")

                # Send command to targets
                for agent_id in targets:
                    try:
                        try:
                            from .opencli_ipc import MessageType
                        except (ImportError, ValueError):
                            from opencli_ipc import MessageType

                        await session.ipc_server.send_to_agent(
                            agent_id,
                            MessageType.COMMAND.value,
                            {
                                'command': command,
                                'type': 'bash',
                                'timestamp': datetime.now().isoformat()
                            }
                        )
                        app.write(f"[green]✓ Command sent to {agent_id[:8]}...[/green]\n")
                    except Exception as e:
                        app.write(f"[red]✗ Failed to send to {agent_id[:8]}...: {e}[/red]\n")

                app.write("\n")
                return

            # Handle Spec-Driven Development commands (Spec-Kit integration)
            spec_commands = ['/specify', '/constitution', '/plan', '/tasks',
                           '/implement', '/test', '/spec-check']

            if any(user_input.startswith(cmd) for cmd in spec_commands):
                try:
                    from .specify_wrapper import get_specify_wrapper
                except (ImportError, ValueError):
                    from specify_wrapper import get_specify_wrapper

                wrapper = get_specify_wrapper()
                parsed = wrapper.parse_slash_command(user_input)

                if parsed:
                    command = parsed['command']
                    content = parsed['content']

                    # Show user what they're requesting
                    app.write(f"[{FRONTIER_COLORS.get('info', '#6B8E9E') if FRONTIER_COLORS else 'cyan'}]Spec-Driven Development: {command}[/]\n\n")

                    # Format the spec command as instructions for the AI
                    ai_prompt = wrapper.format_spec_for_ai(command, content)

                    # Recursively call handle_user_input with the formatted prompt
                    # This sends it to the AI as a regular message
                    await handle_user_input(ai_prompt)

                return

            # Handle other commands via main opencli module
            try:
                import sys
                import os
                # Add home dir to path for opencli import
                home = os.path.expanduser('~')
                if home not in sys.path:
                    sys.path.insert(0, home)

                # Import handle_slash_command
                import importlib
                opencli = importlib.import_module('opencli')
                handle_slash_command = opencli.handle_slash_command

                # Parse command
                parts = user_input.split(maxsplit=1)
                cmd = parts[0]
                args = parts[1] if len(parts) > 1 else None

                # Run in thread to avoid blocking
                handled = await asyncio.to_thread(
                    handle_slash_command,
                    cmd,
                    args,
                    session,
                    config,
                    None  # agent_manager
                )

                if handled:
                    app.update_status()
                    return

            except Exception as e:
                app.write(f"[red]Command error: {e}[/red]\n")
                import traceback
                app.write(f"[dim]{traceback.format_exc()}[/dim]\n")
                return

        # Add to session
        session.messages.append({
            "role": "user",
            "content": user_input
        })

        # Auto-save session state (non-blocking)
        if session.debug_mode:
            app.write(f"[dim]🐛 STALL DEBUG: Saving user message...[/dim]\n")
        await asyncio.to_thread(session.save)
        if session.debug_mode:
            app.write(f"[dim]🐛 STALL DEBUG: User message save COMPLETED, starting AI response...[/dim]\n")

        # Stream response in separate thread to avoid blocking UI
        def restore_ui_state(error_msg: str = None):
            """GUARANTEED UI restoration - call on ANY error"""
            try:
                if hasattr(app, 'stop_spinner'):
                    app.stop_spinner()
                if hasattr(app, 'finish_stream') and not getattr(session, 'fast_mode', False):
                    app.finish_stream()
                if error_msg:
                    app.write(f"\n[red]❌ {error_msg}[/red]\n")
                app.write("\n[yellow]⚠️ You can continue chatting.[/yellow]\n\n")
                app.update_status()
            except:
                pass  # Ignore errors in error handler

        async def stream_ai_response():
            """Run AI streaming in background without blocking UI"""
            nonlocal client
            try:
                # STALL DEBUG: Starting message preparation
                if session.debug_mode:
                    app.write(f"[dim]🐛 STALL DEBUG: Starting message preparation...[/dim]\n")

                # Prepare messages with system context (same as fallback mode)
                if agent_manager:
                    if session.debug_mode:
                        app.write(f"[dim]🐛 STALL DEBUG: Using agent_manager.prepare_messages...[/dim]\n")
                    # Use agent manager for context - RUN IN THREAD TO PREVENT BLOCKING!
                    messages_with_context = await asyncio.to_thread(
                        agent_manager.prepare_messages,
                        session.current_agent,
                        session.messages,
                        session.cwd if hasattr(session, 'cwd') else os.getcwd(),
                        session.session_id
                    )
                    if session.debug_mode:
                        app.write(f"[dim]🐛 STALL DEBUG: agent_manager.prepare_messages COMPLETED[/dim]\n")
                else:
                    if session.debug_mode:
                        app.write(f"[dim]🐛 STALL DEBUG: Using prepare_messages_with_context...[/dim]\n")
                    # Fallback to basic context preparation WITH GOAL TRACKING (NOW ASYNC!)
                    messages_with_context = await prepare_messages_with_context(
                        session.messages,
                        config,
                        spec_memory=spec_memory,
                        goal_tracker=goal_tracker
                    )
                    if session.debug_mode:
                        app.write(f"[dim]🐛 STALL DEBUG: prepare_messages_with_context COMPLETED[/dim]\n")

                # Debug: Show system message is being sent (only in debug mode)
                if session.debug_mode and messages_with_context and messages_with_context[0].get('role') == 'system':
                    app.write(f"[dim]📋 System context: {len(messages_with_context[0]['content'])} chars[/dim]\n")

                # Debug: Log message structure for debugging (only if debug mode enabled)
                if session.debug_mode:
                    app.write(f"[dim]🔍 DEBUG: Sending {len(messages_with_context)} messages to API[/dim]\n")
                    for i, msg in enumerate(messages_with_context):
                        role = msg.get('role', 'unknown')
                        has_tool_calls = 'tool_calls' in msg
                        has_content = 'content' in msg
                        tool_call_id = msg.get('tool_call_id', '')
                        app.write(f"[dim]  {i}: {role} (tool_calls:{has_tool_calls}, content:{has_content}, tool_id:{tool_call_id})[/dim]\n")

                    # EXTREME DEBUG: Dump exact JSON being sent to API
                    app.write(f"[dim]🚨 EXTREME DEBUG - Exact JSON being sent to API:[/dim]\n")
                    app.write(f"[dim]{json.dumps(messages_with_context, indent=2)}[/dim]\n")

                # NO TIMEOUT - Let AI run as long as needed (user's choice)
                api_timeout = None
                if session.debug_mode:
                    app.write(f"[dim]🐛 STALL DEBUG: About to call API (no timeout - unlimited)...[/dim]\n")
                    app.write(f"[dim]🐛 STALL DEBUG: Message count: {len(messages_with_context)}, tools: {len(TOOLS)}[/dim]\n")

                # CRITICAL FIX: Yield control to event loop before heavy API call
                await asyncio.sleep(0)

                request_format = config.get("requestFormat", "openai-chat")
                if request_format == "anthropic-messages":
                    success, reply_text, error_msg = await perform_anthropic_request(
                        messages_with_context,
                        session,
                        config,
                        timeout=api_timeout
                    )

                    if not success:
                        restore_ui_state(error_msg or "Anthropic request failed")
                        return

                    if reply_text:
                        session.add("assistant", reply_text)
                        await asyncio.to_thread(session.save)
                        await write_markdown_response(app, reply_text)
                        app.write("\n")

                    restore_ui_state()
                    return

                if request_format != "openai-chat":
                    restore_ui_state(f"Unsupported provider request format: {request_format}")
                    return

                async def handle_policy_error(error_text: str) -> str:
                    # Import needed modules (deep nesting loses module scope)
                    import os

                    # Create local ModelManager to avoid scope issues
                    try:
                        from .model_manager import ModelManager
                    except (ImportError, ValueError):
                        from model_manager import ModelManager

                    local_mgr = ModelManager()
                    provider_id = local_mgr.get_provider_for_model(session.model or config.get("model")) or config.get("provider") or "openrouter"
                    current_headers = config.get("defaultHeaders", {}) or {}

                    # Suggested headers from environment overrides (if provided)
                    proposed = {}
                    site_url = os.getenv("OPENROUTER_SITE_URL")
                    app_name = os.getenv("OPENROUTER_APP_NAME")
                    if site_url:
                        proposed["HTTP-Referer"] = site_url
                    if app_name:
                        proposed["X-Title"] = app_name
                    if not proposed:
                        proposed = None

                    handler = getattr(app, 'permission_handler', None)
                    allowed = True
                    if handler:
                        allowed, _ = await handler.check_and_prompt(
                            "ConfigureHeaders",
                            {
                                "provider": provider_id,
                                "model": session.model or config.get("model"),
                                "issue": error_text,
                                "current_headers": current_headers,
                                "proposed_headers": proposed
                            },
                            current_dir=session.cwd if hasattr(session, 'cwd') else os.getcwd()
                        )

                    if not allowed:
                        restore_ui_state("Provider headers unchanged.")
                        return "denied"

                    if proposed and any(current_headers.get(k) != v for k, v in proposed.items()):
                        local_mgr.update_provider_headers(provider_id, proposed, None)
                        config.update(local_mgr.config)
                        app.config = config
                        app.write("[green]✓ Applied provider headers from environment overrides.[/green]\n")
                        return "updated"

                    session._pending_header_update = {
                        "provider": provider_id,
                        "fields": ["HTTP-Referer", "X-Title"],
                        "index": 0,
                        "current": current_headers,
                        "collected": {}
                    }
                    restore_ui_state("Streaming paused: update provider headers to continue.")
                    if hasattr(app, 'stream_display'):
                        app.stream_display.add_permission_prompt({
                            "title": "Configure Provider Headers",
                            "message": "Enter value for HTTP-Referer. Leave blank to keep existing value.",
                            "details": {
                                "current": current_headers.get("HTTP-Referer", "[unset]")
                            },
                            "options": []
                        })
                    else:
                        app.write("[cyan]Enter value for HTTP-Referer (leave blank to keep existing):[/cyan]\n")
                    return "await"

                response = None
                attempt = 0
                while True:
                    attempt += 1
                    try:
                        if session.debug_mode:
                            app.write(f"[dim]🐛 STALL DEBUG: Creating API request object (attempt {attempt})...[/dim]\n")

                        # Create the API call - COMPLETELY CLEAN
                        api_call = client.chat.completions.create(
                            model=session.model or config["model"],
                            messages=messages_with_context,
                            stream=True
                        )

                        if session.debug_mode:
                            app.write(f"[dim]🐛 STALL DEBUG: API request created, waiting for response...[/dim]\n")

                        # No timeout - let it run indefinitely (user's choice)
                        if api_timeout:
                            response = await asyncio.wait_for(api_call, timeout=api_timeout)
                        else:
                            response = await api_call

                        if session.debug_mode:
                            app.write(f"[dim]🐛 STALL DEBUG: API call returned, starting to stream...[/dim]\n")
                        break
                    except asyncio.TimeoutError:
                        timeout_msg = f"{api_timeout}s" if api_timeout else "unknown"
                        app.write(f"[red]❌ API request timed out after {timeout_msg}[/red]\n")
                        app.write("[yellow]⚠️ The API did not respond. Check your connection or try again.[/yellow]\n")
                        restore_ui_state()
                        return
                    except Exception as e:
                        policy_error = extract_openrouter_policy_error(e)
                        if policy_error:
                            remediation = await handle_policy_error(policy_error)
                            if remediation == "updated" and attempt < 3:
                                client = create_async_client(config)
                                continue
                            if remediation in ("await", "denied"):
                                return
                        restore_ui_state(f"Streaming Error: {e}")
                        return

                if not response:
                    return

                full_response = ""
                tool_calls_dict = {}
                chunk_count = 0
                last_chunk_time = asyncio.get_event_loop().time()

                # Create stream buffer and status display
                stream_buffer = StreamBuffer(chars_per_batch=20, batch_delay_ms=50)
                status_display = BufferStatusDisplay(app, stream_buffer)

                # Start buffer and status animation
                stream_buffer.start()
                await status_display.start()

                async for chunk in response:
                    # CRITICAL: Yield at start of each chunk to keep UI responsive
                    await asyncio.sleep(0)

                    chunk_count += 1
                    current_time = asyncio.get_event_loop().time()

                    if session.debug_mode and chunk_count % 10 == 0:
                        elapsed = current_time - last_chunk_time
                        app.write(f"[dim]🐛 STREAM: Chunk #{chunk_count}, elapsed: {elapsed:.2f}s[/dim]\n")
                        last_chunk_time = current_time

                    if app.should_exit:
                        stream_buffer.interrupt()
                        break

                    # Check for finish_reason and errors
                    if chunk.choices and session.debug_mode:
                        finish_reason = chunk.choices[0].finish_reason if chunk.choices[0] else None
                        if finish_reason:
                            app.write(f"[dim]🐛 STREAM FINISH: Chunk #{chunk_count}, finish_reason: {finish_reason}[/dim]\n")

                    delta = chunk.choices[0].delta if chunk.choices else None
                    if not delta:
                        continue

                    # Handle tool calls
                    if delta.tool_calls:
                        for tc in delta.tool_calls:
                            idx = tc.index
                            if idx not in tool_calls_dict:
                                # ALWAYS include "type": "function" - DeepSeek doesn't return it!
                                tool_calls_dict[idx] = {"id": tc.id or "", "type": "function", "name": "", "arguments": ""}
                            if tc.function:
                                if tc.function.name:
                                    tool_calls_dict[idx]["name"] = tc.function.name
                                if tc.function.arguments:
                                    tool_calls_dict[idx]["arguments"] += tc.function.arguments

                    # Handle content
                    if delta.content:
                        full_response += delta.content
                        # Buffer the content instead of writing immediately
                        await stream_buffer.add_chunk(delta.content)

                # Finish receiving and stop status
                stream_buffer.finish_receiving()
                await status_display.stop()
                status_display.write_final_status()

                if session.debug_mode:
                    app.write(f"[dim]🐛 STREAM: Streaming complete. Total chunks: {chunk_count}[/dim]\n")
                    app.write(f"[dim]🐛 STREAM: Full response length: {len(full_response)} chars[/dim]\n")

                # Render markdown ONCE from complete response (no incremental rendering)
                if full_response and not tool_calls_dict:
                    await write_markdown_response(app, full_response)
                    app.write("\n")

                # Check if we have tool calls
                if tool_calls_dict:
                    # Finish any streaming content first
                    if session.debug_mode:
                        app.write(f"[dim]🐛 POST-STREAM: About to call finish_stream (tool path)...[/dim]\n")
                    if hasattr(app, 'finish_stream') and not getattr(session, 'fast_mode', False):
                        app.finish_stream()
                    if session.debug_mode:
                        app.write(f"[dim]🐛 POST-STREAM: finish_stream done (tool path)[/dim]\n")
                    app.write("\n")
                    # CRITICAL: Yield after write
                    await asyncio.sleep(0)

                    # Build tool calls list
                    from types import SimpleNamespace
                    tool_calls = []
                    for idx, tc_data in tool_calls_dict.items():
                        tc_obj = SimpleNamespace(
                            id=tc_data["id"],
                            function=SimpleNamespace(name=tc_data["name"], arguments=tc_data["arguments"])
                        )
                        tool_calls.append(tc_obj)

                    # Save assistant message with tool calls
                    assistant_msg = {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in tool_calls]
                    }
                    session.messages.append(assistant_msg)
                    if session.debug_mode:
                        app.write(f"[dim]🔍 DEBUG: Added assistant message with {len(tool_calls)} tool calls[/dim]\n")

                    # Execute each tool WITH GOAL SANITY VALIDATION (ASYNC - NO BLOCKING!)
                    for tc in tool_calls:
                        if session.debug_mode:
                            app.write(f"[dim]🐛 Starting tool execution: {tc.function.name}[/dim]\n")
                        app.write(f"[dim]⚙ {tc.function.name}[/dim]\n")

                        args = json.loads(tc.function.arguments)

                        # GOAL SANITY CHECK - validate tool call aligns with current goal
                        sanity_check = (True, "No goal tracker")
                        if goal_tracker:
                            sanity_check = goal_tracker.validate_tool_call(tc.function.name, args)

                            # Show sanity check result in verbose/debug mode
                            if session.debug_mode or not sanity_check[0]:
                                status = "✅" if sanity_check[0] else "⚠️"
                                app.write(f"[dim]{status} Goal Check: {sanity_check[1]}[/dim]\n")

                        # PERMISSION CHECK - Non-blocking, fail-open if errors
                        if hasattr(session, 'tool_permissions_enabled') and session.tool_permissions_enabled:
                            try:
                                # Import handler - try both import styles
                                get_global_handler = None
                                try:
                                    from async_permissions import get_global_handler
                                except ImportError:
                                    pass

                                if not get_global_handler:
                                    try:
                                        import sys
                                        import importlib
                                        async_perms = importlib.import_module('async_permissions')
                                        get_global_handler = async_perms.get_global_handler
                                    except:
                                        pass

                                if get_global_handler:
                                    handler = get_global_handler()

                                    if handler and session.permission_manager:
                                        should_prompt, reason, risk_level = session.permission_manager.should_prompt(
                                            tc.function.name, args, session.cwd if hasattr(session, 'cwd') else os.getcwd()
                                        )

                                        # Show permission decision in debug mode only
                                        if session.debug_mode:
                                            app.write(f"[dim]🔒 {tc.function.name}: should_prompt={should_prompt}, reason={reason}[/dim]\n")

                                        if should_prompt:
                                            # Show permission prompt and wait for user response
                                            allowed, perm_reason = await handler.check_and_prompt(
                                                tc.function.name, args, session.cwd if hasattr(session, 'cwd') else os.getcwd()
                                            )

                                            if not allowed:
                                                # Permission denied - skip tool execution
                                                result = f"❌ Operation cancelled by user"
                                                session.messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
                                                continue  # Skip to next tool call
                                    else:
                                        app.write(f"[yellow]⚠️ handler={handler is not None}, perm_mgr={session.permission_manager is not None}[/yellow]\n")
                                else:
                                    app.write(f"[yellow]⚠️ Could not import get_global_handler[/yellow]\n")
                            except Exception as e:
                                # Permission check failed - show error for now
                                app.write(f"[red]⚠️ Permission check error: {e}[/red]\n")
                                pass

                        # Execute tool ASYNCHRONOUSLY - no blocking!
                        try:
                            result = await execute_tool_async(
                                tc.function.name,
                                args,
                                permission_manager=None,  # Already checked above
                                current_dir=session.cwd if hasattr(session, 'cwd') else os.getcwd(),
                                app=app
                            )
                            if session.debug_mode:
                                app.write(f"[dim]✓ {tc.function.name} completed[/dim]\n")
                            await asyncio.sleep(0)  # Yield to UI
                        except Exception as e:
                            result = f"Tool execution error: {str(e)}"
                            if session.debug_mode:
                                app.write(f"[dim]⚠️ {tc.function.name} failed: {e}[/dim]\n")

                        # Record tool execution in goal tracker
                        if goal_tracker:
                            goal_tracker.record_tool_call(tc.function.name, args, result, sanity_check)

                        # Check result size and truncate if needed
                        result_size = len(str(result))
                        if session.debug_mode:
                            app.write(f"[dim]📊 Result size: {result_size:,} chars[/dim]\n")
                        await asyncio.sleep(0)  # Yield BEFORE writing large result

                        # Truncate extremely large results
                        if result_size > 50000:
                            app.write(f"[yellow]⚠️ Result too large ({result_size:,} chars), truncating to 50,000...[/yellow]\n")
                            result_display = str(result)[:50000] + f"\n\n... [TRUNCATED {result_size - 50000:,} chars]"
                        else:
                            result_display = result

                        # Write result to display
                        app.write(f"[dim]{result_display}[/dim]\n")

                        # Add tool result to messages
                        tool_msg = {"role": "tool", "tool_call_id": tc.id, "content": result}
                        session.messages.append(tool_msg)
                        if session.debug_mode:
                            app.write(f"[dim]🔍 DEBUG: Added tool result for {tc.id}[/dim]\n")
                        await asyncio.sleep(0)  # Yield after each tool result added

                    # Save session with tool results (non-blocking)
                    if session.debug_mode:
                        app.write(f"[dim]🐛 STALL DEBUG: About to save session after tools...[/dim]\n")
                    await asyncio.to_thread(session.save)
                    if session.debug_mode:
                        app.write(f"[dim]🐛 STALL DEBUG: Session save COMPLETED[/dim]\n")

                    # Continue conversation - LOOP until API sends EOS token (finish_reason: "stop")
                    app.write("\n[dim]Continuing with tool results...[/dim]\n")
                    await asyncio.sleep(0)  # Yield to UI

                    continuation_round = 0
                    max_continuation_rounds = 100  # Safety limit to prevent infinite loops (API should send EOS)

                    try:
                        while continuation_round < max_continuation_rounds:
                            continuation_round += 1

                            if session.debug_mode:
                                app.write(f"[dim]🐛 CONTINUATION ROUND #{continuation_round}: Preparing messages...[/dim]\n")
        
                            # Recursive call to get AI's response to tool results
                            # Debug: Show session messages before processing (only if debug mode enabled)
                            if session.debug_mode:
                                app.write(f"[dim]🔍 DEBUG RAW SESSION: {len(session.messages)} messages before agent processing[/dim]\n")
                                for i, msg in enumerate(session.messages):
                                    role = msg.get('role', 'unknown')
                                    has_tool_calls = 'tool_calls' in msg
                                    has_content = 'content' in msg
                                    tool_call_id = msg.get('tool_call_id', '')
                                    app.write(f"[dim]  {i}: {role} (tool_calls:{has_tool_calls}, content:{has_content}, tool_id:{tool_call_id})[/dim]\n")
                            
                            # Prepare messages with agent manager (same as initial call)
                            try:
                                if agent_manager:
                                    if session.debug_mode:
                                        app.write(f"[dim]🐛 STALL DEBUG: Using agent manager for continuation...[/dim]\n")
                                    # RUN IN THREAD TO PREVENT BLOCKING THE EVENT LOOP!
                                    messages_with_context = await asyncio.to_thread(
                                        agent_manager.prepare_messages,
                                        session.current_agent,
                                        session.messages,
                                        session.cwd if hasattr(session, 'cwd') else os.getcwd(),
                                        session.session_id
                                    )
                                    if session.debug_mode:
                                        app.write(f"[dim]🐛 STALL DEBUG: agent_manager continuation COMPLETED[/dim]\n")
                                else:
                                    if session.debug_mode:
                                        app.write(f"[dim]🐛 STALL DEBUG: Using fallback context for continuation...[/dim]\n")
                                    messages_with_context = await prepare_messages_with_context(
                                        session.messages,
                                        config,
                                        spec_memory=spec_memory,
                                        goal_tracker=goal_tracker
                                    )
                                    if session.debug_mode:
                                        app.write(f"[dim]🐛 STALL DEBUG: Fallback context continuation COMPLETED[/dim]\n")
                            except Exception as e:
                                if session.debug_mode:
                                    app.write(f"[dim]🔍 DEBUG ERROR in message preparation: {e}[/dim]\n")
                                import traceback
                                app.write(f"[dim]{traceback.format_exc()}[/dim]\n")
                                return
        
                            # Debug: Log continuation message structure (only if debug mode enabled)
                            if session.debug_mode:
                                app.write(f"[dim]🔍 DEBUG CONTINUATION: Sending {len(messages_with_context)} messages to API[/dim]\n")
                                for i, msg in enumerate(messages_with_context):
                                    role = msg.get('role', 'unknown')
                                    has_tool_calls = 'tool_calls' in msg
                                    has_content = 'content' in msg
                                    tool_call_id = msg.get('tool_call_id', '')
                                    app.write(f"[dim]  {i}: {role} (tool_calls:{has_tool_calls}, content:{has_content}, tool_id:{tool_call_id})[/dim]\n")
        
                                # EXTREME DEBUG: Show exact continuation messages
                                app.write(f"[dim]🚨 CONTINUATION JSON:[/dim]\n")
                                app.write(f"[dim]{json.dumps(messages_with_context, indent=1)}[/dim]\n")
        
                            # Add timeout protection to continuation API call
                            app.write(f"[dim]⏳ Calling API (round {continuation_round})...[/dim]\n")
                            await asyncio.sleep(0)  # Yield to UI
    
                            if session.debug_mode:
                                app.write(f"[dim]🐛 STALL DEBUG: About to call continuation API...[/dim]\n")
                                app.write(f"[dim]🐛 STALL DEBUG: Message count: {len(messages_with_context)}, tools: {len(TOOLS)}[/dim]\n")
    
                            # CRITICAL FIX: Yield control to event loop before heavy API call
                            await asyncio.sleep(0)
        
                            try:
                                if session.debug_mode:
                                    app.write(f"[dim]🐛 STALL DEBUG: Creating API request object...[/dim]\n")
        
                                # Create the API call - COMPLETELY CLEAN
                                # NO tools parameter, NO extra_body, NOTHING
                                # Tools are in system message context - AI responds naturally
                                api_call = client.chat.completions.create(
                                    model=session.model or config["model"],
                                    messages=messages_with_context,
                                    stream=True
                                )
        
                                if session.debug_mode:
                                    app.write(f"[dim]🐛 STALL DEBUG: API request created, waiting for response (no timeout)...[/dim]\n")

                                # No timeout - let it run indefinitely
                                if api_timeout:
                                    response = await asyncio.wait_for(api_call, timeout=api_timeout)
                                else:
                                    response = await api_call

                                if session.debug_mode:
                                    app.write(f"[dim]🐛 STALL DEBUG: Continuation API returned, streaming...[/dim]\n")
                            except asyncio.TimeoutError:
                                timeout_msg = f"{api_timeout}s" if api_timeout else "unknown"
                                app.write(f"[red]❌ Continuation API request timed out after {timeout_msg}[/red]\n")
                                app.write("[yellow]⚠️ The API did not respond to tool results. Try again.[/yellow]\n")
                                restore_ui_state()
                                return
                            except Exception as api_error:
                                # CRITICAL: Catch ALL API errors (422, network, etc.)
                                app.write(f"\n[red]❌ API Error (continuation round {continuation_round}):[/red]\n")
                                app.write(f"[red]{str(api_error)}[/red]\n\n")

                                if session.debug_mode:
                                    import traceback
                                    app.write(f"[dim]{traceback.format_exc()}[/dim]\n")

                                app.write("[yellow]⚠️ API rejected the tool results. Check message format.[/yellow]\n")
                                restore_ui_state()
                                return

                            # Process the continuation response - CAN have more tool calls!
                            full_response = ""
                            tool_calls_dict_continuation = {}
                            finish_reason_continuation = None
                            chunk_count = 0
                            last_chunk_time = asyncio.get_event_loop().time()

                            # Create stream buffer and status display for continuation
                            stream_buffer_cont = StreamBuffer(chars_per_batch=20, batch_delay_ms=50)
                            status_display_cont = BufferStatusDisplay(app, stream_buffer_cont)

                            # Start buffer and status animation
                            stream_buffer_cont.start()
                            await status_display_cont.start()

                            async for chunk in response:
                                # CRITICAL: Yield at start of each chunk to keep UI responsive
                                await asyncio.sleep(0)

                                try:
                                    chunk_count += 1
                                    current_time = asyncio.get_event_loop().time()

                                    if app.should_exit:
                                        stream_buffer_cont.interrupt()
                                        break

                                    # Capture finish_reason (CRITICAL for knowing when to stop!)
                                    if chunk.choices and chunk.choices[0].finish_reason:
                                        finish_reason_continuation = chunk.choices[0].finish_reason
                                        if session.debug_mode:
                                            app.write(f"[dim]🐛 STREAM FINISH: Chunk #{chunk_count}, finish_reason: {finish_reason_continuation}[/dim]\n")

                                    delta = chunk.choices[0].delta if chunk.choices else None
                                    if not delta:
                                        continue

                                    # Handle tool calls in continuation too!
                                    if delta.tool_calls:
                                        for tc in delta.tool_calls:
                                            idx = tc.index
                                            if idx not in tool_calls_dict_continuation:
                                                tool_calls_dict_continuation[idx] = {"id": tc.id or "", "type": "function", "name": "", "arguments": ""}
                                            if tc.function:
                                                if tc.function.name:
                                                    tool_calls_dict_continuation[idx]["name"] = tc.function.name
                                                if tc.function.arguments:
                                                    tool_calls_dict_continuation[idx]["arguments"] += tc.function.arguments

                                    # Handle content
                                    if delta.content:
                                        full_response += delta.content
                                        # Buffer the content instead of writing immediately
                                        await stream_buffer_cont.add_chunk(delta.content)

                                except Exception as chunk_error:
                                    # CRITICAL: Don't let chunk errors kill the entire stream
                                    app.write(f"\n[red]⚠️ Chunk #{chunk_count} error: {chunk_error}[/red]\n")
                                    if session.debug_mode:
                                        import traceback
                                        app.write(f"[dim]{traceback.format_exc()}[/dim]\n")
                                    # Continue processing next chunk
                                    await asyncio.sleep(0)

                            # Finish receiving and stop status
                            stream_buffer_cont.finish_receiving()
                            await status_display_cont.stop()
                            status_display_cont.write_final_status()

                            if session.debug_mode:
                                app.write(f"[dim]🐛 CONTINUATION STREAM: Streaming complete. Total chunks: {chunk_count}[/dim]\n")
                                app.write(f"[dim]🐛 CONTINUATION STREAM: Full response length: {len(full_response)} chars[/dim]\n")
                                app.write(f"[dim]🐛 CONTINUATION STREAM: Tool calls dict size: {len(tool_calls_dict_continuation)}[/dim]\n")

                            # Render markdown ONCE from complete response (no incremental rendering)
                            if full_response and not tool_calls_dict_continuation:
                                await write_markdown_response(app, full_response)
                                app.write("\n")

                            # Check if continuation has MORE tool calls - HANDLE THEM RECURSIVELY!
                            if tool_calls_dict_continuation:
                                if session.debug_mode:
                                    app.write(f"\n[dim]🐛 RECURSIVE TOOLS: Continuation returned {len(tool_calls_dict_continuation)} tool calls[/dim]\n")
                                    for idx, tc_data in tool_calls_dict_continuation.items():
                                        app.write(f"[dim]  Tool #{idx}: {tc_data['name']}[/dim]\n")
        
                                app.write("\n")
        
                                # Build tool calls list from continuation
                                from types import SimpleNamespace
                                tool_calls_continuation = []
                                for idx, tc_data in tool_calls_dict_continuation.items():
                                    tc_obj = SimpleNamespace(
                                        id=tc_data["id"],
                                        function=SimpleNamespace(name=tc_data["name"], arguments=tc_data["arguments"])
                                    )
                                    tool_calls_continuation.append(tc_obj)
        
                                # Save assistant message with tool calls
                                assistant_msg = {
                                    "role": "assistant",
                                    "content": full_response if full_response else "",
                                    "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in tool_calls_continuation]
                                }
                                session.messages.append(assistant_msg)
        
                                # Execute each continuation tool
                                for tc in tool_calls_continuation:
                                    if session.debug_mode:
                                        app.write(f"[dim]🐛 RECURSIVE: Executing {tc.function.name}[/dim]\n")
                                    app.write(f"[dim]⚙ {tc.function.name}[/dim]\n")
                                    args = json.loads(tc.function.arguments)

                                    # PERMISSION CHECK - Non-blocking, fail-open if errors
                                    if hasattr(session, 'tool_permissions_enabled') and session.tool_permissions_enabled:
                                        try:
                                            # Import handler - try both import styles
                                            get_global_handler = None
                                            try:
                                                from async_permissions import get_global_handler
                                            except ImportError:
                                                pass

                                            if not get_global_handler:
                                                try:
                                                    import sys
                                                    import importlib
                                                    async_perms = importlib.import_module('async_permissions')
                                                    get_global_handler = async_perms.get_global_handler
                                                except:
                                                    pass

                                            if get_global_handler:
                                                handler = get_global_handler()

                                                if handler and session.permission_manager:
                                                    should_prompt, reason, risk_level = session.permission_manager.should_prompt(
                                                        tc.function.name, args, session.cwd if hasattr(session, 'cwd') else os.getcwd()
                                                    )

                                                    # Show permission decision in debug mode only
                                                    if session.debug_mode:
                                                        app.write(f"[dim]🔒 {tc.function.name}: should_prompt={should_prompt}, reason={reason}[/dim]\n")

                                                    if should_prompt:
                                                        # Show permission prompt and wait for user response
                                                        allowed, perm_reason = await handler.check_and_prompt(
                                                            tc.function.name, args, session.cwd if hasattr(session, 'cwd') else os.getcwd()
                                                        )

                                                        if not allowed:
                                                            # Permission denied - skip tool execution
                                                            result = f"❌ Operation cancelled by user"
                                                            session.messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
                                                            continue  # Skip to next tool call
                                                else:
                                                    app.write(f"[yellow]⚠️ handler={handler is not None}, perm_mgr={session.permission_manager is not None}[/yellow]\n")
                                            else:
                                                app.write(f"[yellow]⚠️ Could not import get_global_handler[/yellow]\n")
                                        except Exception as e:
                                            # Permission check failed - show error for now
                                            app.write(f"[red]⚠️ Permission check error: {e}[/red]\n")
                                            pass

                                    # Execute tool
                                    try:
                                        result = await execute_tool_async(
                                            tc.function.name,
                                            args,
                                            permission_manager=None,  # Already checked above
                                            current_dir=session.cwd if hasattr(session, 'cwd') else os.getcwd(),
                                            app=app
                                        )
                                        # CRITICAL: Show completion and yield to UI
                                        app.write(f"[dim]✓ Tool {tc.function.name} completed (continuation)[/dim]\n")
                                        await asyncio.sleep(0)  # Yield to UI
                                    except Exception as e:
                                        result = f"Tool execution error: {str(e)}"
    
                                    # Show result size and truncate if needed
                                    result_size = len(str(result))
                                    app.write(f"[dim]📊 Result size: {result_size:,} chars[/dim]\n")
                                    await asyncio.sleep(0)  # Yield BEFORE writing large result
    
                                    # Truncate extremely large results
                                    if result_size > 50000:
                                        app.write(f"[yellow]⚠️ Result too large ({result_size:,} chars), truncating to 50,000...[/yellow]\n")
                                        result_display = str(result)[:50000] + f"\n\n... [TRUNCATED {result_size - 50000:,} chars]"
                                    else:
                                        result_display = result
    
                                    # CRITICAL: Write in chunks to prevent blocking on large results

    
                                    chunk_size = 5000

    
                                    result_str = f"[dim]{result_display}[/dim]\n"

    
                                    for i in range(0, len(result_str), chunk_size):
                                        chunk = result_str[i:i+chunk_size]
                                        # Write in thread to prevent blocking UI
                                        await async_write(app, chunk, end="")
        
                                    # Add tool result
                                    tool_msg = {"role": "tool", "tool_call_id": tc.id, "content": result}
                                    session.messages.append(tool_msg)
                                    await asyncio.sleep(0)  # Yield after adding to messages
    
                                # Save and loop to make ANOTHER continuation call AUTOMATICALLY
                                await asyncio.to_thread(session.save)
        
                                if session.debug_mode:
                                    app.write(f"\n[dim]🐛 RECURSIVE: Tools executed, looping for another API call...[/dim]\n")
        
                                app.write("\n[dim]Continuing with more tool results...[/dim]\n")
                                await asyncio.sleep(0)  # Yield before next loop iteration
    
                                # Continue the while loop - will make another API call with new tool results
                                continue
        
                            # No tool calls in this response - check finish_reason to know what to do
                            if session.debug_mode:
                                app.write(f"[dim]🐛 LOOP: No tool calls, finish_reason: {finish_reason_continuation}[/dim]\n")
    
                            # Only exit on EOS token (finish_reason: "stop")
                            if finish_reason_continuation != "stop":
                                # Not done yet - continue streaming
                                if session.debug_mode:
                                    app.write(f"[dim]🐛 LOOP: No stop token, continuing loop...[/dim]\n")
                                continue
    
                            # finish_reason == "stop" - EOS token, conversation complete
                            if session.debug_mode:
                                app.write(f"[dim]🐛 LOOP: EOS token received, exiting continuation loop[/dim]\n")
        
                            # Finish and save continuation (EOS reached)
                            if session.debug_mode:
                                app.write(f"[dim]🐛 POST-STREAM: About to call finish_stream...[/dim]\n")
                            if hasattr(app, 'finish_stream') and not getattr(session, 'fast_mode', False):
                                app.finish_stream()
                            if session.debug_mode:
                                app.write(f"[dim]🐛 POST-STREAM: finish_stream done, writing newlines...[/dim]\n")
                            app.write("\n\n")
                            # CRITICAL: Yield after write
                            await asyncio.sleep(0)
        
                            if session.debug_mode:
                                app.write(f"[dim]🐛 POST-STREAM: About to stop_spinner...[/dim]\n")
                            if hasattr(app, 'stop_spinner'):
                                app.stop_spinner()
                            if session.debug_mode:
                                app.write(f"[dim]🐛 POST-STREAM: stop_spinner done[/dim]\n")
        
                            # Only save if we have content
                            if full_response.strip():
                                session.messages.append({
                                    "role": "assistant",
                                    "content": full_response
                                })
                                if session.debug_mode:
                                    app.write(f"[dim]🐛 STALL DEBUG: Saving continuation response...[/dim]\n")
                                await asyncio.to_thread(session.save)
                                if session.debug_mode:
                                    app.write(f"[dim]🐛 STALL DEBUG: Continuation save COMPLETED[/dim]\n")
                                app.update_status()
    
                            break  # Exit the continuation loop
    
                        # End of while loop - all continuation rounds complete
                        if session.debug_mode:
                            app.write(f"[dim]🐛 LOOP COMPLETE: Exited after {continuation_round} rounds[/dim]\n")

                        # Warn if safety limit was hit
                        if continuation_round >= max_continuation_rounds:
                            app.write(f"[yellow]⚠️ Safety limit reached: {max_continuation_rounds} continuation rounds. Response may be incomplete.[/yellow]\n")

                    except Exception as e:
                        # CRITICAL: Gracefully handle continuation errors instead of freezing
                        if session.debug_mode:
                            import traceback
                            app.write(f"[dim]{traceback.format_exc()}[/dim]\n")

                        # GUARANTEED UI restoration
                        restore_ui_state(f"Continuation error: {e}")

                    return  # Exit after tool continuation

                # No tool calls - regular response
                # Finish streaming to process markdown FIRST (before adding newlines)
                if session.debug_mode:
                    app.write(f"[dim]🐛 POST-STREAM: About to call finish_stream (regular path)...[/dim]\n")
                if hasattr(app, 'finish_stream') and not getattr(session, 'fast_mode', False):
                    app.finish_stream()
                if session.debug_mode:
                    app.write(f"[dim]🐛 POST-STREAM: finish_stream done (regular path)[/dim]\n")

                # Then add spacing after rendered markdown
                app.write("\n\n")
                # CRITICAL: Yield after write
                await asyncio.sleep(0)

                # Stop spinner - API response complete
                if session.debug_mode:
                    app.write(f"[dim]🐛 POST-STREAM: About to stop_spinner (regular path)...[/dim]\n")
                if hasattr(app, 'stop_spinner'):
                    app.stop_spinner()
                if session.debug_mode:
                    app.write(f"[dim]🐛 POST-STREAM: stop_spinner done (regular path)[/dim]\n")

                # Save response
                session.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

                # Auto-save session state (non-blocking)
                if session.debug_mode:
                    app.write(f"[dim]🐛 STALL DEBUG: Saving regular response...[/dim]\n")
                await asyncio.to_thread(session.save)
                if session.debug_mode:
                    app.write(f"[dim]🐛 STALL DEBUG: Regular response save COMPLETED[/dim]\n")

                # Broadcast response to IPC clients
                if hasattr(session, 'ipc_server') and session.ipc_server and session.ipc_server.running:
                    try:
                        from .opencli_ipc import MessageType
                    except (ImportError, ValueError):
                        from opencli_ipc import MessageType

                    await session.ipc_server.broadcast(
                        MessageType.MESSAGE.value,
                        {
                            "role": "assistant",
                            "content": full_response,
                            "from_ai": True
                        }
                    )

                # Update status
                app.update_status()

                if session.debug_mode:
                    app.write(f"[dim]🐛 STALL DEBUG: ✅ Stream AI response FULLY COMPLETED[/dim]\n")

            except Exception as e:
                # Show error with traceback
                if session.debug_mode:
                    import traceback
                    tb = traceback.format_exc()
                    app.write(f"[dim]{tb}[/dim]\n")

                # GUARANTEED UI restoration
                restore_ui_state(f"Streaming Error: {e}")

        # Start streaming in background task with error handling wrapper
        async def safe_stream_wrapper():
            """Wrapper to catch unhandled errors from stream_ai_response"""
            try:
                await stream_ai_response()
            except Exception as e:
                if session.debug_mode:
                    import traceback
                    app.write(f"[dim]{traceback.format_exc()}[/dim]\n")
                # GUARANTEED UI restoration
                restore_ui_state(f"Fatal streaming error: {e}")

        # Store the streaming task so it can be cancelled with ESC
        app._streaming_task = asyncio.create_task(safe_stream_wrapper())

    # Set message handler
    app.message_handler = handle_user_input

    # Run TUI (this blocks until app exits)
    await app.run_async()


def run_interactive_async(config, session, initial_prompt=None):
    """
    Sync wrapper to run async interactive mode
    """
    asyncio.run(interactive_async(config, session, initial_prompt))
