"""
Simple Textual TUI for OpenCLI
Provides scrollable content area with fixed prompt at bottom
"""

from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Static, Input, RichLog, TextArea
from textual.reactive import reactive
from rich.text import Text
from datetime import datetime
import os
import asyncio
import time
import threading
from queue import Queue
from pathlib import Path

# Import custom multi-line input (with integrated spinner)
try:
    from .multiline_input import MultiLineInput
except (ImportError, ValueError):
    from multiline_input import MultiLineInput

# Import custom modules - relative imports since we're in modules/ dir
try:
    from .tui_config import get_tui_config
    from .selectable_richlog import SelectableRichLog
    from .streaming_display import StreamingDisplay
    from .ansi_background import create_ansi_background_app
    from .frontier_colors import FRONTIER_COLORS, STATUS_COLORS
    CUSTOM_WIDGETS_AVAILABLE = True
except (ImportError, ValueError) as e:
    # ValueError for relative imports when run as script
    # Try absolute fallback
    try:
        from tui_config import get_tui_config
        from selectable_richlog import SelectableRichLog
        from streaming_display import StreamingDisplay
        from ansi_background import create_ansi_background_app
        from frontier_colors import FRONTIER_COLORS, STATUS_COLORS
        CUSTOM_WIDGETS_AVAILABLE = True
    except ImportError as e2:
        CUSTOM_WIDGETS_AVAILABLE = False
        StreamingDisplay = None
        create_ansi_background_app = None
        FRONTIER_COLORS = {}
        STATUS_COLORS = {}
        print(f"Warning: Custom TUI widgets not available: {e2}")


class StatusLine(Static):
    """Fixed status line showing session info with IPC activity spinner"""

    is_spinning = reactive(False)
    spinner_frame = reactive(0)
    spinner_mode = reactive("idle")  # "idle", "read", "write"

    # Spinner frames
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, session, config):
        super().__init__()
        self.session = session
        self.config = config
        self._spin_task = None

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

        # Get IPC server status
        ipc_status = "off"
        subagent_count = 0
        if hasattr(self.session, 'ipc_server') and self.session.ipc_server:
            if self.session.ipc_server.running:
                subagent_count = self.session.ipc_server.get_subagent_count()
                ipc_status = str(subagent_count)

        status = Text()

        # Use frontier colors if available
        if FRONTIER_COLORS:
            status.append(" S: ", style=f"dim {STATUS_COLORS['time']}")

            # Show spinner when IPC is active, otherwise show count
            if self.is_spinning:
                frame = self.SPINNER_FRAMES[self.spinner_frame % len(self.SPINNER_FRAMES)]
                if self.spinner_mode == "read":
                    status.append(frame, style="#6B9E78")  # Frontier green/blue for read
                elif self.spinner_mode == "write":
                    status.append(frame, style="#9B86BD")  # Purple for write
                else:
                    status.append(frame, style="#89B8C2")  # Soft cyan default
            elif ipc_status == "off":
                status.append(f"{ipc_status}", style="#5C6773")  # Gray for off
            else:
                status.append(f"{ipc_status}", style="#89B8C2")  # Soft cyan for active
            status.append(" │ Model: ", style=f"dim {STATUS_COLORS['time']}")
            status.append(f"{model_short}", style=STATUS_COLORS['model'])
            status.append(" │ Tokens: ", style=f"dim {STATUS_COLORS['time']}")
            status.append(f"{tokens:,}", style=STATUS_COLORS['tokens'])
            status.append(" │ Turn: ", style=f"dim {STATUS_COLORS['time']}")
            status.append(f"{turns}", style=STATUS_COLORS['turn'])
            status.append(" │ CWD: ", style=f"dim {STATUS_COLORS['time']}")
            status.append(f"{cwd_short}", style=STATUS_COLORS['cwd'])
            status.append(f" │ {now}", style=STATUS_COLORS['time'])
        else:
            # Fallback to original colors
            status.append(" S: ", style="dim")
            status.append(f"{ipc_status}", style="dim" if ipc_status == "off" else "cyan")
            status.append(" │ Model: ", style="dim")
            status.append(f"{model_short}", style="cyan")
            status.append(" │ Tokens: ", style="dim")
            status.append(f"{tokens:,}", style="magenta")
            status.append(" │ Turn: ", style="dim")
            status.append(f"{turns}", style="magenta")
            status.append(" │ CWD: ", style="dim")
            status.append(f"{cwd_short}", style="yellow")
            status.append(f" │ {now}", style="dim")

        return status

    def start_spinner(self, mode: str = "idle") -> None:
        """Start the IPC activity spinner

        Args:
            mode: "read" (blue), "write" (purple), or "idle" (cyan)
        """
        self.spinner_mode = mode
        if not self.is_spinning:
            self.is_spinning = True
            if self._spin_task is None or self._spin_task.done():
                self._spin_task = asyncio.create_task(self._spin())

    def stop_spinner(self) -> None:
        """Stop the IPC activity spinner"""
        self.is_spinning = False
        if self._spin_task and not self._spin_task.done():
            try:
                self._spin_task.cancel()
            except Exception:
                pass
        self.spinner_frame = 0
        self.spinner_mode = "idle"
        self._spin_task = None
        self.refresh()

    async def _spin(self) -> None:
        """Async task that updates the spinner"""
        try:
            while self.is_spinning:
                self.spinner_frame = (self.spinner_frame + 1) % len(self.SPINNER_FRAMES)
                self.refresh()
                await asyncio.sleep(0.08)  # 80ms per frame
        except asyncio.CancelledError:
            pass

    def watch_is_spinning(self, old_value: bool, new_value: bool) -> None:
        """React to spinning state changes"""
        if old_value != new_value:
            self.refresh()

    def watch_spinner_frame(self, old_value: int, new_value: int) -> None:
        """React to frame changes - refresh already handled by _spin"""
        pass

    def watch_spinner_mode(self, old_value: str, new_value: str) -> None:
        """React to mode changes"""
        if old_value != new_value and self.is_spinning:
            self.refresh()


