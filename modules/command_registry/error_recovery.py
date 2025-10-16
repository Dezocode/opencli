"""
Command Error Recovery System
Recovery strategies, fallback mechanisms, and user assistance for command errors
"""

from typing import Dict, List, Optional, Tuple, Any

from .error_types import CommandError, CommandErrorType, CommandSimilarityMatcher
from .error_handlers import CommandErrorClassifier, ErrorMessageFormatter


class CommandErrorRecovery:
    """Handles error recovery and fallback strategies"""
    
    def __init__(self, error_handler):
        """Initialize error recovery.
        
        Args:
            error_handler: CommandErrorHandler instance
        """
        self.error_handler = error_handler
        
    def attempt_command_recovery(self, command: str, available_commands: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Attempt to recover from command error by suggesting alternatives.
        
        Args:
            command: Failed command
            available_commands: Available commands dictionary
            
        Returns:
            Tuple of (success, suggested_command)
        """
        # Try to find exact match with different casing
        normalized_command = command.lower()
        for cmd_name in available_commands.keys():
            if cmd_name.lower() == normalized_command:
                return True, cmd_name
                
        # Try to find close matches
        similar_commands = CommandSimilarityMatcher.find_similar_commands(command, available_commands)
        if similar_commands:
            return True, similar_commands[0]  # Return best match
            
        return False, None
        
    def create_error_context(self, error: CommandError, user_context: Dict = None) -> Dict[str, Any]:
        """Create rich error context for user display.
        
        Args:
            error: CommandError to create context for
            user_context: Additional user context
            
        Returns:
            Rich error context dictionary
        """
        context = {
            'error': error.to_dict(),
            'user_friendly_message': self._get_user_friendly_message(error),
            'suggested_actions': self._get_suggested_actions(error),
            'help_resources': self._get_help_resources(error)
        }
        
        if user_context:
            context['user_context'] = user_context
            
        return context
        
    def _get_user_friendly_message(self, error: CommandError) -> str:
        """Get user-friendly error message.
        
        Args:
            error: CommandError to generate message for
            
        Returns:
            User-friendly error message
        """
        error_messages = {
            CommandErrorType.UNKNOWN_COMMAND: "That command doesn't exist.",
            CommandErrorType.PERMISSION_DENIED: "You don't have permission to use that command.",
            CommandErrorType.INVALID_ARGUMENTS: "The command arguments are incorrect.",
            CommandErrorType.FEATURE_UNAVAILABLE: "That feature isn't available right now.",
            CommandErrorType.EXECUTION_FAILED: "The command couldn't be completed.",
            CommandErrorType.VALIDATION_ERROR: "There's an issue with the command format.",
            CommandErrorType.CONFIGURATION_ERROR: "There's a configuration problem.",
            CommandErrorType.SYSTEM_ERROR: "A system error occurred."
        }
        
        return error_messages.get(error.error_type, "An error occurred.")
        
    def _get_suggested_actions(self, error: CommandError) -> List[str]:
        """Get suggested actions for error recovery.
        
        Args:
            error: CommandError to generate suggestions for
            
        Returns:
            List of suggested action strings
        """
        actions = {
            CommandErrorType.UNKNOWN_COMMAND: [
                "Type '/help' to see all available commands",
                "Check spelling and try again",
                "Use tab completion for command suggestions"
            ],
            CommandErrorType.PERMISSION_DENIED: [
                "Use '/commands' to check command permissions",
                "Contact administrator if you need access",
                "Try an alternative command"
            ],
            CommandErrorType.INVALID_ARGUMENTS: [
                "Check the command help for correct usage",
                "Verify argument format and try again",
                "Use '/help [command]' for specific guidance"
            ],
            CommandErrorType.FEATURE_UNAVAILABLE: [
                "Check if the feature can be enabled",
                "Try an alternative approach",
                "Contact support for feature availability"
            ]
        }
        
        return actions.get(error.error_type, ["Try again later", "Contact support if the problem persists"])
        
    def _get_help_resources(self, error: CommandError) -> List[str]:
        """Get help resources for error type.
        
        Args:
            error: CommandError to get resources for
            
        Returns:
            List of help resource strings
        """
        return [
            "/help - Show all available commands",
            "/commands - Manage command permissions", 
            "/status - Check system status"
        ]


class ErrorRecoveryStrategies:
    """Implements various error recovery strategies"""
    
    @staticmethod
    def fuzzy_command_matching(command: str, available_commands: Dict[str, Any], threshold: float = 0.6) -> List[str]:
        """Find commands using fuzzy matching.
        
        Args:
            command: Input command to match
            available_commands: Available commands dictionary
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            List of matching command names
        """
        matches = []
        command_lower = command.lower().strip('/')
        
        for cmd_name in available_commands.keys():
            cmd_clean = cmd_name.lower().strip('/')
            
            # Various matching strategies
            strategies = [
                # Exact match
                lambda: 1.0 if cmd_clean == command_lower else 0.0,
                # Prefix match
                lambda: 0.9 if cmd_clean.startswith(command_lower) else 0.0,
                # Suffix match
                lambda: 0.8 if cmd_clean.endswith(command_lower) else 0.0,
                # Contains match
                lambda: 0.7 if command_lower in cmd_clean else 0.0,
                # Character overlap
                lambda: ErrorRecoveryStrategies._character_overlap_score(command_lower, cmd_clean)
            ]
            
            max_score = max(strategy() for strategy in strategies)
            if max_score >= threshold:
                matches.append((cmd_name, max_score))
        
        # Sort by score and return command names
        matches.sort(key=lambda x: x[1], reverse=True)
        return [cmd for cmd, score in matches[:5]]
    
    @staticmethod
    def _character_overlap_score(str1: str, str2: str) -> float:
        """Calculate character overlap score between two strings."""
        if not str1 or not str2:
            return 0.0
        
        set1 = set(str1)
        set2 = set(str2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def command_abbreviation_expansion(abbrev: str, available_commands: Dict[str, Any]) -> List[str]:
        """Expand command abbreviations to full command names.
        
        Args:
            abbrev: Abbreviated command
            available_commands: Available commands dictionary
            
        Returns:
            List of possible full command names
        """
        abbrev_lower = abbrev.lower().strip('/')
        matches = []
        
        for cmd_name in available_commands.keys():
            cmd_clean = cmd_name.lower().strip('/')
            
            # Check if abbreviation matches command initials
            cmd_initials = ''.join(word[0] for word in cmd_clean.split('_') if word)
            if cmd_initials.startswith(abbrev_lower):
                matches.append((cmd_name, 100))
            # Check if abbreviation is prefix of any word in command
            elif any(word.startswith(abbrev_lower) for word in cmd_clean.split('_')):
                matches.append((cmd_name, 80))
            # Check if abbreviation matches start of command
            elif cmd_clean.startswith(abbrev_lower):
                matches.append((cmd_name, 90))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        return [cmd for cmd, score in matches[:3]]
    
    @staticmethod
    def context_aware_suggestions(error: CommandError, user_history: List[str] = None) -> List[str]:
        """Provide context-aware command suggestions.
        
        Args:
            error: CommandError that occurred
            user_history: Recent user command history
            
        Returns:
            List of contextually relevant suggestions
        """
        suggestions = []
        
        if error.error_type == CommandErrorType.UNKNOWN_COMMAND:
            # If user recently used similar commands, suggest those
            if user_history:
                recent_commands = user_history[-5:]  # Last 5 commands
                for cmd in recent_commands:
                    if cmd and cmd != error.command:
                        suggestions.append(f"Recently used: {cmd}")
            
            # Suggest common alternatives based on command pattern
            if error.command:
                cmd_lower = error.command.lower()
                if 'help' in cmd_lower:
                    suggestions.extend(["/help", "/commands", "/status"])
                elif 'list' in cmd_lower or 'ls' in cmd_lower:
                    suggestions.extend(["/list", "/show", "/status"])
                elif 'config' in cmd_lower or 'setting' in cmd_lower:
                    suggestions.extend(["/config", "/settings", "/commands"])
        
        elif error.error_type == CommandErrorType.PERMISSION_DENIED:
            suggestions.extend([
                "Use '/commands' to review permissions",
                "Try '/help' to see available commands",
                "Contact administrator for access"
            ])
        
        elif error.error_type == CommandErrorType.INVALID_ARGUMENTS:
            suggestions.extend([
                f"Try '/help {error.command}' for usage information",
                "Check argument format and syntax",
                "Use '/examples' for command examples"
            ])
        
        return suggestions[:5]  # Limit to top 5 suggestions


class ErrorRecoveryUI:
    """Handles user interface aspects of error recovery"""
    
    @staticmethod
    def format_recovery_suggestions(error: CommandError, suggestions: List[str]) -> str:
        """Format recovery suggestions for display.
        
        Args:
            error: CommandError that occurred
            suggestions: List of recovery suggestions
            
        Returns:
            Formatted suggestions string
        """
        if not suggestions:
            return "No specific suggestions available."
        
        severity = CommandErrorClassifier.classify_error_severity(error)
        
        if severity in ['low', 'medium']:
            header = "💡 Here are some suggestions:"
        else:
            header = "🆘 Recovery options:"
        
        formatted_suggestions = [f"  • {suggestion}" for suggestion in suggestions]
        return f"{header}\n" + "\n".join(formatted_suggestions)
    
    @staticmethod
    def create_error_dialog(error: CommandError, recovery_options: Dict[str, Any]) -> Dict[str, Any]:
        """Create an interactive error dialog structure.
        
        Args:
            error: CommandError that occurred
            recovery_options: Available recovery options
            
        Returns:
            Dialog structure dictionary
        """
        severity = CommandErrorClassifier.classify_error_severity(error)
        is_recoverable = CommandErrorClassifier.is_user_recoverable(error)
        
        dialog = {
            'title': f"Command Error ({severity.title()})",
            'message': ErrorMessageFormatter.format_for_cli(error),
            'details': error.details,
            'severity': severity,
            'recoverable': is_recoverable,
            'timestamp': error.timestamp.isoformat(),
            'actions': []
        }
        
        if is_recoverable:
            if recovery_options.get('suggested_command'):
                dialog['actions'].append({
                    'type': 'retry',
                    'label': f"Try '{recovery_options['suggested_command']}'",
                    'command': recovery_options['suggested_command']
                })
            
            dialog['actions'].extend([
                {'type': 'help', 'label': 'Show Help', 'command': '/help'},
                {'type': 'cancel', 'label': 'Cancel', 'command': None}
            ])
        else:
            dialog['actions'].extend([
                {'type': 'report', 'label': 'Report Issue', 'command': '/report'},
                {'type': 'help', 'label': 'Get Help', 'command': '/help'},
                {'type': 'dismiss', 'label': 'Dismiss', 'command': None}
            ])
        
        return dialog
    
    @staticmethod
    def format_error_summary(errors: List[CommandError], limit: int = 5) -> str:
        """Format a summary of recent errors.
        
        Args:
            errors: List of CommandError objects
            limit: Maximum number of errors to include
            
        Returns:
            Formatted error summary
        """
        if not errors:
            return "✅ No recent errors"
        
        recent_errors = errors[-limit:]
        summary_lines = ["📊 Recent Error Summary:"]
        
        for i, error in enumerate(recent_errors, 1):
            severity = CommandErrorClassifier.classify_error_severity(error)
            emoji_map = {'low': '⚠️', 'medium': '❌', 'high': '🚨', 'critical': '💥'}
            emoji = emoji_map.get(severity, '❓')
            
            timestamp = error.timestamp.strftime("%H:%M:%S")
            summary_lines.append(f"{i}. {emoji} [{timestamp}] {error.error_type.value}: {error.command or 'N/A'}")
        
        return "\n".join(summary_lines)


class ErrorRecoveryMetrics:
    """Tracks metrics related to error recovery effectiveness"""
    
    def __init__(self):
        """Initialize recovery metrics."""
        self.recovery_attempts = 0
        self.successful_recoveries = 0
        self.recovery_strategies_used = {}
        self.user_acceptance_rate = {}
    
    def record_recovery_attempt(self, strategy: str, success: bool, user_accepted: bool = None):
        """Record a recovery attempt.
        
        Args:
            strategy: Recovery strategy used
            success: Whether recovery was successful
            user_accepted: Whether user accepted the suggestion
        """
        self.recovery_attempts += 1
        
        if success:
            self.successful_recoveries += 1
        
        self.recovery_strategies_used[strategy] = self.recovery_strategies_used.get(strategy, 0) + 1
        
        if user_accepted is not None:
            if strategy not in self.user_acceptance_rate:
                self.user_acceptance_rate[strategy] = {'accepted': 0, 'total': 0}
            
            self.user_acceptance_rate[strategy]['total'] += 1
            if user_accepted:
                self.user_acceptance_rate[strategy]['accepted'] += 1
    
    def get_recovery_effectiveness(self) -> Dict[str, Any]:
        """Get recovery effectiveness metrics.
        
        Returns:
            Dictionary with effectiveness metrics
        """
        success_rate = (self.successful_recoveries / self.recovery_attempts * 100) if self.recovery_attempts > 0 else 0
        
        strategy_effectiveness = {}
        for strategy, count in self.recovery_strategies_used.items():
            if strategy in self.user_acceptance_rate:
                acceptance_data = self.user_acceptance_rate[strategy]
                acceptance_rate = (acceptance_data['accepted'] / acceptance_data['total'] * 100) if acceptance_data['total'] > 0 else 0
                strategy_effectiveness[strategy] = {
                    'usage_count': count,
                    'acceptance_rate': round(acceptance_rate, 2)
                }
        
        return {
            'overall_success_rate': round(success_rate, 2),
            'total_attempts': self.recovery_attempts,
            'successful_recoveries': self.successful_recoveries,
            'strategy_effectiveness': strategy_effectiveness
        }