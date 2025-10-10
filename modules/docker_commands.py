"""
Docker Commands - STREAMLINED for ExecutionSystem

COMPLIANT pattern:
- Simple async functions
- NO manual buffer management
- Return results, ExecutionSystem handles display
- For workflows, return list of ExecutionSteps
"""

import asyncio
from execution.executor import ExecutionStep
from execution.registry import RiskLevel


async def docker_main(app, session, **context):
    """
    Parent /docker command - shows available Docker operations
    """
    app.write("[bold cyan]Docker Operations[/bold cyan]\n\n")
    app.write("Available commands:\n")
    app.write("  [cyan]/docker ollama setup[/cyan]  - Setup Ollama in Docker\n")
    app.write("  [cyan]/docker ollama start[/cyan]  - Start Ollama container\n")
    app.write("  [cyan]/docker ollama stop[/cyan]   - Stop Ollama container\n\n")
    return True


async def docker_ollama_setup(app, session, **context):
    """
    STREAMLINED Docker Ollama setup

    PermissionManager already approved this
    Just do the work with sensible defaults
    """
    from docker_manager import DockerManager
    from docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

    # Use conservative defaults (4 CPUs, 8GB RAM)
    cpu_limit = '4'
    memory_limit = '8g'
    gpu_enabled = False

    try:
        # Check Docker
        is_running, msg = await docker_async.check_docker_running()
        if not is_running:
            app.write(f"[red]✗ Docker not running: {msg}[/red]\n\n")
            return False

        # Check existing container
        container_id, status, name = await docker_async.get_ollama_container_status()
        if container_id and status == 'running':
            app.write(f"[yellow]! Container already running: {name}[/yellow]\n\n")
            return True

        if container_id:
            # Remove old container
            await docker_async.remove_ollama_container(True)

        # Pull image
        app.write("[cyan]→ Pulling Ollama image...[/cyan]\n")
        success, msg = await docker_async.pull_ollama_image()
        if not success:
            app.write(f"[red]✗ Failed to pull image: {msg}[/red]\n\n")
            return False
        app.write("[green]✓ Image pulled[/green]\n")

        # Create container
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

        # Verify running
        is_running, container_id = await docker_async.is_ollama_running()
        if not is_running:
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


async def docker_ollama_start(app, session, **context):
    """STREAMLINED Docker Ollama start"""
    from docker_manager import DockerManager
    from docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

    try:
        # Check if already running
        is_running, container_id = await docker_async.is_ollama_running()
        if is_running:
            app.write("[yellow]! Ollama container already running[/yellow]\n\n")
            return True

        # Start container
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


async def docker_ollama_stop(app, session, **context):
    """STREAMLINED Docker Ollama stop"""
    from docker_manager import DockerManager
    from docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

    try:
        # Check if running
        is_running, container_id = await docker_async.is_ollama_running()
        if not is_running:
            app.write("[yellow]! Ollama container not running[/yellow]\n\n")
            return True

        # Stop container
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


async def docker_status(app, session, **context):
    """Show Docker daemon status and core diagnostics."""
    from docker_manager import DockerManager
    from docker_async_handler import DockerAsyncHandler

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


async def docker_ps(app, session, **context):
    """List running Docker containers."""
    from docker_manager import DockerManager
    from docker_async_handler import DockerAsyncHandler

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


async def docker_stats(app, session, **context):
    """Show lightweight stats for running containers."""
    from docker_manager import DockerManager
    from docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

    containers = await docker_async.list_containers(all_containers=False)
    app.write("[bold cyan]Container Stats[/bold cyan]\n")
    if not containers:
        app.write("[dim]No running containers to inspect.[/dim]\n\n")
        return

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
    app.write("\n")


async def docker_ollama_status(app, session, **context):
    """Show status for the OpenCLI Ollama container."""
    from docker_manager import DockerManager
    from docker_async_handler import DockerAsyncHandler

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
            f"Mem: {stats.get('memory_usage', 'N/A')} ({stats.get('memory_percent', '0')}%)\n"
        )
    app.write("\n")
