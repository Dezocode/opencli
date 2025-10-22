"""
MultiLineInput Widget - Modular Permission-First Input System

Clean architecture with permission priority:
1. Permission prompts take full control when active
2. Command suggestions second priority
3. Normal input only when nothing else active

All components under 500 lines for maintainability.
"""

from .widget import MultiLineInput

# Export nested message classes at module level for easier importing
# This allows: from input_widget import Submitted, PermissionResponse, etc.
Submitted = MultiLineInput.Submitted
PermissionResponse = MultiLineInput.PermissionResponse
PermissionCancelled = MultiLineInput.PermissionCancelled
ShowCommandSuggestions = MultiLineInput.ShowCommandSuggestions
HideCommandSuggestions = MultiLineInput.HideCommandSuggestions
CommandSuggestionNavigate = MultiLineInput.CommandSuggestionNavigate
CommandSuggestionSelect = MultiLineInput.CommandSuggestionSelect
NavigationEvent = MultiLineInput.NavigationEvent

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
