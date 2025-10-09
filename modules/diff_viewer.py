"""Diff viewer widget for displaying code diffs in dropdown buffer.

This module provides an interactive diff viewing system that:
- Displays unified diffs with color-coded additions/deletions
- Supports arrow key navigation through diff hunks
- Shows context lines for clarity
- Integrates with Docker venv and worktree workflows
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from textual.widgets import Static
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.console import RenderableType

try:
    from .frontier_colors import FRONTIER_COLORS
except (ImportError, ValueError):
    from frontier_colors import FRONTIER_COLORS


@dataclass
class DiffHunk:
    """Represents a single diff hunk with context."""

    file_path: str
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: List[Tuple[str, str]]  # (type, content) where type is '+', '-', ' ', '@'

    def __repr__(self) -> str:
        return f"DiffHunk(file='{self.file_path}', lines={len(self.lines)})"


class DiffViewerWidget(Static):
    """Interactive diff viewer widget with keyboard navigation.

    This widget displays unified diffs with syntax highlighting,
    allowing navigation with arrow keys and selection with Enter.

    Attributes:
        hunks: List of DiffHunk objects to display
        selected_hunk: Currently selected hunk index
        scroll_offset: Vertical scroll offset for large diffs
        max_visible_lines: Maximum number of visible lines (default: 20)
    """

    # Reactive properties for automatic UI updates
    hunks: reactive[List[DiffHunk]] = reactive(list, init=False)
    selected_hunk: reactive[int] = reactive(0)
    scroll_offset: reactive[int] = reactive(0)
    max_visible_lines: reactive[int] = reactive(20)
    show_line_numbers: reactive[bool] = reactive(True)

    # Message types for communication with parent widgets
    class ShowDiff(Message):
        """Posted when diff should be displayed."""
        def __init__(self, hunks: List[DiffHunk]) -> None:
            self.hunks = hunks
            super().__init__()

    class HunkSelected(Message):
        """Posted when user selects a hunk with Enter."""
        def __init__(self, hunk: DiffHunk, index: int) -> None:
            self.hunk = hunk
            self.index = index
            super().__init__()

    class CloseDiff(Message):
        """Posted when diff should be hidden."""
        pass

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ) -> None:
        """Initialize the diff viewer widget.

        Args:
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.hunks = []
        self.selected_hunk = 0
        self.scroll_offset = 0
        self.max_visible_lines = 20
        self.show_line_numbers = True

    def render(self) -> RenderableType:
        """Render the diff viewer with Frontier colors.

        Returns:
            Rich Text object with formatted diff
        """
        if not self.hunks:
            text = Text()
            text.append("No diff to display\n", style="dim")
            text.append("Press Esc to close", style="dim italic")
            return text

        text = Text()

        # Header showing hunk count
        total_hunks = len(self.hunks)
        text.append(
            f"Diff Viewer ({total_hunks} file{'s' if total_hunks != 1 else ''})\n",
            style=f"bold {FRONTIER_COLORS['info']}"
        )
        text.append("─" * 80 + "\n", style=FRONTIER_COLORS['border'])

        # Render hunks
        line_count = 0
        for hunk_idx, hunk in enumerate(self.hunks):
            if line_count >= self.max_visible_lines:
                remaining = total_hunks - hunk_idx
                text.append(
                    f"\n... {remaining} more file{'s' if remaining != 1 else ''} (↓ to scroll)\n",
                    style="dim italic"
                )
                break

            # Hunk header with file path
            is_selected = (hunk_idx == self.selected_hunk)

            if is_selected:
                text.append("❯ ", style=f"bold {FRONTIER_COLORS['info']}")
            else:
                text.append("  ", style="")

            text.append(f"{hunk.file_path}", style="bold")
            text.append(
                f" @@ -{hunk.old_start},{hunk.old_count} +{hunk.new_start},{hunk.new_count} @@\n",
                style=FRONTIER_COLORS['text_secondary']
            )
            line_count += 1

            # Render diff lines
            for line_type, content in hunk.lines:
                if line_count >= self.max_visible_lines:
                    break

                # Indent diff content
                if is_selected:
                    text.append("  │ ", style=f"dim {FRONTIER_COLORS['info']}")
                else:
                    text.append("  │ ", style="dim")

                # Color-code based on line type
                if line_type == '+':
                    # Addition - green
                    text.append(f"+ {content}\n", style=FRONTIER_COLORS['success'])
                elif line_type == '-':
                    # Deletion - red
                    text.append(f"- {content}\n", style=FRONTIER_COLORS['error'])
                elif line_type == ' ':
                    # Context - dimmed
                    text.append(f"  {content}\n", style=FRONTIER_COLORS['text_dim'])
                elif line_type == '@':
                    # Hunk marker - cyan
                    text.append(f"@ {content}\n", style=FRONTIER_COLORS['info'])
                else:
                    # Unknown - default
                    text.append(f"{line_type} {content}\n", style="")

                line_count += 1

            # Add separator between hunks
            if hunk_idx < len(self.hunks) - 1 and line_count < self.max_visible_lines:
                text.append("  │\n", style="dim")
                line_count += 1

        # Footer with navigation hints
        text.append("─" * 80 + "\n", style=FRONTIER_COLORS['border'])
        text.append(
            "↑/↓: Navigate  Enter: Select  Esc: Close  c: Copy hunk\n",
            style=f"dim italic {FRONTIER_COLORS['text_secondary']}"
        )

        return text

    def set_hunks(self, hunks: List[DiffHunk]) -> None:
        """Set the diff hunks to display.

        Args:
            hunks: List of DiffHunk objects
        """
        self.hunks = hunks
        self.selected_hunk = 0
        self.scroll_offset = 0
        self.refresh()

    def navigate_up(self) -> None:
        """Move selection up one hunk."""
        if self.selected_hunk > 0:
            self.selected_hunk -= 1
            self.refresh()

    def navigate_down(self) -> None:
        """Move selection down one hunk."""
        if self.selected_hunk < len(self.hunks) - 1:
            self.selected_hunk += 1
            self.refresh()

    def select_current_hunk(self) -> None:
        """Select the currently highlighted hunk."""
        if self.hunks and 0 <= self.selected_hunk < len(self.hunks):
            hunk = self.hunks[self.selected_hunk]
            self.post_message(self.HunkSelected(hunk, self.selected_hunk))

    def close(self) -> None:
        """Close the diff viewer."""
        self.post_message(self.CloseDiff())


