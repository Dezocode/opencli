"""
Markdown Renderer for OpenCLI
Converts markdown to Rich Text with frontier color scheme
"""

import re
from rich.text import Text
from rich.style import Style
try:
    from .frontier_colors import FRONTIER_COLORS
except (ImportError, ValueError):
    from frontier_colors import FRONTIER_COLORS


class MarkdownRenderer:
    """Render markdown text to Rich Text with proper formatting"""

    def __init__(self):
        self.colors = FRONTIER_COLORS

    def render(self, markdown_text: str) -> Text:
        """
        Render markdown string to Rich Text object

        Supports:
        - Headings (###)
        - Bold (**text**)
        - Italic (*text*)
        - Inline code (`code`)
        - Code blocks (```code```)
        - Lists (- item)
        - Links (though not clickable in terminal)
        """
        result = Text()
        lines = markdown_text.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]

            # Code blocks
            if line.strip().startswith('```'):
                i += 1
                code_lines = []
                # Collect code block lines
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1

                # Render code block
                if code_lines:
                    result.append('\n')  # Spacing before code block
                    for code_line in code_lines:
                        result.append('  ')  # Indent
                        result.append(code_line, style=Style(
                            color=self.colors['code_text'],
                            bgcolor=self.colors['code_bg']
                        ))
                        result.append('\n')
                    result.append('\n')  # Spacing after code block
                i += 1
                continue

            # Headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2)

                # Render heading with appropriate styling
                result.append(heading_text, style=Style(
                    color=self.colors['heading'],
                    bold=True
                ))
                result.append('\n')
                i += 1
                continue

            # List items
            list_match = re.match(r'^(\s*)[-*]\s+(.+)$', line)
            if list_match:
                indent = list_match.group(1)
                item_text = list_match.group(2)

                result.append(indent)
                result.append('• ', style=Style(color=self.colors['list_marker']))
                result.append_text(self._render_inline(item_text))
                result.append('\n')
                i += 1
                continue

            # Regular line with inline formatting
            if line.strip():
                result.append_text(self._render_inline(line))
                result.append('\n')
            else:
                # Empty line
                result.append('\n')

            i += 1

        return result

    def _render_inline(self, text: str) -> Text:
        """Render inline markdown elements (bold, italic, code, links)"""
        result = Text()
        pos = 0

        # Pattern for inline elements: **bold**, *italic*, `code`
        # Process text character by character to handle overlapping patterns
        while pos < len(text):
            # Try to match inline code first (highest priority)
            code_match = re.match(r'`([^`]+)`', text[pos:])
            if code_match:
                code_text = code_match.group(1)
                result.append(code_text, style=Style(
                    color=self.colors['inline_code'],
                    bgcolor=self.colors['code_bg']
                ))
                pos += len(code_match.group(0))
                continue

            # Try to match bold
            bold_match = re.match(r'\*\*([^*]+)\*\*', text[pos:])
            if bold_match:
                bold_text = bold_match.group(1)
                result.append(bold_text, style=Style(
                    color=self.colors['bold'],
                    bold=True
                ))
                pos += len(bold_match.group(0))
                continue

            # Try to match italic (single asterisk or underscore)
            italic_match = re.match(r'(?:\*|_)([^*_]+)(?:\*|_)', text[pos:])
            if italic_match and not text[pos:].startswith('**'):
                italic_text = italic_match.group(1)
                result.append(italic_text, style=Style(
                    color=self.colors['italic'],
                    italic=True
                ))
                pos += len(italic_match.group(0))
                continue

            # No special formatting - regular character
            result.append(text[pos], style=Style(color=self.colors['text_primary']))
            pos += 1

        return result

    def render_message(self, role: str, content: str, username: str = None) -> Text:
        """
        Render a complete message (user or assistant) with proper formatting

        Args:
            role: 'user' or 'assistant'
            content: Message content (may contain markdown)
            username: Optional username override

        Returns:
            Rich Text object ready to display
        """
        result = Text()

        # Render username/role
        if role == 'user':
            display_name = username if username else 'You'
            result.append(display_name, style=Style(
                color=self.colors['user_name'],
                bold=True
            ))
            result.append(': ', style=Style(color=self.colors['text_secondary']))
            # User messages are dimmer (they typed it, less important to re-read)
            result.append(content, style=Style(color=self.colors['text_secondary']))
        else:
            # Assistant message
            result.append('AI', style=Style(
                color=self.colors['ai_name'],
                bold=True
            ))
            result.append(': ', style=Style(color=self.colors['text_secondary']))
            # Render assistant message with full markdown support
            result.append_text(self.render(content))

        return result


# Singleton instance
_renderer = None

def get_markdown_renderer() -> MarkdownRenderer:
    """Get the global markdown renderer instance"""
    global _renderer
    if _renderer is None:
        _renderer = MarkdownRenderer()
    return _renderer
