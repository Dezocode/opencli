"""
Text Selection System for Streaming Display
Handles text selection, highlighting, and copying functionality
"""

from typing import Optional, Tuple
from rich.text import Text
from rich.style import Style

try:
    from ..frontier_colors import FRONTIER_COLORS
except (ImportError, ValueError):
    from frontier_colors import FRONTIER_COLORS


class TextSelection:
    """Manages text selection state and operations"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.selection_start: Optional[Tuple[int, int]] = None
        self.selection_end: Optional[Tuple[int, int]] = None
        self.is_selecting = False
        
    def start_selection(self, line: int, col: int) -> None:
        """Start text selection at given position"""
        self.selection_start = (line, col)
        self.selection_end = (line, col)
        self.is_selecting = True
        
    def update_selection(self, line: int, col: int) -> None:
        """Update selection end position"""
        if self.is_selecting:
            self.selection_end = (line, col)
            
    def end_selection(self) -> None:
        """End text selection"""
        self.is_selecting = False
        
    def clear_selection(self) -> None:
        """Clear current selection"""
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        
    def has_selection(self) -> bool:
        """Check if there is an active selection"""
        return (self.selection_start is not None and
                self.selection_end is not None and
                self.selection_start != self.selection_end)

    def get_span(self, y: int) -> Optional[Tuple[int, int]]:
        """Get selection span for a given line (required by Textual)

        Args:
            y: Line index

        Returns:
            Tuple of (start_col, end_col) if line is selected, None otherwise
        """
        if not self.has_selection():
            return None

        start_line, start_col = self.selection_start
        end_line, end_col = self.selection_end

        # Ensure start comes before end
        if (start_line > end_line or
            (start_line == end_line and start_col > end_col)):
            start_line, start_col, end_line, end_col = end_line, end_col, start_line, start_col

        # Check if line y is within selection range
        if y < start_line or y > end_line:
            return None

        # Single line selection
        if start_line == end_line:
            return (start_col, end_col)

        # Multi-line selection
        if y == start_line:
            # First line - from start_col to end of line (use large number)
            return (start_col, 10000)
        elif y == end_line:
            # Last line - from beginning to end_col
            return (0, end_col)
        else:
            # Middle line - entire line selected
            return (0, 10000)

    def get_selected_text(self, content_lines: list) -> str:
        """Extract selected text from content lines"""
        if not self.has_selection():
            return ""
            
        start_line, start_col = self.selection_start
        end_line, end_col = self.selection_end
        
        # Ensure start comes before end
        if (start_line > end_line or 
            (start_line == end_line and start_col > end_col)):
            start_line, start_col, end_line, end_col = end_line, end_col, start_line, start_col
            
        selected_text = []
        
        for line_idx in range(start_line, min(end_line + 1, len(content_lines))):
            line_content = content_lines[line_idx]
            
            if isinstance(line_content, Text):
                line_text = line_content.plain
            else:
                line_text = str(line_content)
                
            if line_idx == start_line and line_idx == end_line:
                # Selection within single line
                selected_text.append(line_text[start_col:end_col])
            elif line_idx == start_line:
                # First line of multi-line selection
                selected_text.append(line_text[start_col:])
            elif line_idx == end_line:
                # Last line of multi-line selection
                selected_text.append(line_text[:end_col])
            else:
                # Full line in middle of selection
                selected_text.append(line_text)
                
        return '\n'.join(selected_text)
        
    def apply_selection_highlight(self, content_lines: list) -> list:
        """Apply selection highlighting to content lines"""
        if not self.has_selection():
            return content_lines
            
        start_line, start_col = self.selection_start
        end_line, end_col = self.selection_end
        
        # Ensure start comes before end
        if (start_line > end_line or 
            (start_line == end_line and start_col > end_col)):
            start_line, start_col, end_line, end_col = end_line, end_col, start_line, start_col
            
        highlighted_lines = []
        selection_style = Style(bgcolor=FRONTIER_COLORS.get("selection", "#3A3A3A"))
        
        for line_idx, line_content in enumerate(content_lines):
            if line_idx < start_line or line_idx > end_line:
                highlighted_lines.append(line_content)
                continue
                
            if isinstance(line_content, Text):
                line_text = line_content.copy()
            else:
                line_text = Text(str(line_content))
                
            if line_idx == start_line and line_idx == end_line:
                # Selection within single line
                line_text.stylize(selection_style, start_col, end_col)
            elif line_idx == start_line:
                # First line of multi-line selection
                line_text.stylize(selection_style, start_col, len(line_text))
            elif line_idx == end_line:
                # Last line of multi-line selection
                line_text.stylize(selection_style, 0, end_col)
            else:
                # Full line in middle of selection
                line_text.stylize(selection_style, 0, len(line_text))
                
            highlighted_lines.append(line_text)
            
        return highlighted_lines
        
    def select_all(self, content_lines: list) -> None:
        """Select all text content"""
        if not content_lines:
            return
            
        self.selection_start = (0, 0)
        
        last_line_idx = len(content_lines) - 1
        last_line = content_lines[last_line_idx]
        
        if isinstance(last_line, Text):
            last_col = len(last_line.plain)
        else:
            last_col = len(str(last_line))
            
        self.selection_end = (last_line_idx, last_col)
        
    def copy_selection(self, content_lines: list) -> bool:
        """Copy selected text to clipboard"""
        selected_text = self.get_selected_text(content_lines)
        if not selected_text:
            return False
            
        try:
            import subprocess
            import platform
            
            system = platform.system().lower()
            
            if system == "darwin":  # macOS
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                process.communicate(selected_text.encode('utf-8'))
            elif system == "linux":
                # Try xclip first, then xsel
                try:
                    process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                             stdin=subprocess.PIPE)
                    process.communicate(selected_text.encode('utf-8'))
                except FileNotFoundError:
                    process = subprocess.Popen(['xsel', '--clipboard', '--input'], 
                                             stdin=subprocess.PIPE)
                    process.communicate(selected_text.encode('utf-8'))
            elif system == "windows":
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
                process.communicate(selected_text.encode('utf-8'))
            else:
                return False
                
            return True
            
        except Exception:
            return False
            
    def copy_all(self, content_lines: list) -> bool:
        """Copy all content to clipboard"""
        all_text = []
        
        for line in content_lines:
            if isinstance(line, Text):
                all_text.append(line.plain)
            else:
                all_text.append(str(line))
                
        full_text = '\n'.join(all_text)
        
        if not full_text:
            return False
            
        try:
            import subprocess
            import platform
            
            system = platform.system().lower()
            
            if system == "darwin":  # macOS
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                process.communicate(full_text.encode('utf-8'))
            elif system == "linux":
                try:
                    process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                             stdin=subprocess.PIPE)
                    process.communicate(full_text.encode('utf-8'))
                except FileNotFoundError:
                    process = subprocess.Popen(['xsel', '--clipboard', '--input'], 
                                             stdin=subprocess.PIPE)
                    process.communicate(full_text.encode('utf-8'))
            elif system == "windows":
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
                process.communicate(full_text.encode('utf-8'))
            else:
                return False
                
            return True
            
        except Exception:
            return False