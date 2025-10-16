"""
Mouse Handler for Streaming Display
Manages mouse events, text selection, and interaction tracking
"""

from typing import Optional, Tuple
from textual import events
from .selection import TextSelection

try:
    from ..frontier_colors import FRONTIER_COLORS
except (ImportError, ValueError):
    try:
        from frontier_colors import FRONTIER_COLORS
    except ImportError:
        FRONTIER_COLORS = {}


class MouseHandler:
    """Handles mouse interactions for streaming display"""
    
    def __init__(self, parent_widget, text_selection: TextSelection):
        self.parent = parent_widget
        self.text_selection = text_selection
        self.last_click_time = 0
        self.click_count = 0
        self.double_click_threshold = 0.5  # seconds
        
    def handle_mouse_down(self, event: events.MouseDown) -> bool:
        """Handle mouse button press"""
        try:
            widget_x, widget_y = event.x, event.y
            
            # Convert screen coordinates to content coordinates
            line_idx, col_idx = self._screen_to_content_coords(widget_x, widget_y)
            
            if line_idx is None or col_idx is None:
                return False
                
            # Handle click timing for double-click detection
            import time
            current_time = time.time()
            
            if current_time - self.last_click_time < self.double_click_threshold:
                self.click_count += 1
            else:
                self.click_count = 1
                
            self.last_click_time = current_time
            
            # Handle different click types
            if self.click_count == 1:
                # Single click - start selection
                self.text_selection.start_selection(line_idx, col_idx)
            elif self.click_count == 2:
                # Double click - select word
                self._select_word_at_position(line_idx, col_idx)
            elif self.click_count >= 3:
                # Triple click - select line
                self._select_line_at_position(line_idx)
                
            return True
            
        except Exception:
            return False
            
    def handle_mouse_move(self, event: events.MouseMove) -> bool:
        """Handle mouse movement during selection"""
        if not self.text_selection.is_selecting:
            return False
            
        try:
            widget_x, widget_y = event.x, event.y
            line_idx, col_idx = self._screen_to_content_coords(widget_x, widget_y)
            
            if line_idx is not None and col_idx is not None:
                self.text_selection.update_selection(line_idx, col_idx)
                return True
                
        except Exception:
            pass
            
        return False
        
    def handle_mouse_up(self, event: events.MouseUp) -> bool:
        """Handle mouse button release"""
        if self.text_selection.is_selecting:
            self.text_selection.end_selection()
            return True
        return False
        
    def _screen_to_content_coords(self, screen_x: int, screen_y: int) -> Tuple[Optional[int], Optional[int]]:
        """Convert screen coordinates to content line/column"""
        try:
            # Get scroll offset
            scroll_offset = self.parent._get_scroll_offset()
            
            # Calculate line index
            line_idx = screen_y + scroll_offset
            
            # Get content lines
            if hasattr(self.parent, 'content_lines'):
                content_lines = self.parent.content_lines
            else:
                return None, None
                
            # Validate line index
            if line_idx < 0 or line_idx >= len(content_lines):
                return None, None
                
            # Calculate column index
            line_content = content_lines[line_idx]
            if hasattr(line_content, 'plain'):
                line_text = line_content.plain
            else:
                line_text = str(line_content)
                
            # Ensure column is within line bounds
            col_idx = min(max(0, screen_x), len(line_text))
            
            return line_idx, col_idx
            
        except Exception:
            return None, None
            
    def _select_word_at_position(self, line_idx: int, col_idx: int) -> None:
        """Select the word at the given position"""
        try:
            if hasattr(self.parent, 'content_lines'):
                content_lines = self.parent.content_lines
            else:
                return
                
            if line_idx >= len(content_lines):
                return
                
            line_content = content_lines[line_idx]
            if hasattr(line_content, 'plain'):
                line_text = line_content.plain
            else:
                line_text = str(line_content)
                
            # Find word boundaries
            start_col = col_idx
            end_col = col_idx
            
            # Find start of word
            while start_col > 0 and self._is_word_char(line_text[start_col - 1]):
                start_col -= 1
                
            # Find end of word
            while end_col < len(line_text) and self._is_word_char(line_text[end_col]):
                end_col += 1
                
            # Set selection
            self.text_selection.selection_start = (line_idx, start_col)
            self.text_selection.selection_end = (line_idx, end_col)
            self.text_selection.is_selecting = False
            
        except Exception:
            pass
            
    def _select_line_at_position(self, line_idx: int) -> None:
        """Select the entire line at the given position"""
        try:
            if hasattr(self.parent, 'content_lines'):
                content_lines = self.parent.content_lines
            else:
                return
                
            if line_idx >= len(content_lines):
                return
                
            line_content = content_lines[line_idx]
            if hasattr(line_content, 'plain'):
                line_length = len(line_content.plain)
            else:
                line_length = len(str(line_content))
                
            # Select entire line
            self.text_selection.selection_start = (line_idx, 0)
            self.text_selection.selection_end = (line_idx, line_length)
            self.text_selection.is_selecting = False
            
        except Exception:
            pass
            
    def _is_word_char(self, char: str) -> bool:
        """Check if character is part of a word"""
        return char.isalnum() or char in '_-.'
        
    def get_click_count(self) -> int:
        """Get current click count for multi-click detection"""
        return self.click_count
        
    def reset_click_count(self) -> None:
        """Reset click count"""
        self.click_count = 0
        self.last_click_time = 0