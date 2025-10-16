"""
Docker Commands - SDK COMPLIANT

SDK-COMPLIANT: All commands use interactive permission buffer pages.
User interaction happens in buffer, handlers execute based on selections.
"""

import asyncio

# SDK-compliant imports only
from .permission_prompt import PermissionResponse
from .permission_buffer_manager import get_permission_buffer_manager


# ============================================================================
# /docker ollama setup (unified) - Setup Ollama in Docker with resource selection
# ============================================================================

async def docker_ollama_setup_unified_prompt(app, session, registration, context):
    """Interactive prompt for /docker ollama setup unified command"""

    # Get system resources for display
    try:
        from docker_manager import DockerManager
        from docker_async_handler import DockerAsyncHandler
    except ImportError:
        from modules.docker_manager import DockerManager
        from modules.docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

    resources = await docker_async.get_system_resources()
    cpu_count = resources.get('cpu_count', 4)
    memory_gb = resources.get('memory_gb', 8)

    prompt_data = {
        'title': 'System: /docker ollama setup',
        'message': f"""# Docker Ollama Setup

**Your System:** {cpu_count} CPUs, {memory_gb:.1f}GB RAM
**Estimated Duration:** 2-3 minutes

**Workflow Steps:**
1. Check Docker daemon
2. Pull Ollama image (~2.7GB download)
3. Create container with selected resources
4. Start container and verify

**Select resource allocation:**""",
        'options': [
            {
                'text': f'Conservative (4 CPUs, 8GB RAM) - Recommended',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'setup', 'cpu_limit': '4', 'memory_limit': '8g', 'gpu_enabled': False}
            },
            {
                'text': f'Balanced (6 CPUs, 12GB RAM)',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'setup', 'cpu_limit': '6', 'memory_limit': '12g', 'gpu_enabled': False}
            },
            {
                'text': 'With GPU Support (requires nvidia-docker)',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'setup', 'cpu_limit': '6', 'memory_limit': '12g', 'gpu_enabled': True}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }

    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=60.0)


async def docker_ollama_setup_unified(app, session, **context):
    """Docker Ollama setup unified - SDK COMPLIANT"""

    # Get user selection
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return False

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return False

    # Get selected resources
    cpu_limit = user_selection.get('cpu_limit', '4')
    memory_limit = user_selection.get('memory_limit', '8g')
    gpu_enabled = user_selection.get('gpu_enabled', False)

    # Execute - setup Ollama in Docker
    try:
        from docker_manager import DockerManager
        from docker_async_handler import DockerAsyncHandler
    except ImportError:
        from modules.docker_manager import DockerManager
        from modules.docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

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
        success, msg_pull = await docker_async.pull_ollama_image()
        if not success:
            app.write(f"[red]✗ Failed to pull image: {msg_pull}[/red]\n\n")
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
# /docker ollama start (unified) - Start Ollama container
# ============================================================================

async def docker_ollama_start_unified_prompt(app, session, registration, context):
    """Interactive prompt for /docker ollama start unified command"""

    prompt_data = {
        'title': 'System: /docker ollama start',
        'message': """# Start Ollama Container

**Action:** Start Ollama Docker container

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


async def docker_ollama_start_unified(app, session, **context):
    """Docker Ollama start unified - SDK COMPLIANT"""

    # Get user selection
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return False

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return False

    # Execute - start Ollama
    try:
        from docker_manager import DockerManager
        from docker_async_handler import DockerAsyncHandler
    except ImportError:
        from modules.docker_manager import DockerManager
        from modules.docker_async_handler import DockerAsyncHandler

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)

    try:
        # Check if already running
        is_running, container_id = await docker_async.is_ollama_running()
        if is_running:
            app.write("[yellow]! Ollama container already running[/yellow]\n\n")
            return True

        # Check if container exists
        container_id, status, name = await docker_async.get_ollama_container_status()
        if not container_id:
            app.write("[red]✗ No Ollama container found[/red]\n")
            app.write("[dim]Run '/docker ollama setup' first[/dim]\n\n")
            return False

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


# ============================================================================
# /docker ollama stop (unified) - Stop Ollama container
# ============================================================================

async def docker_ollama_stop_unified_prompt(app, session, registration, context):
    """Interactive prompt for /docker ollama stop unified command"""

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


async def docker_ollama_stop_unified(app, session, **context):
    """Docker Ollama stop unified - SDK COMPLIANT"""

    # Get user selection
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

    # Execute - stop Ollama
    try:
        from docker_manager import DockerManager
        from docker_async_handler import DockerAsyncHandler
    except ImportError:
        from modules.docker_manager import DockerManager
        from modules.docker_async_handler import DockerAsyncHandler

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
