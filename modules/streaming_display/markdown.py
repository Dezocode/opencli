"""
Markdown Processing for Streaming Display
Handles markdown rendering and formatting for displayed content
"""

from typing import Optional
from rich.text import Text
from rich.markdown import Markdown
from rich.console import Console

try:
    from ..markdown_renderer import get_markdown_renderer
    from ..frontier_colors import FRONTIER_COLORS
except (ImportError, ValueError):
    try:
        from markdown_renderer import get_markdown_renderer
        from frontier_colors import FRONTIER_COLORS
    except ImportError:
        def get_markdown_renderer():
            return None
        FRONTIER_COLORS = {}


class MarkdownProcessor:
    """Processes markdown text for display in streaming widget"""
    
    def __init__(self):
        self.renderer = get_markdown_renderer()
        self.console = Console(legacy_windows=False, force_terminal=True)
        
    def process_markdown(self, markdown_text: str) -> Text:
        """Process markdown text into Rich Text object"""
        if not markdown_text:
            return Text("")
            
        try:
            if self.renderer:
                # Use custom markdown renderer if available
                return self.renderer.render(markdown_text)
            else:
                # Fallback to Rich's built-in markdown
                markdown = Markdown(markdown_text)
                
                # Render to Text object
                with self.console.capture() as capture:
                    self.console.print(markdown)
                
                rendered_text = capture.get()
                return Text.from_ansi(rendered_text)
                
        except Exception:
            # If markdown processing fails, return plain text
            return Text(markdown_text)
            
    def is_markdown_content(self, text: str) -> bool:
        """Detect if text contains markdown formatting"""
        if not text:
            return False
            
        markdown_indicators = [
            '# ', '## ', '### ', '#### ', '##### ', '###### ',  # Headers
            '**', '__', '*', '_',  # Bold/italic
            '```', '`',  # Code blocks/inline code
            '[', '](', # Links
            '- ', '* ', '+ ',  # Lists
            '1. ', '2. ', '3. ',  # Numbered lists
            '> ',  # Blockquotes
            '|',  # Tables
            '---', '===',  # Horizontal rules
        ]
        
        return any(indicator in text for indicator in markdown_indicators)
        
    def extract_code_blocks(self, text: str) -> list:
        """Extract code blocks from markdown text"""
        code_blocks = []
        lines = text.split('\n')
        in_code_block = False
        current_block = []
        current_language = ""
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    code_blocks.append({
                        'language': current_language,
                        'code': '\n'.join(current_block)
                    })
                    current_block = []
                    current_language = ""
                    in_code_block = False
                else:
                    # Start of code block
                    current_language = line.strip()[3:].strip()
                    in_code_block = True
            elif in_code_block:
                current_block.append(line)
                
        return code_blocks
        
    def format_code_block(self, code: str, language: str = "") -> Text:
        """Format a code block with syntax highlighting"""
        try:
            from pygments import highlight
            from pygments.lexers import get_lexer_by_name, TextLexer
            from pygments.formatters import Terminal256Formatter
            
            if language:
                try:
                    lexer = get_lexer_by_name(language)
                except:
                    lexer = TextLexer()
            else:
                lexer = TextLexer()
                
            formatter = Terminal256Formatter(style='monokai')
            highlighted = highlight(code, lexer, formatter)
            return Text.from_ansi(highlighted)
            
        except ImportError:
            # Fallback without syntax highlighting
            code_style = f"color: {FRONTIER_COLORS.get('code', '#F8F8F2')} bgcolor: {FRONTIER_COLORS.get('code_bg', '#272822')}"
            return Text(code, style=code_style)
            
    def format_inline_code(self, text: str) -> Text:
        """Format inline code spans"""
        result = Text()
        parts = text.split('`')
        
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Regular text
                result.append(part)
            else:
                # Inline code
                code_style = f"color: {FRONTIER_COLORS.get('code', '#F8F8F2')} bgcolor: {FRONTIER_COLORS.get('code_bg', '#272822')}"
                result.append(part, style=code_style)
                
        return result
        
    def format_headers(self, text: str) -> Text:
        """Format markdown headers"""
        lines = text.split('\n')
        result = Text()
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                # Count header level
                level = 0
                for char in stripped:
                    if char == '#':
                        level += 1
                    else:
                        break
                        
                header_text = stripped[level:].strip()
                
                # Style based on header level
                if level == 1:
                    style = f"bold color: {FRONTIER_COLORS.get('header1', '#FF6B6B')}"
                elif level == 2:
                    style = f"bold color: {FRONTIER_COLORS.get('header2', '#4ECDC4')}"
                elif level == 3:
                    style = f"bold color: {FRONTIER_COLORS.get('header3', '#45B7D1')}"
                else:
                    style = f"bold color: {FRONTIER_COLORS.get('header', '#95E1D3')}"
                    
                result.append(header_text, style=style)
                result.append('\n')
            else:
                result.append(line + '\n')
                
        return result
        
    def format_emphasis(self, text: str) -> Text:
        """Format bold and italic text"""
        result = Text()
        
        # Simple regex-like processing for **bold** and *italic*
        chars = list(text)
        i = 0
        current_text = ""
        
        while i < len(chars):
            char = chars[i]
            
            if char == '*' and i + 1 < len(chars):
                if chars[i + 1] == '*':
                    # Bold text
                    if current_text:
                        result.append(current_text)
                        current_text = ""
                    
                    # Find closing **
                    j = i + 2
                    bold_text = ""
                    while j + 1 < len(chars):
                        if chars[j] == '*' and chars[j + 1] == '*':
                            break
                        bold_text += chars[j]
                        j += 1
                    
                    if j + 1 < len(chars):
                        result.append(bold_text, style="bold")
                        i = j + 2
                    else:
                        current_text += char
                        i += 1
                else:
                    # Italic text
                    if current_text:
                        result.append(current_text)
                        current_text = ""
                    
                    # Find closing *
                    j = i + 1
                    italic_text = ""
                    while j < len(chars):
                        if chars[j] == '*':
                            break
                        italic_text += chars[j]
                        j += 1
                    
                    if j < len(chars):
                        result.append(italic_text, style="italic")
                        i = j + 1
                    else:
                        current_text += char
                        i += 1
            else:
                current_text += char
                i += 1
                
        if current_text:
            result.append(current_text)
            
        return result