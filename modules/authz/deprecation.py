"""
Deprecation Warnings for Legacy Permission Systems

This module provides deprecation utilities to mark old permission imports
and guide developers to use the canonical authz facade instead.
"""

import warnings
import functools
import sys


def deprecated_permission_import(old_module: str, new_import: str):
    """
    Decorator to mark permission functions as deprecated
    
    Args:
        old_module: Name of the deprecated module
        new_import: Suggested new import path
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{old_module}.{func.__name__} is deprecated. "
                f"Use {new_import} instead. "
                f"See modules/authz/README.md for migration guide.",
                DeprecationWarning,
                stacklevel=2
            )
            # Also log to stderr for visibility
            sys.stderr.write(
                f"\n⚠️  DEPRECATION WARNING: {old_module}.{func.__name__}\n"
                f"   → Use {new_import} instead\n"
                f"   → See modules/authz/README.md for migration\n\n"
            )
            sys.stderr.flush()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def deprecated_module(module_name: str, replacement: str):
    """
    Mark an entire module as deprecated
    
    Usage:
        # At the top of deprecated module
        from modules.authz.deprecation import deprecated_module
        deprecated_module(__name__, "modules.authz")
    """
    warnings.warn(
        f"Module {module_name} is deprecated. "
        f"Use {replacement} instead. "
        f"This module will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2
    )
    
    sys.stderr.write(
        f"\n{'='*70}\n"
        f"⚠️  DEPRECATED MODULE: {module_name}\n"
        f"{'='*70}\n"
        f"This module is deprecated and will be removed in a future version.\n"
        f"Please migrate to: {replacement}\n"
        f"See: modules/authz/README.md for migration guide\n"
        f"{'='*70}\n\n"
    )
    sys.stderr.flush()


class DeprecatedPermissionManagerWarning(DeprecationWarning):
    """Custom warning for deprecated permission managers"""
    pass


# Enable deprecation warnings by default for this project
warnings.filterwarnings('default', category=DeprecatedPermissionManagerWarning)
