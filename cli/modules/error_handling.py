"""
CLI Error Handling Module
Comprehensive error handling for CLI operations and API interactions
"""

import asyncio
from typing import Dict, Any, Optional
from pathlib import Path


class CLIErrorHandler:
    """Handles various types of CLI errors with appropriate responses"""
    
    def __init__(self, component_init, system_init):
        """Initialize CLI error handler
        
        Args:
            component_init: Component initializer
            system_init: System initializer
        """
        self.component_init = component_init
        self.system_init = system_init
    
    def handle_api_error(self, error: Exception, session, config) -> str:
        """Handle API errors, particularly OpenRouter policy errors
        
        Args:
            error: Exception from API call
            session: Current session
            config: Configuration dictionary
            
        Returns:
            Action to take: "retry", "denied", or "abort"
        """
        try:
            from modules.async_interactive import extract_openrouter_policy_error
            policy_message = extract_openrouter_policy_error(error)
        except ImportError:
            policy_message = None
        
        if policy_message:
            return self._handle_openrouter_policy_error(policy_message, session, config)
        
        # Re-raise non-policy errors
        raise error
    
    def _handle_openrouter_policy_error(self, policy_message: str, session, config) -> str:
        """Handle OpenRouter policy errors
        
        Args:
            policy_message: Policy error message
            session: Current session
            config: Configuration dictionary
            
        Returns:
            Action to take: "retry" or "denied"
        """
        from .interactive_helpers import configure_openrouter_headers_cli
        
        # Get model manager for header configuration
        if self.component_init.is_feature_available('MODEL_MANAGER'):
            ModelManager = self.component_init.get_component('model_manager')
            model_mgr = ModelManager()
            
            action = configure_openrouter_headers_cli(policy_message, session, config, model_mgr)
            return action
        
        return "denied"
    
    def handle_import_error(self, component_name: str, error: ImportError) -> None:
        """Handle component import errors with informative messages
        
        Args:
            component_name: Name of the component that failed to import
            error: Import error that occurred
        """
        error_messages = {
            'async_tui': "TUI not available, using fallback mode",
            'model_manager': "Model management features limited",
            'tool_utils': "Tool processing features limited",
            'uptime_checker': "Model uptime checking unavailable",
            'rich_prompt': "Basic prompt interface will be used",
            'agent_system': "Agent management unavailable",
            'command_registry': "Command registry unavailable", 
            'prompt_processor': "Prompt processing limited",
            'tool_permissions': "Tool permissions unavailable",
            'api_server': "API server unavailable",
            'cache_manager': "Cache management unavailable"
        }
        
        message = error_messages.get(component_name, f"{component_name} unavailable")
        print(f"\033[33m⚠️  {message}: {error}\033[0m")
    
    def handle_component_initialization_error(self, component_name: str, error: Exception) -> None:
        """Handle component initialization errors
        
        Args:
            component_name: Name of the component that failed to initialize
            error: Initialization error that occurred
        """
        print(f"\033[33m⚠️  {component_name} initialization failed: {error}\033[0m\n")
    
    def handle_session_error(self, error: Exception) -> Optional[object]:
        """Handle session loading/creation errors
        
        Args:
            error: Session error that occurred
            
        Returns:
            None if error is unrecoverable
        """
        print(f"\033[31mSession error: {error}\033[0m")
        print("Creating new session...")
        return None
    
    def handle_configuration_error(self, error: Exception) -> Dict[str, Any]:
        """Handle configuration loading errors
        
        Args:
            error: Configuration error that occurred
            
        Returns:
            Default configuration dictionary
        """
        print(f"\033[33m⚠️  Configuration error: {error}\033[0m")
        print("Using default configuration...")
        
        # Return minimal default configuration
        return {
            "model": "gpt-3.5-turbo",
            "contextWindow": 128000,
            "maxTurns": 25,
            "debug": False
        }
    
    def handle_keyboard_interrupt(self) -> bool:
        """Handle keyboard interrupt (Ctrl+C)
        
        Returns:
            True to continue, False to exit
        """
        print("\n\033[2m[Interrupted]\033[0m\n")
        return True  # Continue execution
    
    def handle_eof_error(self) -> bool:
        """Handle EOF error (Ctrl+D)
        
        Returns:
            False to exit gracefully
        """
        print()  # New line
        return False  # Exit
    
    def handle_general_error(self, error: Exception, context: str = "") -> None:
        """Handle general errors with context
        
        Args:
            error: General error that occurred
            context: Context where the error occurred
        """
        context_str = f" in {context}" if context else ""
        print(f"\n\033[31mError{context_str}: {error}\033[0m\n")
    
    def handle_tool_execution_error(self, tool_name: str, error: Exception) -> str:
        """Handle tool execution errors
        
        Args:
            tool_name: Name of the tool that failed
            error: Tool execution error
            
        Returns:
            Error message for the tool result
        """
        error_message = f"Tool '{tool_name}' execution failed: {error}"
        print(f"\033[31m⚙ {error_message}\033[0m")
        return error_message
    
    def handle_permission_error(self, action: str, reason: str) -> None:
        """Handle permission-related errors
        
        Args:
            action: Action that was denied
            reason: Reason for permission denial
        """
        print(f"\033[31m🔒 Permission denied for {action}: {reason}\033[0m")
    
    def handle_validation_error(self, validation_type: str, error: Exception) -> None:
        """Handle validation errors
        
        Args:
            validation_type: Type of validation that failed
            error: Validation error that occurred
        """
        print(f"\033[33m⚠️  {validation_type} validation failed: {error}\033[0m")
    
    def create_error_context(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Create error context for logging and debugging
        
        Args:
            error: Error that occurred
            operation: Operation being performed when error occurred
            
        Returns:
            Error context dictionary
        """
        return {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'operation': operation,
            'timestamp': self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for error logging
        
        Returns:
            ISO format timestamp string
        """
        from datetime import datetime
        return datetime.now().isoformat()


class ErrorRecoveryManager:
    """Manages error recovery strategies and fallback mechanisms"""
    
    def __init__(self, error_handler: CLIErrorHandler):
        """Initialize error recovery manager
        
        Args:
            error_handler: CLI error handler instance
        """
        self.error_handler = error_handler
        self.recovery_attempts = {}
    
    def attempt_api_recovery(self, error: Exception, session, config, max_attempts: int = 3) -> str:
        """Attempt to recover from API errors
        
        Args:
            error: API error that occurred
            session: Current session
            config: Configuration dictionary
            max_attempts: Maximum recovery attempts
            
        Returns:
            Recovery action: "retry", "fallback", or "abort"
        """
        error_key = f"api_{type(error).__name__}"
        attempts = self.recovery_attempts.get(error_key, 0)
        
        if attempts >= max_attempts:
            print(f"⚠️  Maximum recovery attempts ({max_attempts}) reached for API errors")
            return "abort"
        
        self.recovery_attempts[error_key] = attempts + 1
        
        try:
            action = self.error_handler.handle_api_error(error, session, config)
            if action == "retry":
                print(f"🔄 Retry attempt {attempts + 1}/{max_attempts}")
            return action
        except Exception:
            return "abort"
    
    def attempt_component_recovery(self, component_name: str, init_func, max_attempts: int = 2):
        """Attempt to recover from component initialization failures
        
        Args:
            component_name: Name of component to recover
            init_func: Function to re-initialize component
            max_attempts: Maximum recovery attempts
            
        Returns:
            Component instance or None if recovery failed
        """
        recovery_key = f"component_{component_name}"
        attempts = self.recovery_attempts.get(recovery_key, 0)
        
        if attempts >= max_attempts:
            return None
        
        self.recovery_attempts[recovery_key] = attempts + 1
        
        try:
            return init_func()
        except Exception as e:
            self.error_handler.handle_component_initialization_error(component_name, e)
            return None
    
    def reset_recovery_attempts(self, error_type: str = None) -> None:
        """Reset recovery attempt counters
        
        Args:
            error_type: Specific error type to reset, or None for all
        """
        if error_type:
            self.recovery_attempts.pop(error_type, None)
        else:
            self.recovery_attempts.clear()


def create_cli_error_handler(component_init, system_init) -> CLIErrorHandler:
    """Factory function to create CLI error handler
    
    Args:
        component_init: Component initializer
        system_init: System initializer
        
    Returns:
        CLIErrorHandler instance
    """
    return CLIErrorHandler(component_init, system_init)


def create_error_recovery_manager(error_handler: CLIErrorHandler) -> ErrorRecoveryManager:
    """Factory function to create error recovery manager
    
    Args:
        error_handler: CLI error handler instance
        
    Returns:
        ErrorRecoveryManager instance
    """
    return ErrorRecoveryManager(error_handler)