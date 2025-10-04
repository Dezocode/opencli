"""
Simple Textual TUI for OpenCLI
Provides scrollable content area with fixed prompt at bottom
"""

from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Static, Input, RichLog
from textual.reactive import reactive
from rich.text import Text
from rich.console import Console
from datetime import datetime
import os
import asyncio
import time

# Import custom modules - relative imports since we're in modules/ dir
try:
    from .tui_config import get_tui_config
    from .selectable_richlog import SelectableRichLog
    from .streaming_display import StreamingDisplay
    from .ansi_background import create_ansi_background_app
    CUSTOM_WIDGETS_AVAILABLE = True
except (ImportError, ValueError) as e:
    # ValueError for relative imports when run as script
    # Try absolute fallback
    try:
        from tui_config import get_tui_config
        from selectable_richlog import SelectableRichLog
        from streaming_display import StreamingDisplay
        from ansi_background import create_ansi_background_app
        CUSTOM_WIDGETS_AVAILABLE = True
    except ImportError as e2:
        CUSTOM_WIDGETS_AVAILABLE = False
        StreamingDisplay = None
        create_ansi_background_app = None
        print(f"Warning: Custom TUI widgets not available: {e2}")


class StatusLine(Static):
    """Fixed status line showing session info"""

    def __init__(self, session, config):
        super().__init__()
        self.session = session
        self.config = config

    def render(self) -> Text:
        """Render status bar"""
        now = datetime.now().strftime("%H:%M:%S")
        model_short = (self.session.model or self.config.get("model", "grok-4-fast")).split('/')[-1].split(':')[0]

        # Count tokens and turns
        try:
            # Estimate tokens (simple approximation: 1 token ≈ 4 chars)
            total_chars = sum(len(str(m.get('content', ''))) for m in self.session.messages)
            tokens = total_chars // 4
        except:
            tokens = 0

        turns = len([m for m in self.session.messages if m.get('role') == 'user'])
        cwd_short = os.path.basename(self.session.cwd)

        status = Text()
        status.append(" Model: ", style="dim")
        status.append(f"{model_short}", style="cyan")
        status.append(" │ Tokens: ", style="dim")
        status.append(f"{tokens:,}", style="magenta")
        status.append(" │ Turn: ", style="dim")
        status.append(f"{turns}", style="magenta")
        status.append(" │ CWD: ", style="dim")
        status.append(f"{cwd_short}", style="yellow")
        status.append(f" │ {now}", style="dim")
        return status


class OpenCLITUI(App):
    """Simple TUI with scrollable content and fixed prompt"""

    # Force ANSI colors mode and disable dark mode
    ENABLE_COMMAND_PALETTE = False

    CSS = """
    Screen {
        layout: vertical;
        background: $background;
    }

    #content {
        height: 1fr;
        border: solid #888888;
        border-title-align: left;
        background: $background;
        scrollbar-background: $panel;
        scrollbar-color: $primary;
    }

    VerticalScroll {
        background: $background;
    }

    #stream-display {
        background: $background;
        color: auto;
    }

    #footer {
        height: auto;
        dock: bottom;
        background: $background;
    }

    StatusLine {
        height: 1;
        padding: 0 1;
        background: $background;
        color: auto;
    }

    #prompt-container {
        height: auto;
        layout: horizontal;
        padding: 0 1;
        background: $background;
    }

    #prompt-label {
        width: auto;
        padding-right: 1;
    }

    #prompt-input {
        width: 1fr;
        background: $surface;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit_app", "Quit"),
        ("ctrl+d", "quit_app", "Quit"),
    ]

    def __init__(self, session, config):
        super().__init__()
        self.session = session
        self.config = config

        # Load TUI configuration
        if CUSTOM_WIDGETS_AVAILABLE:
            self.tui_config = get_tui_config()
        else:
            self.tui_config = None

        # Configure color mode BEFORE anything else
        if self.tui_config and CUSTOM_WIDGETS_AVAILABLE:
            try:
                from .color_manager import configure_color_mode
            except (ImportError, ValueError):
                from color_manager import configure_color_mode
            color_mode = configure_color_mode(self.tui_config.config)
            print(f"🎨 Color mode: {color_mode.value}")

        self.input_future = None
        self.should_exit = False
        self.message_handler = None  # Async callback for messages
        self.initial_prompt = None
        self._write_buffer = ""  # Buffer for streaming text

        # Configure laser effect from config
        if self.tui_config:
            self._laser_mode = self.tui_config.laser_enabled
            self._laser_colors = self.tui_config.laser_colors
            self._laser_intensity = self.tui_config.laser_intensity
        else:
            self._laser_mode = True
            self._laser_colors = ["#8B0000", "#FF4500", "#FFA500", "#FFFF00", "#FFFFFF"]
            self._laser_intensity = 1.0

        self._char_timestamps = []  # Track when each char was written
        self._streaming_active = False  # Track if currently streaming

        # Always disable dark mode for ANSI background mode
        self.dark = False

    def compose(self) -> ComposeResult:
        """Create TUI layout"""
        # Scrollable content area with streaming support
        if CUSTOM_WIDGETS_AVAILABLE and StreamingDisplay:
            # Use streaming display for laser effect - keep ID as "content"
            yield StreamingDisplay(id="content")
        elif CUSTOM_WIDGETS_AVAILABLE and self.tui_config and self.tui_config.get('text_selection.mode') == 'custom':
            yield SelectableRichLog(
                id="content",
                highlight=True,
                markup=True,
                wrap=True,
                auto_scroll=True,
            )
        else:
            yield RichLog(
                id="content",
                highlight=True,
                markup=True,
                wrap=True,
                auto_scroll=True,
            )

        # Fixed footer
        with Container(id="footer"):
            yield StatusLine(self.session, self.config)
            with Container(id="prompt-container"):
                yield Static("[green]│ > [/green]", id="prompt-label")
                yield Input(placeholder="Enter your message...", id="prompt-input")

    def on_mount(self) -> None:
        """Initialize"""
        # Get content widget - expect our implementation
        content = self.query_one("#content")

        # Configure if it's StreamingDisplay (check if class is available first)
        if StreamingDisplay is not None and isinstance(content, StreamingDisplay):
            content.set_laser_colors(self._laser_colors)
            content.set_laser_enabled(self._laser_mode)

            # Show welcome
            welcome = f""" ██████╗ ██████╗ ███████╗███╗   ██╗     ██████╗██╗     ██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██╔════╝██║     ██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║     ██║     ██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██║     ██║     ██║
