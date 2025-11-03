"""
Permission System Integration - Unified permission management
Connects permission buffer manager with UI widgets, risk assessment, and external systems

⚠️  DEPRECATION NOTICE ⚠️
This module is being phased out in favor of the canonical authorization boundary.
Please migrate to: from modules.authz import check_authorization
See: modules/authz/README.md for migration guide
"""

import warnings
from typing import Dict, Any, Optional, Callable
import threading
from .manager import PermissionBufferManager
# REMOVED: from .widget import PermissionPrompt (unused widget deleted)
from .enums import PermissionResponse
from .templates import PermissionTemplates
from .risk_assessment import RiskAssessmentManager, RiskLevel

# Issue deprecation warning when this module is imported
warnings.warn(
    "modules.permissions.integration is deprecated. "
    "Use modules.authz.check_authorization instead. "
    "See modules/authz/README.md for migration guide.",
    DeprecationWarning,
    stacklevel=2
)


class UnifiedPermissionManager:
    """
    Unified permission manager that integrates buffer management with UI widgets and risk assessment
    Provides a single interface for all permission-related operations
    """
    
    def __init__(self):
        # Instance tracking for verification (Phase 10)
        import sys
        sys.stderr.write(f"[INSTANCE] UnifiedPermissionManager created: {id(self)}\n")
        sys.stderr.flush()
        
        self._buffer_manager = PermissionBufferManager()
        self._risk_manager = RiskAssessmentManager()
        self._ui_callback: Optional[Callable] = None
        self._response_handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()
    
    def get_buffer_manager(self) -> PermissionBufferManager:
        """Get the buffer manager instance"""
        return self._buffer_manager
    
    def get_risk_manager(self) -> RiskAssessmentManager:
        """Get the risk assessment manager instance"""
        return self._risk_manager
        
    def set_ui_callback(self, callback: Callable) -> None:
        """Set callback function for UI integration (e.g., TUI's _show_permission_prompt)"""
        import sys
        with self._lock:
            self._ui_callback = callback
            sys.stderr.write(f"[UPM.set_ui_callback] ✓ Callback SET on instance {id(self)}: {callback.__name__ if hasattr(callback, '__name__') else callback}\n")
            sys.stderr.flush()
    
    def register_response_handler(self, handler_name: str, handler: Callable) -> None:
        """Register a response handler for specific permission types"""
        with self._lock:
            self._response_handlers[handler_name] = handler
    
    def show_permission_prompt(self, prompt_data: Dict[str, Any], handler_name: str = None) -> bool:
        """Show a permission prompt using the UI system"""
        try:
            # Validate prompt data
            is_valid, error = self._buffer_manager.validate_prompt_data(prompt_data)
            if not is_valid:
                import sys
                sys.stderr.write(f"[UnifiedPermissionManager] Invalid prompt data: {error}\n")
                sys.stderr.flush()
                return False

            # Call UI callback if available
            if self._ui_callback:
                import sys
                sys.stderr.write(f"[UnifiedPermissionManager.show_permission_prompt] Calling _ui_callback with prompt_data\n")
                sys.stderr.flush()

                # Store handler name in prompt_data for response routing
                if handler_name:
                    prompt_data['_handler_name'] = handler_name

                # Call UI callback - it will set permission_prompt_data on MultiLineInput
                self._ui_callback(prompt_data)

                sys.stderr.write(f"[UnifiedPermissionManager.show_permission_prompt] _ui_callback returned\n")
                sys.stderr.flush()
                return True
            else:
                # Fallback to console-based prompt
                return self._show_console_prompt(prompt_data)

        except Exception as e:
            import sys
            sys.stderr.write(f"[UnifiedPermissionManager] Error showing prompt: {e}\n")
            sys.stderr.flush()
            return False

    async def request_permission(self, app, session, prompt_data: Dict[str, Any], timeout: float = None) -> Dict[str, Any]:
        """Request permission with async waiting for response"""
        import asyncio
        import sys
        import inspect

        # Execution path tracing (Phase 11)
        caller_frame = inspect.stack()[1]
        caller_function = caller_frame.function
        caller_file = caller_frame.filename.split('/')[-1] if '/' in caller_frame.filename else caller_frame.filename
        sys.stderr.write(f"[PATH] request_permission called from: {caller_function} in {caller_file}\n")
        sys.stderr.flush()

        sys.stderr.write(f"[UnifiedPermissionManager.request_permission] ENTERED\n")
        sys.stderr.flush()

        # Create a future to wait for the response
        future = asyncio.Future()

        def response_callback(response_data):
            """Callback to resolve the future when response is received"""
            if not future.done():
                future.set_result(response_data)

        # Register a temporary response handler
        temp_handler_name = f"temp_{id(future)}"

        def temp_handler(response, data):
            response_callback({
                'response': response,
                'data': data or {}
            })
            return True

        self.register_response_handler(temp_handler_name, temp_handler)

        try:
            # Show the permission prompt
            success = self.show_permission_prompt(prompt_data, temp_handler_name)

            if not success:
                sys.stderr.write(f"[UnifiedPermissionManager.request_permission] Failed to show prompt\n")
                sys.stderr.flush()
                return {'response': 'error', 'reason': 'failed_to_show'}

            # Wait for the response (with optional timeout)
            try:
                if timeout is None:
                    # NO TIMEOUT - Wait indefinitely for user response
                    sys.stderr.write(f"[UnifiedPermissionManager.request_permission] Waiting for response (NO TIMEOUT - will wait indefinitely)\n")
                    sys.stderr.flush()
                    result = await future
                else:
                    # WITH TIMEOUT - Auto-dismiss after timeout
                    sys.stderr.write(f"[UnifiedPermissionManager.request_permission] Waiting for response (timeout={timeout}s)\n")
                    sys.stderr.flush()
                    result = await asyncio.wait_for(future, timeout=timeout)

                sys.stderr.write(f"[UnifiedPermissionManager.request_permission] Got response: {result}\n")
                sys.stderr.flush()
                return result
            except asyncio.TimeoutError:
                sys.stderr.write(f"[UnifiedPermissionManager.request_permission] Timeout waiting for response\n")
                sys.stderr.flush()
                return {'response': 'timeout', 'reason': 'timeout_expired'}

        finally:
            # Clean up the temporary handler
            if temp_handler_name in self._response_handlers:
                del self._response_handlers[temp_handler_name]
    
    def handle_permission_response(self, response: PermissionResponse, data: Dict[str, Any] = None) -> bool:
        """Handle permission response from UI or other sources"""
        try:
            import sys
            sys.stderr.write(f"\n[UnifiedPermissionManager.handle_permission_response] ENTERED\n")
            sys.stderr.write(f"[UnifiedPermissionManager] Response: {response}\n")
            sys.stderr.write(f"[UnifiedPermissionManager] Data: {data}\n")
            sys.stderr.flush()

            response_data = {
                'response': response,
                'data': data or {}
            }

            # Validate response
            is_valid, error = self._buffer_manager.validate_prompt_response(response_data)
            if not is_valid:
                sys.stderr.write(f"[UnifiedPermissionManager] Invalid response: {error}\n")
                sys.stderr.flush()
                return False

            sys.stderr.write(f"[UnifiedPermissionManager] Response validated successfully\n")
            sys.stderr.flush()

            # Route to specific handler if available
            if handler_name and handler_name in self._response_handlers:
                sys.stderr.write(f"[UnifiedPermissionManager] Routing to specific handler: {handler_name}\n")
                sys.stderr.flush()
                handler = self._response_handlers[handler_name]
                result = handler(response, data)
                self._clear_current_prompt()
                sys.stderr.write(f"[UnifiedPermissionManager] Handler completed, prompt cleared\n")
                sys.stderr.flush()
                return result

            # Default handling - resolve through buffer manager
            sys.stderr.write(f"[UnifiedPermissionManager] Using default handling - resolving buffer manager\n")
            sys.stderr.flush()
            self._buffer_manager.resolve(response_data)
            sys.stderr.write(f"[UnifiedPermissionManager] Buffer manager resolved\n")
            sys.stderr.flush()

            self._clear_current_prompt()
            sys.stderr.write(f"[UnifiedPermissionManager] Prompt cleared, returning True\n")
            sys.stderr.flush()
            return True

        except Exception as e:
            import sys
            import traceback
            sys.stderr.write(f"[UnifiedPermissionManager] Error handling response: {e}\n")
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
            return False
    
    def clear_permission_prompt(self) -> bool:
        """Clear current permission prompt"""
        try:
            self._buffer_manager.clear()
            self._clear_current_prompt()
            return True
        except Exception as e:
            import sys
            sys.stderr.write(f"[UnifiedPermissionManager] Error clearing prompt: {e}\n")
            sys.stderr.flush()
            return False
    
    def _clear_current_prompt(self) -> None:
        """Internal method to clear current widget state"""
        with self._lock:
            # Widget cleared via UI callback now - MultiLineInput handles clearing
            pass

    # Risk assessment delegation methods
    
    def assess_operation_risk(
        self, 
        tool_name: str, 
        args: Optional[Dict[str, Any]] = None, 
        current_dir: Optional[str] = None
    ) -> tuple[RiskLevel, str]:
        """Assess risk level for an operation"""
        return self._risk_manager.assess_operation_risk(tool_name, args, current_dir)
    
    def assess_path_risk(self, file_path: str, current_dir: Optional[str] = None) -> tuple[RiskLevel, str]:
        """Assess risk level for a file path"""
        return self._risk_manager.assess_path_risk(file_path, current_dir)
    
    def should_prompt_for_operation(
        self, 
        tool_name: str, 
        args: Optional[Dict[str, Any]] = None, 
        current_dir: Optional[str] = None
    ) -> tuple[bool, str, RiskLevel]:
        """Determine if operation requires permission prompt"""
        return self._risk_manager.should_prompt(tool_name, args, current_dir)
    
    def is_tool_allowed(self, tool_name: str) -> bool:
        """Check if tool is in allowed list"""
        return self._risk_manager.is_tool_allowed(tool_name)
    
    def add_allowed_tool(self, tool_name: str) -> bool:
        """Add tool to allowed list"""
        return self._risk_manager.add_allowed_tool(tool_name)
    
    def remove_allowed_tool(self, tool_name: str) -> bool:
        """Remove tool from allowed list"""
        return self._risk_manager.remove_allowed_tool(tool_name)
    
    def set_auto_accept(self, enabled: bool) -> None:
        """Enable/disable global auto-accept mode"""
        self._risk_manager.set_auto_accept(enabled)
    
    def format_operation_preview(
        self, 
        tool_name: str, 
        args: Dict[str, Any], 
        current_dir: Optional[str] = None
    ) -> str:
        """Format operation preview for display"""
        return self._risk_manager.format_operation_preview(tool_name, args, current_dir)
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get risk assessment configuration summary"""
        return self._risk_manager.get_risk_summary()
    
    def _show_console_prompt(self, prompt_data: Dict[str, Any]) -> bool:
        """Fallback console-based permission prompt"""
        try:
            import sys
            sys.stderr.write(f"[UPM._show_console_prompt] ENTERED\n")
            sys.stderr.flush()
            print(f"\n=== {prompt_data.get('title', 'Permission Required')} ===")
            print(prompt_data.get('message', 'Allow this operation?'))
            
            details = prompt_data.get('details', {})
            if details:
                print("\nDetails:")
                for key, value in details.items():
                    print(f"  {key}: {value}")
            
            options = prompt_data.get('options', [])
            print("\nOptions:")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option.get('text', 'Unknown option')}")
            
            while True:
                try:
                    import sys
                    sys.stderr.write(f"[UPM._show_console_prompt] About to call input()\n")
                    sys.stderr.flush()
                    choice = input("\nEnter choice (number): ").strip()
                    sys.stderr.write(f"[UPM._show_console_prompt] Got choice: '{choice}'\n")
                    sys.stderr.flush()
                    if choice.isdigit():
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(options):
                            selected_option = options[choice_num - 1]
                            response = selected_option.get('response', PermissionResponse.DENY)
                            data = selected_option.get('data', {})
                            sys.stderr.write(f"[UPM._show_console_prompt] Returning success\n")
                            sys.stderr.flush()
                            return self.handle_permission_response(response, data)
                    print("Invalid choice. Please enter a valid number.")
                except (KeyboardInterrupt, EOFError):
                    sys.stderr.write(f"[UPM._show_console_prompt] KeyboardInterrupt/EOFError\n")
                    sys.stderr.flush()
                    return self.handle_permission_response(PermissionResponse.CANCEL)
                    
        except Exception as e:
            import sys
            sys.stderr.write(f"[UnifiedPermissionManager] Console prompt error: {e}\n")
            sys.stderr.flush()
            return False
    
    def get_buffer_manager(self) -> PermissionBufferManager:
        """Get the underlying buffer manager for advanced operations"""
        return self._buffer_manager
    
    async def check_permission(
        self,
        registration,
        context: Dict[str, Any],
        app=None,
        session=None
    ) -> bool:
        """
        Check if execution should be permitted
        
        PHASE 2: Now routes through canonical authz facade

        Args:
            registration: ExecutionRegistration - What's being executed
            context: Execution context (args, paths, etc.)
            app: TUI app (for showing prompts)
            session: Session object

        Returns:
            True if approved, False if denied
        """
        # PHASE 2: Route through canonical authz boundary
        try:
            from ..authz import check_authorization, AuthzSubject
            
            # Create subject
            subject = AuthzSubject(
                id=getattr(session, 'id', 'unknown') if session else 'unknown',
                type='user'
            )
            
            # Map to action
            action_map = {
                'command': 'command:execute',
                'tool': 'tool:execute',
                'api': 'api:call'
            }
            action = action_map.get(
                registration.type.value if hasattr(registration, 'type') else 'unknown',
                f"execute:{registration.name}"
            )
            
            # Extract resource
            resource = (
                context.get('file_path') or 
                context.get('resource') or 
                context.get('command') or 
                registration.name
            )
            
            # Call canonical authz
            decision = await check_authorization(
                subject=subject,
                action=action,
                resource=resource,
                context=context,
                app=app,
                session=session
            )
            
            return decision.allowed
            
        except ImportError:
            # Fallback to legacy if authz not available
            return await self._legacy_check_permission(registration, context, app, session)
    
    async def _legacy_check_permission(
        self,
        registration,
        context: Dict[str, Any],
        app=None,
        session=None
    ) -> bool:
        """Legacy implementation (fallback only)"""
        # Skip if doesn't require approval
        if not registration.requires_approval:
            return True

        # Check for custom prompt function
        custom_prompt_func = registration.metadata.get('custom_prompt_func') if registration.metadata else None

        if custom_prompt_func:
            try:
                prompt_data = custom_prompt_func(app, session, registration, context)
            except Exception:
                return False

            if not prompt_data:
                return False
        else:
            prompt_data = {
                'title': f'System: {registration.name}',
                'message': registration.description or f'Execute {registration.name}?',
                'options': [
                    {'text': 'Yes, allow this once', 'response': 'allow_once', 'data': {}},
                    {'text': 'No, cancel', 'response': 'cancel', 'data': {}}
                ]
            }

        try:
            response_data = await self.request_permission(app, session, prompt_data, timeout=None)
            response = response_data.get('response', 'cancel')
            return response in ['allow_once', 'allow_session', 'allow_always']
        except Exception:
            return False

    def shutdown(self) -> None:
        """Shutdown the unified permission manager"""
        self._buffer_manager.shutdown()
        self._clear_current_prompt()


# Global instance management
_unified_manager: Optional[UnifiedPermissionManager] = None
_manager_lock = threading.Lock()


def get_unified_permission_manager() -> UnifiedPermissionManager:
    """Get singleton unified permission manager instance"""
    import sys
    global _unified_manager
    if _unified_manager is None:
        with _manager_lock:
            if _unified_manager is None:
                _unified_manager = UnifiedPermissionManager()
                sys.stderr.write(f"[GET_UPM] Created NEW instance: {id(_unified_manager)}\n")
                sys.stderr.flush()

    # CRITICAL: Log callback status EVERY time
    callback_status = "SET" if _unified_manager._ui_callback else "NONE"
    sys.stderr.write(f"[GET_UPM] Returning instance {id(_unified_manager)}, callback={callback_status}\n")
    sys.stderr.flush()

    return _unified_manager


def reset_unified_permission_manager() -> None:
    """Reset singleton (for testing)"""
    global _unified_manager
    with _manager_lock:
        if _unified_manager:
            _unified_manager.shutdown()
        _unified_manager = None


# Convenience functions for common operations
def show_file_permission_prompt(file_path: str, operation: str, **kwargs) -> bool:
    """Show file operation permission prompt"""
    manager = get_unified_permission_manager()
    prompt_data = PermissionTemplates.create_file_permission_prompt(
        file_path, operation, **kwargs
    )
    return manager.show_permission_prompt(prompt_data, 'file_operation')


def show_bash_permission_prompt(command: str, **kwargs) -> bool:
    """Show bash command permission prompt"""
    manager = get_unified_permission_manager()
    prompt_data = PermissionTemplates.create_bash_permission_prompt(
        command, **kwargs
    )
    return manager.show_permission_prompt(prompt_data, 'bash_command')


def show_api_permission_prompt(api_name: str, **kwargs) -> bool:
    """Show API operation permission prompt"""
    manager = get_unified_permission_manager()
    prompt_data = PermissionTemplates.create_api_permission_prompt(
        api_name, **kwargs
    )
    return manager.show_permission_prompt(prompt_data, 'api_operation')


def show_tool_permission_prompt(tool_name: str, tool_args: Dict[str, Any], **kwargs) -> bool:
    """Show tool execution permission prompt"""
    manager = get_unified_permission_manager()
    prompt_data = PermissionTemplates.create_tool_permission_prompt(
        tool_name, tool_args, **kwargs
    )
    return manager.show_permission_prompt(prompt_data, 'tool_execution')