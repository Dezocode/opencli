"""Selectable RichLog fallback implementation.

This keeps API compatibility with the expected custom widget so the TUI
can enable text selection features when requested without importing
external files.
"""

from textual.widgets import RichLog


class SelectableRichLog(RichLog):
    """RichLog with selection enabled by default."""

    DEFAULT_CSS = """
    SelectableRichLog {
        border: none;
        background: $background;
        color: auto;
    }
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("markup", True)
        kwargs.setdefault("highlight", True)
        kwargs.setdefault("wrap", True)
        kwargs.setdefault("auto_scroll", True)
        super().__init__(*args, **kwargs)

    @property
    def can_focus(self) -> bool:  # type: ignore[override]
        return True
