"""
Permission Prompt Widget - Buffered UI for tool execution approval
Shows formatted markdown-style boxes with selectable options
"""

from textual.widget import Widget
from textual.message import Message
from textual.reactive import reactive
from rich.text import Text
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.style import Style
from enum import Enum

# Import Frontier colors
try:
    from .frontier_colors import FRONTIER_COLORS, STATUS_COLORS
except (ImportError, ValueError):
    from frontier_colors import FRONTIER_COLORS, STATUS_COLORS


class PermissionResponse(Enum):
    """Permission response types"""
    ALLOW_ONCE = "allow_once"
    ALLOW_ALWAYS = "allow_always"
    ALLOW_DOMAIN = "allow_domain"
    DENY = "deny"
    CANCEL = "cancel"


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
        if not self.is_active:
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
        self.is_active = True
        self.selected_option = 0
        self.refresh()

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


class PermissionTemplates:
    """Standard permission prompt templates for common operations"""

    @staticmethod
    def webfetch(url: str, domain: str = None) -> dict:
        """Create WebFetch permission prompt"""
        if not domain:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc

        return {
            'title': 'Fetch',
            'message': f'Claude wants to fetch content from {domain}\n\nDo you want to allow Claude to fetch this content?',
            'details': {
                'url': url
            },
            'options': [
                {
                    'text': 'Yes',
                    'response': PermissionResponse.ALLOW_ONCE
                },
                {
                    'text': f"Yes, and don't ask again for {domain}",
                    'response': PermissionResponse.ALLOW_DOMAIN,
                    'data': {'domain': domain}
                },
                {
                    'text': 'No, and tell Claude what to do differently (esc)',
                    'response': PermissionResponse.DENY
                }
            ]
        }

    @staticmethod
    def file_edit(file_path: str, old_str: str, new_str: str) -> dict:
        """Create file Edit permission prompt"""
        # Truncate strings for display
        old_preview = old_str[:80] + "..." if len(old_str) > 80 else old_str
        new_preview = new_str[:80] + "..." if len(new_str) > 80 else new_str

        return {
            'title': 'Edit File',
            'message': f'Claude wants to modify a file.\n\nDo you want to allow this edit?',
            'details': {
                'file': file_path,
                'replace': old_preview,
                'with': new_preview
            },
            'options': [
                {
                    'text': 'Yes, allow this edit',
                    'response': PermissionResponse.ALLOW_ONCE
                },
                {
                    'text': "Yes, and don't ask again for Edit operations",
                    'response': PermissionResponse.ALLOW_ALWAYS,
                    'data': {'tool': 'Edit'}
                },
                {
                    'text': 'No, skip this operation (esc)',
                    'response': PermissionResponse.DENY
                }
            ]
        }

    @staticmethod
    def file_write(file_path: str, content: str) -> dict:
        """Create file Write permission prompt"""
        content_preview = content[:100] + "..." if len(content) > 100 else content

        return {
            'title': 'Write File',
            'message': f'Claude wants to write a new file.\n\nDo you want to allow this?',
            'details': {
                'file': file_path,
                'content': f"({len(content)} chars) {content_preview}"
            },
            'options': [
                {
                    'text': 'Yes, allow this write',
                    'response': PermissionResponse.ALLOW_ONCE
                },
                {
                    'text': "Yes, and don't ask again for Write operations",
                    'response': PermissionResponse.ALLOW_ALWAYS,
                    'data': {'tool': 'Write'}
                },
                {
                    'text': 'No, skip this operation (esc)',
                    'response': PermissionResponse.DENY
                }
            ]
        }

    @staticmethod
    def bash_command(command: str, description: str = None) -> dict:
        """Create Bash command permission prompt"""
        desc_text = f"\n{description}" if description else ""

        return {
            'title': 'Execute Command',
            'message': f'Claude wants to execute a bash command.{desc_text}\n\nDo you want to allow this?',
            'details': {
                'command': command
            },
            'options': [
                {
                    'text': 'Yes, execute this command',
                    'response': PermissionResponse.ALLOW_ONCE
                },
                {
                    'text': "Yes, and don't ask again for Bash operations",
                    'response': PermissionResponse.ALLOW_ALWAYS,
                    'data': {'tool': 'Bash'}
                },
                {
                    'text': 'No, skip this command (esc)',
                    'response': PermissionResponse.DENY
                }
            ]
        }

    @staticmethod
    def trust_directory(directory: str) -> dict:
        """Create directory trust permission prompt"""
        return {
            'title': 'Trust Directory',
            'message': 'Do you trust the files in this folder?\n\nClaude Code may read, write, or execute files contained in this directory. This can pose security risks, so only use files, hooks, and bash commands from trusted sources.\n\nExecution allowed by:\n\n  • .claude/settings.json, .claude/settings.local.json\n\nLearn more ( https://docs.claude.com/s/claude-code-security )',
            'details': {
                'directory': directory
            },
            'options': [
                {
                    'text': 'Yes, proceed',
                    'response': PermissionResponse.ALLOW_ALWAYS,
                    'data': {'directory': directory}
                },
                {
                    'text': 'No, exit',
                    'response': PermissionResponse.DENY
                }
            ]
        }

    @staticmethod
    def configure_headers(provider: str, model: str, issue: str, current_headers: dict, proposed_headers: dict = None) -> dict:
        """Create provider header configuration prompt"""
        provider_name = provider or "Provider"
        current_details = [f"{key}: {value or '[unset]'}" for key, value in (current_headers or {}).items()]

        if proposed_headers:
            proposed_details = [f"{key}: {value}" for key, value in proposed_headers.items()]
            message = (
                f"OpenCLI needs to update {provider_name} headers so this model can stream."\
                f"\nReason: {issue or 'Provider rejected the request.'}\n\n"
                "Apply the suggested headers from your environment?"
            )
            details = {
                'provider': provider_name,
                'model': model or '[unknown model]',
                'current headers': '\n'.join(current_details) or '[none]',
                'suggested headers': '\n'.join(proposed_details)
            }
        else:
            message = (
                f"{provider_name} returned a policy error for this model."\
                f"\nReason: {issue or 'Provider rejected the request.'}\n\n"
                "Provide the required header values from your provider privacy settings."
            )
            details = {
                'provider': provider_name,
                'model': model or '[unknown model]',
                'current headers': '\n'.join(current_details) or '[none]'
            }

        options = [
            {
                'text': 'Yes, continue',
                'response': PermissionResponse.ALLOW_ONCE
            },
            {
                'text': 'No, cancel (esc)',
                'response': PermissionResponse.DENY
            }
        ]

        return {
            'title': 'Configure Provider Headers',
            'message': message,
            'details': details,
            'options': options
        }

    @staticmethod
    def code_refactoring(plan: dict, result: dict) -> dict:
        """Create code refactoring permission prompt"""
        # Extract info from plan and result
        source_file = plan.get('source_file', '')
        target_file = plan.get('target_file', '')
        functions = plan.get('functions_to_move', [])
        estimated_lines = plan.get('estimated_lines', 0)
        rationale = plan.get('rationale', '')

        test_results = result.get('test_results', '')
        test_passed = 'exit code: 0' in test_results.lower() if test_results else False

        # Create details
        details = {
            'source': source_file,
            'target': target_file,
            'functions': ', '.join(functions) if len(', '.join(functions)) < 80 else f"{len(functions)} functions",
            'lines': f"~{estimated_lines} lines",
            'tests': '✅ PASSED' if test_passed else '⚠️  NOT VERIFIED' if not test_results else '❌ FAILED'
        }

        message = f"Auto-refactoring suggests extracting functions to improve code organization.\n\n{rationale}\n\nDo you want to apply this refactoring?"

        return {
            'title': 'Code Refactoring',
            'message': message,
            'details': details,
            'options': [
                {
                    'text': 'Yes, apply this refactoring',
                    'response': PermissionResponse.ALLOW_ONCE
                },
                {
                    'text': "Yes, and don't ask again for refactoring",
                    'response': PermissionResponse.ALLOW_ALWAYS,
                    'data': {'tool': 'Refactoring'}
                },
                {
                    'text': 'No, skip this refactoring (esc)',
                    'response': PermissionResponse.DENY
                }
            ]
        }
