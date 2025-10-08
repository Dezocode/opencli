"""Command suggestion buffer with intelligent search and keyboard navigation.

This module provides an interactive command autocomplete system that:
- Intercepts slash commands before they reach the chat API
- Searches commands with priority-based ranking
- Displays suggestions in a buffer below multiline input
- Supports arrow key navigation and Enter selection
- Tracks command usage frequency for smart sorting
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from textual.widgets import Static
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.console import RenderableType


@dataclass
class CommandMatch:
    """Represents a command match with search metadata."""

    name: str
    description: str
    category: str
    score: int
    usage_count: int

    def __repr__(self) -> str:
        return f"CommandMatch(name='{self.name}', score={self.score}, usage={self.usage_count})"


class CommandSuggestionBuffer(Static):
    """Interactive command suggestion buffer with keyboard navigation.

    This widget displays filtered command suggestions based on user input,
    allowing navigation with arrow keys and selection with Enter.

    Attributes:
        suggestions: List of CommandMatch objects sorted by relevance
        selected_index: Currently selected suggestion index
        query: Current search query
        max_visible: Maximum number of visible suggestions (default: 10)
    """

    # Reactive properties for automatic UI updates
    suggestions: reactive[List[CommandMatch]] = reactive(list, init=False)
    selected_index: reactive[int] = reactive(0)
    query: reactive[str] = reactive("")
    max_visible: reactive[int] = reactive(10)

    # Message types for communication with parent widgets
    class ShowSuggestions(Message):
        """Posted when suggestions should be displayed."""
        def __init__(self, query: str) -> None:
            self.query = query
            super().__init__()

    class UpdateSuggestions(Message):
        """Posted when query changes and suggestions need updating."""
        def __init__(self, query: str) -> None:
            self.query = query
            super().__init__()

    class CommandSelected(Message):
        """Posted when user selects a command with Enter."""
        def __init__(self, command: str, command_match: CommandMatch) -> None:
            self.command = command
            self.command_match = command_match
            super().__init__()

    class CloseSuggestions(Message):
        """Posted when suggestions should be hidden."""
        pass

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ) -> None:
        """Initialize the command suggestion buffer.

        Args:
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.suggestions = []
        self.selected_index = 0
        self.query = ""
        self.max_visible = 10

    def render(self) -> RenderableType:
        """Render the suggestion buffer with Frontier colors.

        Returns:
            Rich Text object with formatted suggestions
        """
        if not self.suggestions:
            # No matches case
            if self.query and self.query != "/":
                text = Text()
                text.append("No matching commands\n", style="dim")
                text.append("Press Esc to cancel", style="dim italic")
                return text
            else:
                # Empty state - just show command count
                text = Text()
                text.append("Type a command name to filter...", style="dim italic")
                return text

        # Build suggestion list
        text = Text()

        # Header showing result count
        total_count = len(self.suggestions)
        showing_count = min(total_count, self.max_visible)

        if total_count > showing_count:
            text.append(
                f"Commands ({total_count} total, showing {showing_count})\n",
                style="bold #89B8C2"  # Frontier accent
            )
        else:
            text.append(
                f"Commands ({total_count})\n",
                style="bold #89B8C2"
            )

        # Render visible suggestions
        visible_start = max(0, self.selected_index - self.max_visible // 2)
        visible_end = min(total_count, visible_start + self.max_visible)

        # Adjust start if we're near the end
        if visible_end - visible_start < self.max_visible:
            visible_start = max(0, visible_end - self.max_visible)

        for i in range(visible_start, visible_end):
            suggestion = self.suggestions[i]
            is_selected = (i == self.selected_index)

            # Selection indicator
            if is_selected:
                text.append("❯ ", style="bold #89B8C2")  # Frontier accent
            else:
                text.append("  ", style="")

            # Command name
            name_style = "bold #89B8C2" if is_selected else "#89B8C2"
            text.append(suggestion.name, style=name_style)

            # Description
            text.append(" - ", style="dim")
            desc_style = "white" if is_selected else "dim"
            text.append(suggestion.description, style=desc_style)

            # Usage count (if > 0)
            if suggestion.usage_count > 0:
                text.append(f" ({suggestion.usage_count} uses)", style="dim italic")

            text.append("\n")

        # Show scroll indicator if needed
        if visible_end < total_count:
            remaining = total_count - visible_end
            text.append(f"  ↓ {remaining} more...\n", style="dim italic")

        if visible_start > 0:
            text.append(f"  ↑ {visible_start} above...\n", style="dim italic")

        return text

    def move_selection_up(self) -> None:
        """Move selection up one item (with wrapping)."""
        if self.suggestions:
            self.selected_index = (self.selected_index - 1) % len(self.suggestions)

    def move_selection_down(self) -> None:
        """Move selection down one item (with wrapping)."""
        if self.suggestions:
            self.selected_index = (self.selected_index + 1) % len(self.suggestions)

    def get_selected_command(self) -> Optional[CommandMatch]:
        """Get the currently selected command match.

        Returns:
            CommandMatch object if selection is valid, None otherwise
        """
        if 0 <= self.selected_index < len(self.suggestions):
            return self.suggestions[self.selected_index]
        return None

    def update_suggestions(self, new_suggestions: List[CommandMatch], query: str) -> None:
        """Update the suggestion list and reset selection.

        Args:
            new_suggestions: New list of CommandMatch objects
            query: Search query that produced these suggestions
        """
        self.suggestions = new_suggestions
        self.query = query
        self.selected_index = 0  # Reset to top
        self.refresh()  # Trigger re-render

    def clear(self) -> None:
        """Clear all suggestions and reset state."""
        self.suggestions = []
        self.selected_index = 0
        self.query = ""
        self.refresh()
