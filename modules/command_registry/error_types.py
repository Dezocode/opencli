"""
Command Error Types and Base Classes
Core error types, exceptions, and foundational error handling classes
"""

from enum import Enum
from typing import Dict, List, Any
from datetime import datetime


class CommandErrorType(Enum):
    """Types of command-related errors"""
    UNKNOWN_COMMAND = "unknown_command"
    PERMISSION_DENIED = "permission_denied"
    INVALID_ARGUMENTS = "invalid_arguments"
    FEATURE_UNAVAILABLE = "feature_unavailable"
    EXECUTION_FAILED = "execution_failed"
    VALIDATION_ERROR = "validation_error"
    CONFIGURATION_ERROR = "configuration_error"
    SYSTEM_ERROR = "system_error"


class CommandError(Exception):
    """Base exception for command-related errors"""
    
    def __init__(self, message: str, error_type: CommandErrorType, command: str = None, details: Dict = None):
        """Initialize command error.
        
        Args:
            message: Human-readable error message
            error_type: Type of error from CommandErrorType enum
            command: Command name that caused the error
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.command = command
        self.details = details or {}
        self.timestamp = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            'message': self.message,
            'error_type': self.error_type.value,
            'command': self.command,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


class ErrorStatistics:
    """Manages error statistics and patterns"""
    
    def __init__(self):
        """Initialize error statistics."""
        self.error_counts = {}
        self.recent_errors = []
        self.max_recent_errors = 100
    
    def record_error(self, error: CommandError) -> None:
        """Record an error for statistics.
        
        Args:
            error: CommandError to record
        """
        # Update statistics
        error_type_str = error.error_type.value
        self.error_counts[error_type_str] = self.error_counts.get(error_type_str, 0) + 1
        
        # Add to recent errors
        self.recent_errors.append(error)
        if len(self.recent_errors) > self.max_recent_errors:
            self.recent_errors.pop(0)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics and patterns.
        
        Returns:
            Dictionary with error statistics
        """
        total_errors = sum(self.error_counts.values())
        
        # Calculate error distribution
        error_distribution = {}
        for error_type, count in self.error_counts.items():
            percentage = (count / total_errors * 100) if total_errors > 0 else 0
            error_distribution[error_type] = {
                'count': count,
                'percentage': round(percentage, 2)
            }
            
        return {
            'total_errors': total_errors,
            'error_distribution': error_distribution,
            'recent_errors_count': len(self.recent_errors),
            'most_common_error': max(self.error_counts.items(), key=lambda x: x[1])[0] if self.error_counts else None
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors.
        
        Args:
            limit: Maximum number of recent errors to return
            
        Returns:
            List of recent error dictionaries
        """
        return [error.to_dict() for error in self.recent_errors[-limit:]]
    
    def clear_error_history(self) -> None:
        """Clear error history and statistics."""
        self.error_counts.clear()
        self.recent_errors.clear()


class ErrorPatternAnalyzer:
    """Analyzes error patterns for insights"""
    
    def __init__(self, statistics: ErrorStatistics):
        """Initialize pattern analyzer.
        
        Args:
            statistics: ErrorStatistics instance
        """
        self.statistics = statistics
    
    def analyze_error_patterns(self) -> Dict[str, Any]:
        """Analyze error patterns for insights.
        
        Returns:
            Dictionary with error pattern analysis
        """
        patterns = {
            'frequent_unknown_commands': [],
            'permission_hotspots': [],
            'validation_issues': []
        }
        
        # Analyze recent errors for patterns
        unknown_commands = {}
        permission_commands = {}
        
        for error in self.statistics.recent_errors:
            if error.error_type == CommandErrorType.UNKNOWN_COMMAND and error.command:
                unknown_commands[error.command] = unknown_commands.get(error.command, 0) + 1
            elif error.error_type == CommandErrorType.PERMISSION_DENIED and error.command:
                permission_commands[error.command] = permission_commands.get(error.command, 0) + 1
                
        # Get top patterns
        patterns['frequent_unknown_commands'] = sorted(
            unknown_commands.items(), key=lambda x: x[1], reverse=True
        )[:5]
        
        patterns['permission_hotspots'] = sorted(
            permission_commands.items(), key=lambda x: x[1], reverse=True
        )[:5]
        
        return patterns
    
    def generate_error_recommendations(self) -> List[str]:
        """Generate recommendations based on error patterns.
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        stats = self.statistics.get_error_statistics()
        
        total_errors = stats['total_errors']
        if total_errors == 0:
            return ["No errors recorded - system is running smoothly!"]
            
        distribution = stats['error_distribution']
        
        # Check for high unknown command rate
        unknown_rate = distribution.get('unknown_command', {}).get('percentage', 0)
        if unknown_rate > 30:
            recommendations.append(
                "High rate of unknown commands detected. Consider improving command discovery or autocomplete."
            )
            
        # Check for permission issues
        permission_rate = distribution.get('permission_denied', {}).get('percentage', 0)
        if permission_rate > 20:
            recommendations.append(
                "Frequent permission denials detected. Review command permissions setup."
            )
            
        # Check for validation errors
        validation_rate = distribution.get('validation_error', {}).get('percentage', 0)
        if validation_rate > 15:
            recommendations.append(
                "High validation error rate. Consider improving command argument validation messages."
            )
            
        # Check for system errors
        system_rate = distribution.get('system_error', {}).get('percentage', 0)
        if system_rate > 5:
            recommendations.append(
                "System errors detected. Review system configuration and dependencies."
            )
            
        if not recommendations:
            recommendations.append("Error patterns look normal. No specific recommendations.")
            
        return recommendations


class ErrorReportGenerator:
    """Generates comprehensive error reports"""
    
    def __init__(self, statistics: ErrorStatistics, analyzer: ErrorPatternAnalyzer):
        """Initialize report generator.
        
        Args:
            statistics: ErrorStatistics instance
            analyzer: ErrorPatternAnalyzer instance
        """
        self.statistics = statistics
        self.analyzer = analyzer
    
    def export_error_report(self) -> Dict[str, Any]:
        """Export comprehensive error report.
        
        Returns:
            Complete error report
        """
        return {
            'report_generated': datetime.now().isoformat(),
            'statistics': self.statistics.get_error_statistics(),
            'recent_errors': self.statistics.get_recent_errors(20),
            'error_patterns': self.analyzer.analyze_error_patterns(),
            'recommendations': self.analyzer.generate_error_recommendations()
        }


class CommandSimilarityMatcher:
    """Finds similar commands for error recovery"""
    
    @staticmethod
    def find_similar_commands(command: str, available_commands: Dict[str, Any]) -> List[str]:
        """Find commands similar to the unknown command.
        
        Args:
            command: Unknown command to find similarities for
            available_commands: Dictionary of available commands
            
        Returns:
            List of similar command names
        """
        if not command.startswith('/'):
            command = f'/{command}'
            
        similarities = []
        command_lower = command.lower()
        
        for cmd_name in available_commands.keys():
            # Exact substring match
            if command_lower[1:] in cmd_name.lower():  # Remove leading /
                similarities.append((cmd_name, 100))
            # Starts with match
            elif cmd_name.lower().startswith(command_lower):
                similarities.append((cmd_name, 90))
            # Contains match
            elif command_lower[1:] in cmd_name.lower():
                similarities.append((cmd_name, 70))
            # Levenshtein-like similarity
            else:
                similarity = CommandSimilarityMatcher._calculate_similarity(command_lower, cmd_name.lower())
                if similarity > 0.6:  # 60% similarity threshold
                    similarities.append((cmd_name, int(similarity * 100)))
                    
        # Sort by similarity score and return command names
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [cmd for cmd, score in similarities[:5]]  # Top 5 matches
    
    @staticmethod
    def _calculate_similarity(str1: str, str2: str) -> float:
        """Calculate similarity between two strings using simple algorithm.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        if not str1 or not str2:
            return 0.0
            
        # Simple character overlap calculation
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0