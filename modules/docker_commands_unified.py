"""
Docker Commands using Unified Permission-First Execution

All Docker commands flow through the unified command executor with:
- Live progress in permission buffer
- Step-by-step execution display
- Proper permission gating
- Thread-safe async execution
"""

import asyncio
from typing import Dict


async def docker_ollama_setup_unified(app, session):
    """
    Execute Docker Ollama setup through PERMISSION BUFFER FIRST!

    CORRECT FLOW:
    1. Show initial permission in buffer
    2. Show resource selection in buffer  ← USER CHOOSES HERE!
    3. Execute workflow with chosen resources in buffer
    4. Clear buffer
    5. Write results to chat

    This ensures:
    - Permission-first flow with resource selection IN BUFFER
    - Live progress in permission buffer
    - NO writes to chat during buffer execution
    """

    # Import required modules
    try:
        from modules.docker_manager import DockerManager
        from modules.docker_async_handler import DockerAsyncHandler
        from modules.unified_command_executor import CommandStep, CommandRiskLevel
    except ImportError:
        import importlib
        docker_mgr_mod = importlib.import_module('docker_manager')
        DockerManager = docker_mgr_mod.DockerManager
        docker_async_mod = importlib.import_module('docker_async_handler')
        DockerAsyncHandler = docker_async_mod.DockerAsyncHandler
        executor_mod = importlib.import_module('unified_command_executor')
        CommandStep = executor_mod.CommandStep
        CommandRiskLevel = executor_mod.CommandRiskLevel

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=None)  # NO writes during execution!

    # ═══════════════════════════════════════════════════════════════
    # STEP 1: SHOW RESOURCE SELECTION IN PERMISSION BUFFER
    # ═══════════════════════════════════════════════════════════════

    # Get system resources
    resources = await docker_async.get_system_resources()
    cpu_count = resources.get('cpu_count', 4)
    memory_gb = resources.get('memory_gb', 8)

    # Show resource selection IN PERMISSION BUFFER
    prompt_input = app.query_one("#prompt-input")

    from modules.permission_prompt import PermissionResponse

    resource_prompt = {
        'title': 'Docker: /docker ollama setup',
        'message': f'Choose resource allocation:\n\n'
                   f'Your system: {cpu_count} CPUs, {memory_gb:.1f}GB RAM\n\n'
                   f'Conservative settings are safest for daily use.',
        'options': [
            {
                'text': f'Conservative (4 CPUs, 8GB RAM) - Recommended',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'cpu_limit': '4', 'memory_limit': '8g', 'gpu_enabled': False}
            },
            {
                'text': f'Balanced (6 CPUs, 12GB RAM)',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'cpu_limit': '6', 'memory_limit': '12g', 'gpu_enabled': False}
            },
            {
                'text': 'With GPU Support (requires nvidia-docker)',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'cpu_limit': '6', 'memory_limit': '12g', 'gpu_enabled': True}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }

    prompt_input.permission_prompt_data = resource_prompt
    prompt_input.permission_selected_option = 0
    prompt_input.refresh(layout=True)

    # Wait for user selection
    session._awaiting_docker_resource_selection = True
    session._docker_resource_choice = None

    while session._awaiting_docker_resource_selection:
        await asyncio.sleep(0.1)

    # Get selected resources
    resource_data = getattr(session, '_docker_resource_choice', None)
    if not resource_data:
        # User cancelled
        prompt_input.permission_prompt_data = None
        prompt_input.refresh(layout=True)
        app.write("[yellow]Docker setup cancelled[/yellow]\n")
        return

    cpu_limit = resource_data.get('cpu_limit', '4')
    memory_limit = resource_data.get('memory_limit', '8g')
    gpu_enabled = resource_data.get('gpu_enabled', False)

    # ═══════════════════════════════════════════════════════════════
    # STEP 2: EXECUTE WORKFLOW IN PERMISSION BUFFER
    # ═══════════════════════════════════════════════════════════════

    # Create execution steps
    steps = []

    # Step 1: Check Docker daemon
    async def check_docker():
        is_running, msg = await docker_async.check_docker_running()
        if not is_running:
            raise Exception(f"Docker daemon not running: {msg}")
        return "Docker daemon is running"

    steps.append(CommandStep(
        id="check_docker",
        title="Check Docker daemon status",
        description="Verify Docker daemon is running",
        category="docker",
        requires_permission=False,
        risk_level=CommandRiskLevel.SAFE,
        execute_func=check_docker
    ))

    # Step 2: Check/remove existing container
    async def check_existing():
        container_id, status, name = await docker_async.get_ollama_container_status()
        if container_id:
            if status == 'running':
                return f"Container already running: {name}"
            else:
                # Remove failed/stopped container
                success, msg = await docker_async.remove_ollama_container(True)
                if not success:
                    raise Exception(f"Failed to remove existing container: {msg}")
                return f"Removed existing container: {name}"
        return "No existing container found"

    steps.append(CommandStep(
        id="check_existing",
        title="Check for existing Ollama containers",
        description="Check and remove any existing Ollama containers",
        category="docker",
        requires_permission=False,
        risk_level=CommandRiskLevel.LOW,
        execute_func=check_existing
    ))

    # Step 3: Pull Docker image
    async def pull_image():
        # Check if image exists
        import subprocess
        result = await asyncio.to_thread(
            subprocess.run,
            ["docker", "images", "-q", docker_mgr.OLLAMA_IMAGE],
            capture_output=True,
            text=True
        )

        if not result.stdout.strip():
            # Need to pull
            success, msg = await docker_async.pull_image(docker_mgr.OLLAMA_IMAGE)
            if not success:
                raise Exception(f"Failed to pull image: {msg}")
            return "Image pulled successfully (~2.7GB)"
        return "Image already cached"

    steps.append(CommandStep(
        id="pull_image",
        title="Pull Ollama Docker image (~2.7GB download)",
        description=f"Download {docker_mgr.OLLAMA_IMAGE} from Docker Hub if not cached",
        category="docker",
        requires_permission=True,
        risk_level=CommandRiskLevel.MEDIUM,
        execute_func=pull_image
    ))

    # Step 4: Create container
    async def create_container():
        success, result_msg = await docker_async.create_ollama_container(
            gpu_enabled, cpu_limit, memory_limit
        )
        if not success:
            raise Exception(f"Failed to create container: {result_msg}")
        return f"Container created: {result_msg[:12]}"

    resource_desc = f"{cpu_limit} CPUs, {memory_limit} RAM"
    if gpu_enabled:
        resource_desc += " + GPU"

    steps.append(CommandStep(
        id="create_container",
        title=f"Create Ollama container ({resource_desc})",
        description=f"Create container with resource limits: {resource_desc}",
        category="docker",
        requires_permission=True,
        risk_level=CommandRiskLevel.HIGH,
        execute_func=create_container
    ))

    # Step 5: Verify container running
    async def verify_running():
        is_running, container_id = await docker_async.is_ollama_running()
        if not is_running:
            raise Exception("Container created but failed to start")
        return f"Container running successfully"

    steps.append(CommandStep(
        id="verify_running",
        title="Verify container is running",
        description="Confirm Ollama container started successfully",
        category="docker",
        requires_permission=False,
        risk_level=CommandRiskLevel.SAFE,
        execute_func=verify_running
    ))

    # Define completion callback
    async def on_complete(execution):
        """Called when setup completes successfully"""
        if execution.status == "completed":
            app.write(f"\n[bold]Ollama is now available at:[/bold] [cyan]http://localhost:{docker_mgr.OLLAMA_PORT}[/cyan]\n\n")

            # Enable Docker stats in statusline
            try:
                from simple_tui import StatusLine
                status_line = app.query_one("StatusLine", StatusLine)
                status_line.enable_docker_stats(docker_mgr.OLLAMA_CONTAINER_NAME)
                app.write("[dim]✓ Docker stats monitoring enabled in statusline[/dim]\n\n")
            except Exception:
                pass

            app.write("[dim]Next steps:[/dim]\n")
            app.write("  1. [cyan]/providers add ollama[/cyan]  - Add as provider\n")
            app.write("  2. [cyan]/model[/cyan]  - See and switch to Ollama models\n")
            app.write("  3. [cyan]/docker ollama status[/cyan]  - Check container status\n\n")

    # Execute through unified command executor
    if app.command_executor:
        await app.command_executor.execute_command(
            command="/docker ollama setup",
            steps=steps,
            on_complete=on_complete
        )
    else:
        app.write("[red]✗ Unified command executor not available[/red]\n\n")


