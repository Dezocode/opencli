"""
Core OpenCLI TUI application
Main TUI class with imports from modular components
"""

import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from textual.app import App
from textual.widgets import Static
from textual.containers import Vertical, Horizontal, Container
from textual.reactive import reactive

# Import ANSI background patches for terminal transparency
# This MUST happen before any widgets are created
try:
    from .. import ansi_background
except (ImportError, ValueError):
    try:
        import ansi_background
    except ImportError:
        pass  # Patches not available

# Import modular components
from .status_lines import PerformanceStatusLine, RefactoringStatusLine, StatusLine
from .permission_handlers import PermissionHandlers
from .command_handlers import CommandHandlers  
from .model_handlers import ModelHandlers

# Per-widget availability flags to avoid all-or-nothing gating
# CRITICAL: Import multiline_input.MultiLineInput FIRST - it has complete action_submit() with suggestions_active
try:
    from ..multiline_input import MultiLineInput
    HAS_MULTILINE = True
except Exception:
    try:
        from ..input_widget import MultiLineInput  # Fallback only
        HAS_MULTILINE = True
    except Exception:
        MultiLineInput = None
        HAS_MULTILINE = False

try:
    from ..command_suggestions import CommandSuggestionBuffer
    HAS_SUGGESTIONS = True
except Exception:
    CommandSuggestionBuffer = None
    HAS_SUGGESTIONS = False

try:
    from ..streaming_display import StreamingDisplay
    HAS_STREAMING = True
except Exception:
    StreamingDisplay = None
    HAS_STREAMING = False

try:
    from ..sdk_loading_buffer import SDKLoadingBuffer
    HAS_SDK_BUFFER = True
except Exception:
    SDKLoadingBuffer = None
    HAS_SDK_BUFFER = False

try:
    from ..frontier_colors import FRONTIER_COLORS, STATUS_COLORS
except Exception:
    FRONTIER_COLORS = {}
    STATUS_COLORS = {}

try:
    from ..tui_config import get_tui_config
except Exception:
    def get_tui_config():
        return None


