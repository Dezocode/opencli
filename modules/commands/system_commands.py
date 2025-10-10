"""System Commands"""

async def restart_session(app, session, **context):
    """Restart the current session"""
    app.write("[cyan]Restarting session...[/cyan]\n\n")

    # Clear session history
    if hasattr(session, 'messages'):
        session.messages = []

    # Reset turn counter
    if hasattr(session, 'turn_counter'):
        session.turn_counter = 0

    # Clear any pending operations
    session._awaiting_permission = False
    session._permission_response = None

    app.write("[green]✓ Session restarted[/green]\n\n")


async def upgrade_opencli(app, session, **context):
    """Upgrade OpenCLI to latest version"""
    import subprocess

    app.write("[cyan]Checking for OpenCLI updates...[/cyan]\n\n")

    try:
        # Pull latest from git
        result = subprocess.run(
            ["git", "pull", "dev", "Main"],
            cwd="/Users/dezmondhollins/opencli",
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            if "Already up to date" in result.stdout:
                app.write("[green]✓ OpenCLI is already up to date[/green]\n\n")
            else:
                app.write("[green]✓ OpenCLI updated successfully[/green]\n\n")
                app.write("[yellow]⚠ Please restart OpenCLI to use the new version[/yellow]\n\n")
        else:
            app.write(f"[red]✗ Update failed: {result.stderr}[/red]\n\n")

    except Exception as e:
        app.write(f"[red]✗ Error checking for updates: {e}[/red]\n\n")


async def api_server_control(app, session, **context):
    """Control the OpenCLI API server"""
    action = context.get('args', '').strip().lower()

    if not action:
        app.write("[cyan]API Server Control[/cyan]\n\n")
        app.write("[dim]Usage: /api-server <start|stop|status|restart>[/dim]\n\n")
        return

    import subprocess

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
        try:
            result = subprocess.run(
                ["pgrep", "-f", "api_server"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
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
        app.write("[dim]Usage: /api-server <start|stop|status|restart>[/dim]\n\n")


async def rollback_opencli(app, session, **context):
    """List available backups and guide through rollback."""
    from rollback_manager import RollbackManager

    manager = RollbackManager()
    backups = manager.list_backups()

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


# Placeholders for advanced features - will implement when needed
async def refactor_interactive(app, session, **context):
    """Interactive refactoring mode"""
    app.write("[yellow]⚠ Refactoring mode not yet available[/yellow]\n")
    app.write("[dim]Use /help for available commands[/dim]\n\n")


async def autorefactor(app, session, **context):
    """Automatic code refactoring"""
    app.write("[yellow]⚠ Auto-refactoring not yet available[/yellow]\n")
    app.write("[dim]Use /help for available commands[/dim]\n\n")


async def code_inject(app, session, **context):
    """Code injection tool"""
    app.write("[yellow]⚠ Code injection not yet available[/yellow]\n")
    app.write("[dim]Use /help for available commands[/dim]\n\n")
