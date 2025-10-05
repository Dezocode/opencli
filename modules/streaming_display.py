"""
Streaming Display Widget with Laser Effect
Supports live pulsing animation that reverts to default color when done

Uses ANSI background (terminal default) while preserving full RGB colors for text
"""

from textual.widgets import Static
from textual.reactive import reactive
from textual import events
from rich.text import Text
from rich.console import RenderableType
from rich.style import Style
import subprocess

try:
    from .frontier_colors import FRONTIER_LASER_COLORS, FRONTIER_COLORS
    from .markdown_renderer import get_markdown_renderer
except (ImportError, ValueError):
    from frontier_colors import FRONTIER_LASER_COLORS, FRONTIER_COLORS
    from markdown_renderer import get_markdown_renderer


class StreamingDisplay(Static):
    """
    Display widget that supports streaming text with live laser effect
    and color reversion when streaming completes

    Background: ANSI default (terminal native)
    Foreground: Full RGB colors (16.7M colors)
    """

    content: reactive[RenderableType] = reactive("")
    can_focus = True

    # CSS to ensure ANSI background with no color override
    DEFAULT_CSS = """
    StreamingDisplay {
        background: default;
    }
    """

    BINDINGS = [
        ("ctrl+a", "select_all", "Select All"),
        ("cmd+c", "copy_all", "Copy"),
        ("ctrl+c", "copy_all", "Copy"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lines = []
        self._current_stream = ""
        self._streaming = False
        self._laser_colors = FRONTIER_LASER_COLORS
        self._laser_enabled = True
        self._markdown_renderer = get_markdown_renderer()

        # Text selection state
        self._selection_start = None
        self._selection_end = None
        self._selecting = False

    def write_stream(self, text: str):
        """Write streaming text with markdown rendering and optional laser effect"""
        self._streaming = True
        self._current_stream += text

        # Render the current stream as markdown IN REAL-TIME
        rendered_stream = self._markdown_renderer.render(self._current_stream)

        # Build complete display
        display_text = Text()

        # Add completed lines
        for line in self._lines:
            if isinstance(line, Text):
                display_text.append_text(line)
            else:
                display_text.append(str(line))
            display_text.append("\n")

        # Add the rendered markdown (current stream)
        # Apply laser effect to the trailing characters if enabled
        if self._laser_enabled and rendered_stream:
            # Get the plain text length for laser calculation
            plain_text = rendered_stream.plain
            stream_len = len(plain_text)
            trail_length = 20  # Characters in the laser trail

            # Apply laser glow to trailing characters
            # We'll rebuild with laser colors on the tail
            for i, span in enumerate(rendered_stream._spans):
                start, end, style = span.start, span.end, span.style
                for pos in range(start, end):
                    char = plain_text[pos] if pos < len(plain_text) else ''
                    distance_from_front = stream_len - pos - 1

                    if distance_from_front < trail_length:
                        # In the laser trail - override with gradient
                        intensity = 1.0 - (distance_from_front / trail_length)
                        color_idx = int(intensity * (len(self._laser_colors) - 1))
                        color_idx = min(color_idx, len(self._laser_colors) - 1)
                        color = self._laser_colors[color_idx]
                        display_text.append(char, style=Style(color=color, bold=True))
                    else:
                        # Beyond trail - use original markdown formatting
                        display_text.append(char, style=style)
        else:
            # No laser - just show rendered markdown
            display_text.append_text(rendered_stream)

        self.update(display_text)
        self._scroll_to_bottom()

    def finish_stream(self):
        """Finish streaming and render markdown - REPLACES streamed content"""
        if self._current_stream:
            # Render the streamed content as markdown (replaces the plain text stream)
            rendered = self._markdown_renderer.render(self._current_stream)

            # IMPORTANT: Replace the stream, don't append it
            # Clear the current stream and add as rendered markdown
            stream_content = self._current_stream
            self._current_stream = ""
            self._streaming = False

            # Add the rendered markdown to lines
            self._lines.append(rendered)

            # Rebuild display with all lines
            display_text = Text()
            for line in self._lines:
                if isinstance(line, Text):
                    display_text.append_text(line)
                else:
                    display_text.append(str(line))

                # Add newline if not present
                if isinstance(line, Text):
                    if not line.plain.endswith("\n"):
                        display_text.append("\n")
                elif not line.endswith("\n"):
                    display_text.append("\n")

            self.update(display_text)
            self._scroll_to_bottom()

    def write(self, text: str | Text, style: str = None):
        """
        Write text (compatibility with RichLog interface)

        Args:
            text: Text string or Rich Text object
            style: Optional style string
        """
        # Handle Rich Text objects
        if isinstance(text, Text):
            # Already a Text object - store it directly
            self._lines.append(text)
        else:
            # String - parse markup and create Text
            text_str = str(text)
            if style:
                # Apply style
                self._lines.append(Text(text_str, style=style))
            else:
                # Parse markup like [green]...[/green]
                self._lines.append(Text.from_markup(text_str))

        # Rebuild display
        display_text = Text()
        for line in self._lines:
            # Each line might be Text object or string
            if isinstance(line, Text):
                display_text.append_text(line)
            else:
                display_text.append(str(line))

            # Add newline if not present
            if not (isinstance(line, str) and line.endswith("\n")):
                if not (isinstance(line, Text) and line.plain.endswith("\n")):
                    display_text.append("\n")

        self.update(display_text)
        self._scroll_to_bottom()

    def write_line(self, text: str, style: str = None):
        """Write a complete line (no laser effect) - alias for write()"""
        self.write(text, style=style)

    def clear(self):
        """Clear all content"""
        self._lines = []
        self._current_stream = ""
        self._streaming = False
        self.update("")

    def set_laser_colors(self, colors: list):
        """Set laser color gradient"""
        self._laser_colors = colors

    def set_laser_enabled(self, enabled: bool):
        """Enable/disable laser effect"""
        self._laser_enabled = enabled

    def write_markdown(self, text: str):
        """Write markdown-formatted text with proper rendering"""
        rendered = self._markdown_renderer.render(text)
        self._lines.append(rendered)

        # Rebuild display
        display_text = Text()
        for line in self._lines:
            if isinstance(line, Text):
                display_text.append_text(line)
            else:
                display_text.append(str(line))

            # Add newline if not present
            if not (isinstance(line, str) and line.endswith("\n")):
                if not (isinstance(line, Text) and line.plain.endswith("\n")):
                    display_text.append("\n")

        self.update(display_text)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        """Scroll the parent container to bottom - NON-BLOCKING async version"""
        def do_scroll():
            try:
                # Find parent VerticalScroll container
                parent = self.parent
                while parent is not None:
                    if parent.__class__.__name__ == 'VerticalScroll':
                        # Scroll to end without animation (faster)
                        parent.scroll_end(animate=False)
                        break
                    parent = parent.parent
            except Exception:
                pass  # Silently ignore if scrolling fails

        # Schedule scroll on next event loop cycle - doesn't block current operation
        try:
            self.call_later(do_scroll)
        except Exception:
            # Fallback to immediate if call_later not available
            do_scroll()

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Handle mouse down - start selection"""
        self._selecting = True
        self._selection_start = (event.x, event.y)
        self._selection_end = (event.x, event.y)

    def on_mouse_move(self, event: events.MouseMove) -> None:
        """Handle mouse move - update selection"""
        if self._selecting:
            self._selection_end = (event.x, event.y)

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """Handle mouse up - finish selection and copy to clipboard"""
        if self._selecting:
            self._selecting = False
            self._copy_selection()

    def _get_selected_text(self) -> str:
        """Get the currently selected text"""
        if not self._selection_start or not self._selection_end:
            return ""

        # Get all text content
        all_text = []
        for line in self._lines:
            if isinstance(line, Text):
                all_text.append(line.plain)
            else:
                all_text.append(str(line))

        if self._current_stream:
            all_text.append(self._current_stream)

        full_text = "\\n".join(all_text)

        # For now, return all text (simple implementation)
        # TODO: Implement proper character-level selection based on coordinates
        return full_text

    def _copy_selection(self):
        """Copy selected text to clipboard"""
        selected_text = self._get_selected_text()
        if not selected_text:
            return

        try:
            # Use pbcopy on macOS, xclip on Linux, clip on Windows
            import platform
            system = platform.system()

            if system == "Darwin":  # macOS
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                process.communicate(selected_text.encode('utf-8'))
            elif system == "Linux":
                try:
                    process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
                    process.communicate(selected_text.encode('utf-8'))
                except FileNotFoundError:
                    # Fallback to xsel
                    process = subprocess.Popen(['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE)
                    process.communicate(selected_text.encode('utf-8'))
            elif system == "Windows":
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
                process.communicate(selected_text.encode('utf-8'))

        except Exception:
            pass  # Silently ignore clipboard errors

    def action_select_all(self) -> None:
        """Select all text (Ctrl+A)"""
        # Set selection to cover all text
        self._selection_start = (0, 0)
        self._selection_end = (999, 999)  # Large values to cover all

    def action_copy_all(self) -> None:
        """Copy all text to clipboard (Cmd+C / Ctrl+C)"""
        # Get all text
        all_text = []
        for line in self._lines:
            if isinstance(line, Text):
                all_text.append(line.plain)
            else:
                all_text.append(str(line))

        if self._current_stream:
            all_text.append(self._current_stream)

        full_text = "\n".join(all_text)

        # Copy to clipboard
        try:
            import platform
            system = platform.system()

            if system == "Darwin":  # macOS
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                process.communicate(full_text.encode('utf-8'))
            elif system == "Linux":
                try:
                    process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
                    process.communicate(full_text.encode('utf-8'))
                except FileNotFoundError:
                    process = subprocess.Popen(['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE)
                    process.communicate(full_text.encode('utf-8'))
            elif system == "Windows":
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
                process.communicate(full_text.encode('utf-8'))

        except Exception:
            pass
