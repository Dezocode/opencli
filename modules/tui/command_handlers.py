"""
Command suggestion and navigation handlers for OpenCLI TUI
Extracted from simple_tui.py
"""

import os
from typing import Any

# CRITICAL: Import actual MultiLineInput, not stub!
from ..command_suggestions import CommandSuggestionBuffer, CommandMatch, check_command_health
from ..multiline_input import MultiLineInput
from ..execution.registry import ExecutionType


class CommandHandlers:
    """Mixin class containing command-related event handlers"""
    
    def on_multi_line_input_show_command_suggestions(self, event: MultiLineInput.ShowCommandSuggestions) -> None:
        """Handle slash command typed - show/update command suggestions"""
        # DEBUG LOGGING
        if os.getenv('OPENCLI_DEBUG_AUTOCOMPLETE'):
            with open('/tmp/opencli-autocomplete-debug.log', 'a') as f:
                f.write(f"[SimpleTUI] Received ShowCommandSuggestions('{event.query}')\n")

        try:
            # Get command suggestion buffer
            suggestions_buffer = self.query_one("#command-suggestions", CommandSuggestionBuffer)

            # DEBUG
            if os.getenv('OPENCLI_DEBUG_AUTOCOMPLETE'):
                with open('/tmp/opencli-autocomplete-debug.log', 'a') as f:
                    f.write(f"[SimpleTUI] Found suggestions buffer\n")

            # Get command registry - PRIORITIZE SDK ExecutionRegistry
            query = event.query
            sdk_registry = None

            # Try to get ExecutionRegistry from SDK (ExecutionSystem)
            # DEBUG: Log what we're checking
            import sys
            sys.stderr.write(f"[AUTOSUGGEST] Checking for _command_router... ")
            sys.stderr.flush()

            if hasattr(self, '_command_router'):
                sys.stderr.write(f"FOUND\n")
                sys.stderr.flush()
                executor = getattr(self._command_router, 'executor', None)
                sys.stderr.write(f"[AUTOSUGGEST] Executor: {executor is not None}\n")
                sys.stderr.flush()
                if executor and hasattr(executor, 'registry'):
                    sdk_registry = executor.registry
                    sys.stderr.write(f"[AUTOSUGGEST] Registry: {sdk_registry is not None}, Commands: {len(sdk_registry.commands) if sdk_registry else 0}\n")
                    sys.stderr.flush()
                    # DEBUG
                    if os.getenv('OPENCLI_DEBUG_AUTOCOMPLETE'):
                        with open('/tmp/opencli-autocomplete-debug.log', 'a') as f:
                            f.write(f"[SimpleTUI] Using SDK ExecutionRegistry with {len(sdk_registry.commands)} commands\n")
                else:
                    sys.stderr.write(f"[AUTOSUGGEST] No registry found on executor\n")
                    sys.stderr.flush()
            else:
                sys.stderr.write(f"NOT FOUND\n")
                sys.stderr.write(f"[AUTOSUGGEST] self type: {type(self)}\n")
                sys.stderr.write(f"[AUTOSUGGEST] self attrs: {[attr for attr in dir(self) if 'command' in attr.lower()]}\n")
                sys.stderr.flush()

            # Try SDK ExecutionRegistry first, fallback to legacy
            prompt_input = self.query_one("#prompt-input", MultiLineInput)

            if not sdk_registry:
                # SDK registry not available yet - check if initialization is in progress
                import sys
                sys.stderr.write(f"[WARN] SDK ExecutionRegistry not available yet - router still initializing\n")
                sys.stderr.flush()

                # Check if router is initializing and start SDK loading display
                if hasattr(self, '_command_router') and hasattr(self._command_router, '_initializing'):
                    if self._command_router._initializing:
                        sys.stderr.write(f"[WAIT] Router is initializing, starting SDK loading display\n")
                        sys.stderr.flush()

                        # Start SDK loading if not already active
                        if not suggestions_buffer.is_sdk_loading:
                            suggestions_buffer.start_sdk_loading()

                        suggestions_buffer.remove_class("hidden")
                        return

                # Otherwise show fallback loading message
                sys.stderr.write(f"[WAIT] Showing fallback 'loading' state\n")
                sys.stderr.flush()
                loading_matches = [
                    CommandMatch(
                        name="/initializing...",
                        description="Command system is initializing, please wait...",
                        category="SYSTEM",
                        score=0,
                        usage_count=0,
                        health_status=False
                    )
                ]
                suggestions_buffer.update_suggestions(loading_matches, query)
                suggestions_buffer.remove_class("hidden")
                return

            # Registry is available - search for commands
            matches = sdk_registry.search_commands(query)

            # DEBUG
            sys.stderr.write(f"[AUTOSUGGEST] Registry has {len(sdk_registry.commands)} total commands\n")
            sys.stderr.write(f"[AUTOSUGGEST] Search returned {len(matches)} matches for '{query}'\n")
            sys.stderr.flush()

            if os.getenv('OPENCLI_DEBUG_AUTOCOMPLETE'):
                with open('/tmp/opencli-autocomplete-debug.log', 'a') as f:
                    f.write(f"[SimpleTUI] Found {len(matches)} matches from SDK\n")

            # Convert SDK results to CommandMatch objects
            command_matches = []
            for m in matches:
                reg = m['registration']
                cmd_name = m['name']

                # Health check from SDK registration
                is_healthy = (
                    reg.handler is not None and      # Has handler
                    reg.requires_approval and         # Permission-integrated
                    reg.enabled                       # Is enabled
                )

                command_matches.append(
                    CommandMatch(
                        name=cmd_name,
                        description=reg.description,
                        category=reg.category.value if hasattr(reg.category, 'value') else str(reg.category),
                        score=m['score'],
                        usage_count=reg.usage_count,
                        health_status=is_healthy
                    )
                )

            # Check if no matches found (registry is ready but query has no matches)
            if not command_matches:
                import sys
                sys.stderr.write(f"[AUTOSUGGEST] Registry ready but no matches for '{query}'\n")
                sys.stderr.flush()

                # Show "no matches" message instead of hiding completely
                no_match = [
                    CommandMatch(
                        name=query,
                        description=f"No commands match '{query}'",
                        category="SYSTEM",
                        score=0,
                        usage_count=0,
                        health_status=False
                    )
                ]
                suggestions_buffer.update_suggestions(no_match, query)
                suggestions_buffer.remove_class("hidden")
                return

            # Update suggestion buffer
            suggestions_buffer.update_suggestions(command_matches, query)

            # DEBUG
            if os.getenv('OPENCLI_DEBUG_AUTOCOMPLETE'):
                with open('/tmp/opencli-autocomplete-debug.log', 'a') as f:
                    f.write(f"[SimpleTUI] Updated suggestions buffer\n")

            # Show the buffer
            suggestions_buffer.remove_class("hidden")

            # DEBUG
            if os.getenv('OPENCLI_DEBUG_AUTOCOMPLETE'):
                with open('/tmp/opencli-autocomplete-debug.log', 'a') as f:
                    f.write(f"[SimpleTUI] Removed 'hidden' class from buffer\n")

        except Exception as e:
            # CRITICAL FAILSAFE: Reset suggestions_active on error!
            import sys
            import traceback
            sys.stderr.write(f"[AUTOSUGGEST ERROR] {e}\n")
            sys.stderr.write(traceback.format_exc())
            sys.stderr.flush()

            try:
                prompt_input = self.query_one("#prompt-input", MultiLineInput)
                prompt_input.suggestions_active = False
                sys.stderr.write(f"[FAILSAFE] Reset suggestions_active after error\n")
            except:
                pass

            if os.getenv('OPENCLI_DEBUG_AUTOCOMPLETE'):
                with open('/tmp/opencli-autocomplete-debug.log', 'a') as f:
                    f.write(f"[SimpleTUI] ERROR: {e}\n")
                    f.write(traceback.format_exc())

    def on_multi_line_input_hide_command_suggestions(self, event: MultiLineInput.HideCommandSuggestions) -> None:
        """Handle hiding command suggestions"""
        # CRITICAL: ALWAYS reset flag even if widgets not found
        prompt_input = None
        try:
            prompt_input = self.query_one("#prompt-input", MultiLineInput)
        except:
            pass

        try:
            suggestions_buffer = self.query_one("#command-suggestions", CommandSuggestionBuffer)
            suggestions_buffer.add_class("hidden")
            suggestions_buffer.clear()
        except Exception:
            pass
        finally:
            # ALWAYS reset suggestions_active, no matter what
            if prompt_input:
                prompt_input.suggestions_active = False
                import sys
                sys.stderr.write(f"[HIDE] Reset suggestions_active\n")
                sys.stderr.flush()

    def on_multi_line_input_command_suggestion_navigate(self, event: MultiLineInput.CommandSuggestionNavigate) -> None:
        """Handle arrow key navigation in command suggestions"""
        try:
            suggestions_buffer = self.query_one("#command-suggestions", CommandSuggestionBuffer)

            if event.direction == "up":
                suggestions_buffer.move_selection_up()
            elif event.direction == "down":
                suggestions_buffer.move_selection_down()

        except Exception:
            pass

    async def on_multi_line_input_command_suggestion_select(self, event: MultiLineInput.CommandSuggestionSelect) -> None:
        """Handle Enter key with command suggestions active"""
        try:
            suggestions_buffer = self.query_one("#command-suggestions", CommandSuggestionBuffer)
            prompt_input = self.query_one("#prompt-input", MultiLineInput)

            # Get selected command
            selected = suggestions_buffer.get_selected_command()

            if selected:
                # Record usage in ExecutionRegistry (SDK system)
                if hasattr(self, '_command_router'):
                    executor = getattr(self._command_router, 'executor', None)
                    if executor and hasattr(executor, 'registry'):
                        # Use SDK ExecutionRegistry for tracking
                        executor.registry.record_usage(ExecutionType.COMMAND, selected.name)

                # Replace input with selected command
                command_text = selected.name
                prompt_input.value = command_text
                prompt_input.cursor_position = len(command_text)

                # Hide suggestions
                suggestions_buffer.add_class("hidden")
                suggestions_buffer.clear()
                prompt_input.suggestions_active = False

                # Submit the command
                prompt_input.clear()
                await self._handle_user_message(command_text, prompt_input)
            else:
                # No selection: submit current input
                import sys
                sys.stderr.write(f"[FAILSAFE] No selection, submitting message\n")
                sys.stderr.flush()

                try:
                    suggestions_buffer.add_class("hidden")
                    suggestions_buffer.clear()
                except Exception:
                    pass
                prompt_input.suggestions_active = False

                user_input = prompt_input.value.strip()
                if user_input:
                    prompt_input.clear()
                    await self._handle_user_message(user_input, prompt_input)

        except Exception as e:
            # Log error instead of silent failure
            import sys
            import traceback
            sys.stderr.write(f"[SELECT ERROR] {e}\n")
            sys.stderr.write(traceback.format_exc())
            sys.stderr.flush()
            # Robust fallback: reset suggestions and submit current input if present
            try:
                prompt_input = self.query_one("#prompt-input", MultiLineInput)
                prompt_input.suggestions_active = False
                user_input = prompt_input.value.strip()
                if user_input:
                    prompt_input.clear()
                    import asyncio
                    asyncio.create_task(self._handle_user_message(user_input, prompt_input))
            except Exception:
                pass

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