"""
Message classes for MultiLineInput widget
All Textual messages for event communication
"""

from textual.message import Message


class Submitted(Message):
    """Posted when user submits the input"""
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__()


class PermissionResponse(Message):
    """Posted when user selects a permission option"""
    def __init__(self, option: dict) -> None:
        self.option = option
        super().__init__()


class PermissionCancelled(Message):
    """Posted when user cancels permission prompt"""
    pass


class ShowCommandSuggestions(Message):
    """Posted when slash command typed - triggers suggestion buffer"""
    def __init__(self, query: str) -> None:
        self.query = query
        super().__init__()


class HideCommandSuggestions(Message):
    """Posted when suggestions should be hidden"""
    pass


class CommandSuggestionNavigate(Message):
    """Posted when user navigates in suggestions with arrow keys"""
    def __init__(self, direction: str) -> None:
        self.direction = direction  # "up" or "down"
        super().__init__()


class CommandSuggestionSelect(Message):
    """Posted when user presses Enter with suggestions active"""
    pass


class NavigationEvent(Message):
    """Posted when user navigates away (focus lost) - triggers auto-dismiss"""
    def __init__(self, event_type: str) -> None:
        self.event_type = event_type  # "focus_lost", "window_change", etc.
        super().__init__()

class DebugMessage(Message):
    """Posted for debug output"""
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__()
