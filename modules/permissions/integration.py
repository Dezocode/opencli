"""
Permission System Integration - Unified permission management
Connects permission buffer manager with UI widgets and external systems
"""

from typing import Dict, Any, Optional, Callable
import threading
from .manager import PermissionBufferManager
from .widget import PermissionPrompt
from .enums import PermissionResponse
from .templates import PermissionTemplates


class UnifiedPermissionManager:
    """
    Unified permission manager that integrates buffer management with UI widgets
    Provides a single interface for all permission-related operations
    """
    
    def __init__(self):
        self._buffer_manager = PermissionBufferManager()
        self._current_widget: Optional[PermissionPrompt] = None
        self._ui_callback: Optional[Callable] = None
        self._response_handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        
    def set_ui_callback(self, callback: Callable) -> None:
        """Set callback function for UI integration (e.g., TUI's _show_permission_prompt)"""
        with self._lock:
            self._ui_callback = callback
    
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
            
            # Create widget if UI callback available
            if self._ui_callback:
                with self._lock:
                    self._current_widget = PermissionPrompt(
                        title=prompt_data.get('title', 'Permission Required'),
                        message=prompt_data.get('message', 'Allow this operation?'),
                        options=prompt_data.get('options', []),
                        details=prompt_data.get('details', {})
                    )
                    
                    # Store handler name for response routing
                    if handler_name:
                        self._current_widget.handler_name = handler_name
                
                # Call UI to show the prompt
                self._ui_callback(prompt_data)
                return True
            else:
                # Fallback to console-based prompt
                return self._show_console_prompt(prompt_data)
                
        except Exception as e:
            import sys
            sys.stderr.write(f"[UnifiedPermissionManager] Error showing prompt: {e}\n")
            sys.stderr.flush()
            return False
    
    def handle_permission_response(self, response: PermissionResponse, data: Dict[str, Any] = None) -> bool:
        """Handle permission response from UI or other sources"""
        try:
            response_data = {
                'response': response,
                'data': data or {}
            }
            
            # Validate response
            is_valid, error = self._buffer_manager.validate_prompt_response(response_data)
            if not is_valid:
                import sys
                sys.stderr.write(f"[UnifiedPermissionManager] Invalid response: {error}\n")
                sys.stderr.flush()
                return False
            
            # Route to specific handler if available
            handler_name = getattr(self._current_widget, 'handler_name', None)
            if handler_name and handler_name in self._response_handlers:
                handler = self._response_handlers[handler_name]
                result = handler(response, data)
                self._clear_current_prompt()
                return result
            
            # Default handling
            self._buffer_manager.resolve(response_data)
            self._clear_current_prompt()
            return True
            
        except Exception as e:
            import sys
            sys.stderr.write(f"[UnifiedPermissionManager] Error handling response: {e}\n")
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
            if self._current_widget:
                self._current_widget.hide()
                self._current_widget = None
    
    def _show_console_prompt(self, prompt_data: Dict[str, Any]) -> bool:
        """Fallback console-based permission prompt"""
        try:
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
                    choice = input("\nEnter choice (number): ").strip()
                    if choice.isdigit():
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(options):
                            selected_option = options[choice_num - 1]
                            response = selected_option.get('response', PermissionResponse.DENY)
                            data = selected_option.get('data', {})
                            return self.handle_permission_response(response, data)
                    print("Invalid choice. Please enter a valid number.")
                except (KeyboardInterrupt, EOFError):
                    return self.handle_permission_response(PermissionResponse.CANCEL)
                    
        except Exception as e:
            import sys
            sys.stderr.write(f"[UnifiedPermissionManager] Console prompt error: {e}\n")
            sys.stderr.flush()
            return False
    
    def get_buffer_manager(self) -> PermissionBufferManager:
        """Get the underlying buffer manager for advanced operations"""
        return self._buffer_manager
    
    def get_current_widget(self) -> Optional[PermissionPrompt]:
        """Get current permission widget (for UI integration)"""
        return self._current_widget
    
    def shutdown(self) -> None:
        """Shutdown the unified permission manager"""
        self._buffer_manager.shutdown()
        self._clear_current_prompt()


# Global instance management
_unified_manager: Optional[UnifiedPermissionManager] = None
_manager_lock = threading.Lock()


def get_unified_permission_manager() -> UnifiedPermissionManager:
    """Get singleton unified permission manager instance"""
    global _unified_manager
    if _unified_manager is None:
        with _manager_lock:
            if _unified_manager is None:
                _unified_manager = UnifiedPermissionManager()
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