class OpenCLITUI(App):
    """Simple TUI with scrollable content and fixed prompt"""

    # Force ANSI colors mode and disable dark mode
    ENABLE_COMMAND_PALETTE = False

    CSS = """
    Screen {
        layout: vertical;
        background: transparent;
    }

    Container {
        background: transparent;
        border: none;
    }

    #content {
        height: 1fr;
        border: none;
        background: transparent;
        overflow-y: auto;
        scrollbar-size: 0 0;
    }

    VerticalScroll {
        background: transparent;
        height: 100%;
        overflow-y: auto;
        scrollbar-size: 0 0;
    }

    #stream-display {
        background: transparent;
        height: auto;
        min-height: 100%;
    }

    #footer {
        height: auto;
        dock: bottom;
        background: transparent;
        border: none;
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
        background: transparent;
        border: none;
    }

    #prompt-label {
        width: auto;
        height: 1;
        padding: 0;
        background: $background;
        color: auto;
    }

    Input {
        width: 1fr;
        height: 3;
        background: #151A21;
        border: round #3E4B59;
        padding: 0 1;
        color: #B3B1AD;
    }

    Input:focus {
        border: round #3E4B59;
    }

    MultiLineInput {
        width: 1fr;
        height: auto;
        min-height: 3;
        max-height: 10;
        margin: 0;
        background: #151A21;
        border: round #3E4B59;
        padding: 0 1;
        color: #B3B1AD;
    }

    MultiLineInput:focus {
        border: round #6B9E78;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit_app", "Quit"),
        ("ctrl+d", "quit_app", "Quit"),
    ]

    def __init__(self, session, config, ipc_server=None):
        super().__init__()
        self.session = session
        self.config = config
        self.ipc_server = ipc_server

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
            # Use frontier colors if available, otherwise fallback
            if FRONTIER_COLORS:
                try:
                    from .frontier_colors import FRONTIER_LASER_COLORS
                    self._laser_colors = FRONTIER_LASER_COLORS
                except (ImportError, ValueError):
                    from frontier_colors import FRONTIER_LASER_COLORS
                    self._laser_colors = FRONTIER_LASER_COLORS
            else:
                self._laser_colors = ["#3E4450", "#5C6773", "#7B91A3", "#89B8C2", "#B3B1AD"]
            self._laser_intensity = 1.0

        self._char_timestamps = []  # Track when each char was written
        self._streaming_active = False  # Track if currently streaming

        # Thread-safe queue for decoupling streaming writes from the UI thread
        self._write_queue_threadsafe = Queue()
        self._queue_thread = None
        self._stop_queue_thread = threading.Event()
        self._content_widget = None  # Output widget resolved on mount

        # Prompt history for up/down arrow navigation
        self._prompt_history = []
        self._history_index = -1
        self._load_prompt_history()

        # Always disable dark mode for ANSI background mode
        self.dark = False

    def compose(self) -> ComposeResult:
        """Create TUI layout"""
        # Scrollable content area with streaming support
        if CUSTOM_WIDGETS_AVAILABLE and StreamingDisplay:
            # Use streaming display wrapped in scrollable container
            with VerticalScroll(id="content"):
                yield StreamingDisplay(id="stream-display")
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
                # Multi-line input with integrated spinner
                yield MultiLineInput(id="prompt-input", placeholder="Type your message...")

    def on_mount(self) -> None:
        """Initialize"""
        # Start background queue processor thread
        self._start_queue_thread()

        # Try to get StreamingDisplay widget
        stream_display = None
        try:
            stream_display = self.query_one("#stream-display", StreamingDisplay)
        except:
            # Might be old structure
            try:
                content = self.query_one("#content")
                if StreamingDisplay is not None and isinstance(content, StreamingDisplay):
                    stream_display = content
            except:
                pass

        # Configure if it's StreamingDisplay
        if stream_display is not None:
            self._content_widget = stream_display
            stream_display.set_laser_colors(self._laser_colors)
            stream_display.set_laser_enabled(self._laser_mode)

            # Show welcome
            welcome = f""" ██████╗ ██████╗ ███████╗███╗   ██╗     ██████╗██╗     ██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██╔════╝██║     ██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║     ██║     ██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██║     ██║     ██║
