"""
Status line components for OpenCLI TUI
Performance, refactoring, and main status lines extracted from simple_tui.py
"""

import os
import asyncio
from datetime import datetime
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text

try:
    from ..frontier_colors import FRONTIER_COLORS, STATUS_COLORS
except (ImportError, ValueError):
    FRONTIER_COLORS = {}
    STATUS_COLORS = {}


class PerformanceStatusLine(Static):
    """Live performance monitoring statusline (bottom of screen)"""

    enabled = reactive(False)

    def __init__(self, session, **kwargs):
        super().__init__(**kwargs)
        self.session = session
        self._update_interval = None
        self.perf_monitor = None

    def on_mount(self) -> None:
        """Initialize performance monitor when mounted"""
        try:
            from ..performance_monitor import get_monitor
        except (ImportError, ValueError):
            from performance_monitor import get_monitor

        self.perf_monitor = get_monitor()
        self._update_interval = self.set_interval(2.0, self._update_display)

    def _update_display(self) -> None:
        """Periodic update callback - lightweight (2 sec)"""
        if self.enabled and self.perf_monitor and self.perf_monitor.enabled:
            self.refresh()

    def render(self) -> Text:
        """Render performance statusline"""
        if not self.enabled or not self.perf_monitor or not self.perf_monitor.enabled:
            return Text("")

        status_str = self.perf_monitor.get_status_line()
        if not status_str:
            return Text("")

        try:
            return Text.from_markup(status_str)
        except:
            return Text(status_str)

    def toggle(self) -> bool:
        """Toggle performance monitoring on/off, returns new state"""
        if self.perf_monitor:
            if self.perf_monitor.enabled:
                self.perf_monitor.stop()
                self.enabled = False
            else:
                self.perf_monitor.start()
                self.enabled = True
            self.refresh()
            return self.enabled
        return False


class RefactoringStatusLine(Static):
    """Live refactoring system statusline (bottom of screen)"""

    enabled = reactive(False)

    def __init__(self, session, **kwargs):
        super().__init__(**kwargs)
        self.session = session
        self._update_interval = None
        self.orchestrator = None

    def on_mount(self) -> None:
        """Initialize refactoring orchestrator when mounted"""
        try:
            from ..refactor_orchestrator import get_orchestrator
        except (ImportError, ValueError):
            try:
                from refactor_orchestrator import get_orchestrator
            except ImportError:
                return

        try:
            self.orchestrator = get_orchestrator()
        except Exception:
            pass

        self._update_interval = self.set_interval(2.0, self._update_display)

    def _update_display(self) -> None:
        """Periodic update callback - lightweight (2 sec)"""
        if self.enabled and self.orchestrator and self.orchestrator._monitoring:
            self.refresh()

    def render(self) -> Text:
        """Render refactoring statusline"""
        if not self.enabled or not self.orchestrator or not self.orchestrator._monitoring:
            return Text("")

        status_str = self.orchestrator.get_status_line()
        if not status_str:
            return Text("")

        try:
            return Text.from_markup(status_str)
        except:
            return Text(status_str)

    def toggle(self) -> bool:
        """Toggle refactoring monitoring on/off, returns new state"""
        if self.orchestrator:
            if self.orchestrator._monitoring:
                self.orchestrator.stop_monitoring()
                self.enabled = False
            else:
                self.orchestrator.start_monitoring()
                self.enabled = True
            self.refresh()
            return self.enabled
        return False


