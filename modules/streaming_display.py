"""
Streaming Display Widget with Laser Effect
Supports live pulsing animation that reverts to default color when done

Uses ANSI background (terminal default) while preserving full RGB colors for text
"""

from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.console import RenderableType
from rich.style import Style


class StreamingDisplay(Static):
    """
    Display widget that supports streaming text with live laser effect
    and color reversion when streaming completes

    Background: ANSI default (terminal native)
    Foreground: Full RGB colors (16.7M colors)
    """

    content: reactive[RenderableType] = reactive("")
    can_focus = True

    # CSS to ensure ANSI background and scrolling
    DEFAULT_CSS = """
    StreamingDisplay {
        background: default;
        color: auto;
        overflow-y: auto;
        height: 1fr;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lines = []
        self._current_stream = ""
        self._streaming = False
        self._laser_colors = ["#8B0000", "#FF4500", "#FFA500", "#FFFF00", "#FFFFFF"]
        self._laser_enabled = True

    def write_stream(self, text: str):
        """Write streaming text with trailing laser wave effect"""
        self._streaming = True
        self._current_stream += text

        # Build complete display with trailing wave effect
        display_text = Text()

        # Add completed lines in default color
        for line in self._lines:
            if isinstance(line, Text):
                display_text.append_text(line)
            else:
                display_text.append(str(line))
            display_text.append("\n")

        # Add current streaming line with trailing wave effect
        if self._laser_enabled and self._current_stream:
            stream_len = len(self._current_stream)
            trail_length = 20  # Characters in the laser trail

            for i, char in enumerate(self._current_stream):
                # Calculate distance from the "front" (most recent character)
                distance_from_front = stream_len - i - 1

                if distance_from_front < trail_length:
                    # In the laser trail - apply gradient
                    # 0 = hottest (newest), trail_length = coolest (oldest)
                    intensity = 1.0 - (distance_from_front / trail_length)
                    color_idx = int(intensity * (len(self._laser_colors) - 1))
                    color_idx = min(color_idx, len(self._laser_colors) - 1)

                    color = self._laser_colors[color_idx]
                    # Use RGB color for foreground, no background (ANSI default shows through)
                    display_text.append(char, style=Style(color=color, bold=True))
                else:
                    # Beyond the trail - default color
                    display_text.append(char)

        else:
            display_text.append(self._current_stream)

        self.update(display_text)

    def finish_stream(self):
        """Finish streaming and revert to default color"""
        if self._current_stream:
            # Add current stream as completed line (default color)
            # Parse markup if present
            self._lines.append(Text.from_markup(self._current_stream))
            self._current_stream = ""
            self._streaming = False

            # Rebuild display with all lines in default color
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
