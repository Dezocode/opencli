"""
Basic command handlers exposed through the unified ExecutionSystem.

These handlers keep side effects minimal while providing clear feedback
inside the chat stream so users can understand the current session state
and available capabilities.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable

from command_registry import CommandRegistry
from execution.permission_manager import PermissionManager
from tool_permissions import ToolPermissionManager


def _feature_flags(session) -> Dict[str, bool]:
    """
    Derive feature flags from the current session when possible.

    Falls back to optimistic defaults so help/commands still display when
    feature metadata is unavailable.
    """
    session_flags = getattr(session, "feature_flags", None)
    if isinstance(session_flags, dict):
        return {
            "AGENT_SYSTEM": session_flags.get("AGENT_SYSTEM", True),
            "UPGRADE_SYSTEM": session_flags.get("UPGRADE_SYSTEM", True),
            "TOOL_PERMISSIONS": session_flags.get("TOOL_PERMISSIONS", True),
            "GITHUB_TOOL": session_flags.get("GITHUB_TOOL", True),
        }

    return {
        "AGENT_SYSTEM": True,
        "UPGRADE_SYSTEM": True,
        "TOOL_PERMISSIONS": True,
        "GITHUB_TOOL": True,
    }


async def show_help(app, session, **context):
    """Display categorized command overview."""
    registry = CommandRegistry()
    feature_flags = _feature_flags(session)

    categories: Dict[str, list] = {}
    for name, info in registry.get_all_commands().items():
        required = info.get("requires_feature")
        if required and not feature_flags.get(required, False):
            continue

        cat = info.get("category", "other")
        categories.setdefault(cat, []).append((name, info.get("description", "")))

    app.write("[bold cyan]Available Commands[/bold cyan]\n")
    for category in sorted(categories.keys()):
        app.write(f"\n[bold]{category.title()}[/bold]\n")
        for name, description in sorted(categories[category]):
            app.write(f"  [cyan]{name}[/cyan] - {description}\n")

    app.write("\nUse `/commands` to manage enable/disable status.\n")


async def show_status(app, session, **context):
    """Show current session metadata (model, agent, cwd, etc.)."""
    cwd = getattr(session, "cwd", Path.cwd())
    model = getattr(session, "model", getattr(session, "current_model", "unknown"))
    agent = getattr(session, "current_agent", "assistant")
    turn = getattr(session, "turn_counter", 0)
    start_time = getattr(session, "started_at", None)
    start_text = start_time if isinstance(start_time, str) else None
    if start_time and not isinstance(start_time, str):
        start_text = start_time.isoformat()

    app.write("[bold cyan]Session Status[/bold cyan]\n")
    app.write(f"  [cyan]Working dir:[/cyan] {cwd}\n")
    app.write(f"  [cyan]Model:[/cyan] {model}\n")
    app.write(f"  [cyan]Agent:[/cyan] {agent}\n")
    app.write(f"  [cyan]Turns:[/cyan] {turn}\n")
    if start_text:
        app.write(f"  [cyan]Started:[/cyan] {start_text}\n")
    app.write(f"  [cyan]Timestamp:[/cyan] {datetime.utcnow().isoformat()}Z\n")
    app.write("\n")


async def clear_history(app, session, **context):
    """Clear chat history from the UI and the in-memory session object."""
    if hasattr(session, "messages") and isinstance(session.messages, list):
        session.messages.clear()

    if hasattr(app, "stream_display") and app.stream_display:
        try:
            app.stream_display.clear()
        except Exception:
            pass

    app.write("[yellow]Chat history cleared for the current session.[/yellow]\n\n")


async def list_background_tasks(app, session, **context):
    """Show background tasks tracked on the session (if any)."""
    tasks: Iterable = getattr(session, "background_tasks", [])
    tasks = tasks or []

    app.write("[bold cyan]Background Tasks[/bold cyan]\n")
    if not tasks:
        app.write("[dim]No active background tasks.[/dim]\n\n")
        return

    for task in tasks:
        label = getattr(task, "label", str(task))
        status = getattr(task, "status", "running")
        app.write(f"  • {label} ([cyan]{status}[/cyan])\n")
    app.write("\n")


async def show_command_overview(app, session, **context):
    """Summarize enabled/disabled commands for the user."""
    registry = CommandRegistry()
    feature_flags = _feature_flags(session)

    enabled = registry.get_enabled_commands(feature_flags)
    disabled = sorted(
        set(registry.available_commands.keys()) - set(enabled)
    )

    app.write("[bold cyan]Command Permissions[/bold cyan]\n")
    app.write(f"[green]Enabled ({len(enabled)}):[/green]\n")
    for cmd in enabled:
        app.write(f"  [cyan]{cmd}[/cyan]\n")

    if disabled:
        app.write(f"\n[yellow]Disabled ({len(disabled)}):[/yellow]\n")
        for cmd in disabled:
            app.write(f"  [dim]{cmd}[/dim]\n")

    app.write("\nUse `/commands enable <command>` or `/commands disable <command>` from the classic CLI if needed.\n")


async def show_permissions(app, session, **context):
    """Display stored permission choices for commands and tools."""
    permission_manager = PermissionManager()
    tool_manager = ToolPermissionManager()

    allowed_commands = [
        item for item, allowed in permission_manager.allowed_items.items() if allowed
    ]
    allowed_tools = tool_manager.permissions.get("allowed_tools", [])

    app.write("[bold cyan]Stored Permissions[/bold cyan]\n")
    if allowed_commands:
        app.write("[green]Command approvals remembered:[/green]\n")
        for item in allowed_commands:
            app.write(f"  • {item}\n")
    else:
        app.write("[dim]No command approvals stored.[/dim]\n")

    if allowed_tools:
        app.write("\n[green]Tools allowed without prompts:[/green]\n")
        for tool in allowed_tools:
            app.write(f"  • {tool}\n")
    else:
        app.write("\n[dim]No tool approvals stored.[/dim]\n")

    if tool_manager.permissions.get("auto_accept"):
        app.write("\n[yellow]Global auto-accept mode is ENABLED.[/yellow]\n")

    app.write("\n")


async def exit_session(app, session, **context):
    """Exit the TUI application."""
    if hasattr(app, "action_quit_app"):
        app.action_quit_app()
        await asyncio.sleep(0)  # yield so shutdown can schedule
    else:
        app.exit()


# Alias quit to the same behaviour
quit_session = exit_session
