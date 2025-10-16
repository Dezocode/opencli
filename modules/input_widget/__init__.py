"""
MultiLineInput Widget - Modular Permission-First Input System

Clean architecture with permission priority:
1. Permission prompts take full control when active
2. Command suggestions second priority
3. Normal input only when nothing else active

All components under 500 lines for maintainability.
"""

from .widget import MultiLineInput
from .messages import (
    Submitted,
    PermissionResponse,
    PermissionCancelled,
    ShowCommandSuggestions,
    HideCommandSuggestions,
    CommandSuggestionNavigate,
    CommandSuggestionSelect,
    NavigationEvent
)

__all__ = [
    'MultiLineInput',
    'Submitted',
    'PermissionResponse',
    'PermissionCancelled',
    'ShowCommandSuggestions',
    'HideCommandSuggestions',
    'CommandSuggestionNavigate',
    'CommandSuggestionSelect',
    'NavigationEvent'
]