class OpenCLITUI(App, PermissionHandlers, CommandHandlers, ModelHandlers):
    """Simple TUI with scrollable content and fixed prompt"""

    # Force ANSI colors mode and disable dark mode
    ENABLE_COMMAND_PALETTE = False

    # Global text selection state
    _selection_start = None
    _selection_end = None
    _is_selecting = False

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

    #prompt-container {
        height: auto;
        min-height: 3;
        max-height: 10;
        border: none;
        background: transparent;
    }

    #prompt-input {
        width: 1fr;
        height: auto;
        min-height: 3;
        max-height: 20;
        margin: 0;
        background: #151A21;
        border: round #3E4B59;
        padding: 0 1;
        color: #B3B1AD;
    }

    #prompt-input:focus {
        border: round #6B9E78;
    }

    #command-suggestions {
        height: auto;
        max-height: 8;
        background: $surface;
        border: solid $primary;
    }

    #command-suggestions.hidden {
        display: none;
    }

    #status-line {
        height: 1;
        background: transparent;
        border: none;
    }

    #performance-status {
        height: 1;
        background: transparent;
    }

    #refactoring-status {
        height: 1;
        background: transparent;
    }

    #sdk-loading-buffer {
        height: auto;
        max-height: 12;
        background: $surface;
        border: solid $primary;
    }

    #sdk-loading-buffer.hidden {
        display: none;
    }
    """

    def __init__(self, session, config):
        super().__init__()
        self.session = session
        self.config = config
        self.tui_config = get_tui_config()

        # Configure color mode for transparent backgrounds (BEFORE anything else)
        if self.tui_config:
            try:
                from ..color_manager import configure_color_mode
                color_mode = configure_color_mode(self.tui_config.config)
            except (ImportError, ValueError):
                try:
                    from color_manager import configure_color_mode
                    color_mode = configure_color_mode(self.tui_config.config)
                except ImportError:
                    pass  # Color manager not available

        # Disable dark mode for ANSI background transparency
        self.dark = False

        # Message handling
        self._write_queue = asyncio.Queue()
        self._write_task = None
        self._prompt_history = []
        self._history_index = -1

        # Status line references
        self.status_line = None
        self.performance_status = None
        self.refactoring_status = None

    def compose(self):
        """Compose the TUI layout"""
        with Vertical():
            # Scrollable content area with streaming support (dev6 structure)
            if HAS_STREAMING and StreamingDisplay:
                from textual.containers import VerticalScroll
                with VerticalScroll(id="content"):
                    yield StreamingDisplay(id="stream-display")
            else:
                yield Static("", id="content")

            # Command suggestions (hidden by default)
            if HAS_SUGGESTIONS and CommandSuggestionBuffer:
                yield CommandSuggestionBuffer(classes="hidden", id="command-suggestions")

            # SDK loading buffer (hidden by default)
            if HAS_SDK_BUFFER and SDKLoadingBuffer:
                yield SDKLoadingBuffer(classes="hidden", id="sdk-loading-buffer")

            # Prompt container
            with Container(id="prompt-container"):
                if HAS_MULTILINE and MultiLineInput:
                    yield MultiLineInput(
                        placeholder="Type your message...",
                        id="prompt-input"
                    )
                else:
                    yield Static("Input not available", id="prompt-input")

            # Status lines
            yield PerformanceStatusLine(self.session, id="performance-status")
            yield RefactoringStatusLine(self.session, id="refactoring-status")
            yield StatusLine(self.session, self.config, id="status-line")

    def on_mount(self) -> None:
        """Initialize the TUI when mounted"""
        # Store status line references
        self.status_line = self.query_one("#status-line", StatusLine)
        self.performance_status = self.query_one("#performance-status", PerformanceStatusLine)
        self.refactoring_status = self.query_one("#refactoring-status", RefactoringStatusLine)

        # Start write queue processor
        self._write_task = asyncio.create_task(self._process_write_queue())

        # Show ASCII art banner with session info
        stream_display = None
        try:
            stream_display = self.query_one("#stream-display", StreamingDisplay)
        except:
            # Fallback to content widget if stream-display not found
            try:
                content = self.query_one("#content")
                if StreamingDisplay is not None and isinstance(content, StreamingDisplay):
                    stream_display = content
            except:
                pass

        # Display welcome banner
        if stream_display is not None:
            welcome = f""" ██████╗ ██████╗ ███████╗███╗   ██╗     ██████╗██╗     ██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██╔════╝██║     ██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║     ██║     ██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██║     ██║     ██║
╚██████╔╝██║     ███████╗██║ ╚████║    ╚██████╗███████╗██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝     ╚═════╝╚══════╝╚═╝

