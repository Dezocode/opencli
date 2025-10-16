"""
OpenCLI Command Registry
Centralized command management with permission system
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

class CommandRegistry:
    def __init__(self, config_dir=None, executor=None):
        """Initialize command registry.

        Args:
            config_dir: Configuration directory path
            executor: Optional ExecutionSystem instance for runtime command lookup
        """
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.permissions_file = self.config_dir / "command_permissions.json"
        self.usage_file = self.config_dir / "command_usage.json"

        # Optional reference to runtime executor
        self.executor = executor

        # Import static command definitions from modular system
        try:
            # Try relative imports first (when imported as package)
            from .command_registry import get_static_commands
            from .command_registry.core import CommandRegistrationCore
            from .command_registry.validation import CommandValidator, InteractivePermissionManager
            from .command_registry.lifecycle import CommandLifecycleManager, CommandAnalytics
            from .command_registry.error_handling import CommandErrorHandler, CommandErrorRecovery
        except ImportError:
            # Fallback to absolute imports (when run directly)
            from command_registry import get_static_commands
            from command_registry.core import CommandRegistrationCore
            from command_registry.validation import CommandValidator, InteractivePermissionManager
            from command_registry.lifecycle import CommandLifecycleManager, CommandAnalytics
            from command_registry.error_handling import CommandErrorHandler, CommandErrorRecovery
        
        self.available_commands = get_static_commands()
        self.core = CommandRegistrationCore()
        self.validator = CommandValidator(self.permissions_file, self.available_commands)
        self.interactive_manager = InteractivePermissionManager(self.validator)
        self.lifecycle = CommandLifecycleManager(self.usage_file, self.available_commands)
        self.analytics = CommandAnalytics(self.lifecycle)
        
        # Initialize error handling system
        error_log_path = self.config_dir / "command_errors.log"
        self.error_handler = CommandErrorHandler(error_log_path)
        self.error_recovery = CommandErrorRecovery(self.error_handler)
        
        self.permissions = self.validator.permissions

    def get_runtime_commands(self) -> Dict[str, Dict]:
        """Get commands from runtime registry or fallback to static definitions."""
        return self.core.get_runtime_commands(self.executor, self.available_commands)

    def is_enabled(self, command):
        """Check if a command is enabled"""
        return self.validator.is_enabled(command)

    def enable_command(self, command):
        """Enable a command"""
        success, message = self.validator.enable_command(command)
        # Update local permissions reference
        self.permissions = self.validator.permissions
        return success, message

    def disable_command(self, command):
        """Disable a command"""
        success, message = self.validator.disable_command(command)
        # Update local permissions reference
        self.permissions = self.validator.permissions
        return success, message

    def get_enabled_commands(self, feature_flags=None):
        """Get list of currently enabled commands"""
        return self.validator.get_enabled_commands(feature_flags)

    def get_all_commands(self):
        """Get all available commands with metadata"""
        return self.available_commands

    def get_command_info(self, command):
        """Get information about a specific command"""
        if not command.startswith('/'):
            command = f'/{command}'

        return self.available_commands.get(command)

    def interactive_permission_setup(self, feature_flags=None):
        """Interactive setup to enable/disable commands one by one"""
        updated_permissions = self.interactive_manager.interactive_setup(feature_flags)
        # Update local permissions reference
        self.permissions = updated_permissions
        return updated_permissions

    # ========================================================================
    # COMMAND SEARCH AND AUTOCOMPLETE
    # ========================================================================

    def search_commands(
        self,
        query: str,
        feature_flags: Optional[Dict] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Search commands with priority-based ranking."""
        return self.core.search_commands(
            query=query,
            available_commands=self.get_runtime_commands(),
            permissions=self.permissions,
            feature_flags=feature_flags,
            usage_stats=self.get_usage_stats(),
            limit=limit
        )


    # ========================================================================
    # USAGE TRACKING
    # ========================================================================

    def get_usage_stats(self) -> Dict[str, int]:
        """Load command usage statistics from file."""
        return self.lifecycle.get_usage_stats()

    def record_usage(self, command: str) -> None:
        """Increment usage counter for a command."""
        self.lifecycle.record_usage(command)

    def get_most_used_commands(self, limit: int = 10) -> List[Dict]:
        """Get most frequently used commands."""
        return self.lifecycle.get_most_used_commands(limit)

    # ========================================================================
    # ERROR HANDLING
    # ========================================================================

    def handle_command_error(self, command: str, error_type: str, **kwargs):
        """Handle a command error with appropriate error type."""
        if error_type == 'unknown':
            return self.error_handler.handle_unknown_command(command, self.get_runtime_commands())
        elif error_type == 'permission_denied':
            reason = kwargs.get('reason')
            return self.error_handler.handle_permission_denied(command, reason)
        elif error_type == 'invalid_arguments':
            expected = kwargs.get('expected')
            provided = kwargs.get('provided')
            return self.error_handler.handle_invalid_arguments(command, expected, provided)
        elif error_type == 'feature_unavailable':
            feature = kwargs.get('feature')
            return self.error_handler.handle_feature_unavailable(command, feature)
        elif error_type == 'execution_failed':
            exception = kwargs.get('exception')
            return self.error_handler.handle_execution_error(command, exception)
        elif error_type == 'validation_error':
            message = kwargs.get('message')
            return self.error_handler.handle_validation_error(command, message)
        else:
            return self.error_handler.handle_system_error(f"Unknown error type: {error_type}")

    def get_error_statistics(self):
        """Get error statistics."""
        return self.error_handler.get_error_statistics()

    def get_recent_errors(self, limit: int = 10):
        """Get recent errors."""
        return self.error_handler.get_recent_errors(limit)

    def export_error_report(self):
        """Export comprehensive error report."""
        return self.error_handler.export_error_report()

    def attempt_command_recovery(self, command: str):
        """Attempt to recover from command error."""
        return self.error_recovery.attempt_command_recovery(command, self.get_runtime_commands())

    def create_error_context(self, error, user_context=None):
        """Create rich error context for user display."""
        return self.error_recovery.create_error_context(error, user_context)
