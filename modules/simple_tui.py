"""
OpenCLI TUI - Modular Architecture
Main entry point importing from focused components

Refactored from 2,719-line monolithic file into modular components:
- tui/core.py - Main TUI application class
- tui/status_lines.py - Status line components  
- tui/permission_handlers.py - Permission event handling
- tui/command_handlers.py - Command suggestion handling
- tui/model_handlers.py - Model selection workflows
"""

# Import the main TUI class from modular components
from .tui.core import OpenCLITUI

# Import other components for backward compatibility
from .tui.status_lines import PerformanceStatusLine, RefactoringStatusLine, StatusLine
from .tui.permission_handlers import PermissionHandlers
from .tui.command_handlers import CommandHandlers
from .tui.model_handlers import ModelHandlers

# Re-export for backward compatibility
__all__ = [
    'OpenCLITUI',
    'PerformanceStatusLine',
    'RefactoringStatusLine', 
    'StatusLine',
    'PermissionHandlers',
    'CommandHandlers',
    'ModelHandlers'
]