def parse_unified_diff(diff_text: str) -> List[DiffHunk]:
    """Parse unified diff format into DiffHunk objects.

    Args:
        diff_text: Unified diff text (output from git diff, diff -u, etc.)

    Returns:
        List of DiffHunk objects
    """
    hunks = []
    current_hunk = None
    current_file = None

    for line in diff_text.split('\n'):
        # File header
        if line.startswith('--- '):
            # Old file path
            continue
        elif line.startswith('+++ '):
            # New file path
            current_file = line[4:].split('\t')[0]  # Remove tab and timestamp
            if current_file.startswith('b/'):
                current_file = current_file[2:]
        # Hunk header
        elif line.startswith('@@'):
            if current_hunk:
                hunks.append(current_hunk)

            # Parse hunk range: @@ -old_start,old_count +new_start,new_count @@
            parts = line.split('@@')
            if len(parts) >= 2:
                ranges = parts[1].strip().split()
                old_range = ranges[0][1:].split(',')  # Remove leading '-'
                new_range = ranges[1][1:].split(',')  # Remove leading '+'

                old_start = int(old_range[0])
                old_count = int(old_range[1]) if len(old_range) > 1 else 1
                new_start = int(new_range[0])
                new_count = int(new_range[1]) if len(new_range) > 1 else 1

                current_hunk = DiffHunk(
                    file_path=current_file or 'unknown',
                    old_start=old_start,
                    old_count=old_count,
                    new_start=new_start,
                    new_count=new_count,
                    lines=[]
                )
        # Diff content
        elif current_hunk is not None:
            if line.startswith('+'):
                current_hunk.lines.append(('+', line[1:]))
            elif line.startswith('-'):
                current_hunk.lines.append(('-', line[1:]))
            elif line.startswith(' '):
                current_hunk.lines.append((' ', line[1:]))
            elif line.strip():  # Non-empty line without prefix
                current_hunk.lines.append((' ', line))

    # Add last hunk
    if current_hunk:
        hunks.append(current_hunk)

    return hunks


def git_diff_to_hunks(repo_path: str, ref1: str = 'HEAD', ref2: str = None) -> List[DiffHunk]:
    """Get diff hunks from git repository.

    Args:
        repo_path: Path to git repository
        ref1: First git reference (default: HEAD)
        ref2: Second git reference (default: working tree)

    Returns:
        List of DiffHunk objects
    """
    import subprocess

    try:
        if ref2:
            cmd = ['git', '-C', repo_path, 'diff', ref1, ref2]
        else:
            cmd = ['git', '-C', repo_path, 'diff', ref1]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return parse_unified_diff(result.stdout)
        else:
            return []
    except Exception:
        return []


def docker_venv_diff(container_id: str, venv_path: str, worktree_path: str) -> List[DiffHunk]:
    """Get diff between Docker venv and worktree.

    Args:
        container_id: Docker container ID
        venv_path: Path in container
        worktree_path: Local worktree path

    Returns:
        List of DiffHunk objects
    """
    import subprocess
    import tempfile

    try:
        # Copy file from container to temp location
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as tmp:
            tmp_path = tmp.name

        # Docker cp
        subprocess.run(
            ['docker', 'cp', f'{container_id}:{venv_path}', tmp_path],
            capture_output=True,
            timeout=10
        )

        # Run diff
        result = subprocess.run(
            ['diff', '-u', tmp_path, worktree_path],
            capture_output=True,
            text=True
        )

        # diff returns 1 for differences, 0 for identical, 2 for errors
        if result.returncode in [0, 1]:
            return parse_unified_diff(result.stdout)
        else:
            return []
    except Exception:
        return []
    finally:
        # Cleanup
        try:
            import os
            os.unlink(tmp_path)
        except:
            pass
