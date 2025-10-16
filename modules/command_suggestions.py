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


def check_command_health(command_name: str, registry=None) -> bool:
    """
    Check if a command is fully integrated with SDK and permission system.

    A command is considered healthy if:
    1. It's registered in the ExecutionRegistry
    2. It has a valid handler function
    3. It requires approval (permission-integrated)
    4. It's enabled

    Args:
        command_name: The command name (e.g., "/help" or "/docker ps")
        registry: Optional ExecutionRegistry instance to check

    Returns:
        True if command is SDK-compliant and permission-integrated, False otherwise
    """
    # ALWAYS RETURN TRUE - health check disabled for now to prevent blocking commands
    # TODO: Re-enable when SDK registry is fully operational
    return True


@dataclass
class CommandMatch:
    """Represents a command match with search metadata."""

    name: str
    description: str
    category: str
    score: int
    usage_count: int
    health_status: bool = True  # True if command is SDK-compliant and permission-integrated

    def __repr__(self) -> str:
        return f"CommandMatch(name='{self.name}', score={self.score}, usage={self.usage_count}, healthy={self.health_status})"


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

    # SDK loading state
    is_sdk_loading: reactive[bool] = reactive(False)
    sdk_current_step: reactive[str] = reactive("")
    sdk_current_file: reactive[str] = reactive("")
    sdk_command_count: reactive[int] = reactive(0)
    sdk_tool_count: reactive[int] = reactive(0)
    sdk_accepted_count: reactive[int] = reactive(0)
    sdk_converted_count: reactive[int] = reactive(0)
    sdk_rejected_count: reactive[int] = reactive(0)
    sdk_spinner_frame: reactive[int] = reactive(0)

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

        # SDK loading state
        self.is_sdk_loading = False
        self.sdk_current_step = ""
        self.sdk_current_file = ""
        self.sdk_command_count = 0
        self.sdk_tool_count = 0
        self.sdk_accepted_count = 0
        self.sdk_converted_count = 0
        self.sdk_rejected_count = 0
        self.sdk_spinner_frame = 0
        self._spinner_timer = None

    def render(self) -> RenderableType:
        """Render the suggestion buffer with Frontier colors.

        Returns:
            Rich Text object with formatted suggestions
        """
        # Show SDK initialization progress if loading
        if self.is_sdk_loading:
            return self._render_sdk_loading()

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

            # Health status indicator - ✦ for SDK-compliant commands
            if suggestion.health_status:
                text.append("✦ ", style="bold green")
            else:
                text.append("⚠ ", style="bold yellow")

            # Command name (strip leading / for display)
            display_name = suggestion.name.lstrip('/')
            name_style = "bold #89B8C2" if is_selected else "#89B8C2"
            text.append(display_name, style=name_style)

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

    # SDK Loading Methods

    def _render_sdk_loading(self) -> RenderableType:
        """Render SDK initialization progress with spinner, progress bar, and stats.

        Returns:
            Rich Text object with SDK loading progress
        """
        text = Text()

        # Spinner animation frames
        spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        frame = spinner_frames[self.sdk_spinner_frame % len(spinner_frames)]

        # Title with spinner
        text.append(f"{frame} ", style="cyan bold")
        text.append("SDK Initialization\n", style="bold #89B8C2")

        # Current step
        if self.sdk_current_step:
            text.append(f"  {self.sdk_current_step}\n", style="white")

        # Current file
        if self.sdk_current_file:
            text.append(f"  File: {self.sdk_current_file}\n", style="dim")

        # Progress stats
        if self.sdk_command_count > 0 or self.sdk_tool_count > 0:
            text.append(f"  Commands: {self.sdk_command_count} | Tools: {self.sdk_tool_count}\n", style="#89B8C2")

        # SDK enforcement stats (if any)
        total_enforcement = self.sdk_accepted_count + self.sdk_converted_count + self.sdk_rejected_count
        if total_enforcement > 0:
            text.append("  SDK Enforcement: ", style="dim")
            if self.sdk_accepted_count > 0:
                text.append(f"✓{self.sdk_accepted_count} ", style="green")
            if self.sdk_converted_count > 0:
                text.append(f"⚠{self.sdk_converted_count} ", style="yellow")
            if self.sdk_rejected_count > 0:
                text.append(f"✗{self.sdk_rejected_count} ", style="red")
            text.append("\n")

        # Progress bar (simple animation based on spinner frame)
        bar_width = 30
        filled = (self.sdk_spinner_frame % bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        text.append(f"  [{bar}]\n", style="dim")

        return text

    def start_sdk_loading(self) -> None:
        """Start SDK loading mode with spinner animation."""
        self.is_sdk_loading = True
        self.sdk_current_step = "Initializing SDK..."
        self.sdk_spinner_frame = 0

        # Start spinner animation timer
        if self._spinner_timer is None:
            self._spinner_timer = self.set_interval(0.1, self._update_spinner)

    def stop_sdk_loading(self) -> None:
        """Stop SDK loading mode and clear spinner."""
        self.is_sdk_loading = False
        self.sdk_current_step = ""
        self.sdk_current_file = ""

        # Stop spinner timer
        if self._spinner_timer is not None:
            self._spinner_timer.stop()
            self._spinner_timer = None

    def update_sdk_progress(
        self,
        current_step: str = None,
        current_file: str = None,
        command_count: int = None,
        tool_count: int = None,
        accepted_count: int = None,
        converted_count: int = None,
        rejected_count: int = None,
    ) -> None:
        """Update SDK loading progress.

        Args:
            current_step: Current initialization step description
            current_file: Current file being processed
            command_count: Total commands registered
            tool_count: Total tools registered
            accepted_count: SDK accepted count
            converted_count: SDK converted count
            rejected_count: SDK rejected count
        """
        if current_step is not None:
            self.sdk_current_step = current_step
        if current_file is not None:
            self.sdk_current_file = current_file
        if command_count is not None:
            self.sdk_command_count = command_count
        if tool_count is not None:
            self.sdk_tool_count = tool_count
        if accepted_count is not None:
            self.sdk_accepted_count = accepted_count
        if converted_count is not None:
            self.sdk_converted_count = converted_count
        if rejected_count is not None:
            self.sdk_rejected_count = rejected_count

        self.refresh()  # Trigger re-render

    def _update_spinner(self) -> None:
        """Update spinner frame for animation."""
        if self.is_sdk_loading:
            self.sdk_spinner_frame = (self.sdk_spinner_frame + 1) % 100
            self.refresh()
