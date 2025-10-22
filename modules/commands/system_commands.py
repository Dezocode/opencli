"""System Commands - SDK COMPLIANT

SDK-COMPLIANT: All commands use interactive permission buffer pages.
User interaction happens in buffer, handlers execute based on selections.
"""

# SDK-compliant imports only
from ..permission_prompt import PermissionResponse
# Legacy import removed - using unified_permission_manager via SDK executor


# ============================================================================
# /restart - Restart OpenCLI with current session
# ============================================================================

def restart_session_prompt(app, session, registration, context):
    """Interactive prompt for /restart command"""

    prompt_data = {
        'title': 'System: /restart',
        'message': """# Restart OpenCLI

**Action:** Restart OpenCLI and reload all modules
**Session:** Will be saved and resumed

**Affected:**
- Current TUI session
- All running background tasks
- Unsaved in-memory state

**Warning:** The session will be saved but may disconnect briefly!

**Confirm restart:**""",
        'options': [
            {
                'text': 'Yes, restart OpenCLI',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'restart', 'confirmed': True}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def restart_session(app, session, **context):
    """Restart OpenCLI with the current session - SDK COMPLIANT"""
    import asyncio
    import sys
    import os

    # Get user selection
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')
    confirmed = user_selection.get('confirmed', False)

    if not action or not confirmed:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    # Execute - restart session
    app.write("[cyan]🔄 Restarting OpenCLI...[/cyan]\n\n")

    try:
        # Keep IPC server alive by enabling persistence
        if hasattr(session, 'ipc_server') and session.ipc_server and session.ipc_server.running:
            # Enable persistence mode (20 min timeout)
            async def persist_server():
                await session.ipc_server.stop(persist=True)

            try:
                asyncio.create_task(persist_server())
                app.write("[dim]✓ IPC server will remain active for 20 minutes[/dim]\n")
            except Exception:
                pass

        # Save current session (non-blocking)
        await asyncio.to_thread(session.save)
        app.write("[dim]✓ Session saved[/dim]\n\n")

        # Get the OpenCLI command path
        opencli_path = os.path.expanduser("~/bin/opencli")

        # Prepare restart command that will resume this session
        restart_cmd = f"{opencli_path} --resume {session.session_id}"

        app.write(f"[green]Restarting with session {session.session_id[:8]}...[/green]\n\n")

        # Use os.execv to replace the current process
        # This maintains the shell and restarts OpenCLI
        os.execv(sys.executable, [sys.executable, opencli_path, '--resume', session.session_id])

    except Exception as e:
        app.write(f"[red]✗ Restart failed: {e}[/red]\n\n")
        import traceback
        app.write(f"[dim]{traceback.format_exc()}[/dim]\n\n")


# ============================================================================
# /upgrade - Reload OpenCLI modules
# ============================================================================

def upgrade_opencli_prompt(app, session, registration, context):
    """Interactive prompt for /upgrade command"""
    import sys

    modules_to_reload = [
        'simple_tui', 'streaming_display', 'frontier_colors',
        'markdown_renderer', 'async_interactive', 'opencli_ipc', 'model_manager'
    ]
    loaded_count = len([m for m in modules_to_reload if m in sys.modules])

    prompt_data = {
        'title': 'System: /upgrade',
        'message': f"""# Reload Modules

**Action:** Reload {len(modules_to_reload)} core OpenCLI modules
**Currently Loaded:** {loaded_count} modules

**Confirm action:**""",
        'options': [
            {
                'text': 'Reload modules',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'upgrade'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def upgrade_opencli(app, session, **context):
    """Reload OpenCLI modules - SDK COMPLIANT"""
    import importlib
    import sys

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

    # List of modules to reload
    modules_to_reload = [
        'simple_tui', 'streaming_display', 'frontier_colors',
        'markdown_renderer', 'async_interactive', 'opencli_ipc', 'model_manager'
    ]

    # Execute - reload modules
    app.write("[cyan]🔄 Reloading modules...[/cyan]\n\n")

    try:
        reloaded_count = 0
        for module_name in modules_to_reload:
            if module_name in sys.modules:
                try:
                    importlib.reload(sys.modules[module_name])
                    reloaded_count += 1
                    app.write(f"[dim]✓ Reloaded {module_name}[/dim]\n")
                except Exception as e:
                    app.write(f"[yellow]⚠ Could not reload {module_name}: {e}[/yellow]\n")

        app.write(f"\n[green]✓ Reloaded {reloaded_count} modules[/green]\n\n")

        # Refresh laser colors on the running app instance
        try:
            try:
                from frontier_colors import FRONTIER_LASER_COLORS
            except ImportError:
                try:
                    from modules.frontier_colors import FRONTIER_LASER_COLORS
                except ImportError:
                    raise

            # Update main app colors
            app._laser_colors = FRONTIER_LASER_COLORS

            # Update streaming display widget colors
            try:
                stream_display = app.query_one("#stream-display")
                stream_display.set_laser_colors(FRONTIER_LASER_COLORS)
                app.write(f"[dim]✓ Refreshed laser colors: {FRONTIER_LASER_COLORS[:3]}...[/dim]\n\n")
            except Exception:
                # Fallback if query fails
                if hasattr(app, '_content_widget') and app._content_widget:
                    app._content_widget.set_laser_colors(FRONTIER_LASER_COLORS)
                    app.write(f"[dim]✓ Refreshed laser colors: {FRONTIER_LASER_COLORS[:3]}...[/dim]\n\n")
                else:
                    app.write(f"[dim]✓ Refreshed app laser colors (restart may be needed for full effect)[/dim]\n\n")
        except Exception as e:
            app.write(f"[yellow]⚠ Could not refresh laser colors: {e}[/yellow]\n\n")

        app.write("[dim]Note: Some changes may require restarting OpenCLI[/dim]\n\n")

    except Exception as e:
        app.write(f"[red]✗ Module reload failed: {e}[/red]\n\n")
        import traceback
        app.write(f"[dim]{traceback.format_exc()}[/dim]\n\n")


# ============================================================================
# /api - API server control
# ============================================================================

def api_server_control_prompt(app, session, registration, context):
    """Interactive prompt for /api command"""
    import subprocess

    action = context.get('args', '').strip().lower()

    if not action:
        return None  # Will show usage in handler

    # Check current status
    try:
        result = subprocess.run(["pgrep", "-f", "api_server"], capture_output=True, timeout=5)
        is_running = result.returncode == 0
    except:
        is_running = False

    if action == "status":
        return None  # Status doesn't need permission

    if action == "start":
        prompt_data = {
            'title': 'System: /api start',
            'message': f"""# Start API Server

**Current Status:** {'Running' if is_running else 'Not Running'}
**Action:** Start API server in background

**Confirm action:**""",
            'options': [
                {'text': 'Start API server', 'response': PermissionResponse.ALLOW_ONCE, 'data': {'action': 'start'}},
                {'text': 'Cancel', 'response': PermissionResponse.CANCEL}
            ]
        }
    elif action in ["stop", "restart"]:
        prompt_data = {
            'title': f'System: /api {action}',
            'message': f"""# {action.title()} API Server

**Action:** {action.title()} the OpenCLI API server
**Warning:** {'Active API requests will be interrupted!' if action == 'stop' else 'Brief service interruption will occur!'}

**Affected:**
- Running API server process
- Active API connections
{'- API endpoints' if action == 'stop' else ''}

**Confirm {action}:**""",
            'options': [
                {'text': f'Yes, {action} API server', 'response': PermissionResponse.ALLOW_ONCE, 'data': {'action': action, 'confirmed': True}},
                {'text': 'Cancel', 'response': PermissionResponse.CANCEL}
            ]
        }
    else:
        return None
    return prompt_data


async def api_server_control(app, session, **context):
    """Control the OpenCLI API server - SDK COMPLIANT"""
    import subprocess

    action = context.get('args', '').strip().lower()

    if not action:
        app.write("[cyan]API Server Control[/cyan]\n\n")
        app.write("[dim]Usage: /api <start|stop|status|restart>[/dim]\n\n")
        return

    # Check current status
    try:
        result = subprocess.run(["pgrep", "-f", "api_server"], capture_output=True, timeout=5)
        is_running = result.returncode == 0
    except:
        is_running = False

    # Status check doesn't need permission
    if action == "status":
        try:
            if is_running:
                app.write("[green]✓ API server is running[/green]\n\n")
            else:
                app.write("[yellow]○ API server is not running[/yellow]\n\n")
        except Exception as e:
            app.write(f"[red]✗ Error checking status: {e}[/red]\n\n")
        return

    # Get user selection for other actions
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    selected_action = user_selection.get('action')

    if not selected_action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    if action in ["stop", "restart"] and not user_selection.get('confirmed'):
        app.write("[yellow]Destructive action requires confirmation[/yellow]\n")
        return

    # Execute action
    if action == "start":
        app.write("[cyan]Starting API server...[/cyan]\n\n")
        try:
            subprocess.Popen(
                ["python3", "-m", "api_server"],
                cwd="/Users/dezmondhollins/opencli"
            )
            app.write("[green]✓ API server starting[/green]\n\n")
        except Exception as e:
            app.write(f"[red]✗ Failed to start: {e}[/red]\n\n")

    elif action == "stop":
        app.write("[cyan]Stopping API server...[/cyan]\n\n")
        try:
            subprocess.run(["pkill", "-f", "api_server"], timeout=5)
            app.write("[green]✓ API server stopped[/green]\n\n")
        except Exception as e:
            app.write(f"[red]✗ Failed to stop: {e}[/red]\n\n")

    elif action == "status":
        # Status check doesn't need permission - it's read-only
        try:
            if is_running:
                app.write("[green]✓ API server is running[/green]\n\n")
            else:
                app.write("[yellow]○ API server is not running[/yellow]\n\n")
        except Exception as e:
            app.write(f"[red]✗ Error checking status: {e}[/red]\n\n")

    elif action == "restart":
        app.write("[cyan]Restarting API server...[/cyan]\n\n")
        try:
            subprocess.run(["pkill", "-f", "api_server"], timeout=5)
            subprocess.Popen(
                ["python3", "-m", "api_server"],
                cwd="/Users/dezmondhollins/opencli"
            )
            app.write("[green]✓ API server restarted[/green]\n\n")
        except Exception as e:
            app.write(f"[red]✗ Failed to restart: {e}[/red]\n\n")

    else:
        app.write(f"[red]✗ Unknown action: {action}[/red]\n")
        app.write("[dim]Usage: /api <start|stop|status|restart>[/dim]\n\n")


# ============================================================================
# /rollback - List available backups
# ============================================================================

def rollback_opencli_prompt(app, session, registration, context):
    """Interactive prompt for /rollback command"""
    from ..rollback_manager import RollbackManager

    manager = RollbackManager()
    backups = manager.list_backups()
    backup_count = len(backups)

    prompt_data = {
        'title': 'System: /rollback',
        'message': f"""# Available Backups

**Total Backups:** {backup_count}
**Status:** {'No backups found' if backup_count == 0 else f'{backup_count} backups available'}

**Select action:**""",
        'options': [
            {'text': 'View all backups', 'response': PermissionResponse.ALLOW_ONCE, 'data': {'action': 'view'}},
            {'text': 'Export to file', 'response': PermissionResponse.ALLOW_ONCE, 'data': {'action': 'export'}},
            {'text': 'Cancel', 'response': PermissionResponse.CANCEL}
        ]
    }
    return prompt_data


async def rollback_opencli(app, session, **context):
    """List available backups and guide through rollback - SDK COMPLIANT"""
    from ..rollback_manager import RollbackManager

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

    manager = RollbackManager()
    backups = manager.list_backups()

    if action == 'view':
        if not backups:
            app.write("[yellow]No OpenCLI backups were found. Unable to rollback.[/yellow]\n\n")
            return

        app.write("[bold cyan]Available OpenCLI Backups[/bold cyan]\n")
        for backup in backups:
            app.write(
                f"  [cyan]{backup['timestamp_str']}[/cyan] · "
                f"Version {backup['version']} · {backup['age']} · {backup['size']}\n"
            )

        app.write(
            "\nTo perform a rollback, run `./emergency-rollback.sh <timestamp>` "
            "from the project root. Always back up your current configuration first.\n\n"
        )

    elif action == 'export':
        from pathlib import Path
        export_path = Path.cwd() / "opencli-backups.txt"
        with open(export_path, 'w') as f:
            f.write("OpenCLI Available Backups\n")
            f.write("=" * 40 + "\n\n")
            for backup in backups:
                f.write(f"{backup['timestamp_str']}\n")
                f.write(f"  Version: {backup['version']}\n")
                f.write(f"  Age: {backup['age']}\n")
                f.write(f"  Size: {backup['size']}\n\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# ============================================================================
# Placeholder commands - will implement when needed
# ============================================================================

def refactor_interactive_prompt(app, session, registration, context):
    """Interactive prompt for /refactor command"""
    prompt_data = {
        'title': 'System: /refactor',
        'message': """# Interactive Refactoring

**Status:** Feature not yet implemented
**Risk Level:** MEDIUM

**Confirm action:**""",
        'options': [
            {'text': 'Execute placeholder', 'response': PermissionResponse.ALLOW_ONCE, 'data': {'action': 'execute'}},
            {'text': 'Cancel', 'response': PermissionResponse.CANCEL}
        ]
    }
    return prompt_data


async def refactor_interactive(app, session, **context):
    """Interactive refactoring mode - SDK COMPLIANT"""
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return
    user_selection = prompt_data.get('data', {})
    if not user_selection.get('action'):
        app.write("[yellow]Command cancelled[/yellow]\n")
        return
    app.write("[yellow]⚠ Refactoring mode not yet available[/yellow]\n")
    app.write("[dim]Use /help for available commands[/dim]\n\n")


def autorefactor_prompt(app, session, registration, context):
    """Interactive prompt for /autorefactor command"""
    prompt_data = {
        'title': 'System: /autorefactor',
        'message': """# Automatic Refactoring

**Status:** Feature not yet implemented
**Risk Level:** HIGH
**Warning:** This would automatically modify your code!

**Affected:**
- Source code files
- Code structure
- Existing implementations

**Confirm action:**""",
        'options': [
            {'text': 'Execute placeholder', 'response': PermissionResponse.ALLOW_ONCE, 'data': {'action': 'execute', 'confirmed': True}},
            {'text': 'Cancel', 'response': PermissionResponse.CANCEL}
        ]
    }
    return prompt_data


async def autorefactor(app, session, **context):
    """Automatic code refactoring - SDK COMPLIANT"""
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return
    user_selection = prompt_data.get('data', {})
    if not user_selection.get('action'):
        app.write("[yellow]Command cancelled[/yellow]\n")
        return
    app.write("[yellow]⚠ Auto-refactoring not yet available[/yellow]\n")
    app.write("[dim]Use /help for available commands[/dim]\n\n")


def code_inject_prompt(app, session, registration, context):
    """Interactive prompt for /inject command"""
    prompt_data = {
        'title': 'System: /inject',
        'message': """# Code Injection

**Status:** Feature not yet implemented
**Risk Level:** ⚠️ CRITICAL
**Warning:** This can crash the application or cause data loss!

**Affected:**
- Running Python process
- Application memory space
- System stability
- ALL loaded modules

**Confirm action:**""",
        'options': [
            {'text': 'Execute placeholder', 'response': PermissionResponse.ALLOW_ONCE, 'data': {'action': 'execute', 'confirmed': True}},
            {'text': 'Cancel', 'response': PermissionResponse.CANCEL}
        ]
    }
    return prompt_data


async def code_inject(app, session, **context):
    """Code injection tool - SDK COMPLIANT"""
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return
    user_selection = prompt_data.get('data', {})
    if not user_selection.get('action') or not user_selection.get('confirmed'):
        app.write("[yellow]Command cancelled[/yellow]\n")
        return
    app.write("[yellow]⚠ Code injection not yet available[/yellow]\n")
    app.write("[dim]Use /help for available commands[/dim]\n\n")
