"""
Modular OpenCLI TUI package
Refactored from monolithic simple_tui.py into focused components
"""

from .core import OpenCLITUI
from .status_lines import PerformanceStatusLine, RefactoringStatusLine, StatusLine
from .permission_handlers import PermissionHandlers
from .command_handlers import CommandHandlers
from .model_handlers import ModelHandlers

__all__ = [
    'OpenCLITUI',
    'PerformanceStatusLine', 
    'RefactoringStatusLine',
    'StatusLine',
    'PermissionHandlers',
    'CommandHandlers', 
    'ModelHandlers'
]