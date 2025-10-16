# RESTORE DEV6 MESSAGE HANDLING PIPELINE - TODO

## Overview
Reconnect the prompt → execution → buffer → streaming pipeline that worked in dev6.

---

## 1. modules/tui/core.py

### Task 1.1: Add message_handler setter
**Location**: After `__init__` method (after line 235)

**Add**:
```python
def set_message_handler(self, handler):
    """Set the message handler coroutine for processing user input

    Args:
        handler: Async function that takes (user_input: str, prompt_widget) and processes the message
    """
    self.message_handler = handler
    import sys
    sys.stderr.write(f"[TUI] Message handler set: {handler}\n")
    sys.stderr.flush()
```

### Task 1.2: Simplify _handle_user_message to delegate
**Location**: lines 420-468

**Replace** the entire method body with:
```python
async def _handle_user_message(self, user_input: str, prompt_input) -> None:
    """Handle user message submission - delegate to execution manager"""
    import sys

    # Add to history
    if user_input not in self._prompt_history:
        self._prompt_history.append(user_input)
    self._history_index = len(self._prompt_history)

    # ═══════════════════════════════════════════════════════════
    # CRITICAL: ALL commands MUST go through permission buffer FIRST
    # ═══════════════════════════════════════════════════════════
    if user_input.startswith('/'):
        try:
            # Import command routing system (relative)
            from ..command_router import route_command_unified

            # Parse command (keep the slash)
            parts = user_input.split(maxsplit=1)
            command_name = parts[0]  # e.g., "/model"
            command_args = parts[1] if len(parts) > 1 else None

            # Show command info
            self.write(f"[dim]Executing command: {command_name}[/dim]\n")

            # Route through unified system
            handled = await route_command_unified(self, self.session, command_name, command_args)
            if handled:
                return

        except Exception as e:
            self.write(f"[red]Command error: {e}[/red]\n")
            import traceback
            traceback.print_exc()
            return

    # Forward to message handler if available (dev6 pattern)
    if self.message_handler:
        try:
            sys.stderr.write(f"[TUI] Calling message handler with: '{user_input}'\n")
            sys.stderr.flush()
            await self.message_handler(user_input, prompt_input)
            return
        except Exception as e:
            self.write(f"[red]Message handler error: {e}[/red]\n")
            import traceback
            traceback.print_exc()
            return

    # Fallback: No handler set
    sys.stderr.write(f"[TUI] ERROR: No message handler set! Cannot process message.\n")
    sys.stderr.flush()
    self.write(f"[red]Error: Message handler not initialized[/red]\n")
```

### Task 1.3: Remove or stub _generate_ai_response
**Location**: lines 470-575

**Option A** (delete it entirely):
```python
# REMOVED: _generate_ai_response() - execution manager handles this now
```

**Option B** (keep as deprecated stub):
```python
async def _generate_ai_response(self) -> None:
    """DEPRECATED: Execution manager handles AI responses now"""
    import sys
    sys.stderr.write("[TUI] WARNING: _generate_ai_response called but should use message_handler\n")
    sys.stderr.flush()
```

---

## 2. modules/tui/command_handlers.py

### Task 2.1: Fix on_multi_line_input_submitted to await properly
**Location**: lines 238-266

**Replace** with:
```python
def on_multi_line_input_submitted(self, event: MultiLineInput.Submitted) -> None:
    """Handle message submission from MultiLineInput"""
    import asyncio
    import sys

    # DEBUG: Log that we received the event
    sys.stderr.write(f"\n[HANDLER] on_multi_line_input_submitted CALLED\n")
    sys.stderr.write(f"[HANDLER] Event value: '{event.value}'\n")
    sys.stderr.flush()

    user_input = event.value.strip()

    if not user_input:
        sys.stderr.write(f"[HANDLER] Empty input, returning\n")
        sys.stderr.flush()
        return

    # Guard: Ensure message handler is set
    if not hasattr(self, 'message_handler') or self.message_handler is None:
        sys.stderr.write(f"[HANDLER] ERROR: message_handler not set on TUI!\n")
        sys.stderr.flush()
        self.write(f"[red]Error: Message handler not initialized[/red]\n")
        return

    sys.stderr.write(f"[HANDLER] Getting prompt input widget\n")
    sys.stderr.flush()

    # Clear the input
    prompt_input = self.query_one("#prompt-input", MultiLineInput)
    prompt_input.clear()

    sys.stderr.write(f"[HANDLER] Creating task for _handle_user_message\n")
    sys.stderr.flush()

    # CRITICAL: Create task but don't lose errors
    async def handle_with_error_logging():
        try:
            await self._handle_user_message(user_input, prompt_input)
        except Exception as e:
            import traceback
            sys.stderr.write(f"[HANDLER] ERROR in _handle_user_message: {e}\n")
            sys.stderr.write(traceback.format_exc())
            sys.stderr.flush()
            self.write(f"[red]Error processing message: {e}[/red]\n")

    # Handle the message - this method must be implemented by the inheriting TUI class
    asyncio.create_task(handle_with_error_logging())
```

