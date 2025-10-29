"""
Basic command handlers exposed through the unified ExecutionSystem.

SDK-COMPLIANT: All commands use interactive permission buffer pages.
User interaction happens in buffer, handlers execute based on selections.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable

# SDK-compliant imports only
from modules.permissions import PermissionResponse
# Legacy import removed - using unified_permission_manager via SDK executor


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


# =============================================================================
# /help - Display available commands
# ============================================================================

def show_help_prompt(app, session, registration, context):
    """Interactive prompt for /help command - shows options in buffer"""

    # Build interactive prompt
    prompt_data = {
        'title': 'System: /help',
        'message': """# Command Help

View all available OpenCLI commands and their descriptions.

**Select viewing option:**""",
        'options': [
            {
                'text': 'View all commands',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'view_all'}
            },
            {
                'text': 'View by category',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'view_by_category'}
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


async def show_help(app, session, **context):
    """Display categorized command overview - SDK COMPLIANT"""

    # Get user selection from permission buffer interaction (ALL commands use this now)
    command_selection = context.get('_command_selection', {})
    if not command_selection:
        if app:
            app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = command_selection.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    # Get command data from ExecutionRegistry (passed via context)
    registry = context.get('_registry')
    if not registry:
        app.write("[red]Error: Registry not available[/red]\n")
        return

    # Build categories
    categories: Dict[str, list] = {}
    for name, cmd_reg in registry.commands.items():
        cat = cmd_reg.category.value if hasattr(cmd_reg.category, 'value') else str(cmd_reg.category)
        desc = cmd_reg.description or "No description"
        categories.setdefault(cat, []).append((name, desc))

    # Execute based on selection
    if action == 'view_all' or action == 'view_by_category':
        app.write("[bold cyan]Available Commands[/bold cyan]\n")
        for category in sorted(categories.keys()):
            app.write(f"\n[bold]{category.title()}[/bold]\n")
            for name, description in sorted(categories[category]):
                app.write(f"  [cyan]{name}[/cyan] - {description}\n")
        app.write("\nUse `/commands` to manage command status.\n")

    elif action == 'export':
        export_path = Path.cwd() / "opencli-commands.txt"
        with open(export_path, 'w') as f:
            f.write("OpenCLI Available Commands\n")
            f.write("=" * 40 + "\n\n")
            for category in sorted(categories.keys()):
                f.write(f"\n{category.title()}\n")
                f.write("-" * 20 + "\n")
                for name, description in sorted(categories[category]):
                    f.write(f"{name} - {description}\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# =============================================================================
# /status - Show session information
# ============================================================================

def show_status_prompt(app, session, registration, context):
    """Interactive prompt for /status command"""

    # Gather status data
    cwd = getattr(session, "cwd", Path.cwd())
    model = getattr(session, "model", getattr(session, "current_model", "unknown"))
    agent = getattr(session, "current_agent", "assistant")
    turn = getattr(session, "turn_counter", 0)

    prompt_data = {
        'title': 'System: /status',
        'message': f"""# Session Status

**Model:** {model}
**Agent:** {agent}
**Working Directory:** {cwd}
**Turn Count:** {turn}

