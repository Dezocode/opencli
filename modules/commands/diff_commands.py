"""Handlers for /diff commands - SDK COMPLIANT

SDK-COMPLIANT: All commands use interactive permission buffer pages.
User interaction happens in buffer, handlers execute based on selections.
"""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

# SDK-compliant imports only
from ..permission_prompt import PermissionResponse
# Legacy import removed - using unified_permission_manager via SDK executor


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


# ============================================================================
# /diff - Git status overview
# ============================================================================

def diff_overview_prompt(app, session, registration, context):
    """Interactive prompt for /diff command"""

    cwd = _session_cwd(session)

    prompt_data = {
        'title': 'System: /diff',
        'message': f"""# Git Status Overview

**Type:** Git status overview
**Working Directory:** {cwd}
**Command:** `git status --short`

**Select action:**""",
        'options': [
            {
                'text': 'View git status',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'view'}
            },
            {
                'text': 'Export to file',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'export'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def diff_overview(app, session, **context):
    """Show a high-level overview of working tree state - SDK COMPLIANT"""

    cwd = _session_cwd(session)

    # Get user selection
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    # Execute - run git status
    summary = await _run_command(["git", "status", "--short"], cwd)
    if not summary:
        summary = "Working tree clean."

    # Execute based on selection
    if action == 'view':
        app.write(f"[bold cyan]git status ({cwd})[/bold cyan]\n{summary}\n\n")

    elif action == 'export':
        export_path = Path.cwd() / "opencli-git-status.txt"
        with open(export_path, 'w') as f:
            f.write(f"Git Status - {cwd}\n")
            f.write("=" * 40 + "\n\n")
            f.write(summary + "\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# ============================================================================
# /diff git - Unified diff vs HEAD
# ============================================================================

def diff_git_prompt(app, session, registration, context):
    """Interactive prompt for /diff git command"""

    cwd = _session_cwd(session)

    prompt_data = {
        'title': 'System: /diff git',
        'message': f"""# Git Diff vs HEAD

**Type:** Unified diff vs HEAD
**Working Directory:** {cwd}
**Command:** `git diff`

**Select action:**""",
        'options': [
            {
                'text': 'View diff',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'view'}
            },
            {
                'text': 'Export to file',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'export'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def diff_git(app, session, **context):
    """Display unified diff against HEAD - SDK COMPLIANT"""

    cwd = _session_cwd(session)

    # Get user selection
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    # Execute - run git diff
    diff_output = await _run_command(["git", "diff"], cwd)
    if not diff_output:
        diff_output = "No changes relative to HEAD."

    # Execute based on selection
    if action == 'view':
        app.write(f"[bold cyan]git diff ({cwd})[/bold cyan]\n{diff_output}\n\n")

    elif action == 'export':
        export_path = Path.cwd() / "opencli-git-diff.txt"
        with open(export_path, 'w') as f:
            f.write(f"Git Diff - {cwd}\n")
            f.write("=" * 40 + "\n\n")
            f.write(diff_output + "\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# ============================================================================
# /diff worktree - Worktree comparison (placeholder)
# ============================================================================

def diff_worktree_prompt(app, session, registration, context):
    """Interactive prompt for /diff worktree command"""

    cwd = _session_cwd(session)

    prompt_data = {
        'title': 'System: /diff worktree',
        'message': f"""# Worktree Comparison

**Type:** Worktree comparison (not implemented)
**Working Directory:** {cwd}
**Status:** Feature placeholder

**Select action:**""",
        'options': [
            {
                'text': 'View placeholder info',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'view'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def diff_worktree(app, session, **context):
    """Placeholder for worktree comparisons - SDK COMPLIANT"""

    cwd = _session_cwd(session)

    # Get user selection
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    # Execute - show placeholder message
    if action == 'view':
        message = (
            "Worktree comparison is not yet implemented in the unified SDK.\n"
            "Use `/diff git` for repository changes or run custom scripts manually."
        )
        app.write(f"[bold cyan]Worktree Diff ({cwd})[/bold cyan]\n{message}\n\n")
