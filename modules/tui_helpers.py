"""
TUI Helper Functions and Utilities
Provides helper functions for the TUI system
"""

from typing import Any, Optional, Dict, List
from textual.app import App
from textual.widgets import Static, Input
from textual.message import Message


class MultiLineInputStub:
    """Stub class for MultiLineInput when not available"""
    
    class ShowCommandSuggestions(Message):
        """Message for showing command suggestions"""
        def __init__(self, query: str):
            self.query = query
            super().__init__()
    
    class HideCommandSuggestions(Message):
        """Message for hiding command suggestions"""
        pass
    
    class UpdateSuggestions(Message):
        """Message for updating suggestions"""
        def __init__(self, suggestions):
            self.suggestions = suggestions
            super().__init__()
    
    class SubmitInput(Message):
        """Message for submitting input"""
        def __init__(self, text: str):
            self.text = text
            super().__init__()
    
    class Clear(Message):
        """Message for clearing input"""
        pass
    
    class CommandSuggestionNavigate(Message):
        """Message for navigating command suggestions"""
        def __init__(self, direction: str):
            self.direction = direction
            super().__init__()
    
    class CommandSuggestionSelect(Message):
        """Message for selecting a command suggestion"""
        def __init__(self, command: str):
            self.command = command
            super().__init__()
    
    class Focus(Message):
        """Message for focusing the input"""
        pass
    
    class Blur(Message):
        """Message for blurring the input"""
        pass
    
    class Submitted(Message):
        """Message for when input is submitted"""
        def __init__(self, text: str):
            self.text = text
            super().__init__()
    
    class Changed(Message):
        """Message for when input changes"""
        def __init__(self, text: str):
            self.text = text
            super().__init__()
    
    class CursorMove(Message):
        """Message for cursor movement"""
        def __init__(self, position: int):
            self.position = position
            super().__init__()


class StreamingDisplayStub(Static):
    """Stub for StreamingDisplay when not available"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = ""
    
    def append_chunk(self, chunk: str):
        """Append a chunk of text"""
        self.content += chunk
        self.update(self.content)
    
    def clear(self):
        """Clear the display"""
        self.content = ""
        self.update("")


def create_fallback_multiline():
    """Create a fallback multiline input widget"""
    return Input(placeholder="Type your message...")


def create_fallback_display():
    """Create a fallback streaming display"""
    return StreamingDisplayStub()


def handle_missing_import(module_name: str) -> Any:
    """
    Handle missing imports gracefully
    
    Args:
        module_name: Name of the missing module
        
    Returns:
        Stub object or None
    """
    stubs = {
        'MultiLineInput': MultiLineInputStub,
        'StreamingDisplay': StreamingDisplayStub,
        'CommandSuggestionBuffer': None,
        'SDKLoadingBuffer': None
    }
    
    return stubs.get(module_name)


class OpenCLITUIHelper:
    """Helper class for OpenCLI TUI functionality"""
    
    @staticmethod
    def create_input_widget(multiline: bool = True) -> Any:
        """Create an input widget with fallback"""
        try:
            from modules.multiline_input import MultiLineInput
            return MultiLineInput()
        except ImportError:
            return create_fallback_multiline()
    
    @staticmethod
    def create_output_widget() -> Any:
        """Create an output widget with fallback"""
        try:
            from modules.streaming_display import StreamingDisplay
            return StreamingDisplay()
        except ImportError:
            return create_fallback_display()
    
    @staticmethod
    def format_message(role: str, content: str) -> str:
        """Format a message for display"""
        if role == "user":
            return f"[cyan]>[/cyan] {content}"
        elif role == "assistant":
            return f"[green]🤖[/green] {content}"
        elif role == "system":
            return f"[yellow]⚠️[/yellow] {content}"
        else:
            return content
    
    @staticmethod
    def handle_user_input(text: str, session: Any) -> Dict[str, Any]:
        """Process user input and return action"""
        if text.startswith('/'):
            # It's a command
            parts = text.split(maxsplit=1)
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            
            return {
                'type': 'command',
                'command': command,
                'args': args
            }
        else:
            # Regular message
            return {
                'type': 'message',
                'content': text
            }
    
    @staticmethod
    def create_status_widget(session: Any, config: Dict[str, Any]) -> str:
        """Create a status line for the TUI"""
        model = session.model if hasattr(session, 'model') else config.get('model', 'unknown')
        session_id = session.session_id[:8] if hasattr(session, 'session_id') else 'unknown'
        
        return f"Session: {session_id} | Model: {model}"


# Export helper instance
tui_helper = OpenCLITUIHelper()