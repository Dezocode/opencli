"""
Multi-line input widget with wrapping and history support
Designed to not break chat layout
"""

from textual.widget import Widget
from textual.message import Message
from textual.reactive import reactive
from rich.text import Text
from rich.console import Console
import asyncio


class MultiLineInput(Widget):
    """
    Custom multi-line input that wraps at edge and supports history
    """

    value = reactive("", layout=True)
    cursor_position = reactive(0)
    is_spinning = reactive(False)
    spinner_frame = reactive(0)

    # Spinner frames
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    class Submitted(Message):
        """Posted when user submits the input"""
        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    def __init__(self, placeholder: str = "", **kwargs):
        super().__init__(**kwargs)
        self.placeholder = placeholder
        self._lines = [""]
        self._cursor_row = 0
        self._cursor_col = 0
        self.can_focus = True
        self._spin_task = None

    def render(self) -> Text:
        """Render the current input with cursor"""
        # Build display
        display = Text()

        # Add spinner if active, otherwise show >
        prefix = ""
        if self.is_spinning:
            frame = self.SPINNER_FRAMES[self.spinner_frame % len(self.SPINNER_FRAMES)]
            prefix = frame + " "
            display.append(prefix, style="dim cyan")
        else:
            prefix = "> "
            display.append(prefix, style="dim")

        # Show placeholder if empty and not focused
        if not self.value and self.placeholder and not self.has_focus:
            display.append(self.placeholder, style="dim")
            return display

        # Show empty cursor if no value but focused
        if not self.value and self.has_focus:
            display.append(" ", style="reverse")
            return display

        # Show empty text if no value and no focus
        if not self.value:
            return display

        # For single line or simple rendering, just show value with cursor
        if self.has_focus:
            # Insert cursor at current position
            before = self.value[:self.cursor_position]
            if self.cursor_position < len(self.value):
                cursor = self.value[self.cursor_position]
                after = self.value[self.cursor_position + 1:]
                display.append(before)
                display.append(cursor, style="reverse")
                display.append(after)
            else:
                # Cursor at end
                display.append(self.value)
                display.append(" ", style="reverse")
        else:
            # No focus, just show value
            display.append(self.value)

        return display

    def _wrap_text(self, text: str, width: int = None) -> list[str]:
        """Wrap text to fit width"""
        if width is None:
            width = self.size.width - 2  # Account for padding

        if width <= 0:
            return [text]

        lines = []
        current_line = ""

        for char in text:
            if char == '\n':
                lines.append(current_line)
                current_line = ""
            elif len(current_line) >= width:
                lines.append(current_line)
                current_line = char
            else:
                current_line += char

        if current_line or not lines:
            lines.append(current_line)

        return lines

    def on_key(self, event) -> None:
        """Handle key presses"""
        key = event.key

        # Don't handle up/down - let parent handle for history
        if key in ("up", "down"):
            return

        # Submit on enter
        if key == "enter":
            self.action_submit()
            event.prevent_default()
            return

        # Backspace
        if key == "backspace":
            if self.cursor_position > 0:
                new_pos = self.cursor_position - 1
                new_value = (
                    self.value[:new_pos] +
                    self.value[self.cursor_position:]
                )
                # Update both atomically to avoid race
                self.cursor_position = new_pos
                self.value = new_value
            event.prevent_default()
            return

        # Delete
        if key == "delete":
            if self.cursor_position < len(self.value):
                self.value = (
                    self.value[:self.cursor_position] +
                    self.value[self.cursor_position+1:]
                )
            event.prevent_default()
            return

        # Left arrow
        if key == "left":
            if self.cursor_position > 0:
                self.cursor_position -= 1
            event.prevent_default()
            return

        # Right arrow
        if key == "right":
            if self.cursor_position < len(self.value):
                self.cursor_position += 1
            event.prevent_default()
            return

        # Home
        if key == "home":
            self.cursor_position = 0
            event.prevent_default()
            return

        # End
        if key == "end":
            self.cursor_position = len(self.value)
            event.prevent_default()
            return

        # Use character property for actual character input (best practice)
        # This handles all printable characters including special chars
        if event.character and event.character.isprintable():
            self.value = (
                self.value[:self.cursor_position] +
                event.character +
                self.value[self.cursor_position:]
            )
            self.cursor_position += 1
            event.prevent_default()

    def action_submit(self) -> None:
        """Submit the current value"""
        if self.value.strip():
            self.post_message(self.Submitted(self.value))

    def clear(self) -> None:
        """Clear the input"""
        self.value = ""
        self.cursor_position = 0

    def watch_value(self, old_value: str, new_value: str) -> None:
        """Update when value changes"""
        # Ensure cursor is within bounds
        if self.cursor_position > len(new_value):
            self.cursor_position = len(new_value)
        self.refresh()

    def start_spinner(self) -> None:
        """Start the spinner animation"""
        if not self.is_spinning:
            self.is_spinning = True
            if self._spin_task is None or self._spin_task.done():
                self._spin_task = asyncio.create_task(self._spin())

    def stop_spinner(self) -> None:
        """Stop the spinner animation"""
        self.is_spinning = False
        if self._spin_task and not self._spin_task.done():
            try:
                self._spin_task.cancel()
            except Exception:
                pass
        self.spinner_frame = 0
        self._spin_task = None
        self.refresh()

    async def _spin(self) -> None:
        """Async task that updates the spinner"""
        try:
            while self.is_spinning:
                self.spinner_frame = (self.spinner_frame + 1) % len(self.SPINNER_FRAMES)
                self.refresh()
                await asyncio.sleep(0.08)  # 80ms per frame
        except asyncio.CancelledError:
            pass

    def watch_is_spinning(self, old_value: bool, new_value: bool) -> None:
        """React to spinning state changes"""
        if old_value != new_value:
            self.refresh()

    def watch_spinner_frame(self, old_value: int, new_value: int) -> None:
        """React to frame changes - refresh already handled by _spin"""
        pass
