"""
Command Registry Error Handling
Unified interface for comprehensive error handling, logging, and recovery
"""

# Import all components from split modules
from .error_types import (
    CommandError,
    CommandErrorType,
    ErrorStatistics,
    ErrorPatternAnalyzer,
    ErrorReportGenerator,
    CommandSimilarityMatcher
)

from .error_handlers import (
    CommandErrorHandler,
    CommandErrorClassifier,
    ErrorMessageFormatter
)

from .error_recovery import (
    CommandErrorRecovery,
    ErrorRecoveryStrategies,
    ErrorRecoveryUI,
    ErrorRecoveryMetrics
)

# Re-export everything for backward compatibility
__all__ = [
    # Error types and base classes
    'CommandError',
    'CommandErrorType',
    'ErrorStatistics',
    'ErrorPatternAnalyzer',
    'ErrorReportGenerator',
    'CommandSimilarityMatcher',
    
    # Error handlers
    'CommandErrorHandler',
    'CommandErrorClassifier',
    'ErrorMessageFormatter',
    
    # Error recovery
    'CommandErrorRecovery',
    'ErrorRecoveryStrategies',
    'ErrorRecoveryUI',
    'ErrorRecoveryMetrics'
]