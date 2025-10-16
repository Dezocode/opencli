"""
Permission system for OpenCLI
Modular permission management with caching, analytics, and i18n support
"""

# Export main components
from .manager import PermissionBufferManager, get_permission_buffer_manager
from .enums import PromptPriority, PromptState, SDKState, PermissionResponse
from .task import _PromptTask, TaskQueue
from .i18n import I18nManager
from .validation import ValidationManager
from .analytics import AnalyticsManager
from .audit import AuditManager
from .cache import CacheManager
from .widget import PermissionPrompt
from .templates import PermissionTemplates
from .integration import (
    UnifiedPermissionManager, 
    get_unified_permission_manager,
    show_file_permission_prompt,
    show_bash_permission_prompt,
    show_api_permission_prompt,
    show_tool_permission_prompt
)

# Export for backward compatibility
from .manager import PermissionBufferManager as PermissionBufferManager

__all__ = [
    'PermissionBufferManager',
    'get_permission_buffer_manager',
    'PromptPriority',
    'PromptState', 
    'SDKState',
    'PermissionResponse',
    '_PromptTask',
    'TaskQueue',
    'I18nManager',
    'ValidationManager',
    'AnalyticsManager',
    'AuditManager',
    'CacheManager',
    'PermissionPrompt',
    'PermissionTemplates',
    'UnifiedPermissionManager',
    'get_unified_permission_manager',
    'show_file_permission_prompt',
    'show_bash_permission_prompt',
    'show_api_permission_prompt',
    'show_tool_permission_prompt'
]