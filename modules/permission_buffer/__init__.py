"""
Permission Buffer System - Modular Architecture

Manages permission prompts with priority-based queuing and UI integration.
This replaces the monolithic permission_buffer_manager.py with focused modules.
"""

from .manager import PermissionBufferManager, get_permission_buffer_manager
from .enums import PromptPriority, PromptState
from .task import _PromptTask

# Backward compatibility exports
__all__ = [
    'PermissionBufferManager',
    'get_permission_buffer_manager', 
    'PromptPriority',
    'PromptState',
    '_PromptTask'
]

# Version and metadata
__version__ = '2.0.0'
__description__ = 'Modular permission buffer system for OpenCLI'