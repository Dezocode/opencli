"""Handlers for /diff commands."""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path


def _session_cwd(session) -> Path:
    if hasattr(session, "cwd") and session.cwd:
        return Path(session.cwd).expanduser()
    return Path.cwd()


async def _run_command(cmd: list[str], cwd: Path) -> str:
    def _runner() -> str:
        try:
            completed = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = completed.stdout or completed.stderr
            return output.strip()
        except FileNotFoundError:
            return "Required tooling (git) is not available on this system."
        except subprocess.TimeoutExpired:
            return "Diff command timed out after 30 seconds."
        except Exception as exc:
            return f"Error running {' '.join(cmd)}: {exc}"

    return await asyncio.to_thread(_runner)


async def diff_overview(app, session, **context):
    """Show a high-level overview of working tree state."""
    cwd = _session_cwd(session)
    summary = await _run_command(["git", "status", "--short"], cwd)
    if not summary:
        summary = "Working tree clean."
    app.write(f"[bold cyan]git status ({cwd})[/bold cyan]\n{summary}\n\n")


async def diff_git(app, session, **context):
    """Display unified diff against HEAD."""
    cwd = _session_cwd(session)
    diff_output = await _run_command(["git", "diff"], cwd)
    if not diff_output:
        diff_output = "No changes relative to HEAD."
    app.write(f"[bold cyan]git diff ({cwd})[/bold cyan]\n{diff_output}\n\n")


async def diff_worktree(app, session, **context):
    """Placeholder for worktree comparisons."""
    cwd = _session_cwd(session)
    message = (
        "Worktree comparison is not yet implemented in the unified SDK.\n"
        "Use `/diff git` for repository changes or run custom scripts manually."
    )
    app.write(f"[bold cyan]Worktree Diff ({cwd})[/bold cyan]\n{message}\n\n")