class StatusLine(Static):
    """Fixed status line showing session info with IPC activity spinner and Docker stats"""

    is_spinning = reactive(False)
    spinner_frame = reactive(0)
    spinner_mode = reactive("idle")
    show_docker_stats = reactive(False)
    docker_cpu_percent = reactive("0")
    docker_memory_usage = reactive("0MB")
    sdk_init_message = reactive(None)

    # Spinner frames
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, session, config, **kwargs):
        super().__init__(**kwargs)
        self.session = session
        self.config = config
        self._spin_task = None
        self._docker_stats_task = None

    def render(self) -> Text:
        """Render status bar"""
        status = Text()

        # Show SDK initialization status if active
        if self.sdk_init_message:
            if self.is_spinning and self.spinner_mode == "sdk_init":
                frame = self.SPINNER_FRAMES[self.spinner_frame % len(self.SPINNER_FRAMES)]
                status.append(f" {frame} ", style="#89B8C2" if FRONTIER_COLORS else "cyan")
            status.append(self.sdk_init_message, style="#89B8C2" if FRONTIER_COLORS else "cyan bold")
            return status

        # Normal status display
        now = datetime.now().strftime("%H:%M:%S")
        model_short = (self.session.model or self.config.get("model", "grok-4-fast")).split('/')[-1].split(':')[0]

        # Count tokens and turns
        try:
            total_chars = sum(len(str(m.get('content', ''))) for m in self.session.messages)
            tokens = total_chars // 4
        except:
            tokens = 0

        turns = len([m for m in self.session.messages if m.get('role') == 'user'])
        cwd_short = os.path.basename(self.session.cwd)

        # Get IPC server status
        ipc_status = "off"
        if hasattr(self.session, 'ipc_server') and self.session.ipc_server:
            if self.session.ipc_server.running:
                subagent_count = self.session.ipc_server.get_subagent_count()
                ipc_status = str(subagent_count)

        # Use frontier colors if available
        if FRONTIER_COLORS:
            status.append(" S: ", style=f"dim {STATUS_COLORS['time']}")

            # Show spinner when IPC is active
            if self.is_spinning:
                frame = self.SPINNER_FRAMES[self.spinner_frame % len(self.SPINNER_FRAMES)]
                if self.spinner_mode == "read":
                    status.append(frame, style="#6B9E78")
                elif self.spinner_mode == "write":
                    status.append(frame, style="#9B86BD")
                else:
                    status.append(frame, style="#89B8C2")
            elif ipc_status == "off":
                status.append(f"{ipc_status}", style="#5C6773")
            else:
                status.append(f"{ipc_status}", style="#89B8C2")

            status.append(" │ Model: ", style=f"dim {STATUS_COLORS['time']}")
            status.append(f"{model_short}", style=STATUS_COLORS['model'])
            status.append(" │ Tokens: ", style=f"dim {STATUS_COLORS['time']}")
            status.append(f"{tokens:,}", style=STATUS_COLORS['tokens'])
            status.append(" │ Turn: ", style=f"dim {STATUS_COLORS['time']}")
            status.append(f"{turns}", style=STATUS_COLORS['turn'])
            status.append(" │ CWD: ", style=f"dim {STATUS_COLORS['time']}")
            status.append(f"{cwd_short}", style=STATUS_COLORS['cwd'])

            # Docker stats if enabled
            if self.show_docker_stats:
                status.append(" │ 🐳 ", style=f"dim {STATUS_COLORS['time']}")
                status.append(f"CPU: {self.docker_cpu_percent}%", style=STATUS_COLORS['tokens'])
                status.append(" │ ", style="dim")
                status.append(f"Mem: {self.docker_memory_usage}", style=STATUS_COLORS['tokens'])

            status.append(f" │ {now}", style=STATUS_COLORS['time'])
        else:
            # Fallback colors
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
        """Start the IPC activity spinner"""
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

    def set_sdk_init_status(self, message: str) -> None:
        """Set SDK initialization status message and start spinner"""
        self.sdk_init_message = message
        self.start_spinner("sdk_init")
        self.refresh()

    def clear_sdk_init_status(self) -> None:
        """Clear SDK initialization status and stop spinner"""
        self.sdk_init_message = None
        self.stop_spinner()
        self.refresh()

    async def _spin(self) -> None:
        """Async task that updates the spinner"""
        try:
            while self.is_spinning:
                self.spinner_frame = (self.spinner_frame + 1) % len(self.SPINNER_FRAMES)
                self.refresh()
                await asyncio.sleep(0.08)
        except asyncio.CancelledError:
            pass

    def enable_docker_stats(self, container_name: str = None) -> None:
        """Enable Docker stats monitoring in statusline"""
        if not self.show_docker_stats:
            self.show_docker_stats = True
            if self._docker_stats_task is None or self._docker_stats_task.done():
                self._docker_stats_task = asyncio.create_task(
                    self._update_docker_stats(container_name or "opencli-ollama")
                )

    def disable_docker_stats(self) -> None:
        """Disable Docker stats monitoring"""
        self.show_docker_stats = False
        if self._docker_stats_task and not self._docker_stats_task.done():
            try:
                self._docker_stats_task.cancel()
            except Exception:
                pass
        self._docker_stats_task = None
        self.refresh()

    async def _update_docker_stats(self, container_name: str) -> None:
        """Async task that periodically updates Docker container stats"""
        try:
            from ..docker_manager import DockerManager
        except (ImportError, ValueError):
            from docker_manager import DockerManager

        docker_mgr = DockerManager()

        try:
            while self.show_docker_stats:
                stats = await asyncio.to_thread(
                    docker_mgr.get_container_stats,
                    container_name
                )

                if stats:
                    self.docker_cpu_percent = stats.get('cpu_percent', '0')
                    self.docker_memory_usage = stats.get('memory_usage', '0MB').split('/')[0].strip()
                else:
                    self.docker_cpu_percent = "N/A"
                    self.docker_memory_usage = "N/A"
                
                self.refresh()
                await asyncio.sleep(2.0)

        except asyncio.CancelledError:
            pass
        except Exception:
            self.docker_cpu_percent = "ERR"
            self.docker_memory_usage = "ERR"
            self.refresh()

    def show_indicator(self, category: str, icon: str, color: str) -> None:
        """Show a contextual indicator in the statusline"""
        if icon == "⋯":
            self.start_spinner("idle")
        elif icon == "✓":
            self.stop_spinner()
        elif icon == "✗":
            self.stop_spinner()

    def hide_indicator(self, category: str) -> None:
        """Hide a contextual indicator in the statusline"""
        self.stop_spinner()