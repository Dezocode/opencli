"""
Permission Prompt - Compatibility Stub
Re-exports from modular permissions system for backward compatibility
"""

# Re-export components from modular system
try:
    from .permissions import (
        PermissionResponse, 
        PermissionTemplates, 
        PermissionPrompt,
        get_unified_permission_manager
    )
except ImportError:
    try:
        from permissions import (
            PermissionResponse, 
            PermissionTemplates, 
            PermissionPrompt,
            get_unified_permission_manager
        )
    except ImportError:
        # Fallback for import issues
        from enum import Enum
        
        class PermissionResponse(Enum):
            ALLOW_ONCE = "allow_once"
            ALLOW_SESSION = "allow_session" 
            ALLOW_ALWAYS = "allow_always"
            ALLOW_DOMAIN = "allow_domain"
            DENY = "deny"
            CANCEL = "cancel"
        
        class PermissionTemplates:
            pass
            
        class PermissionPrompt:
            pass
            
        def get_unified_permission_manager():
            return None

# Legacy compatibility
__all__ = [
    'PermissionResponse',
    'PermissionTemplates',
    'PermissionPrompt',
    'get_unified_permission_manager'
]

# Deprecation warning for new development
import warnings
warnings.warn(
    "permission_prompt module is deprecated. Use modular permissions.* components instead.",
    DeprecationWarning,
    stacklevel=2
)