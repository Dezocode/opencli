"""
Command Error Handlers
Concrete error handling implementations for different error types
"""

import logging
import traceback
from typing import Dict, List, Optional, Any
from pathlib import Path

from .error_types import (
    CommandError, 
    CommandErrorType, 
    ErrorStatistics, 
    ErrorPatternAnalyzer,
    ErrorReportGenerator,
    CommandSimilarityMatcher
)


class CommandErrorHandler:
    """Handles command-related errors with logging and recovery"""
    
    def __init__(self, log_file: Optional[Path] = None):
        """Initialize error handler.
        
        Args:
            log_file: Optional path to error log file
        """
        self.log_file = log_file
        self.statistics = ErrorStatistics()
        self.analyzer = ErrorPatternAnalyzer(self.statistics)
        self.report_generator = ErrorReportGenerator(self.statistics, self.analyzer)
        
        # Setup logger
        self.logger = logging.getLogger('command_registry')
        if not self.logger.handlers and log_file:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.WARNING)
    
    def handle_unknown_command(self, command: str, available_commands: Dict[str, Any]) -> CommandError:
        """Handle unknown command error with suggestions.
        
        Args:
            command: Unknown command name
            available_commands: Dictionary of available commands
            
        Returns:
            CommandError with suggestions
        """
        suggestions = CommandSimilarityMatcher.find_similar_commands(command, available_commands)
        details = {'suggestions': suggestions[:3]}  # Top 3 suggestions
        
        if suggestions:
            message = f"Unknown command '{command}'. Did you mean: {', '.join(suggestions[:3])}?"
        else:
            message = f"Unknown command '{command}'. Use '/help' to see available commands."
            
        error = CommandError(message, CommandErrorType.UNKNOWN_COMMAND, command, details)
        self._log_error(error)
        return error
        
    def handle_permission_denied(self, command: str, reason: str = None) -> CommandError:
        """Handle permission denied error.
        
        Args:
            command: Command that was denied
            reason: Optional reason for denial
            
        Returns:
            CommandError with permission guidance
        """
        base_message = f"Permission denied for command '{command}'"
        if reason:
            message = f"{base_message}: {reason}"
        else:
            message = f"{base_message}. Use '/commands' to manage permissions."
            
        details = {'reason': reason} if reason else {}
        error = CommandError(message, CommandErrorType.PERMISSION_DENIED, command, details)
        self._log_error(error)
        return error
        
    def handle_invalid_arguments(self, command: str, expected: str = None, provided: List[str] = None) -> CommandError:
        """Handle invalid arguments error.
        
        Args:
            command: Command with invalid arguments
            expected: Description of expected arguments
            provided: List of provided arguments
            
        Returns:
            CommandError with argument guidance
        """
        message = f"Invalid arguments for command '{command}'"
        details = {}
        
        if expected:
            message += f". Expected: {expected}"
            details['expected'] = expected
            
        if provided:
            message += f". Provided: {', '.join(provided)}"
            details['provided'] = provided
            
        error = CommandError(message, CommandErrorType.INVALID_ARGUMENTS, command, details)
        self._log_error(error)
        return error
        
    def handle_feature_unavailable(self, command: str, feature: str) -> CommandError:
        """Handle feature unavailable error.
        
        Args:
            command: Command requiring unavailable feature
            feature: Name of unavailable feature
            
        Returns:
            CommandError with feature information
        """
        message = f"Command '{command}' requires feature '{feature}' which is not available"
        details = {'required_feature': feature}
        
        error = CommandError(message, CommandErrorType.FEATURE_UNAVAILABLE, command, details)
        self._log_error(error)
        return error
        
    def handle_execution_error(self, command: str, exception: Exception) -> CommandError:
        """Handle command execution error.
        
        Args:
            command: Command that failed to execute
            exception: Original exception that occurred
            
        Returns:
            CommandError with execution details
        """
        message = f"Command '{command}' failed to execute: {str(exception)}"
        details = {
            'original_exception': type(exception).__name__,
            'exception_message': str(exception),
            'traceback': traceback.format_exc()
        }
        
        error = CommandError(message, CommandErrorType.EXECUTION_FAILED, command, details)
        self._log_error(error, level=logging.ERROR)
        return error
        
    def handle_validation_error(self, command: str, validation_message: str) -> CommandError:
        """Handle command validation error.
        
        Args:
            command: Command that failed validation
            validation_message: Validation error message
            
        Returns:
            CommandError with validation details
        """
        message = f"Validation failed for command '{command}': {validation_message}"
        details = {'validation_message': validation_message}
        
        error = CommandError(message, CommandErrorType.VALIDATION_ERROR, command, details)
        self._log_error(error)
        return error
        
    def handle_configuration_error(self, message: str, config_path: str = None) -> CommandError:
        """Handle configuration-related error.
        
        Args:
            message: Configuration error message
            config_path: Path to configuration file if applicable
            
        Returns:
            CommandError with configuration details
        """
        details = {'config_path': config_path} if config_path else {}
        error = CommandError(message, CommandErrorType.CONFIGURATION_ERROR, details=details)
        self._log_error(error, level=logging.ERROR)
        return error
        
    def handle_system_error(self, message: str, system_details: Dict = None) -> CommandError:
        """Handle system-level error.
        
        Args:
            message: System error message
            system_details: Additional system information
            
        Returns:
            CommandError with system details
        """
        details = system_details or {}
        error = CommandError(message, CommandErrorType.SYSTEM_ERROR, details=details)
        self._log_error(error, level=logging.CRITICAL)
        return error
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics and patterns."""
        return self.statistics.get_error_statistics()
        
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors."""
        return self.statistics.get_recent_errors(limit)
        
    def clear_error_history(self) -> None:
        """Clear error history and statistics."""
        self.statistics.clear_error_history()
        
    def export_error_report(self) -> Dict[str, Any]:
        """Export comprehensive error report."""
        return self.report_generator.export_error_report()
        
    def _log_error(self, error: CommandError, level: int = logging.WARNING) -> None:
        """Log error and update statistics.
        
        Args:
            error: CommandError to log
            level: Logging level
        """
        # Record error in statistics
        self.statistics.record_error(error)
            
        # Log the error
        if self.logger:
            log_message = f"[{error.error_type.value}] {error.message}"
            if error.command:
                log_message += f" (command: {error.command})"
            self.logger.log(level, log_message, extra={'error_details': error.details})