Session: {self.session.session_id[:8]} | Ready
"""
            stream_display.write_line(welcome)

        # Focus the input
        try:
            prompt_input = self.query_one("#prompt-input")
            prompt_input.focus()
        except:
            pass

    def write(self, text: str, end: str = "\n") -> None:
        """Queue a write operation to prevent blocking"""
        try:
            self._write_queue.put_nowait((text, end))
        except asyncio.QueueFull:
            # If queue is full, process synchronously
            self._write_direct(text, end)

    def _write_direct(self, text: str, end: str = "\n") -> None:
        """Write directly to content widget"""
        try:
            content = self._resolve_content_widget()
            if hasattr(content, 'write'):
                content.write(text, end)
            else:
                # Fallback for basic Static widget
                current = content.renderable or ""
                content.update(current + text + end)
        except Exception as e:
            # Silent failure to prevent cascade errors
            pass

    async def _process_write_queue(self) -> None:
        """Process queued write operations"""
        try:
            while True:
                text, end = await self._write_queue.get()
                self._write_direct(text, end)
                # Small yield to keep UI responsive
                await asyncio.sleep(0)
        except asyncio.CancelledError:
            pass

    def _resolve_content_widget(self):
        """Resolve the content widget (StreamingDisplay or Static)"""
        try:
            # Try to get StreamingDisplay first (dev6 structure)
            return self.query_one("#stream-display")
        except:
            try:
                # Fallback to #content
                return self.query_one("#content")
            except:
                # Final fallback if query fails
                return Static("")

    async def _handle_user_message(self, user_input: str, prompt_input) -> None:
        """Handle user message submission"""
        # Add to history
        if user_input not in self._prompt_history:
            self._prompt_history.append(user_input)
        self._history_index = len(self._prompt_history)

        # Echo user input
        self.write(f"\n[cyan]>[/cyan] {user_input}\n")

        # ═══════════════════════════════════════════════════════════
        # CRITICAL: ALL commands MUST go through permission buffer FIRST
        # ═══════════════════════════════════════════════════════════
        if user_input.startswith('/'):
            try:
                # Import permission system
                from ..execution.permission_manager import get_permission_manager

                # Get permission manager (creates permission request automatically)
                permission_manager = get_permission_manager(self, self.session)

                # Create permission request for command
                command_name = user_input[1:].split()[0]
                command_args = ' '.join(user_input[1:].split()[1:]) if len(user_input[1:].split()) > 1 else None

                # Show command in permission buffer (non-blocking)
                self.write(f"[dim]Requesting permission: /{command_name}[/dim]\n")

                # Route through permission system → buffer → user approval → execution
                from ..command_router import route_command_unified
                handled = await route_command_unified(self, self.session, command_name, command_args)
                if handled:
                    return

            except Exception as e:
                self.write(f"[red]Command error: {e}[/red]\n")
                import traceback
                traceback.print_exc()
                return

        # Handle as regular message
        self.session.add('user', user_input)
        
        # Trigger AI response (this would be implemented based on your AI integration)
        await self._generate_ai_response()

    async def _generate_ai_response(self) -> None:
        """Generate AI response (placeholder - implement based on your AI integration)"""
        self.write("[dim]AI response generation not implemented in core TUI[/dim]\n")

    def action_quit_app(self) -> None:
        """Quit the application"""
        self.exit()

    def action_toggle_performance(self) -> None:
        """Toggle performance monitoring"""
        if self.performance_status:
            enabled = self.performance_status.toggle()
            status = "enabled" if enabled else "disabled"
            self.write(f"[dim]Performance monitoring {status}[/dim]\n")

    def action_toggle_refactoring(self) -> None:
        """Toggle refactoring monitoring"""
        if self.refactoring_status:
            enabled = self.refactoring_status.toggle()
            status = "enabled" if enabled else "disabled"
            self.write(f"[dim]Refactoring monitoring {status}[/dim]\n")

    def action_clear_screen(self) -> None:
        """Clear the screen content"""
        try:
            content = self._resolve_content_widget()
            if hasattr(content, 'clear'):
                content.clear()
            else:
                content.update("")
        except:
            pass

    # Navigation history methods
    def on_key(self, event) -> None:
        """Handle global key events"""
        # Handle Ctrl+C to quit
        if event.key == "ctrl+c":
            self.action_quit_app()
        # Handle Ctrl+L to clear screen
        elif event.key == "ctrl+l":
            self.action_clear_screen()
        # Handle F11 for performance toggle
        elif event.key == "f11":
            self.action_toggle_performance()
        # Handle F12 for refactoring toggle
        elif event.key == "f12":
            self.action_toggle_refactoring()

    # Utility methods for external integrations
    def show_sdk_status(self, message: str) -> None:
        """Show SDK initialization status"""
        if self.status_line:
            self.status_line.set_sdk_init_status(message)

    def clear_sdk_status(self) -> None:
        """Clear SDK initialization status"""
        if self.status_line:
            self.status_line.clear_sdk_init_status()

    def start_spinner(self, mode: str = "idle") -> None:
        """Start status line spinner"""
        if self.status_line:
            self.status_line.start_spinner(mode)

    def stop_spinner(self) -> None:
        """Stop status line spinner"""
        if self.status_line:
            self.status_line.stop_spinner()

    def enable_docker_stats(self, container_name: str = None) -> None:
        """Enable Docker stats in status line"""
        if self.status_line:
            self.status_line.enable_docker_stats(container_name)

    def disable_docker_stats(self) -> None:
        """Disable Docker stats in status line"""
        if self.status_line:
            self.status_line.disable_docker_stats()

    # Cleanup on exit
    async def on_unmount(self) -> None:
        """Clean up when app is unmounted"""
        if self._write_task and not self._write_task.done():
            self._write_task.cancel()
            try:
                await self._write_task
            except asyncio.CancelledError:
                pass