async def docker_ollama_start_unified(app, session):
    """Start Ollama container through unified executor"""

    try:
        from modules.docker_manager import DockerManager
        from modules.docker_async_handler import DockerAsyncHandler
        from modules.unified_command_executor import CommandStep, CommandRiskLevel
    except ImportError:
        import importlib
        docker_mgr_mod = importlib.import_module('docker_manager')
        DockerManager = docker_mgr_mod.DockerManager
        docker_async_mod = importlib.import_module('docker_async_handler')
        DockerAsyncHandler = docker_async_mod.DockerAsyncHandler
        executor_mod = importlib.import_module('unified_command_executor')
        CommandStep = executor_mod.CommandStep
        CommandRiskLevel = executor_mod.CommandRiskLevel

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=app.write)

    steps = []

    async def check_status():
        is_running, container_id = await docker_async.is_ollama_running()
        if is_running:
            raise Exception("Container is already running")

        # Check if container exists
        container_id, status, name = await docker_async.get_ollama_container_status()
        if not container_id:
            raise Exception("No Ollama container found. Run '/docker ollama setup' first")

        return f"Found container: {name} (status: {status})"

    steps.append(CommandStep(
        id="check_status",
        title="Check container status",
        description="Verify Ollama container exists",
        category="docker",
        requires_permission=False,
        risk_level=CommandRiskLevel.SAFE,
        execute_func=check_status
    ))

    async def start_container():
        container_id, status, name = await docker_async.get_ollama_container_status()
        success, msg = await docker_async.start_container(name)
        if not success:
            raise Exception(f"Failed to start: {msg}")
        return "Container started successfully"

    steps.append(CommandStep(
        id="start_container",
        title="Start Ollama container",
        description="Start the Ollama Docker container",
        category="docker",
        requires_permission=True,
        risk_level=CommandRiskLevel.MEDIUM,
        execute_func=start_container
    ))

    if app.command_executor:
        await app.command_executor.execute_command(
            command="/docker ollama start",
            steps=steps
        )
    else:
        app.write("[red]✗ Unified command executor not available[/red]\n\n")