---

## 3. modules/async_interactive/core.py

### Task 3.1: Wire execution manager's handle_user_prompt
**Location**: After line 47 (after `app.message_handler = create_message_handler(...)`)

**Replace** the entire section (lines 45-47) with:
```python
# CRITICAL: Wire the execution manager's handler (dev6 pattern restored)
# Import execution flow manager
import sys
sys.stderr.write("[TUI] Creating execution flow manager...\n")
sys.stderr.flush()

try:
    from cli.modules.execution_flow import create_execution_flow_manager
    from cli.modules.initialization import initialize_opencli_system

    # Initialize system components
    from pathlib import Path
    CONFIG_DIR = Path.home() / ".opencli"
    component_init, system_init, init_results = initialize_opencli_system(CONFIG_DIR)

    # Create execution flow manager
    execution_manager = create_execution_flow_manager(config, session, component_init, system_init)
    execution_manager.set_client(client)

    # Set the handler on the TUI
    app.set_message_handler(execution_manager.handle_user_prompt)

    sys.stderr.write(f"[TUI] Execution manager wired successfully\n")
    sys.stderr.flush()

except Exception as e:
    sys.stderr.write(f"[TUI] WARNING: Could not wire execution manager: {e}\n")
    sys.stderr.flush()
    # Fallback: Create a simple handler
    async def simple_handler(user_input, prompt_widget):
        sys.stderr.write(f"[SIMPLE HANDLER] Processing: {user_input}\n")
        sys.stderr.flush()
        session.add('user', user_input)
        app.write(f"\n[yellow]Using fallback handler - execution manager not available[/yellow]\n")

    app.set_message_handler(simple_handler)
```

---

## 4. cli/modules/execution_flow.py

### Task 4.1: Add handle_user_prompt method
**Location**: After line 195 (after ExecutionFlowManager class methods)

