"""
Permission event handlers for OpenCLI TUI
Extracted from simple_tui.py to handle permission prompts and responses
"""

from typing import Any, Dict

try:
    from ..permissions import get_unified_permission_manager, PermissionResponse
    from ..multiline_input import MultiLineInput
except (ImportError, ValueError):
    try:
        # Package-relative fallbacks
        from ..permissions import get_unified_permission_manager, PermissionResponse
        from ..multiline_input import MultiLineInput
    except ImportError:
        # Final fallbacks for non-package execution
        def get_unified_permission_manager():
            return None
        class PermissionResponse:
            CANCEL = "cancel"
        from multiline_input import MultiLineInput


class PermissionHandlers:
    """Mixin class containing permission-related event handlers"""
    
    def on_multi_line_input_permission_response(self, event: MultiLineInput.PermissionResponse) -> None:
        """Handle permission response from MultiLineInput"""
        import sys
        sys.stderr.write(f"\n[PermissionHandlers.on_multi_line_input_permission_response] ENTERED\n")
        sys.stderr.write(f"[PermissionHandlers] Response: {event.option.get('response')}\n")
        sys.stderr.flush()

        # Check if this is provider model selection
        if hasattr(self.session, '_awaiting_provider_model_selection') and self.session._awaiting_provider_model_selection:
            sys.stderr.write(f"[PermissionHandlers] Routing to provider model selection handler\n")
            sys.stderr.flush()
            self._handle_provider_model_selection(event)
            return

        # Check if this is local model selection
        if hasattr(self.session, '_awaiting_local_model_selection') and self.session._awaiting_local_model_selection:
            sys.stderr.write(f"[PermissionHandlers] Routing to local model selection handler\n")
            sys.stderr.flush()
            self._handle_local_model_selection(event)
            return

        # Check if this is model browser selection
        if hasattr(self.session, '_awaiting_model_browser_selection') and self.session._awaiting_model_browser_selection:
            sys.stderr.write(f"[PermissionHandlers] Routing to model browser selection handler\n")
            sys.stderr.flush()
            self._handle_model_browser_selection(event)
            return

        # Check unified permission manager first
        manager = get_unified_permission_manager()
        if manager:
            # Extract response from event and forward to manager
            response = event.option.get('response')
            data = event.option.get('data', {})

            sys.stderr.write(f"[PermissionHandlers] Forwarding to unified permission manager\n")
            sys.stderr.write(f"[PermissionHandlers] Response={response}, Data={data}\n")
            sys.stderr.flush()

            # Forward response to manager to resolve the waiting future
            if manager.handle_permission_response(response, data):
                sys.stderr.write(f"[PermissionHandlers] Unified manager handled response successfully\n")
                sys.stderr.flush()
                return
            else:
                sys.stderr.write(f"[PermissionHandlers] Unified manager returned False, falling through\n")
                sys.stderr.flush()

        # Get async permission handler
        sys.stderr.write(f"[PermissionHandlers] Falling back to async permission handler\n")
        sys.stderr.flush()
        self._handle_async_permission_response(event)

    def on_multi_line_input_permission_cancelled(self, event: MultiLineInput.PermissionCancelled) -> None:
        """Handle permission cancellation from MultiLineInput"""
        import sys
        sys.stderr.write(f"\n[PermissionHandlers.on_multi_line_input_permission_cancelled] ENTERED\n")
        sys.stderr.flush()

        manager = get_unified_permission_manager()
        if manager:
            sys.stderr.write(f"[PermissionHandlers] Forwarding CANCEL to unified permission manager\n")
            sys.stderr.flush()
            # Handle cancellation as a CANCEL response
            if manager.handle_permission_response(PermissionResponse.CANCEL, {}):
                sys.stderr.write(f"[PermissionHandlers] Unified manager handled cancellation successfully\n")
                sys.stderr.flush()
                return
            else:
                sys.stderr.write(f"[PermissionHandlers] Unified manager returned False for cancellation\n")
                sys.stderr.flush()

        # Get async permission handler
        sys.stderr.write(f"[PermissionHandlers] Falling back to async cancellation handler\n")
        sys.stderr.flush()
        self._handle_async_permission_cancellation(event)

    def on_multi_line_input_navigation_event(self, event: MultiLineInput.NavigationEvent) -> None:
        """Handle navigation events that should trigger permission auto-dismiss"""
        import sys
        sys.stderr.write(f"[SimpleTUI] Navigation event received: {event.event_type}\n")
        sys.stderr.flush()
        
        # Constitution Principle V: Auto-dismiss on navigation events
        manager = get_unified_permission_manager()
        if manager:
            buffer_manager = manager.get_buffer_manager()
            active_count = buffer_manager.get_active_task_count()
            
            if active_count > 0:
                sys.stderr.write(f"[SimpleTUI] Auto-dismissing {active_count} active permission tasks due to navigation\n")
                sys.stderr.flush()
                
                # Clear all active permission prompts (navigation cancels everything)
                manager.clear_permission_prompt()
            else:
                sys.stderr.write(f"[SimpleTUI] No active permission tasks to dismiss\n")
                sys.stderr.flush()
        else:
            sys.stderr.write(f"[SimpleTUI] Unified permission manager not available\n")
            sys.stderr.flush()

    def _handle_provider_model_selection(self, event) -> None:
        """Handle provider model selection response"""
        try:
            from ..permissions import PermissionResponse
            from ..model_manager import ModelManager
        except ImportError:
            try:
                import importlib
                perms_mod = importlib.import_module('permissions')
                PermissionResponse = perms_mod.PermissionResponse
                model_mgr_mod = importlib.import_module('model_manager')
                ModelManager = model_mgr_mod.ModelManager
            except:
                return

        # Check if user cancelled
        if event.option.get('response') == PermissionResponse.CANCEL:
            self.session._awaiting_provider_model_selection = False
            self.write("\n[dim]Model selection cancelled[/dim]\n\n")
            return

        # Get model data and switch
        option_data = event.option.get('data', {})
        model_id = option_data.get('model_id', '')
        model_name = option_data.get('model_name', '')

        self.session._awaiting_provider_model_selection = False

        # Clear permission prompt
        try:
            prompt_input = self.query_one("#prompt-input")
            self._clear_permission_prompt()
            prompt_input.refresh()
        except:
            pass

        # Switch to the selected model
        model_mgr = ModelManager()
        success = model_mgr.set_current_model(self.session, model_id)

        if success:
            model_mgr.record_model_use(model_id)
            self.write(f"\n[green]✓ Switched to {model_name}[/green]\n")
            self.write(f"[dim]Model ID: {model_id}[/dim]\n\n")
        else:
            self.write(f"\n[red]✗ Failed to switch to {model_name}[/red]\n\n")

    def _handle_local_model_selection(self, event) -> None:
        """Handle local model selection response"""
        try:
            from ..permissions import PermissionResponse
        except ImportError:
            try:
                import importlib
                perms_mod = importlib.import_module('permissions')
                PermissionResponse = perms_mod.PermissionResponse
            except:
                return

        # Check if user cancelled
        if event.option.get('response') == PermissionResponse.CANCEL:
            self.session._awaiting_local_model_selection = False
            self._cleanup_local_model_state()
            self.write("\n[dim]Model installation cancelled[/dim]\n\n")
            return

        # Get current step and handle workflow
        current_step = getattr(self.session, '_local_step', 'setup_type')
        option_data = event.option.get('data', {})

        # Initialize selections if not exists
        if not hasattr(self.session, '_local_selections'):
            self.session._local_selections = {}

        # Handle multi-step workflow
        import asyncio
        asyncio.create_task(self._handle_local_model_step(current_step, option_data))

    def _handle_model_browser_selection(self, event) -> None:
        """Handle model browser selection response"""
        try:
            from ..permissions import PermissionResponse
        except ImportError:
            try:
                import importlib
                perms_mod = importlib.import_module('permissions')
                PermissionResponse = perms_mod.PermissionResponse
            except:
                return

        # Check if user cancelled
        if event.option.get('response') == PermissionResponse.CANCEL:
            self.session._awaiting_model_browser_selection = False
            self.write("\n[dim]Model browser cancelled[/dim]\n\n")
            return

        # Get selected model data
        option_data = event.option.get('data', {})
        model_name = option_data.get('model_name', '')
        
        self.session._awaiting_model_browser_selection = False

        # Clear permission prompt
        try:
            prompt_input = self.query_one("#prompt-input")
            self._clear_permission_prompt()
            prompt_input.refresh()
        except:
            pass

        if model_name:
            self.write(f"\n[green]✓ Selected {model_name} for installation[/green]\n\n")
            # Here you would typically trigger the installation process
        else:
            self.write(f"\n[red]✗ No model selected[/red]\n\n")

    def _handle_async_permission_response(self, event) -> None:
        """Handle async permission response"""
        try:
            from ..async_permissions import get_global_handler
        except ImportError:
            try:
                import importlib
                async_perms = importlib.import_module('async_permissions')
                get_global_handler = async_perms.get_global_handler
            except:
                return

        handler = get_global_handler()
        if handler:
            response_data = {
                'response': event.option.get('response'),
                'data': event.option.get('data', {})
            }
            handler.handle_response(response_data)
            return

        # Fallback: Generic prompt handler
        self._handle_generic_permission_response(event)

    def _handle_async_permission_cancellation(self, event) -> None:
        """Handle async permission cancellation"""
        try:
            from ..async_permissions import get_global_handler
            from ..permissions import PermissionResponse
        except ImportError:
            try:
                import importlib
                async_perms = importlib.import_module('async_permissions')
                get_global_handler = async_perms.get_global_handler
                perms_mod = importlib.import_module('permissions')
                PermissionResponse = perms_mod.PermissionResponse
            except:
                return

        handler = get_global_handler()
        if handler:
            response_data = {
                'response': PermissionResponse.CANCEL,
                'data': {}
            }
            handler.handle_response(response_data)
            return

        # Fallback: Generic prompt cancellation
        self._handle_generic_permission_cancellation()

    def _handle_generic_permission_response(self, event) -> None:
        """Handle generic permission response (SDK loading buffer, etc.)"""
        import sys
        sys.stderr.write(f"\n[SimpleTUI] FALLBACK: Generic permission response\n")
        sys.stderr.write(f"[SimpleTUI] Response: {event.option.get('response')}\n")
        sys.stderr.flush()

        response = event.option.get('response') if isinstance(event.option, dict) else None
        data = event.option.get('data', {}) if isinstance(event.option, dict) else {}

        # First, try to notify unified permission manager (in case we missed it earlier)
        manager = get_unified_permission_manager()
        if manager:
            sys.stderr.write(f"[SimpleTUI] Notifying unified manager from generic fallback\n")
            sys.stderr.flush()
            manager.handle_permission_response(response, data)

        # Only clear UI after manager has been notified
        try:
            prompt_input = self.query_one("#prompt-input")
            self._clear_permission_prompt()
            prompt_input.refresh()
            sys.stderr.write(f"[SimpleTUI] Cleared generic permission buffer (after manager notification)\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"[SimpleTUI] Error clearing buffer: {e}\n")
            sys.stderr.flush()

        if response == 'exit':
            sys.stderr.write(f"[SimpleTUI] Generic prompt requested exit\n")
            sys.stderr.flush()
            self.action_quit_app()

    def _handle_generic_permission_cancellation(self) -> None:
        """Handle generic permission cancellation"""
        import sys
        sys.stderr.write(f"\n[SimpleTUI] FALLBACK: Generic permission cancelled\n")
        sys.stderr.flush()

        # First, try to notify unified permission manager (in case we missed it earlier)
        manager = get_unified_permission_manager()
        if manager:
            sys.stderr.write(f"[SimpleTUI] Notifying unified manager of cancellation from generic fallback\n")
            sys.stderr.flush()
            manager.handle_permission_response(PermissionResponse.CANCEL, {})

        # Only clear UI after manager has been notified
        try:
            prompt_input = self.query_one("#prompt-input")
            self._clear_permission_prompt()
            sys.stderr.write(f"[SimpleTUI] Cleared generic permission buffer (cancelled, after manager notification)\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"[SimpleTUI] Error clearing buffer: {e}\n")
            sys.stderr.flush()

    def _cleanup_local_model_state(self) -> None:
        """Clean up local model selection state"""
        if hasattr(self.session, '_local_context'):
            del self.session._local_context
        if hasattr(self.session, '_local_step'):
            del self.session._local_step
        if hasattr(self.session, '_local_selections'):
            del self.session._local_selections

        # Clear the permission prompt
        try:
            prompt_input = self.query_one("#prompt-input")
            self._clear_permission_prompt()
            prompt_input.refresh()
        except Exception:
            pass

    def _show_permission_prompt(self, prompt_data: dict) -> None:
        """Show permission prompt inside MultiLineInput"""
        try:
            import sys
            sys.stderr.write(f"[TUI._show_permission_prompt] 🔥 SETTING PERMISSION PROMPT DATA 🔥\n")
            sys.stderr.flush()

            prompt_input = self.query_one("#prompt-input", MultiLineInput)
            prompt_data['selected'] = 0
            prompt_input.permission_prompt_data = prompt_data

            # CRITICAL: Force focus to the input widget for permission navigation
            sys.stderr.write(f"[TUI._show_permission_prompt] Forcing focus to prompt_input\n")
            sys.stderr.flush()
            prompt_input.focus()

            # Force refresh to show the permission buffer immediately
            prompt_input.refresh()
            self.refresh()

            sys.stderr.write(f"[TUI._show_permission_prompt] ✅ Permission prompt displayed and focused\n")
            sys.stderr.flush()

            # Debug: Show what the permission buffer looks like
            rendered = prompt_input.render()
            preview = str(rendered).replace('\n', '\\n')[:200]
            sys.stderr.write(f"[TUI._show_permission_prompt] Rendered buffer preview: {preview}...\n")
            sys.stderr.flush()

        except Exception as e:
            import sys
            import traceback
            sys.stderr.write(f"[TUI._show_permission_prompt] ❌ Exception: {e}\n")
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()

    def _clear_permission_prompt(self) -> None:
        """Clear permission prompt from MultiLineInput"""
        try:
            prompt_input = self.query_one("#prompt-input")
            prompt_input.permission_prompt_data = None
            prompt_input.refresh()
        except Exception:
            pass