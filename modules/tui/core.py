"""
Core OpenCLI TUI application
Main TUI class with imports from modular components
"""

import os
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from textual.app import App
from textual.widgets import Static
from textual.containers import Vertical, Horizontal, Container
from textual.reactive import reactive

# Import ANSI background patches for terminal transparency
try:
    from ..ansi_background import *
except ImportError:
    try:
        import ansi_background
    except ImportError:
        pass  # Patches not available

# Import modular components
from .status_lines import PerformanceStatusLine, RefactoringStatusLine, StatusLine
from .permission_handlers import PermissionHandlers
from .command_handlers import CommandHandlers
from .model_handlers import ModelHandlers
from .message_handler_mixin import MessageHandlerMixin
from .response_generator_mixin import ResponseGeneratorMixin
from .action_mixin import ActionMixin

# Per-widget availability
# MODULAR VERSION: Use input_widget (refactored modular implementation)
try:
    from ..input_widget import MultiLineInput
    HAS_MULTILINE = True
except Exception:
    try:
        # Fallback to legacy monolithic version if modular fails
        from ..multiline_input import MultiLineInput
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
    from ..tui_config import get_tui_config
except ImportError:
    def get_tui_config():
        return None

# Set default colors
FRONTIER_COLORS = {
    'bg': '#1E1E2E',
    'fg': '#CDD6F4',
    'accent': '#89B8C2'
}
STATUS_COLORS = {
    'success': '#A6E3A1',
    'error': '#F38BA8',
    'warning': '#FAB387'
}


