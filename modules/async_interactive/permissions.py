"""
Permission management for async interactive mode
"""

from pathlib import Path


async def setup_permissions(session):
    """
    Setup permission manager for the session
    
    Args:
        session: Session object to configure
    """
    TOOL_PERMISSIONS = False
    
    try:
        from tool_permissions import ToolPermissionManager
        from async_permissions import AsyncPermissionHandler, set_global_handler
        TOOL_PERMISSIONS = True
    except (ImportError, ValueError):
        try:
            from tool_permissions import ToolPermissionManager
            from async_permissions import AsyncPermissionHandler, set_global_handler
            TOOL_PERMISSIONS = True
        except ImportError:
            pass

    if TOOL_PERMISSIONS and (not hasattr(session, 'permission_manager') or session.permission_manager is None):
        config_dir = Path.home() / '.opencli'
        session.permission_manager = ToolPermissionManager(config_dir)