**Add**:
```python
async def handle_user_prompt(self, user_input: str, prompt_widget=None):
    """Handle user prompt submission (dev6 pattern restored)

    Args:
        user_input: Raw user input string
        prompt_widget: Optional MultiLineInput widget for spinner control

    This method:
    1. Processes attachments via prompt processor
    2. Adds user message to session
    3. Prepares messages with context (constitution, AGENTS.md, etc.)
    4. Streams AI response through BufferManager
    5. Executes tool calls
    6. Updates session with assistant/tool responses
    """
    import sys
    sys.stderr.write(f"\n[EXEC] handle_user_prompt called: '{user_input}'\n")
    sys.stderr.flush()

    # 1. Process attachments
    prompt_processor = self.initialized_systems.get('prompt_processor')
    if prompt_processor:
        processed_input, metadata = prompt_processor.process_input(user_input)
        # Get original text with attachments preserved
        actual_input = prompt_processor.get_original_text(processed_input, metadata)
    else:
        actual_input = user_input
        metadata = {}

    # 2. Add to session
    self.session.add('user', actual_input)

    # 3. Prepare messages with context (dev6 pattern)
    try:
        prepared_messages = await self._prepare_messages(self.session.messages)
    except Exception as e:
        sys.stderr.write(f"[EXEC] Error preparing messages: {e}\n")
        sys.stderr.flush()
        prepared_messages = self.session.messages

    # 4. Stream AI response
    try:
        await self._stream_ai_response(prepared_messages, prompt_widget)
    except Exception as e:
        sys.stderr.write(f"[EXEC] Error streaming response: {e}\n")
        sys.stderr.flush()
        if prompt_widget and hasattr(prompt_widget, 'app'):
            prompt_widget.app.write(f"[red]Error: {e}[/red]\n")

async def _prepare_messages(self, messages):
    """Prepare messages with context (port from dev6)

    Adds:
    - Constitution principles
    - AGENTS.md content
    - Spec/goal context
    - Working directory
    - Tool definitions
    """
    import sys
    sys.stderr.write(f"[EXEC] Preparing messages with context...\n")
    sys.stderr.flush()

    # Import preparation helper
    try:
        from modules.async_interactive.message_handling import prepare_messages_with_context
        return await prepare_messages_with_context(messages, self.session, self.config)
    except Exception as e:
        sys.stderr.write(f"[EXEC] WARNING: prepare_messages_with_context failed: {e}\n")
        sys.stderr.flush()
        # Fallback: return messages as-is
        return messages

async def _stream_ai_response(self, prepared_messages, prompt_widget=None):
    """Stream AI response using BufferManager and StreamHandler

    Args:
        prepared_messages: Messages prepared with context
        prompt_widget: Optional widget for spinner control
    """
    import sys
    from modules.async_interactive.streaming import StreamHandler
    from modules.async_interactive.buffer_system import BufferManager
    from modules.async_interactive.tool_integration import get_tool_executor

    sys.stderr.write(f"[EXEC] Streaming AI response...\n")
    sys.stderr.flush()

    # Start spinner if widget available
    if prompt_widget:
        try:
            prompt_widget.start_spinner()
        except:
            pass

    # Create buffer manager
    buffer_manager = BufferManager()

    # Create stream handler
    stream_handler = StreamHandler()

    # Create tool executor
    tool_executor = get_tool_executor(self, self.session)

    try:
        # Get app for writing output
        app = prompt_widget.app if prompt_widget and hasattr(prompt_widget, 'app') else None

        if app:
            app.write("🔄 Thinking...\n")

        # Stream from API
        model = self.config.get("model", "")
        assistant_text = ""
        tool_calls = []

        if "claude" in model.lower():
            # Use Anthropic streaming
            async for chunk in stream_handler.stream_anthropic(prepared_messages, self.config):
                if chunk.get("type") == "content":
                    content = chunk["content"]
                    assistant_text += content
                    if app:
                        app.write(content, end="")
                elif chunk.get("type") == "tool_call":
                    tool_calls.extend(chunk.get("tool_calls", []))
                elif chunk.get("type") == "error":
                    if app:
                        app.write(f"\n[red]Error: {chunk['error']}[/red]\n")
                    return
        else:
            # Use OpenRouter streaming
            async for chunk in stream_handler.stream_openrouter(prepared_messages, self.config):
                if chunk.get("type") == "content":
                    content = chunk["content"]
                    assistant_text += content
                    if app:
                        app.write(content, end="")
                elif chunk.get("type") == "tool_call":
                    tool_calls.extend(chunk.get("tool_calls", []))
                elif chunk.get("type") == "error":
                    if app:
                        app.write(f"\n[red]Error: {chunk['error']}[/red]\n")
                    return

        # Add assistant message to session
        if assistant_text:
            self.session.add('assistant', assistant_text)
            if app:
                app.write("\n")

        # Execute tool calls
        if tool_calls and tool_executor:
            for tool_call in tool_calls:
                try:
                    result = await tool_executor.execute_tool_call(tool_call)
                    self.session.add('tool', f"Tool {tool_call.get('name', 'Unknown')}: {result}")
                    if app:
                        app.write(f"\n[dim]Tool: {tool_call.get('name')}[/dim]\n")
                except Exception as e:
                    if app:
                        app.write(f"[red]Tool error: {e}[/red]\n")

    finally:
        # Stop spinner
        if prompt_widget:
            try:
                prompt_widget.stop_spinner()
            except:
                pass
```

---

## 5. modules/async_interactive/message_handling.py

### Task 5.1: Port dev6's prepare_messages_with_context
**Location**: Replace lines 61-110

**Replace** with:
```python
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
```

