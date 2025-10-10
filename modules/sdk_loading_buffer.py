"""SDK Loading Buffer - Dropdown widget for module registration progress.

Shows registration progress in a dropdown above the prompt input,
similar to command suggestions.
"""

import asyncio
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.console import RenderableType


class SDKLoadingBuffer(Static):
    """Dropdown widget showing SDK module registration progress.

    Displays:
    - Loading animation
    - Registered command/tool counts
    - Enforcement stats (accepted, converted, rejected)
    - Latest module being processed
    """

    # Spinner frames (same as MultiLineInput)
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    # Reactive properties
    command_count: reactive[int] = reactive(0)
    tool_count: reactive[int] = reactive(0)
    accepted_count: reactive[int] = reactive(0)
    converted_count: reactive[int] = reactive(0)
    rejected_count: reactive[int] = reactive(0)
    latest_module: reactive[str] = reactive("")
    is_loading: reactive[bool] = reactive(False)
    spinner_frame: reactive[int] = reactive(0)

    def __init__(self, **kwargs):
        """Initialize SDK loading buffer."""
        super().__init__(**kwargs)
        self.command_count = 0
        self.tool_count = 0
        self.accepted_count = 0
        self.converted_count = 0
        self.rejected_count = 0
        self.latest_module = ""
        self.is_loading = False
        self.spinner_frame = 0
        self._spin_task = None

    def render(self) -> RenderableType:
        """Render the loading buffer with Frontier colors."""
        text = Text()

        # Title with animated spinner
        if self.is_loading:
            frame = self.SPINNER_FRAMES[self.spinner_frame % len(self.SPINNER_FRAMES)]
            text.append(f"{frame} ", style="cyan")
        else:
            text.append("✓ ", style="green")

        text.append("OpenCLI SDK - Module Registration\n", style="bold cyan")
        text.append("\n")

        # Registration counts
        text.append("Registered: ", style="dim")
        text.append(f"{self.command_count}", style="cyan")
        text.append(" commands, ", style="dim")
        text.append(f"{self.tool_count}", style="cyan")
        text.append(" tools\n", style="dim")
        text.append("\n")

        # Enforcement stats
        text.append("SDK Enforcement: ", style="dim")
        text.append(f"✓ {self.accepted_count}", style="green")
        text.append(" | ", style="dim")
        text.append(f"⚠ {self.converted_count}", style="yellow")
        text.append(" | ", style="dim")
        text.append(f"✗ {self.rejected_count}", style="red")
        text.append("\n")

        # Latest module
        if self.latest_module:
            text.append("\n")
            text.append("Latest: ", style="dim")
            text.append(self.latest_module, style="cyan")

        return text

    def update_progress(
        self,
        command_count: int,
        tool_count: int,
        accepted_count: int,
        converted_count: int,
        rejected_count: int,
        latest_module: str
    ) -> None:
        """Update registration progress.

        Args:
            command_count: Number of commands registered
            tool_count: Number of tools registered
            accepted_count: Number of modules accepted
            converted_count: Number of modules converted
            rejected_count: Number of modules rejected
            latest_module: Name of latest module processed
        """
        self.command_count = command_count
        self.tool_count = tool_count
        self.accepted_count = accepted_count
        self.converted_count = converted_count
        self.rejected_count = rejected_count
        self.latest_module = latest_module
        self.refresh()

    def start_loading(self) -> None:
        """Mark as loading and start spinner animation."""
        self.is_loading = True
        if self._spin_task is None or self._spin_task.done():
            self._spin_task = asyncio.create_task(self._spin())
        self.refresh()

    def stop_loading(self) -> None:
        """Mark as complete and stop spinner animation."""
        self.is_loading = False
        if self._spin_task and not self._spin_task.done():
            try:
                self._spin_task.cancel()
            except Exception:
                pass
        self._spin_task = None
        self.spinner_frame = 0
        self.refresh()

    async def _spin(self) -> None:
        """Async task that updates the spinner frame."""
        try:
            while self.is_loading:
                self.spinner_frame = (self.spinner_frame + 1) % len(self.SPINNER_FRAMES)
                self.refresh()
                await asyncio.sleep(0.08)  # 80ms per frame (same as MultiLineInput)
        except asyncio.CancelledError:
            pass

    def clear_data(self) -> None:
        """Clear all data."""
        self.command_count = 0
        self.tool_count = 0
        self.accepted_count = 0
        self.converted_count = 0
        self.rejected_count = 0
        self.latest_module = ""
        self.is_loading = False
        self.refresh()
