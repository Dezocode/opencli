"""
Permission Buffer Manager - Compatibility Stub
Re-exports from unified permissions system for backward compatibility
"""

# Re-export all components from unified permission system
try:
    from .permissions import (
        PermissionBufferManager,
        get_permission_buffer_manager,
        PromptPriority,
        PromptState,
        _PromptTask,
        get_unified_permission_manager
    )
    
    # Provide compatibility wrapper for get_permission_buffer_manager
    def get_permission_buffer_manager():
        """Get permission buffer manager (legacy compatibility)"""
        unified_manager = get_unified_permission_manager()
        return unified_manager.get_buffer_manager()
        
except ImportError:
    try:
        from permission_buffer import (
            PermissionBufferManager,
            get_permission_buffer_manager,
            PromptPriority,
            PromptState,
            _PromptTask
        )
    except ImportError:
        # Ultimate fallback
        class PermissionBufferManager:
            def clear(self): return True
            def resolve(self, option): return True
            def get_active_task_count(self): return 0
            
        def get_permission_buffer_manager():
            return PermissionBufferManager()
            
        class PromptPriority:
            LOW = 3
            NORMAL = 2
            HIGH = 1
            URGENT = 0
            
        class PromptState:
            QUEUED = "queued"
            DISPLAYING = "displaying"
            
        class _PromptTask:
            pass

# Legacy compatibility
__all__ = [
    'PermissionBufferManager',
    'get_permission_buffer_manager',
    'PromptPriority', 
    'PromptState',
    '_PromptTask'
]

# Deprecation warning for new development
import warnings
warnings.warn(
    "permission_buffer_manager module is deprecated. Use modular permissions.* components instead.",
    DeprecationWarning,
    stacklevel=2
)