async def docker_ollama_stop_unified(app, session):
    """Stop Ollama container through unified executor"""

    try:
        from modules.docker_manager import DockerManager
        from modules.docker_async_handler import DockerAsyncHandler
        from modules.unified_command_executor import CommandStep, CommandRiskLevel
    except ImportError:
        import importlib
        docker_mgr_mod = importlib.import_module('docker_manager')
        DockerManager = docker_mgr_mod.DockerManager
        docker_async_mod = importlib.import_module('docker_async_handler')
        DockerAsyncHandler = docker_async_mod.DockerAsyncHandler
        executor_mod = importlib.import_module('unified_command_executor')
        CommandStep = executor_mod.CommandStep
        CommandRiskLevel = executor_mod.CommandRiskLevel

    docker_mgr = DockerManager()
    docker_async = DockerAsyncHandler(docker_mgr, debug_callback=app.write)

    steps = []

    async def check_running():
        is_running, container_id = await docker_async.is_ollama_running()
        if not is_running:
            raise Exception("Container is not running")
        return f"Container is running: {container_id[:12]}"

    steps.append(CommandStep(
        id="check_running",
        title="Check if container is running",
        description="Verify Ollama container is currently running",
        category="docker",
        requires_permission=False,
        risk_level=CommandRiskLevel.SAFE,
        execute_func=check_running
    ))

    async def stop_container():
        container_id, status, name = await docker_async.get_ollama_container_status()
        success, msg = await docker_async.stop_container(name, timeout=10)
        if not success:
            raise Exception(f"Failed to stop: {msg}")
        return "Container stopped successfully"

    steps.append(CommandStep(
        id="stop_container",
        title="Stop Ollama container",
        description="Stop the running Ollama Docker container",
        category="docker",
        requires_permission=True,
        risk_level=CommandRiskLevel.MEDIUM,
        execute_func=stop_container
    ))

    if app.command_executor:
        await app.command_executor.execute_command(
            command="/docker ollama stop",
            steps=steps
        )
    else:
        app.write("[red]✗ Unified command executor not available[/red]\n\n")
