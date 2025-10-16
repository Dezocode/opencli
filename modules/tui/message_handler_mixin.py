"""Message Handler Mixin - User message processing logic

Handles all user message processing including:
- Command routing
- Message history
- Message handler delegation
"""


class MessageHandlerMixin:
    """Mixin for handling user messages in TUI"""

    async def _handle_user_message(self, user_input: str, prompt_input) -> None:
        """Handle user message submission"""
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

                # DEBUG: Check if router exists
                if hasattr(self, '_command_router'):
                    self.write(f"[dim]Router exists: initialized={self._command_router._initialized}[/dim]\n")
                else:
                    self.write(f"[dim]Router does not exist yet[/dim]\n")

                # Route through unified system
                self.write(f"[dim]Calling route_command_unified...[/dim]\n")
                handled = await route_command_unified(self, self.session, command_name, command_args)
                self.write(f"[dim]route_command_unified returned: {handled}[/dim]\n")

                if handled:
                    return
                else:
                    # Command not registered - show error instead of falling through
                    self.write(f"[red]Unknown command: {command_name}[/red]\n")
                    self.write(f"[dim]Type /help to see available commands[/dim]\n")
                    return

            except Exception as e:
                self.write(f"[red]Command error: {e}[/red]\n")
                import traceback
                traceback.print_exc()
                return

        # Forward to message handler if available (dev6 pattern)
        if self.message_handler:
            try:
                import sys
                sys.stderr.write(f"[TUI] Calling message handler with: '{user_input}'\n")
                sys.stderr.flush()
                await self.message_handler(user_input, prompt_input)
                return
            except Exception as e:
                self.write(f"[red]Message handler error: {e}[/red]\n")
                import traceback
                traceback.print_exc()
                return

        # Fallback: Handle as regular message directly
        self.write(f"\n[cyan]>[/cyan] {user_input}\n")
        self.session.add('user', user_input)
        await self._generate_ai_response()