### Task 5.2: Remove create_message_handler
**Location**: Delete lines 1-59 (the entire create_message_handler function)

**Replace** with comment:
```python
# REMOVED: create_message_handler() - now handled by ExecutionFlowManager.handle_user_prompt
# See cli/modules/execution_flow.py for the new implementation
```

---

## 6. Create modules/async_interactive/preparation.py (NEW FILE)

**Create**: `/Users/dezmondhollins/opencli/modules/async_interactive/preparation.py`

**Content**:
```python
"""
Message Preparation System
Builds system context with constitution, agents, goals, spec, etc.
Port from dev6 for the refactored architecture
"""

import asyncio
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


async def build_system_context(
    session,
    config: Dict[str, Any],
    agent_manager=None,
    spec_memory=None,
    goal_tracker=None
) -> str:
    """Build comprehensive system context (dev6 pattern)

    Args:
        session: Session object
        config: Configuration dict
        agent_manager: Optional AgentManager instance
        spec_memory: Optional SpecMemory instance
        goal_tracker: Optional GoalTracker instance

    Returns:
        System context string with all relevant information
    """
    system_parts = []

    # 1. Constitution
    constitution = await load_constitution()
    if constitution:
        system_parts.append("# OpenCLI Constitution\n\n" + constitution)

    # 2. Agent context
    if agent_manager and hasattr(session, 'current_agent') and session.current_agent:
        agent_context = await load_agent_context(session.current_agent)
        if agent_context:
            system_parts.append(f"# Active Agent: {session.current_agent}\n\n{agent_context}")

    # 3. Spec context
    if spec_memory:
        spec_context = await load_spec_context(spec_memory)
        if spec_context:
            system_parts.append("# Specification Context\n\n" + spec_context)

    # 4. Goals
    if goal_tracker:
        goals_context = await load_goals_context(goal_tracker)
        if goals_context:
            system_parts.append("# Current Goals\n\n" + goals_context)

    # 5. Working directory
    cwd = os.getcwd()
    system_parts.append(f"# Working Directory\n\n`{cwd}`")

    # 6. Tool definitions
    tools_context = await load_tools_context()
    if tools_context:
        system_parts.append("# Available Tools\n\n" + tools_context)

    return "\n\n---\n\n".join(system_parts)


async def load_constitution() -> Optional[str]:
    """Load constitution from ~/.opencli/CONSTITUTION.md"""
    try:
        constitution_path = Path.home() / ".opencli" / "CONSTITUTION.md"
        if constitution_path.exists():
            async def read_file():
                with open(constitution_path) as f:
                    return f.read()
            return await asyncio.to_thread(read_file)
    except Exception:
        return None


async def load_agent_context(agent_name: str) -> Optional[str]:
    """Load AGENTS.md content for active agent"""
    try:
        agents_path = Path.cwd() / "AGENTS.md"
        if agents_path.exists():
            async def read_file():
                with open(agents_path) as f:
                    return f.read()
            return await asyncio.to_thread(read_file)
    except Exception:
        return None


async def load_spec_context(spec_memory) -> Optional[str]:
    """Load spec context from SpecMemory"""
    try:
        if hasattr(spec_memory, 'get_active_spec'):
            spec = spec_memory.get_active_spec()
            if spec:
                return f"**Spec**: {spec.get('description', 'N/A')}"
    except Exception:
        return None


async def load_goals_context(goal_tracker) -> Optional[str]:
    """Load goals from GoalTracker"""
    try:
        if hasattr(goal_tracker, 'get_active_goals'):
            goals = goal_tracker.get_active_goals()
            if goals:
                return "\n".join([f"- {g}" for g in goals])
    except Exception:
        return None


async def load_tools_context() -> Optional[str]:
    """Load tool definitions"""
    try:
        from .tools import TOOLS
        if TOOLS:
            tool_list = []
            for tool in TOOLS:
                name = tool.get('name', 'unknown')
                desc = tool.get('description', 'No description')
                tool_list.append(f"- **{name}**: {desc}")
            return "\n".join(tool_list)
    except Exception:
        return None
```

---

## 7. Update modules/async_interactive/__init__.py

### Task 7.1: Export preparation utilities
**Location**: After line 11