class CommandErrorClassifier:
    """Classifies and categorizes command errors for analysis"""
    
    @staticmethod
    def classify_error_severity(error: CommandError) -> str:
        """Classify error severity level.
        
        Args:
            error: CommandError to classify
            
        Returns:
            Severity level string
        """
        severity_map = {
            CommandErrorType.UNKNOWN_COMMAND: 'low',
            CommandErrorType.PERMISSION_DENIED: 'medium',
            CommandErrorType.INVALID_ARGUMENTS: 'low',
            CommandErrorType.FEATURE_UNAVAILABLE: 'medium',
            CommandErrorType.EXECUTION_FAILED: 'high',
            CommandErrorType.VALIDATION_ERROR: 'medium',
            CommandErrorType.CONFIGURATION_ERROR: 'high',
            CommandErrorType.SYSTEM_ERROR: 'critical'
        }
        return severity_map.get(error.error_type, 'unknown')
    
    @staticmethod
    def classify_error_category(error: CommandError) -> str:
        """Classify error into broad categories.
        
        Args:
            error: CommandError to classify
            
        Returns:
            Category string
        """
        category_map = {
            CommandErrorType.UNKNOWN_COMMAND: 'user_input',
            CommandErrorType.PERMISSION_DENIED: 'authorization',
            CommandErrorType.INVALID_ARGUMENTS: 'user_input',
            CommandErrorType.FEATURE_UNAVAILABLE: 'configuration',
            CommandErrorType.EXECUTION_FAILED: 'runtime',
            CommandErrorType.VALIDATION_ERROR: 'user_input',
            CommandErrorType.CONFIGURATION_ERROR: 'configuration',
            CommandErrorType.SYSTEM_ERROR: 'system'
        }
        return category_map.get(error.error_type, 'unknown')
    
    @staticmethod
    def is_user_recoverable(error: CommandError) -> bool:
        """Determine if error can be recovered by user action.
        
        Args:
            error: CommandError to check
            
        Returns:
            True if user can potentially recover from this error
        """
        recoverable_types = {
            CommandErrorType.UNKNOWN_COMMAND,
            CommandErrorType.INVALID_ARGUMENTS,
            CommandErrorType.VALIDATION_ERROR
        }
        return error.error_type in recoverable_types
    
    @staticmethod
    def requires_admin_intervention(error: CommandError) -> bool:
        """Determine if error requires administrator intervention.
        
        Args:
            error: CommandError to check
            
        Returns:
            True if admin intervention is likely needed
        """
        admin_types = {
            CommandErrorType.CONFIGURATION_ERROR,
            CommandErrorType.SYSTEM_ERROR,
            CommandErrorType.FEATURE_UNAVAILABLE
        }
        return error.error_type in admin_types


