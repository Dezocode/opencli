"""
Conversation Manager (Async) - Modular orchestration for conversations

Responsibilities:
- Prepare messages with context
- Stream assistant responses
- Execute tool calls
- Update session state

This replaces tightly-coupled logic in cli/modules/execution_flow.py
and is reusable by both CLI and TUI entrypoints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


class ConversationManager:
    """High-level async orchestrator for a single conversation turn."""

    def __init__(self, config: Dict[str, Any], session: Any) -> None:
        self.config = config
        self.session = session

    async def handle_user_prompt(self, user_input: str, prompt_widget: Any = None) -> None:
        """Complete a single conversation turn for the given user_input."""
        # 1) Add to session
        self.session.add('user', user_input)

        # 2) Prepare messages with context
        prepared = await self._prepare_messages(self.session.messages)

        # 3) Stream response and execute tools
        await self._stream_and_execute(prepared, prompt_widget)

    async def _prepare_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            from modules.async_interactive.message_handling import prepare_messages_with_context
            return await prepare_messages_with_context(messages, self.session, self.config)
        except Exception:
            return messages

    async def _stream_and_execute(self, prepared: List[Dict[str, Any]], prompt_widget: Any = None) -> None:
        from modules.async_interactive.streaming import StreamHandler
        from modules.async_interactive.buffer_system import BufferManager
        from modules.async_interactive.tool_integration import get_tool_executor

        stream_handler = StreamHandler()
        buffer_manager = BufferManager()
        tool_executor = get_tool_executor(None, self.session)

        # Spinner UX
        if prompt_widget and hasattr(prompt_widget, 'start_spinner'):
            try:
                prompt_widget.start_spinner()
            except Exception:
                pass

        app = getattr(prompt_widget, 'app', None)
        assistant_text = ""
        tool_calls: List[Dict[str, Any]] = []

        try:
            model = self.config.get("model", "")
            if "claude" in model.lower():
                async for chunk in stream_handler.stream_anthropic(prepared, self.config):
                    if chunk.get("type") == "content":
                        content = chunk["content"]
                        assistant_text += content
                        if app:
                            app.write(content, end="")
                    elif chunk.get("type") == "tool_call":
                        tool_calls.extend(chunk.get("tool_calls", []))
                    elif chunk.get("type") == "error" and app:
                        app.write(f"\n[red]Error: {chunk['error']}[/red]\n")
                        return
            else:
                async for chunk in stream_handler.stream_openrouter(prepared, self.config):
                    if chunk.get("type") == "content":
                        content = chunk["content"]
                        assistant_text += content
                        if app:
                            app.write(content, end="")
                    elif chunk.get("type") == "tool_call":
                        tool_calls.extend(chunk.get("tool_calls", []))
                    elif chunk.get("type") == "error" and app:
                        app.write(f"\n[red]Error: {chunk['error']}[/red]\n")
                        return

            if assistant_text:
                self.session.add('assistant', assistant_text)
                if app:
                    app.write("\n")

            if tool_calls and tool_executor:
                for call in tool_calls:
                    try:
                        result = await tool_executor.execute_tool_call(call)
                        self.session.add('tool', f"Tool {call.get('name', 'Unknown')}: {result}")
                        if app:
                            app.write(f"\n[dim]Tool: {call.get('name')}[/dim]\n")
                    except Exception as e:
                        if app:
                            app.write(f"[red]Tool error: {e}[/red]\n")
        finally:
            if prompt_widget and hasattr(prompt_widget, 'stop_spinner'):
                try:
                    prompt_widget.stop_spinner()
                except Exception:
                    pass