**Add**:
```python
from .preparation import build_system_context, load_constitution
```

**Update __all__**:
```python
__all__ = [
    'interactive_async',
    'run_interactive_async',
    'create_session',
    'create_async_client',
    'async_write',
    'write_markdown_response',
    'execute_tool_async',
    'execute_tool',
    'normalize_tool_call_messages',
    'prepare_messages_with_context',
    'build_system_context',
    'load_constitution'
]
```

---

## 8. Verify buffer_system.py and streaming.py compatibility

### Task 8.1: Check BufferManager interface
**Location**: modules/async_interactive/buffer_system.py

**Verify methods exist**:
- `create_stream_buffer()`
- `update_status()`
- `finish()`

### Task 8.2: Check StreamHandler interface
**Location**: modules/async_interactive/streaming.py

**Verify methods exist**:
- `stream_openrouter(messages, config)`
- `stream_anthropic(messages, config)`
- `interrupt()`

---

## 9. Update tool_integration.py

### Task 9.1: Ensure get_tool_executor works
**Location**: modules/async_interactive/tool_integration.py

**Verify**:
```python
def get_tool_executor(execution_manager, session):
    """Get tool executor instance

    Should return object with:
    - execute_tool_call(tool_call) -> result
    """
    # Implementation exists, just verify it works
```

---

## 10. Tests (NEW FILES)

### Task 10.1: Create tests/test_message_preparation.py
**Create**: `/Users/dezmondhollins/opencli/tests/test_message_preparation.py`

**Content**:
```python
"""Test message preparation utilities"""

import pytest
import asyncio
from modules.async_interactive.message_handling import prepare_messages_with_context


@pytest.mark.asyncio
async def test_prepare_messages_adds_system_context():
    """Test that prepare_messages_with_context adds system message"""
    messages = [
        {'role': 'user', 'content': 'hello'}
    ]

    class MockSession:
        current_agent = None

    class MockConfig:
        def get(self, key, default=None):
            return default

    session = MockSession()
    config = MockConfig()

    prepared = await prepare_messages_with_context(messages, session, config)

    # Should have system message prepended
    assert len(prepared) >= 2
    assert prepared[0]['role'] == 'system'
    assert 'Working Directory' in prepared[0]['content']


@pytest.mark.asyncio
async def test_prepare_messages_preserves_user_messages():
    """Test that user/assistant messages are preserved"""
    messages = [
        {'role': 'user', 'content': 'hello'},
        {'role': 'assistant', 'content': 'hi'},
        {'role': 'user', 'content': 'how are you'}
    ]

    class MockSession:
        current_agent = None

    class MockConfig:
        def get(self, key, default=None):
            return default

    session = MockSession()
    config = MockConfig()

    prepared = await prepare_messages_with_context(messages, session, config)

    # Should preserve all user/assistant messages
    user_messages = [m for m in prepared if m['role'] == 'user']
    assert len(user_messages) == 2
```

---

## Execution Order

1. ✅ **modules/tui/core.py** - Add setter, simplify handler
2. ✅ **modules/tui/command_handlers.py** - Fix await pattern
3. ✅ **cli/modules/execution_flow.py** - Add handle_user_prompt
4. ✅ **modules/async_interactive/message_handling.py** - Port prepare_messages_with_context
5. ✅ **modules/async_interactive/preparation.py** - Create new helper
6. ✅ **modules/async_interactive/__init__.py** - Export new functions
7. ✅ **modules/async_interactive/core.py** - Wire execution manager
8. ✅ **tests/test_message_preparation.py** - Add tests
9. ✅ **Clear caches** - Remove all .pyc files
10. ✅ **Test manually** - Run `opencli tui` and submit a message

---

## Verification Checklist

- [ ] TUI launches without errors
- [ ] Typing a message and pressing Enter shows handler logs
- [ ] Message appears in chat area
- [ ] AI response streams back
- [ ] Tool calls execute (if applicable)
- [ ] Attachments are detected and processed
- [ ] `/commands` work properly
- [ ] ESC cancels streaming (if implemented)
- [ ] Session persists messages correctly
- [ ] No import errors
- [ ] All files under blueprint size limits (`python3 check_architecture.py`)