class ErrorMessageFormatter:
    """Formats error messages for different output contexts"""
    
    @staticmethod
    def format_for_cli(error: CommandError) -> str:
        """Format error message for CLI display.
        
        Args:
            error: CommandError to format
            
        Returns:
            CLI-formatted error message
        """
        severity = CommandErrorClassifier.classify_error_severity(error)
        emoji_map = {
            'low': '⚠️',
            'medium': '❌',
            'high': '🚨',
            'critical': '💥',
            'unknown': '❓'
        }
        
        emoji = emoji_map.get(severity, '❓')
        return f"{emoji} {error.message}"
    
    @staticmethod
    def format_for_log(error: CommandError) -> str:
        """Format error message for log files.
        
        Args:
            error: CommandError to format
            
        Returns:
            Log-formatted error message
        """
        severity = CommandErrorClassifier.classify_error_severity(error)
        category = CommandErrorClassifier.classify_error_category(error)
        
        parts = [
            f"[{error.error_type.value.upper()}]",
            f"[{severity.upper()}]",
            f"[{category}]",
            error.message
        ]
        
        if error.command:
            parts.insert(-1, f"[CMD:{error.command}]")
            
        return " ".join(parts)
    
    @staticmethod
    def format_for_user_help(error: CommandError) -> Dict[str, str]:
        """Format error with helpful guidance for users.
        
        Args:
            error: CommandError to format
            
        Returns:
            Dictionary with formatted message and help text
        """
        help_map = {
            CommandErrorType.UNKNOWN_COMMAND: "Try typing '/help' to see available commands, or check spelling.",
            CommandErrorType.PERMISSION_DENIED: "Use '/commands' to check permissions or contact an administrator.",
            CommandErrorType.INVALID_ARGUMENTS: "Check the command help for correct argument format.",
            CommandErrorType.FEATURE_UNAVAILABLE: "This feature may need to be enabled or is not supported.",
            CommandErrorType.EXECUTION_FAILED: "Try the command again, or contact support if the problem persists.",
            CommandErrorType.VALIDATION_ERROR: "Review the command format and try again.",
            CommandErrorType.CONFIGURATION_ERROR: "Contact an administrator to check system configuration.",
            CommandErrorType.SYSTEM_ERROR: "Contact support - this indicates a system-level problem."
        }
        
        return {
            'message': ErrorMessageFormatter.format_for_cli(error),
            'help': help_map.get(error.error_type, "Contact support for assistance."),
            'recoverable': str(CommandErrorClassifier.is_user_recoverable(error))
        }