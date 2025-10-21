"""
Buffer Status Widget - Inline animated streaming status
Displays in chat area while AI is thinking/receiving tokens
Uses Frontier color palette for consistent UI
"""

from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.style import Style
import random

try:
    from .frontier_colors import FRONTIER_COLORS
except (ImportError, ValueError):
    from frontier_colors import FRONTIER_COLORS


class BufferStatusWidget(Static):
    """
    Inline widget showing streaming progress with animated spinner
    Replaces plain text status updates with proper UI component
    """

    # Reactive properties for live updates
    tokens_received = reactive(0)
    elapsed_seconds = reactive(0)
    is_receiving = reactive(True)
    is_interrupted = reactive(False)

    # Animation state
    _spinner_frame = 0
    _current_tip = ""

    # Braille spinner animation frames
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    # Tips to show while streaming
    TIPS = [
        "Use git worktrees to run multiple Claude sessions in parallel.",
        "Press ESC to interrupt long-running responses.",
        "Use /performance to monitor CPU and streaming metrics.",
        "Try /debug mode to see detailed API interaction logs.",
        "The /clear command resets conversation history.",
        "Markdown renders automatically - no need for code blocks.",
        "Tool execution happens automatically until completion.",
    ]

    DEFAULT_CSS = """
    BufferStatusWidget {
        height: auto;
        padding: 1 2;
        background: #0F1419;
        border: solid #1F2430;
        margin: 1 0;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_tip = random.choice(self.TIPS)

    def on_mount(self) -> None:
        """Start animation when widget mounts (200ms = 5 FPS, reduced from 10 FPS for CPU efficiency)"""
        self.set_interval(0.2, self._update_animation)

    def _update_animation(self) -> None:
        """Update spinner animation frame"""
        self._spinner_frame = (self._spinner_frame + 1) % len(self.SPINNER_FRAMES)
        self.update(self._render_status())

    def _render_status(self) -> Text:
        """Render the current status with spinner and tip - Frontier colors"""
        text = Text()

        # Get current spinner character
        spinner = self.SPINNER_FRAMES[self._spinner_frame]

        # Build status line with Frontier colors
        if self.is_interrupted:
            status = f"⏸ Interrupted (↓ {self.tokens_received} tokens received)"
            text.append(status, style=Style(color=FRONTIER_COLORS["warning"], bold=True))
        elif self.is_receiving:
            status = f"{spinner} Synthesizing… (esc to interrupt · {self.elapsed_seconds}s · ↓ {self.tokens_received} tokens)"
            text.append(status, style=Style(color=FRONTIER_COLORS["info"], bold=True))
        else:
            status = f"{spinner} Rendering… ({self.tokens_received} tokens · {self.elapsed_seconds}s)"
            text.append(status, style=Style(color=FRONTIER_COLORS["success"], bold=True))

        # Add tip on second line
        text.append("\n")
        text.append("  ⎿  Tip: ", style=Style(color=FRONTIER_COLORS["text_secondary"], dim=True))
        text.append(self._current_tip, style=Style(color=FRONTIER_COLORS["text_dim"]))

        return text

    def update_progress(self, tokens: int, elapsed: int) -> None:
        """Update progress metrics"""
        self.tokens_received = tokens
        self.elapsed_seconds = elapsed

    def mark_interrupted(self) -> None:
        """Mark as interrupted by user"""
        self.is_interrupted = True
        self.is_receiving = False

    def mark_rendering(self) -> None:
        """Mark as rendering (receiving complete)"""
        self.is_receiving = False

    def watch_tokens_received(self, new_value: int) -> None:
        """React to token count changes"""
        self.update(self._render_status())

    def watch_elapsed_seconds(self, new_value: int) -> None:
        """React to elapsed time changes"""
        self.update(self._render_status())

    def watch_is_receiving(self, new_value: bool) -> None:
        """React to receiving state changes"""
        self.update(self._render_status())

    def watch_is_interrupted(self, new_value: bool) -> None:
        """React to interrupt state changes"""
        self.update(self._render_status())