class OpenCLITUI(App, PermissionHandlers, CommandHandlers, ModelHandlers, MessageHandlerMixin, ResponseGeneratorMixin, ActionMixin):
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
        height: 100%;
        width: 100%;
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
        background: transparent;
        border: round #3E4B59;
        padding: 0 1;
        color: #B3B1AD;
    }

    #prompt-input:focus {
        border: round #6B9E78;
    }

    #command-suggestions {
        height: auto;
        max-height: 12;
        background: #1C232D;
        border: solid #89B8C2;
        padding: 1;
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
    """

    def __init__(self, session, config, client=None):
        super().__init__()
        self.session = session
        self.config = config
        self.client = client
        self.instance_id = uuid.uuid4()
        self.message_handler = None  # Will be set by the async shell

        # Safely get TUI config
        try:
            self.tui_config = get_tui_config()
        except Exception:
            self.tui_config = None

        # Configure color mode for transparent backgrounds
        if self.tui_config:
            try:
                from ..color_manager import configure_color_mode
                color_mode = configure_color_mode(self.tui_config.config)
            except (ImportError, ValueError):
                try:
                    from color_manager import configure_color_mode
                    color_mode = configure_color_mode(self.tui_config.config)
                except ImportError:
                    pass

        # Disable dark mode for ANSI background transparency
        self.dark = False

        # Message handling
        self._write_queue = asyncio.Queue()
        self._write_task = None
        self._prompt_history = []

        # Initialize unified permission system integration
        self._setup_permission_system()
        self._history_index = -1

        # Status line references
        self.status_line = None
        self.performance_status = None
        self.refactoring_status = None

    def _setup_permission_system(self) -> None:
        """Initialize unified permission system integration with TUI"""
        try:
            from ..permissions import get_unified_permission_manager

            self.permission_manager = get_unified_permission_manager()
            self.permission_manager.set_ui_callback(self._show_permission_prompt)

            # Register response handlers
            self.permission_manager.register_response_handler('file_operation', self._handle_file_operation_response)
            self.permission_manager.register_response_handler('bash_command', self._handle_bash_command_response)
            self.permission_manager.register_response_handler('api_operation', self._handle_api_operation_response)
            self.permission_manager.register_response_handler('tool_execution', self._handle_tool_execution_response)

        except ImportError as e:
            import sys
            sys.stderr.write(f"[TUI] Permission system integration failed: {e}\n")
            sys.stderr.flush()
            self.permission_manager = None

    def _handle_file_operation_response(self, response, data):
        """Handle file operation permission responses"""
        return True

    def _handle_bash_command_response(self, response, data):
        """Handle bash command permission responses"""
        return True

    def _handle_api_operation_response(self, response, data):
        """Handle API operation permission responses"""
        return True

    def _handle_tool_execution_response(self, response, data):
        """Handle tool execution permission responses"""
        return True

    def set_message_handler(self, handler):
        """Set the message handler coroutine for processing user input"""
        self.message_handler = handler
        import sys
        sys.stderr.write(f"[TUI] Message handler set: {handler}\n")
        sys.stderr.flush()

    def compose(self):
        """Compose the TUI layout"""
        import sys
        with open('/tmp/tui-trace.log', 'a') as f:
            f.write("[TUI.compose] ========== COMPOSE CALLED ==========\n")
        sys.stderr.write("[TUI.compose] 🔥🔥🔥 COMPOSE CALLED - BUILDING TUI LAYOUT 🔥🔥🔥\n")
        sys.stderr.flush()

        with Vertical():
            # Scrollable content area
            if HAS_STREAMING and StreamingDisplay:
                with open('/tmp/tui-trace.log', 'a') as f:
                    f.write(f"[TUI.compose] HAS_STREAMING={HAS_STREAMING}, StreamingDisplay={StreamingDisplay}\n")
                sys.stderr.write(f"[TUI.compose] HAS_STREAMING={HAS_STREAMING}, StreamingDisplay={StreamingDisplay}\n")
                sys.stderr.flush()
                from textual.containers import VerticalScroll
                with VerticalScroll(id="content"):
                    widget = StreamingDisplay(id="stream-display")
                    with open('/tmp/tui-trace.log', 'a') as f:
                        f.write(f"[TUI.compose] Created StreamingDisplay: {widget}\n")
                    yield widget
            else:
                with open('/tmp/tui-trace.log', 'a') as f:
                    f.write(f"[TUI.compose] NO STREAMING - creating Static (HAS_STREAMING={HAS_STREAMING}, StreamingDisplay={StreamingDisplay})\n")
                sys.stderr.write(f"[TUI.compose] NO STREAMING - creating Static\n")
                sys.stderr.flush()
                yield Static("", id="content")

            # Command suggestions (hidden by default)
            if HAS_SUGGESTIONS and CommandSuggestionBuffer:
                yield CommandSuggestionBuffer(classes="hidden", id="command-suggestions")

            # Prompt container
            with Container(id="prompt-container"):
                if HAS_MULTILINE and MultiLineInput:
                    yield MultiLineInput(placeholder="Type your message...", id="prompt-input")
                else:
                    yield Static("Input not available", id="prompt-input")

            # Status lines
            yield PerformanceStatusLine(self.session, id="performance-status")
            yield RefactoringStatusLine(self.session, id="refactoring-status")
            yield StatusLine(self.session, self.config, id="status-line")

    def on_mount(self) -> None:
        """Initialize the TUI when mounted"""
        import sys

        # ═══════════════════════════════════════════════════════════
        # CLEAR FOCUS LOG - Fresh start on each opencli TUI launch
        # ═══════════════════════════════════════════════════════════
        try:
            from ..focus_logger import clear_focus_log
            clear_focus_log()
            sys.stderr.write("[TUI.on_mount] ✅ Focus log cleared: /tmp/opencli_focus.log\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"[TUI.on_mount] ⚠️ Failed to clear focus log: {e}\n")
            sys.stderr.flush()

        try:
            with open('/tmp/tui-trace.log', 'a') as f:
                f.write("[TUI.on_mount] ========== ON_MOUNT CALLED ==========\n")
            sys.stderr.write("\n" + "="*80 + "\n")
            sys.stderr.write("[TUI.on_mount] 🔥🔥🔥 ON_MOUNT CALLED - THIS IS THE CORRECT modules/tui/core.py 🔥🔥🔥\n")
            sys.stderr.write("[TUI.on_mount] Module: " + __name__ + "\n")
            sys.stderr.write("="*80 + "\n")
            sys.stderr.flush()

            # Store status line references
            sys.stderr.write("[TUI.on_mount] Querying status lines...\n")
            sys.stderr.flush()
            self.status_line = self.query_one("#status-line", StatusLine)
            self.performance_status = self.query_one("#performance-status", PerformanceStatusLine)
            self.refactoring_status = self.query_one("#refactoring-status", RefactoringStatusLine)
            sys.stderr.write("[TUI.on_mount] Status lines found\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"[TUI.on_mount] ❌ EXCEPTION DURING MOUNT: {e}\n")
            import traceback
            traceback.print_exc()
            sys.stderr.flush()
            # Don't re-raise - let TUI continue

        # Start write queue processor
        self._write_task = asyncio.create_task(self._process_write_queue())

        # Start command router initialization
        sys.stderr.write(f"[TUI.on_mount] Checking for _init_command_router: {hasattr(self, '_init_command_router')}\n")
        sys.stderr.flush()

        if hasattr(self, '_init_command_router'):
            sys.stderr.write("[TUI.on_mount] ✓ _init_command_router found, creating background task\n")
            sys.stderr.flush()
            asyncio.create_task(self._init_command_router())
        else:
            sys.stderr.write("[TUI.on_mount] ✗ WARNING: _init_command_router NOT SET!\n")
            sys.stderr.flush()

        # Show ASCII art banner
        stream_display = None
        try:
            stream_display = self.query_one("#stream-display", StreamingDisplay)
        except:
            try:
                content = self.query_one("#content")
                if StreamingDisplay is not None and isinstance(content, StreamingDisplay):
                    stream_display = content
            except:
                pass

        # Display welcome banner
        with open('/tmp/tui-trace.log', 'a') as f:
            f.write(f"[TUI.on_mount] stream_display = {stream_display}\n")
        if stream_display is not None:
            version = "1.4.0"
            try:
                import json
                version_path = Path(__file__).parent.parent.parent / "version.json"
                if version_path.exists():
                    with open(version_path) as f:
                        version = json.load(f).get("version", "1.4.0")
            except:
                pass

            welcome = f""" ██████╗ ██████╗ ███████╗███╗   ██╗     ██████╗██╗     ██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██╔════╝██║     ██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║     ██║     ██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██║     ██║     ██║
