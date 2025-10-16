"""
Command Registry Package
Modular command registration and management system
"""

from .definitions import (
    STATIC_COMMAND_DEFINITIONS,
    COMMAND_CATEGORIES,
    get_static_commands,
    get_command_categories,
    get_commands_by_category,
    get_core_commands,
    get_commands_with_subcommands,
    get_feature_dependent_commands,
    validate_command_definition,
    merge_runtime_commands
)

from .validation import (
    CommandValidator,
    InteractivePermissionManager
)

from .core import CommandRegistrationCore

from .lifecycle import (
    CommandLifecycleManager,
    CommandAnalytics
)

from .error_handling import (
    CommandError,
    CommandErrorType,
    CommandErrorHandler,
    CommandErrorRecovery,
    CommandErrorClassifier,
    ErrorMessageFormatter,
    ErrorRecoveryStrategies,
    ErrorRecoveryUI,
    ErrorRecoveryMetrics
)

__all__ = [
    'STATIC_COMMAND_DEFINITIONS',
    'COMMAND_CATEGORIES', 
    'get_static_commands',
    'get_command_categories',
    'get_commands_by_category',
    'get_core_commands',
    'get_commands_with_subcommands',
    'get_feature_dependent_commands',
    'validate_command_definition',
    'merge_runtime_commands',
    'CommandValidator',
    'InteractivePermissionManager',
    'CommandRegistrationCore',
    'CommandLifecycleManager',
    'CommandAnalytics',
    'CommandError',
    'CommandErrorType',
    'CommandErrorHandler',
    'CommandErrorRecovery',
    'CommandErrorClassifier',
    'ErrorMessageFormatter',
    'ErrorRecoveryStrategies',
    'ErrorRecoveryUI',
    'ErrorRecoveryMetrics'
]