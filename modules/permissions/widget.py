"""
Permission Prompt Widget - UI Component for permission prompts
Extracted from permission_prompt.py.backup and optimized for modular architecture
"""

from textual.widget import Widget
from textual.message import Message
from textual.reactive import reactive
from rich.text import Text
from rich.style import Style
from .enums import PermissionResponse

# Import Frontier colors
try:
    from ..frontier_colors import FRONTIER_COLORS, STATUS_COLORS
except (ImportError, ValueError):
    from frontier_colors import FRONTIER_COLORS, STATUS_COLORS


class PermissionPrompt(Widget):
    """
    Permission prompt widget with formatted box and selectable options
    Displays in the chat area, between messages like the buffer status
    """

    selected_option = reactive(0)
    is_active = reactive(False)

    class Responded(Message):
        """Posted when user responds to the prompt"""
        def __init__(self, response: PermissionResponse, data: dict = None) -> None:
            self.response = response
            self.data = data or {}
            super().__init__()

    def __init__(self,
                 title: str,
                 message: str,
                 options: list,
                 details: dict = None,
                 **kwargs):
        """
        Args:
            title: Prompt title (e.g., "Fetch", "Edit File")
            message: Main message text
            options: List of option dicts with 'text' and 'response' keys
            details: Optional dict of additional details to display
        """
        super().__init__(**kwargs)
        self.title = title
        self.message = message
        self.options = options  # [{'text': '...', 'response': PermissionResponse}, ...]
        self.details = details or {}
        self.can_focus = True

    def on_focus(self) -> None:
        """Track when widget gains focus"""
        import sys
        sys.stderr.write(f"\n[PermissionPrompt.on_focus] 🔥 GAINED FOCUS 🔥 is_active={self.is_active}\n")
        sys.stderr.flush()
        self.refresh()

    def on_blur(self) -> None:
        """Track when widget loses focus"""
        import sys
        sys.stderr.write(f"\n[PermissionPrompt.on_blur] ⚠️  LOST FOCUS ⚠️  is_active={self.is_active}\n")
        sys.stderr.flush()
        self.refresh()

    def render(self) -> Text:
        """Render the permission prompt as a formatted box with Frontier colors"""
        if not self.is_active:
            return Text("")

        # Build the output with Frontier colors
        output = Text()

        # Calculate content for width
        content_lines = []

        # Title line
        content_lines.append(self.title)
        content_lines.append("")

        # Details (file path, URL, command, etc.)
        for key, value in self.details.items():
            if isinstance(value, str) and len(value) > 100:
                content_lines.append(f"  {value[:100]}...")
            else:
                content_lines.append(f"  {value}")

        if self.details:
            content_lines.append("")

        # Main message
        for line in self.message.split('\n'):
            content_lines.append(line)
        content_lines.append("")

        # Options
        option_lines = []
        for i, option in enumerate(self.options):
            indicator = "❯" if i == self.selected_option else " "
            option_lines.append(f"{indicator} {i + 1}. {option['text']}")

        content_lines.extend(option_lines)
        content_lines.append("")

        # Calculate width
        width = min(max(len(line) for line in content_lines) + 4, 160)

        # Top border
        output.append("╭" + "─" * (width - 2) + "╮\n",
                     style=Style(color=FRONTIER_COLORS.get("border", "#5C6773")))

        # Title
        title_padding = width - len(content_lines[0]) - 4
        output.append("│ ", style=Style(color=FRONTIER_COLORS.get("border", "#5C6773")))
        output.append(content_lines[0], style=Style(color=FRONTIER_COLORS.get("warning", "#E2A478"), bold=True))
        output.append(" " * title_padding)
        output.append(" │\n", style=Style(color=FRONTIER_COLORS.get("border", "#5C6773")))

        # Empty line after title
        output.append("│" + " " * (width - 2) + "│\n",
                     style=Style(color=FRONTIER_COLORS.get("border", "#5C6773")))

        # Details section (skip title and first empty line)
        detail_start = 2
        detail_end = detail_start + len(self.details)
        if self.details:
            detail_end += 1  # Include empty line after details

        for line in content_lines[detail_start:detail_end]:
            padding = width - len(line) - 4
            output.append("│ ", style=Style(color=FRONTIER_COLORS.get("border", "#5C6773")))
            output.append(line, style=Style(color=FRONTIER_COLORS.get("info", "#6B9E78")))
            output.append(" " * padding)
            output.append(" │\n", style=Style(color=FRONTIER_COLORS.get("border", "#5C6773")))

        # Message section
        msg_lines = self.message.split('\n')
        for line in msg_lines:
            padding = width - len(line) - 4
            output.append("│ ", style=Style(color=FRONTIER_COLORS.get("border", "#5C6773")))
            output.append(line, style=Style(color=FRONTIER_COLORS.get("foreground", "#D9D7CE")))
            output.append(" " * padding)
            output.append(" │\n", style=Style(color=FRONTIER_COLORS.get("border", "#5C6773")))

        # Empty line before options
        output.append("│" + " " * (width - 2) + "│\n",
                     style=Style(color=FRONTIER_COLORS.get("border", "#5C6773")))

        # Options section
        for i, option in enumerate(self.options):
            indicator = "❯" if i == self.selected_option else " "
            line_text = f"{indicator} {i + 1}. {option['text']}"
            padding = width - len(line_text) - 4

            output.append("│ ", style=Style(color=FRONTIER_COLORS.get("border", "#5C6773")))

            if i == self.selected_option:
                # Highlight selected option
                output.append(indicator, style=Style(color=FRONTIER_COLORS.get("success", "#6B9E78"), bold=True))
                output.append(f" {i + 1}. {option['text']}",
                            style=Style(color=FRONTIER_COLORS.get("foreground", "#D9D7CE"), bold=True))
            else:
                output.append(line_text, style=Style(color=FRONTIER_COLORS.get("dim", "#5C6773")))

            output.append(" " * padding)
            output.append(" │\n", style=Style(color=FRONTIER_COLORS.get("border", "#5C6773")))

        # Empty line before bottom border
        output.append("│" + " " * (width - 2) + "│\n",
                     style=Style(color=FRONTIER_COLORS.get("border", "#5C6773")))

        # Bottom border
        output.append("╰" + "─" * (width - 2) + "╯\n",
                     style=Style(color=FRONTIER_COLORS.get("border", "#5C6773")))

        # Helper text
        output.append("  Enter to confirm · Esc to cancel",
                     style=Style(color=FRONTIER_COLORS.get("dim", "#5C6773"), italic=True))

        return output

    def on_key(self, event) -> None:
        """Handle key presses for option selection"""
        import sys
        sys.stderr.write(f"\n[PermissionPrompt.on_key] 🔥 KEY='{event.key}' is_active={self.is_active} focused={self.has_focus} 🔥\n")
        sys.stderr.flush()

        if not self.is_active:
            sys.stderr.write(f"[PermissionPrompt.on_key] BLOCKED - widget not active!\n")
            sys.stderr.flush()
            return

        key = event.key

        # Up arrow - move selection up
        if key == "up":
            if self.selected_option > 0:
                self.selected_option -= 1
            event.prevent_default()
            return

        # Down arrow - move selection down
        if key == "down":
            if self.selected_option < len(self.options) - 1:
                self.selected_option += 1
            event.prevent_default()
            return

        # Enter - confirm selection
        if key == "enter":
            self.action_confirm()
            event.prevent_default()
            return

        # Escape - cancel
        if key == "escape":
            self.action_cancel()
            event.prevent_default()
            return

        # Number keys - quick select
        if event.character and event.character.isdigit():
            num = int(event.character)
            if 1 <= num <= len(self.options):
                self.selected_option = num - 1
                self.action_confirm()
                event.prevent_default()
                return

    def action_confirm(self) -> None:
        """Confirm the selected option"""
        if 0 <= self.selected_option < len(self.options):
            selected = self.options[self.selected_option]
            self.post_message(self.Responded(
                response=selected['response'],
                data=selected.get('data', {})
            ))
            self.is_active = False

    def action_cancel(self) -> None:
        """Cancel the prompt"""
        self.post_message(self.Responded(
            response=PermissionResponse.CANCEL,
            data={}
        ))
        self.is_active = False

    def show(self) -> None:
        """Activate the prompt"""
        import sys
        sys.stderr.write(f"\n[PermissionPrompt.show] 🔥 ACTIVATING WIDGET 🔥\n")
        sys.stderr.flush()
        self.is_active = True
        self.selected_option = 0
        self.refresh()
        sys.stderr.write(f"[PermissionPrompt.show] ✅ Widget activated: is_active={self.is_active}\n")
        sys.stderr.flush()

    def hide(self) -> None:
        """Deactivate the prompt"""
        self.is_active = False
        self.refresh()

    def watch_selected_option(self, old_value: int, new_value: int) -> None:
        """React to selection changes"""
        if old_value != new_value:
            self.refresh()

    def watch_is_active(self, old_value: bool, new_value: bool) -> None:
        """React to active state changes"""
        if old_value != new_value:
            self.refresh()