**Select action:**""",
        'options': [
            {
                'text': 'View full status',
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


async def show_status(app, session, **context):
    """Show current session metadata - SDK COMPLIANT"""

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

    # Gather status data
    cwd = getattr(session, "cwd", Path.cwd())
    model = getattr(session, "model", getattr(session, "current_model", "unknown"))
    agent = getattr(session, "current_agent", "assistant")
    turn = getattr(session, "turn_counter", 0)
    start_time = getattr(session, "started_at", None)
    start_text = start_time if isinstance(start_time, str) else None
    if start_time and not isinstance(start_time, str):
        start_text = start_time.isoformat()

    # Execute based on selection
    if action == 'view':
        app.write("[bold cyan]Session Status[/bold cyan]\n")
        app.write(f"  [cyan]Working dir:[/cyan] {cwd}\n")
        app.write(f"  [cyan]Model:[/cyan] {model}\n")
        app.write(f"  [cyan]Agent:[/cyan] {agent}\n")
        app.write(f"  [cyan]Turns:[/cyan] {turn}\n")
        if start_text:
            app.write(f"  [cyan]Started:[/cyan] {start_text}\n")
        app.write(f"  [cyan]Timestamp:[/cyan] {datetime.utcnow().isoformat()}Z\n")
        app.write("\n")

    elif action == 'export':
        export_path = Path.cwd() / "opencli-session-status.txt"
        with open(export_path, 'w') as f:
            f.write("OpenCLI Session Status\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Working Directory: {cwd}\n")
            f.write(f"Model: {model}\n")
            f.write(f"Agent: {agent}\n")
            f.write(f"Turn Count: {turn}\n")
            if start_text:
                f.write(f"Started: {start_text}\n")
            f.write(f"Timestamp: {datetime.utcnow().isoformat()}Z\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# =============================================================================
# /clear - Clear chat history (DESTRUCTIVE)
# ============================================================================

def clear_history_prompt(app, session, registration, context):
    """Interactive prompt for /clear command - DESTRUCTIVE"""

    # Count messages
    message_count = len(session.messages) if hasattr(session, "messages") and isinstance(session.messages, list) else 0

    prompt_data = {
        'title': 'System: /clear',
        'message': f"""# Clear Chat History

**⚠️ DESTRUCTIVE OPERATION**

This will permanently delete:
- {message_count} chat messages
- Conversation history
- Context for AI responses

**This action cannot be undone!**

**Confirm action:**""",
        'options': [
            {
                'text': 'Yes, clear all history',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'confirm', 'confirmed': True}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }

    return prompt_data


async def clear_history(app, session, **context):
    """Clear chat history - SDK COMPLIANT (DESTRUCTIVE)"""

    # Get user confirmation
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    if not user_selection.get('confirmed'):
        app.write("[yellow]Clear history cancelled[/yellow]\n")
        return

    # Execute destructive operation
    if hasattr(session, "messages") and isinstance(session.messages, list):
        session.messages.clear()

    if hasattr(app, "stream_display") and app.stream_display:
        try:
            app.stream_display.clear()
        except Exception:
            pass

    app.write("[yellow]Chat history cleared for the current session.[/yellow]\n\n")


# =============================================================================
# /bashes - List background tasks
# ============================================================================

def list_background_tasks_prompt(app, session, registration, context):
    """Interactive prompt for /bashes command"""

    tasks: Iterable = getattr(session, "background_tasks", [])
    tasks = tasks or []
    task_count = len(tasks)

    prompt_data = {
        'title': 'System: /bashes',
        'message': f"""# Background Tasks

**Active Tasks:** {task_count}
**Status:** {'No tasks running' if task_count == 0 else f'{task_count} tasks active'}

**Select action:**""",
        'options': [
            {
                'text': 'View task list',
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


async def list_background_tasks(app, session, **context):
    """Show background tasks tracked on the session - SDK COMPLIANT"""

    # Get user selection
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    if user_selection.get('action') != 'view':
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    # Execute - show tasks
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


# =============================================================================
# /commands - Show registered commands
# ============================================================================

def show_command_overview_prompt(app, session, registration, context):
    """Interactive prompt for /commands"""

    prompt_data = {
        'title': 'System: /commands',
        'message': """# Command Registry

View all registered commands in the execution system.