╚██████╔╝██║     ███████╗██║ ╚████║    ╚██████╗███████╗██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝     ╚═════╝╚══════╝╚═╝

v{version} | Session: {self.session.session_id[:8]} | Ready
"""
            with open('/tmp/tui-trace.log', 'a') as f:
                f.write(f"[TUI.on_mount] Writing banner to stream_display\n")
            stream_display.write_line(welcome)
            with open('/tmp/tui-trace.log', 'a') as f:
                f.write(f"[TUI.on_mount] Banner written successfully\n")
        else:
            with open('/tmp/tui-trace.log', 'a') as f:
                f.write(f"[TUI.on_mount] stream_display is None - cannot show banner!\n")

        # Focus the input
        try:
            from ..focus_logger import log_focus_attempt
            prompt_input = self.query_one("#prompt-input")

            # Log focus attempt
            widget_type = type(prompt_input).__name__
            log_focus_attempt(
                source_file="tui/core.py",
                source_function="on_mount",
                method="widget.focus()",
                widget_type=widget_type,
                success=None,
                extra_info="Initial focus on TUI mount"
            )

            prompt_input.focus()

            # Log success
            log_focus_attempt(
                source_file="tui/core.py",
                source_function="on_mount",
                method="widget.focus()",
                widget_type=widget_type,
                success=True,
                extra_info=f"has_focus={prompt_input.has_focus}"
            )
        except Exception as e:
            from ..focus_logger import log_focus_attempt
            log_focus_attempt(
                source_file="tui/core.py",
                source_function="on_mount",
                method="widget.focus()",
                widget_type="unknown",
                success=False,
                error=str(e)
            )

    def write(self, text: str, end: str = "\n") -> None:
        """Queue a write operation to prevent blocking"""
        try:
            self._write_queue.put_nowait((text, end))
        except asyncio.QueueFull:
            self._write_direct(text, end)

    def _write_direct(self, text: str, end: str = "\n") -> None:
        """Write directly to content widget"""
        try:
            content = self._resolve_content_widget()
            if hasattr(content, 'write'):
                content.write(text, end)
            else:
                current = content.renderable or ""
                content.update(current + text + end)
        except Exception as e:
            pass

    async def _process_write_queue(self) -> None:
        """Process queued write operations"""
        try:
            while True:
                text, end = await self._write_queue.get()
                self._write_direct(text, end)
                await asyncio.sleep(0.01)  # 10ms - prevents busy-waiting while keeping UI responsive
        except asyncio.CancelledError:
            pass

    def _resolve_content_widget(self):
        """Resolve the content widget (StreamingDisplay or Static)"""
        try:
            return self.query_one("#stream-display")
        except:
            try:
                return self.query_one("#content")
            except:
                return Static("")

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
        import sys
        sys.stderr.write("\n[TUI] on_unmount called - starting cleanup\n")
        sys.stderr.flush()

        # Cancel write queue task
        if self._write_task and not self._write_task.done():
            self._write_task.cancel()
            try:
                await self._write_task
            except asyncio.CancelledError:
                pass

        # Stop all spinner tasks
        if self.status_line:
            self.status_line.stop_spinner()

        if self.performance_status:
            try:
                if hasattr(self.performance_status, 'stop_spinner'):
                    self.performance_status.stop_spinner()
            except Exception:
                pass

        if self.refactoring_status:
            try:
                if hasattr(self.refactoring_status, 'stop_spinner'):
                    self.refactoring_status.stop_spinner()
            except Exception:
                pass

        # Stop input widget spinner
        try:
            prompt_input = self.query_one("#prompt-input")
            if hasattr(prompt_input, 'stop_spinner'):
                prompt_input.stop_spinner()
        except Exception:
            pass

        # Stop streaming display
        try:
            stream_display = self.query_one("#stream-display")
            if hasattr(stream_display, 'cleanup'):
                stream_display.cleanup()
        except Exception:
            pass

        sys.stderr.write("[TUI] on_unmount cleanup complete\n")
        sys.stderr.flush()
