"""
Docker Commands - SDK COMPLIANT

SDK-COMPLIANT: All commands use interactive permission buffer pages.
User interaction happens in buffer, handlers execute based on selections.
"""

import asyncio
from .execution.executor import ExecutionStep
from .execution.registry import RiskLevel

# SDK-compliant imports only
from .permission_prompt import PermissionResponse
from .permission_buffer_manager import get_permission_buffer_manager


# ============================================================================ 
# /docker - Docker operations menu
# ============================================================================ 

async def docker_main_prompt(app, session, registration, context):
    """Interactive prompt for /docker command"""

    prompt_data = {
        'title': 'System: /docker',
        'message': """# Docker Operations

**Type:** Docker operations menu
**Available:** Setup, Start, Stop, Status commands

**Select action:**""",
        'options': [
            {
                'text': 'View Docker operations menu',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'view_menu'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }

    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def docker_main(app, session, **context):
    """Parent /docker command - SDK COMPLIANT"""

    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return False

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return False

    app.write("[bold cyan]Docker Operations[/bold cyan]\n\n")
    app.write("Available commands:\n")
    app.write("  [cyan]/docker ollama setup[/cyan]  - Setup Ollama in Docker\n")
    app.write("  [cyan]/docker ollama start[/cyan]  - Start Ollama container\n")
    app.write("  [cyan]/docker ollama stop[/cyan]   - Stop Ollama container\n")
    app.write("  [cyan]/docker status[/cyan]        - Show Docker daemon status\n")
    app.write("  [cyan]/docker ps[/cyan]            - List running containers\n")
    app.write("  [cyan]/docker stats[/cyan]         - Show container stats\n\n")
    return True


# ============================================================================ 
# /docker ollama setup - Setup Ollama in Docker
# ============================================================================ 

async def docker_ollama_setup_prompt(app, session, registration, context):
    """Interactive prompt for /docker ollama setup command"""

    prompt_data = {
        'title': 'System: /docker ollama setup',
        'message': """# Docker Ollama Setup

**Estimated Duration:** 2-3 minutes

**Workflow Steps:**
1. Check Docker daemon
2. Pull Ollama image from Docker Hub
3. Create container (4 CPUs, 8GB RAM)
4. Start container and verify

**Select action:**""",
        'options': [
            {
                'text': 'Run Docker Ollama setup workflow',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'setup'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }

    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def docker_ollama_setup(app, session, **context):
    """Docker Ollama setup - SDK COMPLIANT"""

    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return False

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return False

    from .docker_manager import DockerManager
    from .docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

    cpu_limit = '4'
    memory_limit = '8g'
    gpu_enabled = False

    try:
        is_running, msg = await docker_async.check_docker_running()
        if not is_running:
            app.write(f"[red]✗ Docker not running: {msg}[/red]\n\n")
            return False

        container_id, status, name = await docker_async.get_ollama_container_status()
        if container_id and status == 'running':
            app.write(f"[yellow]! Container already running: {name}[/yellow]\n\n")
            return True

        if container_id:
            await docker_async.remove_ollama_container(True)

        app.write("[cyan]→ Pulling Ollama image...[/cyan]\n")
        success, msg_pull = await docker_async.pull_ollama_image()
        if not success:
            app.write(f"[red]✗ Failed to pull image: {msg_pull}[/red]\n\n")
            return False
        app.write("[green]✓ Image pulled[/green]\n")

        app.write(f"[cyan]→ Creating container ({cpu_limit} CPUs, {memory_limit} RAM)...[/cyan]\n")
        success, result_msg = await docker_async.create_ollama_container(
            cpu_limit=cpu_limit,
            memory_limit=memory_limit,
            gpu_enabled=gpu_enabled
        )
        if not success:
            app.write(f"[red]✗ Failed to create container: {result_msg}[/red]\n\n")
            return False
        app.write("[green]✓ Container created[/green]\n")

        is_running_verify, container_id_verify = await docker_async.is_ollama_running()
        if not is_running_verify:
            app.write("[red]✗ Container created but not running[/red]\n\n")
            return False

        app.write(f"\n[bold green]✓ Ollama setup complete![/bold green]\n\n")
        app.write(f"[bold]Available at:[/bold] [cyan]http://localhost:{docker_mgr.OLLAMA_PORT}[/cyan]\n\n")
        app.write("[dim]Next steps:[/dim]\n")
        app.write("  • [cyan]/providers add ollama[/cyan]  - Add as provider\n")
        app.write("  • [cyan]/model[/cyan]  - See Ollama models\n\n")

        return True

    except Exception as e:
        app.write(f"[red]✗ Setup failed: {e}[/red]\n\n")
        return False


# ============================================================================ 
# /docker ollama start - Start Ollama container
# ============================================================================ 

async def docker_ollama_start_prompt(app, session, registration, context):
    """Interactive prompt for /docker ollama start command"""

    prompt_data = {
        'title': 'System: /docker ollama start',
        'message': """# Start Ollama Container

**Current Status:** Ollama container stopped
**Action:** Start Ollama container

**Select action:**""",
        'options': [
            {
                'text': 'Start Ollama container',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'start'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def docker_ollama_start(app, session, **context):
    """Docker Ollama start - SDK COMPLIANT"""

    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return False

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return False

    from .docker_manager import DockerManager
    from .docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

    try:
        is_running, container_id = await docker_async.is_ollama_running()
        if is_running:
            app.write("[yellow]! Ollama container already running[/yellow]\n\n")
            return True

        app.write("[cyan]→ Starting Ollama container...[/cyan]\n")
        success, msg = await docker_async.start_ollama_container()

        if success:
            app.write("[green]✓ Container started[/green]\n\n")
            app.write(f"[bold]Available at:[/bold] [cyan]http://localhost:{docker_mgr.OLLAMA_PORT}[/cyan]\n\n")
            return True
        else:
            app.write(f"[red]✗ Failed to start: {msg}[/red]\n\n")
            return False

    except Exception as e:
        app.write(f"[red]✗ Error: {e}[/red]\n\n")
        return False


# ============================================================================ 
# /docker ollama stop - Stop Ollama container
# ============================================================================ 

async def docker_ollama_stop_prompt(app, session, registration, context):
    """Interactive prompt for /docker ollama stop command"""

    prompt_data = {
        'title': 'System: /docker ollama stop',
        'message': """# Stop Ollama Container

**Description:** This will stop the Ollama Docker container.

**Affected Items:**
• Ollama Docker container
• Running models
• Active API connections

**Warning:** Ongoing model operations will be interrupted!

**Confirm action:**""",
        'options': [
            {
                'text': 'Yes, stop Ollama container',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'stop', 'confirmed': True}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def docker_ollama_stop(app, session, **context):
    """Docker Ollama stop - SDK COMPLIANT"""

    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return False

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return False

    if not user_selection.get('confirmed'):
        app.write("[yellow]Stop requires confirmation[/yellow]\n")
        return False

    from .docker_manager import DockerManager
    from .docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

    try:
        is_running, container_id = await docker_async.is_ollama_running()
        if not is_running:
            app.write("[yellow]! Ollama container not running[/yellow]\n\n")
            return True

        app.write("[cyan]→ Stopping Ollama container...[/cyan]\n")
        success, msg = await docker_async.stop_ollama_container()

        if success:
            app.write("[green]✓ Container stopped[/green]\n\n")
            return True
        else:
            app.write(f"[red]✗ Failed to stop: {msg}[/red]\n\n")
            return False

    except Exception as e:
        app.write(f"[red]✗ Error: {e}[/red]\n\n")
        return False


# ============================================================================ 
# /docker status - Show Docker daemon status
# ============================================================================ 

async def docker_status_prompt(app, session, registration, context):
    """Interactive prompt for /docker status command"""

    prompt_data = {
        'title': 'System: /docker status',
        'message': """# Docker Status

**Type:** Docker daemon diagnostics
**Shows:** Installation, daemon status, system resources

**Select action:**""",
        'options': [
            {
                'text': 'Show Docker status',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute'}
            },
            {
                'text': 'Show and export to file',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute_and_export'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def docker_status(app, session, **context):
    """Show Docker daemon status - SDK COMPLIANT"""

    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    from .docker_manager import DockerManager
    from .docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

    installed, version_msg = await docker_async.check_docker_installed()
    running, running_msg = await docker_async.check_docker_running()

    app.write("[bold cyan]Docker Status[/bold cyan]\n")
    app.write(f"  Installed: {'[green]✓[/green]' if installed else '[red]✗[/red]'} {version_msg}\n")
    app.write(f"  Daemon: {'[green]✓[/green]' if running else '[red]✗[/red]'} {running_msg}\n")

    resources = await docker_async.get_system_resources()
    if resources:
        cpu = resources.get('cpu_count')
        mem = resources.get('memory_gb')
        disk = resources.get('disk_gb')
        app.write("\n[bold]System resources[/bold]\n")
        if cpu:
            app.write(f"  CPUs: {cpu}\n")
        if mem:
            app.write(f"  Memory: {mem:.1f} GB\n")
        if disk:
            app.write(f"  Disk free: {disk} GB\n")
    app.write("\n")

    if user_selection.get('action') == 'execute_and_export':
        from pathlib import Path
        export_path = Path.cwd() / "docker-status.txt"
        with open(export_path, 'w') as f:
            f.write("Docker Status\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Installed: {version_msg}\n")
            f.write(f"Daemon: {running_msg}\n")
            if resources:
                f.write(f"\nSystem Resources:\n")
                if cpu:
                    f.write(f"  CPUs: {cpu}\n")
                if mem:
                    f.write(f"  Memory: {mem:.1f} GB\n")
                if disk:
                    f.write(f"  Disk: {disk} GB free\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# ============================================================================ 
# /docker ps - List running containers
# ============================================================================ 

async def docker_ps_prompt(app, session, registration, context):
    """Interactive prompt for /docker ps command"""

    prompt_data = {
        'title': 'System: /docker ps',
        'message': """# List Running Containers

**Type:** List running containers
**Command:** docker ps

**Select action:**""",
        'options': [
            {
                'text': 'List running containers',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute'}
            },
            {
                'text': 'List and export to file',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute_and_export'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def docker_ps(app, session, **context):
    """List running Docker containers - SDK COMPLIANT"""

    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    from .docker_manager import DockerManager
    from .docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

    containers = await docker_async.list_containers(all_containers=False)
    app.write("[bold cyan]Running Containers[/bold cyan]\n")
    if not containers:
        app.write("[dim]No running containers.[/dim]\n\n")
        return

    for container in containers:
        name = container.get("Names", "unknown")
        image = container.get("Image", "unknown")
        status = container.get("Status", "unknown")
        app.write(f"  [cyan]{name}[/cyan] · {image} · {status}\n")
    app.write("\n")

    if user_selection.get('action') == 'execute_and_export':
        from pathlib import Path
        export_path = Path.cwd() / "docker-containers.txt"
        with open(export_path, 'w') as f:
            f.write("Running Docker Containers\n")
            f.write("=" * 40 + "\n\n")
            for container in containers:
                name = container.get("Names", "unknown")
                image = container.get("Image", "unknown")
                status = container.get("Status", "unknown")
                f.write(f"{name}\n")
                f.write(f"  Image: {image}\n")
                f.write(f"  Status: {status}\n\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# ============================================================================ 
# /docker stats - Show container stats
# ============================================================================ 

async def docker_stats_prompt(app, session, registration, context):
    """Interactive prompt for /docker stats command"""

    prompt_data = {
        'title': 'System: /docker stats',
        'message': """# Container Stats

**Type:** Container resource usage
**Shows:** CPU, Memory, Network I/O

**Select action:**""",
        'options': [
            {
                'text': 'Show container stats',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute'}
            },
            {
                'text': 'Show and export to file',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute_and_export'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def docker_stats(app, session, **context):
    """Show lightweight stats for running containers - SDK COMPLIANT"""

    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    from .docker_manager import DockerManager
    from .docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

    containers = await docker_async.list_containers(all_containers=False)
    app.write("[bold cyan]Container Stats[/bold cyan]\n")
    if not containers:
        app.write("[dim]No running containers to inspect.[/dim]\n\n")
        return

    stats_data = []
    for container in containers:
        name = container.get("Names", "unknown")
        stats = await docker_async.get_container_stats(container.get("ID", name))
        if not stats:
            app.write(f"  [cyan]{name}[/cyan] - [red]unable to fetch stats[/red]\n")
            continue

        app.write(
            f"  [cyan]{name}[/cyan] · CPU {stats.get('cpu_percent', '0')}% · "
            f"Mem {stats.get('memory_usage', 'N/A')} ({stats.get('memory_percent', '0')}%) · "
            f"Net {stats.get('network_io', 'N/A')}"
        )
        app.write("\n")
        stats_data.append((name, stats))
    app.write("\n")

    if user_selection.get('action') == 'execute_and_export':
        from pathlib import Path
        export_path = Path.cwd() / "docker-stats.txt"
        with open(export_path, 'w') as f:
            f.write("Docker Container Stats\n")
            f.write("=" * 40 + "\n\n")
            for name, stats in stats_data:
                f.write(f"{name}\n")
                f.write(f"  CPU: {stats.get('cpu_percent', '0')}%\n")
                f.write(f"  Memory: {stats.get('memory_usage', 'N/A')} ({stats.get('memory_percent', '0')}%)\n")
                f.write(f"  Network: {stats.get('network_io', 'N/A')}\n\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# ============================================================================ 
# /docker ollama status - Show Ollama container status
# ============================================================================ 

def docker_ollama_status_prompt(app, session, registration, context):
    """Interactive prompt for /docker ollama status command"""

    prompt_data = {
        'title': 'System: /docker ollama status',
        'message': """# Ollama Container Status

**Type:** Ollama container status
**Shows:** Container name, status, CPU/Memory usage

**Select action:**""",
        'options': [
            {
                'text': 'Show Ollama container status',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute'}
            },
            {
                'text': 'Show and export to file',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute_and_export'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    buffer_manager = get_permission_buffer_manager()
    return buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def docker_ollama_status(app, session, **context):
    """Show status for the OpenCLI Ollama container - SDK COMPLIANT"""

    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    from .docker_manager import DockerManager
    from .docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

    container_id, status, name = await docker_async.get_ollama_container_status()
    if not container_id:
        app.write("[yellow]No OpenCLI Ollama container detected.[/yellow]\n")
        app.write("Use `/docker ollama setup` to create one.\n\n")
        return

    app.write("[bold cyan]Ollama Container[/bold cyan]\n")
    app.write(f"  Name: [cyan]{name}[/cyan]\n")
    app.write(f"  Status: {status}\n")
    stats = await docker_async.get_container_stats(container_id)
    if stats:
        app.write(
            f"  CPU: {stats.get('cpu_percent', '0')}% · "
            f"Mem: {stats.get('memory_usage', 'N/A')} ({stats.get('memory_percent', '0')}%)· "
            f"Net: {stats.get('network_io', 'N/A')}"
        )        
        app.write("\n")

    if user_selection.get('action') == 'execute_and_export':
        from pathlib import Path
        export_path = Path.cwd() / "ollama-container-status.txt"
        with open(export_path, 'w') as f:
            f.write("Ollama Container Status\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Name: {name}\n")
            f.write(f"Status: {status}\n")
            if stats:
                f.write(f"CPU: {stats.get('cpu_percent', '0')}%\n")
                f.write(f"Memory: {stats.get('memory_usage', 'N/A')} ({stats.get('memory_percent', '0')}%)\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")