**Select action:**""",
        'options': [
            {
                'text': 'View all commands',
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


async def show_command_overview(app, session, **context):
    """Summarize registered commands - SDK COMPLIANT"""

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

    # Get commands from ExecutionRegistry (passed via context)
    registry = context.get('_registry')
    if not registry:
        app.write("[red]Error: Registry not available[/red]\n")
        return

    commands = list(registry.commands.keys())

    # Execute based on selection
    if action == 'view':
        app.write("[bold cyan]Registered Commands[/bold cyan]\n")
        app.write(f"[green]Total: {len(commands)}[/green]\n\n")
        for cmd in sorted(commands):
            app.write(f"  [cyan]{cmd}[/cyan]\n")
        app.write("\n")

    elif action == 'export':
        export_path = Path.cwd() / "opencli-registered-commands.txt"
        with open(export_path, 'w') as f:
            f.write("OpenCLI Registered Commands\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Total Commands: {len(commands)}\n\n")
            for cmd in sorted(commands):
                f.write(f"{cmd}\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# =============================================================================
# /permissions - Show stored permissions
# ============================================================================

def show_permissions_prompt(app, session, registration, context):
    """Interactive prompt for /permissions"""

    # Get permission data from SDK PermissionManager
    from modules.execution.permission_manager import get_permission_manager
    permission_manager = get_permission_manager(app, session)

    allowed_count = len(permission_manager.allowed_items)

    prompt_data = {
        'title': 'System: /permissions',
        'message': f"""# Stored Permissions

**Permanently Allowed:** {allowed_count} items

**Select action:**""",
        'options': [
            {
                'text': 'View all permissions',
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


async def show_permissions(app, session, **context):
    """Display stored permission choices - SDK COMPLIANT"""

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

    # Get permission data from SDK PermissionManager
    from modules.execution.permission_manager import get_permission_manager
    permission_manager = get_permission_manager(app, session)

    allowed_items = list(permission_manager.allowed_items.keys())

    # Execute based on selection
    if action == 'view':
        app.write("[bold cyan]Stored Permissions[/bold cyan]\n")
        if allowed_items:
            app.write(f"[green]Permanently allowed ({len(allowed_items)}):[/green]\n")
            for item in allowed_items:
                app.write(f"  • {item}\n")
        else:
            app.write("[dim]No permanently allowed items.[/dim]\n")
        app.write("\n")

    elif action == 'export':
        export_path = Path.cwd() / "opencli-permissions.txt"
        with open(export_path, 'w') as f:
            f.write("OpenCLI Stored Permissions\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Permanently Allowed ({len(allowed_items)}):\n")
            f.write("-" * 20 + "\n")
            if allowed_items:
                for item in allowed_items:
                    f.write(f"  • {item}\n")
            else:
                f.write("  (none)\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# =============================================================================
# /exit and /quit - Exit application (DESTRUCTIVE)
# ============================================================================

def exit_session_prompt(app, session, registration, context):
    """Interactive prompt for /exit command - DESTRUCTIVE"""

    # Count session activity
    message_count = len(session.messages) if hasattr(session, "messages") else 0

    prompt_data = {
        'title': 'System: /exit',
        'message': f"""# Exit OpenCLI

**⚠️ DESTRUCTIVE OPERATION**

This will terminate:
- Current OpenCLI session
- {message_count} chat messages in memory
- Active background tasks (if any)

**Unsaved work will be lost!**

**Confirm action:**""",
        'options': [
            {
                'text': 'Yes, exit now',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'exit', 'confirmed': True}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }

    return prompt_data


async def exit_session(app, session, **context):
    """Exit the TUI application - SDK COMPLIANT (DESTRUCTIVE)"""

    # Get user confirmation
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    if not user_selection.get('confirmed'):
        app.write("[yellow]Exit cancelled[/yellow]\n")
        return

    # Execute - exit application
    app.write("[cyan]Goodbye![/cyan]\n")
    await asyncio.sleep(0.1)  # Brief pause to show message

    if hasattr(app, "action_quit_app"):
        app.action_quit_app()
        await asyncio.sleep(0)  # yield so shutdown can schedule
    else:
        app.exit()


# Alias quit to the same behaviour
quit_session = exit_session
quit_session_prompt = exit_session_prompt