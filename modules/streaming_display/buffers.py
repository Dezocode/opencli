"""
Buffer Management for Streaming Display
Handles permission prompts, status buffers, and display state management
"""

from typing import Optional, Dict, Any, List
from rich.text import Text
from rich.panel import Panel
from rich.align import Align

try:
    from ..frontier_colors import FRONTIER_COLORS, STATUS_COLORS
except (ImportError, ValueError):
    try:
        from frontier_colors import FRONTIER_COLORS, STATUS_COLORS
    except ImportError:
        FRONTIER_COLORS = {}
        STATUS_COLORS = {}


class BufferManager:
    """Manages various display buffers and overlays"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.permission_prompt_data: Optional[Dict[str, Any]] = None
        self.buffer_status_data: Optional[Dict[str, Any]] = None
        self.active_overlays: List[str] = []
        
    def add_permission_prompt(self, prompt_data: Dict[str, Any]) -> None:
        """Add permission prompt overlay"""
        self.permission_prompt_data = prompt_data.copy()
        self.permission_prompt_data.setdefault('selected', 0)
        if 'permission_prompt' not in self.active_overlays:
            self.active_overlays.append('permission_prompt')
            
    def remove_permission_prompt(self) -> None:
        """Remove permission prompt overlay"""
        self.permission_prompt_data = None
        if 'permission_prompt' in self.active_overlays:
            self.active_overlays.remove('permission_prompt')
            
    def add_buffer_status(self, status_data: Dict[str, Any]) -> None:
        """Add buffer status overlay"""
        self.buffer_status_data = status_data.copy()
        if 'buffer_status' not in self.active_overlays:
            self.active_overlays.append('buffer_status')
            
    def update_buffer_status(self, status_data: Dict[str, Any]) -> None:
        """Update existing buffer status"""
        if self.buffer_status_data:
            self.buffer_status_data.update(status_data)
            
    def remove_buffer_status(self) -> None:
        """Remove buffer status overlay"""
        self.buffer_status_data = None
        if 'buffer_status' in self.active_overlays:
            self.active_overlays.remove('buffer_status')
            
    def render_permission_prompt(self) -> Optional[Text]:
        """Render permission prompt overlay"""
        if not self.permission_prompt_data:
            return None
            
        try:
            title = self.permission_prompt_data.get('title', 'Permission Required')
            message = self.permission_prompt_data.get('message', 'Allow this operation?')
            options = self.permission_prompt_data.get('options', [])
            details = self.permission_prompt_data.get('details', {})
            selected = self.permission_prompt_data.get('selected', 0)
            
            # Build prompt content
            content_lines = []
            
            # Title
            content_lines.append(title)
            content_lines.append("")
            
            # Details
            for key, value in details.items():
                if isinstance(value, str) and len(value) > 100:
                    content_lines.append(f"  {value[:100]}...")
                else:
                    content_lines.append(f"  {value}")
            
            if details:
                content_lines.append("")
                
            # Message
            for line in message.split('\n'):
                content_lines.append(line)
            content_lines.append("")
            
            # Options
            for i, option in enumerate(options):
                indicator = "❯" if i == selected else " "
                option_text = option.get('text', f'Option {i+1}')
                content_lines.append(f"{indicator} {i + 1}. {option_text}")
                
            content_lines.append("")
            content_lines.append("  Enter to confirm · Esc to cancel")
            
            # Calculate width
            width = min(max(len(line) for line in content_lines) + 4, 160)
            
            # Create styled output
            output = Text()
            
            # Top border
            border_color = FRONTIER_COLORS.get("border", "#5C6773")
            output.append("╭" + "─" * (width - 2) + "╮\\n", style=f"color: {border_color}")
            
            # Content lines
            for i, line in enumerate(content_lines):
                padding = width - len(line) - 4
                output.append("│ ", style=f"color: {border_color}")
                
                if i == 0:  # Title
                    output.append(line, style=f"color: {FRONTIER_COLORS.get('warning', '#E2A478')} bold")
                elif any(line.startswith(f"{j} {j + 1}.") or line.startswith(f"❯ {j + 1}.") 
                        for j in range(len(options))):  # Option lines
                    if line.startswith("❯"):
                        # Selected option
                        output.append("❯", style=f"color: {FRONTIER_COLORS.get('success', '#6B9E78')} bold")
                        rest = line[1:]
                        output.append(rest, style=f"color: {FRONTIER_COLORS.get('foreground', '#D9D7CE')} bold")
                    else:
                        output.append(line, style=f"color: {FRONTIER_COLORS.get('dim', '#5C6773')}")
                elif line.strip().endswith("Enter to confirm · Esc to cancel"):
                    output.append(line, style=f"color: {FRONTIER_COLORS.get('dim', '#5C6773')} italic")
                elif details and any(str(value) in line for value in details.values()):
                    output.append(line, style=f"color: {FRONTIER_COLORS.get('info', '#6B9E78')}")
                else:
                    output.append(line, style=f"color: {FRONTIER_COLORS.get('foreground', '#D9D7CE')}")
                    
                output.append(" " * padding)
                output.append(" │\\n", style=f"color: {border_color}")
                
            # Bottom border
            output.append("╰" + "─" * (width - 2) + "╯", style=f"color: {border_color}")
            
            return output
            
        except Exception:
            # Fallback simple prompt
            return Text("Permission Required - Press Enter to continue", 
                       style=f"color: {FRONTIER_COLORS.get('warning', '#E2A478')}")
            
    def render_buffer_status(self) -> Optional[Text]:
        """Render buffer status overlay"""
        if not self.buffer_status_data:
            return None
            
        try:
            status_type = self.buffer_status_data.get('type', 'status')
            message = self.buffer_status_data.get('message', 'Processing...')
            progress = self.buffer_status_data.get('progress')
            details = self.buffer_status_data.get('details', {})
            
            output = Text()
            
            # Status indicator
            if status_type == 'loading':
                indicator = "⟳"
                color = STATUS_COLORS.get('loading', '#E2A478')
            elif status_type == 'success':
                indicator = "✓"
                color = STATUS_COLORS.get('success', '#6B9E78')
            elif status_type == 'error':
                indicator = "✗"
                color = STATUS_COLORS.get('error', '#E74C3C')
            elif status_type == 'warning':
                indicator = "⚠"
                color = STATUS_COLORS.get('warning', '#F39C12')
            else:
                indicator = "ℹ"
                color = STATUS_COLORS.get('info', '#3498DB')
                
            output.append(f"{indicator} ", style=f"color: {color}")
            output.append(message, style=f"color: {FRONTIER_COLORS.get('foreground', '#D9D7CE')}")
            
            # Progress indicator
            if progress is not None:
                if isinstance(progress, (int, float)):
                    progress_bar = self._create_progress_bar(progress)
                    output.append(f" {progress_bar}", style=f"color: {color}")
                else:
                    output.append(f" [{progress}]", style=f"color: {color}")
                    
            # Details
            if details:
                output.append("\\n")
                for key, value in details.items():
                    output.append(f"  {key}: {value}\\n", 
                                style=f"color: {FRONTIER_COLORS.get('dim', '#5C6773')}")
                                
            return output
            
        except Exception:
            return Text("Status update available", 
                       style=f"color: {STATUS_COLORS.get('info', '#3498DB')}")
            
    def _create_progress_bar(self, progress: float, width: int = 20) -> str:
        """Create a simple text progress bar"""
        if progress < 0:
            progress = 0
        elif progress > 100:
            progress = 100
            
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {progress:.0f}%"
        
    def has_active_overlays(self) -> bool:
        """Check if there are any active overlays"""
        return len(self.active_overlays) > 0
        
    def get_overlay_count(self) -> int:
        """Get number of active overlays"""
        return len(self.active_overlays)
        
    def clear_all_overlays(self) -> None:
        """Clear all active overlays"""
        self.permission_prompt_data = None
        self.buffer_status_data = None
        self.active_overlays.clear()
        
    def get_overlay_render_order(self) -> List[str]:
        """Get overlays in rendering order (bottom to top)"""
        # Buffer status appears below permission prompts
        order = []
        if 'buffer_status' in self.active_overlays:
            order.append('buffer_status')
        if 'permission_prompt' in self.active_overlays:
            order.append('permission_prompt')
        return order