╚██████╔╝██║     ███████╗██║ ╚████║    ╚██████╗███████╗██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝     ╚═════╝╚══════╝╚═╝

Session: {self.session.session_id[:8]} | Ready
"""
            stream_display.write_line(welcome)
        else:
            # RichLog fallback
            content = self.query_one("#content")
            self._content_widget = content
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
        self.query_one("#prompt-input", MultiLineInput).focus()

        # Process initial prompt if provided
        if self.initial_prompt and self.message_handler:
            self.call_later(self._process_initial_prompt)

    async def _process_initial_prompt(self):
        """Process initial prompt after mount"""
        if self.initial_prompt:
            # Write user prompt using our write method
            user_color = FRONTIER_COLORS.get('user_name', '#7B91A3') if FRONTIER_COLORS else 'green'
            text_color = FRONTIER_COLORS.get('text_secondary', '#5C6773') if FRONTIER_COLORS else 'dim'
            self.write(f"[{user_color}]You:[/{user_color}] [{text_color}]{self.initial_prompt}[/{text_color}]\n\n")

            await self.message_handler(self.initial_prompt)
            self.initial_prompt = None

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input from Input widget"""
        await self._handle_user_message(event.value.strip(), event.input)

    async def on_multi_line_input_submitted(self, event: MultiLineInput.Submitted) -> None:
        """Handle user input from MultiLineInput widget"""
        widget = self.query_one("#prompt-input", MultiLineInput)
        await self._handle_user_message(event.value.strip(), widget)

    async def _handle_user_message(self, user_input: str, widget) -> None:
        """Common handler for user messages"""
        if not user_input:
            return

        # Add to history
        self._add_to_history(user_input)

        # Clear input
        if isinstance(widget, MultiLineInput):
            widget.clear()
        else:
            widget.value = ""

        # Start spinner in the input widget
        try:
            prompt = self.query_one("#prompt-input", MultiLineInput)
            prompt.start_spinner()
        except Exception:
            pass

        # Get GitHub username if authenticated
        username = "You"
        try:
            import subprocess
            result = subprocess.run(
                ["gh", "api", "user", "--jq", ".login"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                username = result.stdout.strip()
        except:
            pass  # Fall back to "You"

        # Show user message with frontier colors
        user_color = FRONTIER_COLORS.get('user_name', '#7B91A3') if FRONTIER_COLORS else 'green'
        text_color = FRONTIER_COLORS.get('text_secondary', '#5C6773') if FRONTIER_COLORS else 'dim'
        self.write(f"[{user_color}]{username}:[/{user_color}] [{text_color}]{user_input}[/{text_color}]\n\n")

        # Call message handler if set
        if self.message_handler:
            await self.message_handler(user_input)
        # Otherwise resolve future (for compatibility)
        elif self.input_future and not self.input_future.done():
            self.input_future.set_result(user_input)

    def on_key(self, event) -> None:
        """Handle key presses for history navigation"""
        prompt = self.query_one("#prompt-input")

        # Up arrow - previous in history
        if event.key == "up":
            if self._prompt_history:
                if self._history_index == -1:
                    self._history_index = len(self._prompt_history) - 1
                elif self._history_index > 0:
                    self._history_index -= 1

                if isinstance(prompt, MultiLineInput):
                    prompt.value = self._prompt_history[self._history_index]
                    prompt.cursor_position = len(prompt.value)
                else:
                    prompt.value = self._prompt_history[self._history_index]
                event.prevent_default()
                event.stop()

        # Down arrow - next in history
        elif event.key == "down":
            if self._prompt_history and self._history_index >= 0:
                if self._history_index < len(self._prompt_history) - 1:
                    self._history_index += 1
                    if isinstance(prompt, MultiLineInput):
                        prompt.value = self._prompt_history[self._history_index]
                        prompt.cursor_position = len(prompt.value)
                    else:
                        prompt.value = self._prompt_history[self._history_index]
                else:
                    # At newest - clear input
                    self._history_index = -1
                    if isinstance(prompt, MultiLineInput):
                        prompt.clear()
                    else:
                        prompt.value = ""
                event.prevent_default()
                event.stop()

    def action_quit_app(self) -> None:
        """Quit and persist IPC server"""
        self.should_exit = True

        # Persist IPC server for 20 minutes
        if self.ipc_server and self.ipc_server.running:
            async def persist_ipc():
                await self.ipc_server.stop(persist=True)

            # Run persistence in event loop
            try:
                asyncio.create_task(persist_ipc())
            except Exception:
                pass  # Ignore if event loop is closing

        # Stop background thread
        self._stop_queue_thread.set()
        if self._queue_thread and self._queue_thread.is_alive():
            self._queue_thread.join(timeout=1.0)
        if self.input_future and not self.input_future.done():
            self.input_future.set_exception(KeyboardInterrupt())
        self.exit()

    def _start_queue_thread(self):
        """Start background thread to process write queue independently"""
        def queue_processor():
            """Background thread worker - batches writes to reduce UI blocking"""
            batch = []
            last_flush = time.time()

            while not self._stop_queue_thread.is_set():
                try:
                    # Get item from queue with timeout
                    text, end = self._write_queue_threadsafe.get(timeout=0.02)
                    batch.append((text, end))

                    # Flush batch if:
                    # 1. We have 10+ items OR
                    # 2. It's been 50ms since last flush OR
                    # 3. This is an end-of-stream marker
                    now = time.time()
                    should_flush = (
                        len(batch) >= 10 or
                        (now - last_flush) >= 0.05 or
                        end != ""
                    )

                    if should_flush and batch:
                        # Send batch to UI thread directly
                        self.call_from_thread(self._write_batch_to_richlog, list(batch))
                        batch.clear()
                        last_flush = now

                except:
                    # Timeout - flush any pending batch
                    if batch:
                        self.call_from_thread(self._write_batch_to_richlog, list(batch))
                        batch.clear()
                        last_flush = time.time()

        self._queue_thread = threading.Thread(target=queue_processor, daemon=True)
        self._queue_thread.start()

    def _load_prompt_history(self):
        """Load prompt history from file"""
        history_file = Path.home() / ".opencli" / "prompt_history.txt"
        if history_file.exists():
            try:
                with open(history_file) as f:
                    self._prompt_history = [line.strip() for line in f if line.strip()]
            except Exception:
                self._prompt_history = []

    def _save_prompt_history(self):
        """Save prompt history to file"""
        history_file = Path.home() / ".opencli" / "prompt_history.txt"
        try:
            with open(history_file, 'w') as f:
                # Save last 100 prompts
                for prompt in self._prompt_history[-100:]:
                    f.write(f"{prompt}\n")
        except Exception:
            pass

    def _add_to_history(self, prompt: str):
        """Add prompt to history"""
        if prompt and prompt.strip():
            # Avoid consecutive duplicates
            if not self._prompt_history or self._prompt_history[-1] != prompt:
                self._prompt_history.append(prompt)
                self._save_prompt_history()
        self._history_index = -1

    def stop_spinner(self):
        """Stop the activity spinner in input widget"""
        try:
            prompt = self.query_one("#prompt-input", MultiLineInput)
            prompt.stop_spinner()
        except Exception:
            pass

    def start_ipc_spinner(self, mode: str = "read"):
        """Start the IPC activity spinner in status line

        Args:
            mode: "read" (green/blue) or "write" (purple)
        """
        try:
            from textual.widgets import Static
            status = self.query_one(StatusLine)
            status.start_spinner(mode)
        except Exception:
            pass

    def stop_ipc_spinner(self):
        """Stop the IPC activity spinner in status line"""
        try:
            status = self.query_one(StatusLine)
            status.stop_spinner()
        except Exception:
            pass

    def _resolve_content_widget(self):
        """Find the active output widget (StreamingDisplay or RichLog)."""
        if self._content_widget and not getattr(self._content_widget, "is_destroyed", False):
            return self._content_widget

        # Prefer StreamingDisplay when custom widgets are available
        if CUSTOM_WIDGETS_AVAILABLE and StreamingDisplay is not None:
            try:
                self._content_widget = self.query_one("#stream-display", StreamingDisplay)
                return self._content_widget
            except Exception:
                pass

        # Fall back to whatever is mounted at #content (RichLog or similar)
        try:
            self._content_widget = self.query_one("#content")
        except Exception:
            self._content_widget = None

        return self._content_widget

    def _write_batch_to_richlog(self, batch: list):
        """Write a batch of text items to RichLog - called from background thread via call_from_thread"""
        try:
            content_widget = self._resolve_content_widget()
            if content_widget is None:
                return

            # Combine batch into single write to minimize UI blocking
            if StreamingDisplay is not None and isinstance(content_widget, StreamingDisplay):
                for text, end in batch:
                    if text:
                        # Use write_stream() ONLY if currently streaming (end is empty)
                        # Otherwise use write() to preserve Rich markup
                        if end == "":
                            content_widget.write_stream(text)
                        else:
                            # Not streaming - write with markup support
                            content_widget.write(text)

                    if end != "":
                        # Finish stream if we were streaming
                        if self._streaming_active:
                            content_widget.finish_stream()

                        # Write the end marker (newlines, etc)
                        if end.strip("\n"):
                            content_widget.write(end)
                        elif end:
                            # Just newlines - add them
                            content_widget.write(end)

                # Streaming is active only if the last batch item keeps the stream open
                self._streaming_active = not (batch and batch[-1][1] != "")
            else:
                combined_text = ""
                for text, end in batch:
                    combined_text += text
                    if end != "":
                        combined_text += end

                # Single write for entire batch
                if combined_text and hasattr(content_widget, "write"):
                    try:
                        renderable = Text.from_markup(combined_text)
                    except Exception:
                        renderable = combined_text

                    content_widget.write(renderable)

                    # Ensure the widget repaints after incremental updates
                    content_widget.refresh(layout=True)

                # Check if streaming ended (last item has non-empty end)
                if batch and batch[-1][1] != "":
                    self._streaming_active = False
                else:
                    self._streaming_active = True

            # Update streaming status
            self.update_status()
        except Exception:
            # Swallow rendering errors to avoid crashing the UI loop
            pass

    def write(self, text: str, end: str = "\n", style: str = None) -> None:
        """Queue write - returns instantly without blocking"""
        # Just queue it - background thread will process
        self._write_queue_threadsafe.put((text, end))
        # Returns immediately!

    def finish_stream(self) -> None:
        """Finish streaming and render markdown"""
        try:
            content = self._resolve_content_widget()
            if content and hasattr(content, 'finish_stream'):
                content.finish_stream()
        except Exception as e:
            pass  # Silently handle errors

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
