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
        height: 100%;
        width: 100%;
    }
    """

    BINDINGS = [
        ("ctrl+a", "select_all", "Select All"),
        ("cmd+c", "copy_all", "Copy"),
        ("ctrl+c", "copy_all", "Copy"),
    ]

    # Reactive selection for visual feedback
    selection_start = reactive(None)
    selection_end = reactive(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lines = []
        self._current_stream = ""
        self._streaming = False
        self._laser_colors = FRONTIER_LASER_COLORS
        self._laser_enabled = True
        self._markdown_renderer = get_markdown_renderer()

        # Text selection state
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

            # Add ✦ symbol to assistant messages
            message_with_symbol = Text()
            message_with_symbol.append("✦ ", style=Style(color=FRONTIER_COLORS["ai_name"]))
            message_with_symbol.append_text(rendered)

            # Add the rendered markdown to lines
            self._lines.append(message_with_symbol)

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
                # Try to parse markup like [green]...[/green], fall back to plain text
                try:
                    self._lines.append(Text.from_markup(text_str))
                except Exception:
                    # If markup parsing fails (e.g., ambiguous color names), use plain text
                    self._lines.append(Text(text_str))

        # Rebuild display with selection highlighting
        display_text = Text()
        for idx, line in enumerate(self._lines):
            # Each line might be Text object or string
            if isinstance(line, Text):
                # Apply selection highlight if active
                highlighted_line = self._apply_selection_highlight(line, idx)
                display_text.append_text(highlighted_line)
            else:
                # Convert string to Text and apply highlighting
                line_text = Text(str(line))
                highlighted_line = self._apply_selection_highlight(line_text, idx)
                display_text.append_text(highlighted_line)

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
        # IMPORTANT: Don't auto-scroll while user is selecting text!
        if self._selecting:
            return

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

    def _get_scroll_offset(self) -> int:
        """Get the scroll offset from parent VerticalScroll container"""
        try:
            parent = self.parent
            while parent is not None:
                if parent.__class__.__name__ == 'VerticalScroll':
                    # Get the scroll offset
                    return int(parent.scroll_offset.y)
                parent = parent.parent
        except:
            pass
        return 0

    def _get_total_lines(self) -> int:
        """Get total number of content lines"""
        total = 0
        for line in self._lines:
            if isinstance(line, tuple):
                continue  # Skip special tuples
            if isinstance(line, Text):
                total += line.plain.count('\n') + 1
            else:
                total += str(line).count('\n') + 1
        if self._current_stream:
            total += self._current_stream.count('\n') + 1
        return total

    def _handle_mouse_down(self, widget_x: int, widget_y: int) -> None:
        """Handle mouse down with widget-relative coordinates"""
        # Widget-relative coords, add scroll offset to get content line
        scroll_offset = self._get_scroll_offset()
        content_line = widget_y + scroll_offset

        # Clamp to valid content range
        max_line = max(0, self._get_total_lines() - 1)
        content_line = max(0, min(content_line, max_line))

        # DEBUG
        try:
            with open('/tmp/opencli_selection_debug.txt', 'w') as f:
                f.write(f"=== MOUSE DOWN ===\n")
                f.write(f"Widget coords: ({widget_x}, {widget_y})\n")
                f.write(f"Scroll offset: {scroll_offset}\n")
                f.write(f"Total lines: {max_line + 1}\n")
                f.write(f"Content line (clamped): {content_line}\n")
        except:
            pass

        # Clear previous selection and start new one
        self.selection_start = (widget_x, content_line)
        self.selection_end = (widget_x, content_line)
        self._selecting = True

    def _handle_mouse_move(self, widget_x: int, widget_y: int) -> None:
        """Handle mouse move with widget-relative coordinates"""
        if self._selecting:
            scroll_offset = self._get_scroll_offset()
            content_line = widget_y + scroll_offset

            # Clamp to valid content range
            max_line = max(0, self._get_total_lines() - 1)
            content_line = max(0, min(content_line, max_line))

            self.selection_end = (widget_x, content_line)

            # DEBUG - show scroll offset changes
            try:
                with open('/tmp/opencli_selection_debug.txt', 'a') as f:
                    f.write(f"MOVE: widget({widget_x}, {widget_y}) + scroll({scroll_offset}) = line {content_line} (max {max_line})\n")
            except:
                pass

    def _handle_mouse_up(self, widget_x: int, widget_y: int) -> None:
        """Handle mouse up with widget-relative coordinates"""
        if self._selecting:
            self._selecting = False

            # Copy selection to clipboard (no visual highlighting to preserve markdown formatting)
            self._copy_selection()

            # DEBUG
            try:
                with open('/tmp/opencli_selection_debug.txt', 'a') as f:
                    f.write(f"UP: selection complete\n")
            except:
                pass

    def watch_selection_start(self, old_value, new_value):
        """Reactive watcher - disabled to preserve markdown formatting"""
        # Visual selection highlighting disabled to preserve Rich Text formatting
        pass

    def watch_selection_end(self, old_value, new_value):
        """Reactive watcher - disabled to preserve markdown formatting"""
        # Visual selection highlighting disabled to preserve Rich Text formatting
        pass


    def _apply_selection_highlight(self, content: Text, line_number: int) -> Text:
        """Apply visual highlight to selected text in a line"""
        if not self.selection_start or not self.selection_end:
            return content

        # Get selection coordinates
        start_x, start_y = self.selection_start
        end_x, end_y = self.selection_end

        # Normalize
        if start_y > end_y or (start_y == end_y and start_x > end_x):
            start_x, start_y, end_x, end_y = end_x, end_y, start_x, start_y

        # Check if this line is in selection range
        if line_number < start_y or line_number > end_y:
            return content

        # Create highlighted version
        highlighted = Text()
        plain_text = content.plain

        if line_number == start_y == end_y:
            # Single line selection - CHARACTER RANGE ONLY
            # DEBUG
            try:
                with open('/tmp/opencli_highlight_debug.txt', 'a') as f:
                    f.write(f"Line {line_number}: HIGHLIGHTING chars {start_x}-{end_x} of '{plain_text[:60]}...'\n")
            except:
                pass

            highlighted.append(plain_text[:start_x])
            highlighted.append(plain_text[start_x:end_x], style=Style(reverse=True))
            highlighted.append(plain_text[end_x:])
        elif line_number == start_y:
            # First line of multi-line selection
            highlighted.append(plain_text[:start_x])
            highlighted.append(plain_text[start_x:], style=Style(reverse=True))
        elif line_number == end_y:
            # Last line of multi-line selection
            highlighted.append(plain_text[:end_x], style=Style(reverse=True))
            highlighted.append(plain_text[end_x:])
        else:
            # Middle line - fully selected
            highlighted.append(plain_text, style=Style(reverse=True))

        return highlighted

    def _get_selected_text(self) -> str:
        """Get the currently selected text"""
        if not self.selection_start or not self.selection_end:
            return ""

        # Build line array SAME WAY as _rebuild_display() to match line numbers
        all_lines = []

        for line in self._lines:
            # Skip special tuples
            if isinstance(line, tuple):
                if line[0] in ("__BUFFER_STATUS__", "__PERMISSION_PROMPT__"):
                    content = line[1]
                    lines = content.plain.split('\n') if isinstance(content, Text) else str(content).split('\n')
                    all_lines.extend(lines)
                continue

            # Split Text/string by newlines to match render logic
            if isinstance(line, Text):
                lines = line.plain.split('\n')
            else:
                lines = str(line).split('\n')

            all_lines.extend(lines)

        # Add current stream
        if self._current_stream:
            rendered_stream = self._markdown_renderer.render(self._current_stream)
            lines = rendered_stream.plain.split('\n')
            all_lines.extend(lines)

        # DEBUG
        try:
            with open('/tmp/opencli_selection_debug.txt', 'a') as f:
                f.write(f"\nGET SELECTED TEXT:\n")
                f.write(f"Total lines: {len(all_lines)}\n")
                # Show a few lines around the selection
                start_x, start_y = self.selection_start
                end_x, end_y = self.selection_end
                for i in range(max(0, start_y - 2), min(len(all_lines), end_y + 3)):
                    line_preview = all_lines[i][:60] if len(all_lines[i]) > 60 else all_lines[i]
                    f.write(f"  Line {i}: {repr(line_preview)}\n")
        except:
            pass

        if not all_lines:
            return ""

        # Extract coordinates
        start_x, start_y = self.selection_start
        end_x, end_y = self.selection_end

        # DEBUG
        try:
            with open('/tmp/opencli_selection_debug.txt', 'a') as f:
                f.write(f"Selection coords: ({start_x},{start_y}) to ({end_x},{end_y})\n")
        except:
            pass

        # Normalize coordinates
        if start_y > end_y or (start_y == end_y and start_x > end_x):
            start_x, start_y, end_x, end_y = end_x, end_y, start_x, start_y

        # Clamp to valid line ranges
        start_y = max(0, min(start_y, len(all_lines) - 1))
        end_y = max(0, min(end_y, len(all_lines) - 1))

        selected_lines = []

        # Single line selection
        if start_y == end_y:
            line = all_lines[start_y]

            # DEBUG - show what's on this line
            try:
                with open('/tmp/opencli_selection_debug.txt', 'a') as f:
                    f.write(f"Line {start_y} content: {repr(line[:100] if len(line) > 100 else line)}\n")
                    f.write(f"Line length: {len(line)}\n")
                    f.write(f"Requested chars: {start_x}-{end_x}\n")
            except:
                pass

            start_x = max(0, min(start_x, len(line)))
            end_x = max(0, min(end_x, len(line)))

            # DEBUG - show clamped positions
            try:
                with open('/tmp/opencli_selection_debug.txt', 'a') as f:
                    f.write(f"Clamped to: {start_x}-{end_x}\n")
                    f.write(f"Extracted: {repr(line[start_x:end_x])}\n")
            except:
                pass

            selected_lines.append(line[start_x:end_x])

        # Multi-line selection
        else:
            for i in range(start_y, end_y + 1):
                line = all_lines[i]

                if i == start_y:
                    # First line - from start_x to end
                    start_x = max(0, min(start_x, len(line)))
                    selected_lines.append(line[start_x:])
                elif i == end_y:
                    # Last line - from beginning to end_x
                    end_x = max(0, min(end_x, len(line)))
                    selected_lines.append(line[:end_x])
                else:
                    # Middle lines - entire line
                    selected_lines.append(line)

        return "\n".join(selected_lines)

    def _copy_selection(self):
        """Copy selected text to clipboard"""
        selected_text = self._get_selected_text()

        # DEBUG
        try:
            with open('/tmp/opencli_selection_debug.txt', 'a') as f:
                f.write(f"\nCOPY SELECTION:\n")
                f.write(f"Text length: {len(selected_text)}\n")
                if selected_text:
                    f.write(f"First 60 chars: {repr(selected_text[:60])}\n")
                else:
                    f.write(f"ERROR: Selected text is empty\n")
        except:
            pass

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

    # Buffer Status Methods (for inline streaming progress display)
    def add_buffer_status(self, tokens: int = 0, elapsed: int = 0) -> None:
        """
        Add inline buffer status display showing streaming progress
        Uses Frontier colors for consistency
        """
        from rich.style import Style

        # Create buffer status text with Frontier colors
        buffer_text = Text()
        buffer_text.append("⠋ Synthesizing… ", style=Style(color=FRONTIER_COLORS["info"], bold=True))
        buffer_text.append(f"(esc to interrupt · {elapsed}s · ↓ {tokens} tokens)\n", style=Style(color=FRONTIER_COLORS["info"]))
        buffer_text.append("  ⎿  Tip: ", style=Style(color=FRONTIER_COLORS["text_secondary"], dim=True))
        buffer_text.append("Press ESC to interrupt long-running responses.", style=Style(color=FRONTIER_COLORS["text_dim"]))

        # Add to lines with special marker
        self._lines.append(("__BUFFER_STATUS__", buffer_text))

        # Rebuild display
        self._rebuild_display()

    def update_buffer_status(self, tokens: int, elapsed: int, spinner_frame: str = "⠋") -> None:
        """Update the buffer status with new progress"""
        from rich.style import Style

        # Find and update buffer status line
        for i, line in enumerate(self._lines):
            if isinstance(line, tuple) and line[0] == "__BUFFER_STATUS__":
                # Update the buffer text
                buffer_text = Text()
                buffer_text.append(f"{spinner_frame} Synthesizing… ", style=Style(color=FRONTIER_COLORS["info"], bold=True))
                buffer_text.append(f"(esc to interrupt · {elapsed}s · ↓ {tokens} tokens)\n", style=Style(color=FRONTIER_COLORS["info"]))
                buffer_text.append("  ⎿  Tip: ", style=Style(color=FRONTIER_COLORS["text_secondary"], dim=True))
                buffer_text.append("Press ESC to interrupt long-running responses.", style=Style(color=FRONTIER_COLORS["text_dim"]))

                self._lines[i] = ("__BUFFER_STATUS__", buffer_text)
                self._rebuild_display()
                break

    def remove_buffer_status(self) -> None:
        """Remove the buffer status line"""
        # Filter out buffer status
        self._lines = [line for line in self._lines if not (isinstance(line, tuple) and line[0] == "__BUFFER_STATUS__")]
        self._rebuild_display()

    def add_permission_prompt(self, prompt_data: dict) -> None:
        """
        Add a permission prompt to the display

        Args:
            prompt_data: Dict with 'title', 'message', 'options', 'details'
        """
        # DON'T add to _lines - that's for chat content
        # Instead, notify the app to show the permission widget in the footer
        try:
            app = self.app
            if not app:
                # Try to get app from parent hierarchy
                parent = self.parent
                while parent:
                    if hasattr(parent, 'app'):
                        app = parent.app
                        break
                    parent = getattr(parent, 'parent', None)

            if app and hasattr(app, '_show_permission_prompt'):
                app._show_permission_prompt(prompt_data)
        except Exception:
            pass  # Silently fail if can't show permission prompt

    def remove_permission_prompt(self) -> None:
        """Remove the permission prompt from display"""
        # Call app to hide the permission widget
        try:
            app = self.app
            if not app:
                # Try to get app from parent hierarchy
                parent = self.parent
                while parent:
                    if hasattr(parent, 'app'):
                        app = parent.app
                        break
                    parent = getattr(parent, 'parent', None)

            if app and hasattr(app, '_hide_permission_prompt'):
                app._hide_permission_prompt()
        except Exception:
            pass

    def _rebuild_display(self) -> None:
        """Rebuild the complete display from _lines with selection highlighting"""
        # DEBUG - clear highlight debug file at start of rebuild
        try:
            with open('/tmp/opencli_highlight_debug.txt', 'w') as f:
                f.write(f"=== REBUILD DISPLAY ===\n")
                f.write(f"Selection: {self.selection_start} to {self.selection_end}\n")
        except:
            pass

        display_text = Text()

        # We need to track line numbers for selection highlighting
        # Split content into actual display lines first
        all_content_lines = []
        for line in self._lines:
            # Handle buffer status tuples
            if isinstance(line, tuple) and line[0] == "__BUFFER_STATUS__":
                all_content_lines.append(("__BUFFER_STATUS__", line[1]))
            # Handle permission prompt tuples
            elif isinstance(line, tuple) and line[0] == "__PERMISSION_PROMPT__":
                all_content_lines.append(("__PERMISSION_PROMPT__", line[1]))
            # Handle regular Text objects and strings
            elif isinstance(line, Text):
                all_content_lines.append(("TEXT", line))
            else:
                all_content_lines.append(("STRING", str(line)))

        # Now render with selection highlighting applied line-by-line
        current_line_idx = 0
        for item_type, content in all_content_lines:
            if item_type == "__BUFFER_STATUS__":
                display_text.append_text(content)
                display_text.append("\n")
                current_line_idx += content.plain.count('\n') + 1
            elif item_type == "__PERMISSION_PROMPT__":
                display_text.append_text(content)
                display_text.append("\n")
                current_line_idx += content.plain.count('\n') + 1
            elif item_type == "TEXT":
                # Split Text object by newlines to get individual lines
                lines = content.plain.split('\n')
                for i, line_text in enumerate(lines):
                    # Create Text for this line
                    line_obj = Text(line_text)
                    # Apply selection highlighting
                    highlighted = self._apply_selection_highlight(line_obj, current_line_idx)
                    display_text.append_text(highlighted)

                    # Add newline unless it's the last line and content didn't end with newline
                    if i < len(lines) - 1 or content.plain.endswith('\n'):
                        display_text.append("\n")
                        current_line_idx += 1
            elif item_type == "STRING":
                # Split string by newlines
                lines = content.split('\n')
                for i, line_text in enumerate(lines):
                    line_obj = Text(line_text)
                    highlighted = self._apply_selection_highlight(line_obj, current_line_idx)
                    display_text.append_text(highlighted)

                    if i < len(lines) - 1 or content.endswith('\n'):
                        display_text.append("\n")
                        current_line_idx += 1

        # Add current stream if any
        if self._current_stream:
            rendered_stream = self._markdown_renderer.render(self._current_stream)
            lines = rendered_stream.plain.split('\n')
            for i, line_text in enumerate(lines):
                line_obj = Text(line_text)
                highlighted = self._apply_selection_highlight(line_obj, current_line_idx)
                display_text.append_text(highlighted)

                if i < len(lines) - 1:
                    display_text.append("\n")
                    current_line_idx += 1

        self.update(display_text)
        self._scroll_to_bottom()