╚██████╔╝██║     ███████╗██║ ╚████║    ╚██████╗███████╗██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝     ╚═════╝╚══════╝╚═╝

Session: {self.session.session_id[:8]} | Ready
"""
            content.write_line(welcome)
        else:
            # RichLog fallback
            content.border_title = f"OpenCLI - {self.session.session_id[:8]}"
            content.write(f"""[bold white] ██████╗ ██████╗ ███████╗███╗   ██╗     ██████╗██╗     ██╗[/bold white]
[bold white]██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██╔════╝██║     ██║[/bold white]
[bold white]██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║     ██║     ██║[/bold white]
[bold white]██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██║     ██║     ██║[/bold white]
[bold white]╚██████╔╝██║     ███████╗██║ ╚████║    ╚██████╗███████╗██║[/bold white]
[bold white] ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝     ╚═════╝╚══════╝╚═╝[/bold white]

[dim]Session: {self.session.session_id[:8]} | Ready[/dim]

""")

        # Focus input
        self.query_one("#prompt-input", Input).focus()

        # Process initial prompt if provided
        if self.initial_prompt and self.message_handler:
            self.call_later(self._process_initial_prompt)

    async def _process_initial_prompt(self):
        """Process initial prompt after mount"""
        if self.initial_prompt:
            # Write user prompt using our write method
            self.write(f"[green]You:[/green] {self.initial_prompt}\n\n")

            await self.message_handler(self.initial_prompt)
            self.initial_prompt = None

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input"""
        user_input = event.value.strip()

        if not user_input:
            return

        # Clear input
        event.input.value = ""

        # Show user message using write() - expects our implementation
        self.write(f"[green]You:[/green] {user_input}\n\n")

        # Call message handler if set
        if self.message_handler:
            await self.message_handler(user_input)
        # Otherwise resolve future (for compatibility)
        elif self.input_future and not self.input_future.done():
            self.input_future.set_result(user_input)

    def action_quit_app(self) -> None:
        """Quit"""
        self.should_exit = True
        if self.input_future and not self.input_future.done():
            self.input_future.set_exception(KeyboardInterrupt())
        self.exit()

    def write(self, text: str, end: str = "\n", style: str = None) -> None:
        """Write to content area with optional hot laser effect"""
        # Try to get streaming display widget first
        try:
            stream_display = self.query_one("#stream-display", StreamingDisplay)
            use_streaming = True
        except:
            stream_display = None
            use_streaming = False

        if use_streaming and stream_display:
            # Use streaming display with laser effect
            if end == "":
                # Streaming mode - write with pulsing laser
                stream_display.write_stream(text)
                self._streaming_active = True
            else:
                # End of streaming - finish and revert to default color
                stream_display.finish_stream()
                self._streaming_active = False

                # Write any final text
                if text and text.strip():
                    stream_display.write_line(text, style=style)
        else:
            # Fallback to RichLog or VerticalScroll
            try:
                content = self.query_one("#content", RichLog)
            except:
                try:
                    # Might be VerticalScroll with RichLog inside
                    content_container = self.query_one("#content")
                    content = content_container.query_one(RichLog)
                except:
                    content = self.query_one("#content")

            if end == "":
                # Streaming - accumulate
                self._write_buffer += text
                self._streaming_active = True
            else:
                # End - write buffered + new
                full_text = self._write_buffer + text
                self._write_buffer = ""
                self._streaming_active = False

                if full_text:
                    if style:
                        content.write(Text(full_text, style=style))
                    else:
                        content.write(full_text)

    def update_status(self) -> None:
        """Refresh status"""
        try:
            status = self.query_one(StatusLine)
            status.refresh()
        except:
            pass  # Status bar might not be mounted yet

    async def get_input(self) -> str:
        """Get user input (async)"""
        self.input_future = asyncio.Future()
        return await self.input_future


# Apply ANSI background support if available
if CUSTOM_WIDGETS_AVAILABLE and create_ansi_background_app:
    OpenCLITUI = create_ansi_background_app(OpenCLITUI)
