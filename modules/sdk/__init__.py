"""OpenCLI SDK - Handler Interface, Enforcement, and Diagnostics"""

from .handler_interface import (
    SDKCompliantHandler,
    HandlerCompliance,
    HandlerRegistration,
    validate_handler
)

from .enforcement import (
    SDKEnforcement,
    EnforcementAction,
    EnforcementResult,
    get_enforcement,
    enforce_handler
)

from .startup_buffer import (
    StartupBuffer,
    show_startup_status
)

from .validation import (
    collect_expected_commands,
    collect_expected_tools,
    validate_full_coverage
)

__all__ = [
    # Handler interface
    'SDKCompliantHandler',
    'HandlerCompliance',
    'HandlerRegistration',
    'validate_handler',

    # Enforcement
    'SDKEnforcement',
    'EnforcementAction',
    'EnforcementResult',
    'get_enforcement',
    'enforce_handler',

    # Startup display
    'StartupBuffer',
    'show_startup_status',

    # Validation
    'collect_expected_commands',
    'collect_expected_tools',
    'validate_full_coverage'
]
