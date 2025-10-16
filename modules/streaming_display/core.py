"""
Core Streaming Display Widget
Main widget that integrates all modular streaming display components
"""

from textual.widgets import Static
from textual.reactive import reactive
from textual import events
from rich.text import Text
from rich.console import RenderableType
from typing import Optional, Dict, Any

from .selection import TextSelection
from .markdown import MarkdownProcessor
from .buffers import BufferManager
from .mouse import MouseHandler

try:
    from ..frontier_colors import FRONTIER_LASER_COLORS, FRONTIER_COLORS
except (ImportError, ValueError):
    try:
        from frontier_colors import FRONTIER_LASER_COLORS, FRONTIER_COLORS
    except ImportError:
        FRONTIER_LASER_COLORS = []
        FRONTIER_COLORS = {}


class StreamingDisplay(Static):
    """
    Display widget that supports streaming text with live laser effect
    and color reversion when streaming completes

    Background: ANSI default (terminal native)
    Foreground: Full RGB colors (16.7M colors)
    """

    content: reactive[RenderableType] = reactive("")
    can_focus = False  # CRITICAL: Don't steal focus from input widget

    # CSS to ensure transparent background with no color override
    DEFAULT_CSS = """
    StreamingDisplay {
        background: transparent;
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
        
        # Core state
        self.content_lines = []
        self._current_stream = ""
        self._streaming = False
        self._laser_colors = FRONTIER_LASER_COLORS
        self._laser_enabled = False  # Disabled - causes visual spam
        
        # Initialize modular components
        self._text_selection = TextSelection(self)
        self._markdown_processor = MarkdownProcessor()
        self._buffer_manager = BufferManager(self)
        self._mouse_handler = MouseHandler(self, self._text_selection)
        
    # Properties for modular component access
    @property
    def text_selection(self) -> TextSelection:
        return self._text_selection
        
    @property 
    def markdown_processor(self) -> MarkdownProcessor:
        return self._markdown_processor
        
    @property
    def buffer_manager(self) -> BufferManager:
        return self._buffer_manager
        
    @property
    def mouse_handler(self) -> MouseHandler:
        return self._mouse_handler

    def write_stream(self, text: str) -> None:
        """Accumulate streaming text silently - display handled by buffer status"""
        self._streaming = True
        self._current_stream += text

    def finish_stream(self) -> None:
        """Complete the stream and display accumulated content"""
        if self._streaming and self._current_stream:
            # Process accumulated stream content
            if self._markdown_processor.is_markdown_content(self._current_stream):
                processed_content = self._markdown_processor.process_markdown(self._current_stream)
            else:
                processed_content = Text(self._current_stream)
                
            # Add to content lines
            for line in str(processed_content).split('\n'):
                self.content_lines.append(Text(line) if line else Text(""))
            
            # Clear stream state
            self._current_stream = ""
            self._streaming = False
            
            # Rebuild display
            self._rebuild_display()
            self._scroll_to_bottom()

    def write(self, text: str | Text, style: str = None) -> None:
        """Write text to the display with optional styling"""
        if isinstance(text, str):
            if style:
                text_obj = Text(text, style=style)
            else:
                text_obj = Text(text)
        else:
            text_obj = text

        # Process markdown if detected
        if isinstance(text, str) and self._markdown_processor.is_markdown_content(text):
            text_obj = self._markdown_processor.process_markdown(text)

        # Split into lines and add to content
        text_lines = str(text_obj).split('\n')
        for i, line in enumerate(text_lines):
            if i == 0 and self.content_lines:
                # Append to last line if it exists
                if hasattr(self.content_lines[-1], 'append'):
                    self.content_lines[-1].append(line)
                else:
                    self.content_lines[-1] = Text(str(self.content_lines[-1]) + line)
            else:
                # Add as new line
                self.content_lines.append(Text(line) if line else Text(""))

        self._rebuild_display()
        self._scroll_to_bottom()

    def write_line(self, text: str, style: str = None) -> None:
        """Write a complete line to the display"""
        self.write(text + "\n", style)

    def clear(self) -> None:
        """Clear all content from the display"""
        self.content_lines = []
        self._text_selection.clear_selection()
        self._buffer_manager.clear_all_overlays()
        self.content = ""

    def write_markdown(self, text: str) -> None:
        """Write markdown text with formatting"""
        processed_text = self._markdown_processor.process_markdown(text)
        self.write(processed_text)

    def set_laser_colors(self, colors: list) -> None:
        """Set laser effect colors"""
        self._laser_colors = colors

    def set_laser_enabled(self, enabled: bool) -> None:
        """Enable or disable laser effect"""
        self._laser_enabled = enabled

    # Buffer management methods
    def add_permission_prompt(self, prompt_data: Dict[str, Any]) -> None:
        """Add permission prompt overlay"""
        self._buffer_manager.add_permission_prompt(prompt_data)
        self._rebuild_display()

    def remove_permission_prompt(self) -> None:
        """Remove permission prompt overlay"""
        self._buffer_manager.remove_permission_prompt()
        self._rebuild_display()

    def add_buffer_status(self, status_data: Dict[str, Any]) -> None:
        """Add buffer status overlay"""
        self._buffer_manager.add_buffer_status(status_data)
        self._rebuild_display()

    def update_buffer_status(self, status_data: Dict[str, Any]) -> None:
        """Update buffer status overlay"""
        self._buffer_manager.update_buffer_status(status_data)
        self._rebuild_display()

    def remove_buffer_status(self) -> None:
        """Remove buffer status overlay"""
        self._buffer_manager.remove_buffer_status()
        self._rebuild_display()

    # Selection and copying methods
    def action_select_all(self) -> None:
        """Select all content"""
        self._text_selection.select_all(self.content_lines)
        self._rebuild_display()

    def action_copy_all(self) -> None:
        """Copy all content to clipboard"""
        if self._text_selection.has_selection():
            self._text_selection.copy_selection(self.content_lines)
        else:
            self._text_selection.copy_all(self.content_lines)

    # Mouse event handlers
    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Handle mouse button press"""
        if self._mouse_handler.handle_mouse_down(event):
            self._rebuild_display()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        """Handle mouse movement"""
        if self._mouse_handler.handle_mouse_move(event):
            self._rebuild_display()

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """Handle mouse button release"""
        if self._mouse_handler.handle_mouse_up(event):
            self._rebuild_display()

    # Selection watchers
    def watch_selection_start(self, old_value, new_value) -> None:
        """React to selection start changes"""
        if old_value != new_value:
            self._text_selection.selection_start = new_value
            self._rebuild_display()

    def watch_selection_end(self, old_value, new_value) -> None:
        """React to selection end changes"""
        if old_value != new_value:
            self._text_selection.selection_end = new_value
            self._rebuild_display()

    # Internal methods
    def _rebuild_display(self) -> None:
        """Rebuild the display content with all overlays"""
        if not self.content_lines:
            display_content = Text("")
        else:
            # Apply text selection highlighting
            highlighted_lines = self._text_selection.apply_selection_highlight(self.content_lines)
            
            # Combine all lines
            display_content = Text()
            for line in highlighted_lines:
                display_content.append(line)
                display_content.append("\n")

        # Add overlays in order
        overlay_order = self._buffer_manager.get_overlay_render_order()
        for overlay_type in overlay_order:
            if overlay_type == 'buffer_status':
                status_content = self._buffer_manager.render_buffer_status()
                if status_content:
                    display_content.append("\n")
                    display_content.append(status_content)
                    display_content.append("\n")
            elif overlay_type == 'permission_prompt':
                prompt_content = self._buffer_manager.render_permission_prompt()
                if prompt_content:
                    display_content.append("\n")
                    display_content.append(prompt_content)
                    display_content.append("\n")

        self.content = display_content

    def _scroll_to_bottom(self) -> None:
        """Scroll to bottom of content"""
        try:
            # Use call_after_refresh to ensure scroll happens after render
            self.call_after_refresh(self._do_scroll)
        except Exception:
            pass

    def _do_scroll(self) -> None:
        """Perform the actual scroll operation"""
        try:
            # Find scrollable parent
            parent = self.parent
            while parent:
                if hasattr(parent, 'scroll_end') or parent.__class__.__name__ == 'VerticalScroll':
                    if hasattr(parent, 'scroll_end'):
                        parent.scroll_end(animate=False)
                    elif hasattr(parent, 'scroll_y'):
                        parent.scroll_y = parent.max_scroll_y
                    break
                parent = getattr(parent, 'parent', None)
        except Exception:
            pass

    def _get_scroll_offset(self) -> int:
        """Get current scroll offset"""
        try:
            parent = self.parent
            while parent:
                if hasattr(parent, 'scroll_y') or parent.__class__.__name__ == 'VerticalScroll':
                    return getattr(parent, 'scroll_y', 0)
                parent = getattr(parent, 'parent', None)
            return 0
        except Exception:
            return 0

    def _get_total_lines(self) -> int:
        """Get total number of lines in content"""
        base_lines = len(self.content_lines)
        overlay_lines = 0
        
        if self._buffer_manager.has_active_overlays():
            # Estimate overlay lines
            if self._buffer_manager.buffer_status_data:
                overlay_lines += 3  # Status typically takes 2-3 lines
            if self._buffer_manager.permission_prompt_data:
                overlay_lines += 10  # Prompt typically takes 8-12 lines
                
        return base_lines + overlay_lines