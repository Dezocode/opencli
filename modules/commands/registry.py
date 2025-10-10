"""
Central Registration - ONE place for ALL commands and tools

Everything registers here with PROPER categorization.
NO duplicates, NO legacy code.

Every registration includes:
- ExecutionType (COMMAND, TOOL, API)
- ExecutionCategory (DOCKER, MODEL, FILE, etc.)
- RiskLevel (SAFE, LOW, MEDIUM, HIGH, CRITICAL)
- requires_approval (bool)
- description (str)

SDK ENFORCEMENT:
All handlers validated at registration time.
Non-compliant handlers auto-converted or rejected.

STREAMLINED FLOW:
register_all(executor) → SDK Enforcement → ExecutionRegistry → PermissionManager → Buffer
"""

from execution.registry import ExecutionType, ExecutionCategory, RiskLevel
from sdk.enforcement import enforce_handler, EnforcementAction


async def register_all(executor):
    """
    ONE registration function for EVERYTHING

    Enforces SDK compliance, then registers with ExecutionSystem.
    ALL ASYNC - non-blocking registration.
    """

    # ========================================================================
    # COMMANDS
    # ========================================================================
    await _register_commands(executor)

    # ========================================================================
    # TOOLS
    # ========================================================================
    await _register_tools(executor)


async def _safe_register(
    executor,
    exec_type: ExecutionType,
    name: str,
    handler,
    category: ExecutionCategory,
    risk_level: RiskLevel,
    requires_approval: bool,
    description: str,
    **kwargs
):
    """
    SDK-enforced registration with LIVE buffer update

    Validates handler, auto-converts if needed, then registers.
    Raises ValueError if handler cannot be made compliant.
    """
    # Enforce SDK compliance
    cat_name = category.value if hasattr(category, 'value') else str(category)

    print(f"[SDK] Enforcing: {name}")
    result = enforce_handler(name, handler, cat_name, auto_convert=True)
    print(f"[SDK]   Action: {result.action.value}")
    print(f"[SDK]   Compliance: {result.compliance.value}")
    print(f"[SDK]   Message: {result.message}")

    # Use final handler (may be converted/wrapped)
    final_handler = result.final_handler

    # Register with executor (ACTUAL registration, not recursive!)
    executor.registry.register(
        exec_type,
        name,
        final_handler,
        category,
        risk_level,
        requires_approval,
        description,
        **kwargs
    )

    # Update SDK loading buffer (if app available)
    if hasattr(executor, 'app') and executor.app:
        try:
            from sdk import get_enforcement
            enforcement = get_enforcement()

            # Update live count in buffer
            cmd_count = len(executor.registry.commands)
            tool_count = len(executor.registry.tools)

            loading_message = f"Validating and registering modules...\n\n"
            loading_message += f"[cyan]Registered so far:[/cyan]\n"
            loading_message += f"Commands: [cyan]{cmd_count}[/cyan] | Tools: [cyan]{tool_count}[/cyan]\n\n"
            loading_message += f"[green]✓ Compliant: {enforcement.accepted_count}[/green]\n"
            loading_message += f"[yellow]⚠ Converted: {enforcement.converted_count}[/yellow]\n"
            loading_message += f"[red]✗ Rejected: {enforcement.rejected_count}[/red]\n\n"
            loading_message += f"[dim]Latest: {name}[/dim]"

            prompt_input = executor.app.query_one("#prompt-input")
            if prompt_input.permission_prompt_data:
                # Update existing buffer
                prompt_input.permission_prompt_data['message'] = loading_message
                prompt_input.refresh(layout=True)
        except Exception as e:
            # Silently fail - don't break registration
            pass


async def _register_commands(executor):
    """Register ALL commands - ASYNC"""

    # ========================================================================
    # DOCKER COMMANDS
    # ========================================================================
    from docker_commands import (
        docker_main,
        docker_ollama_setup,
        docker_ollama_start,
        docker_ollama_stop
    )

    # Parent /docker command
    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/docker',
        docker_main,
        ExecutionCategory.DOCKER,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Docker operations and management"
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/docker ollama setup',
        docker_ollama_setup,
        ExecutionCategory.DOCKER,
        RiskLevel.HIGH,
        requires_approval=True,
        description="Setup Ollama in Docker with resource configuration",
        estimated_duration="2-3 minutes"
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/docker ollama start',
        docker_ollama_start,
        ExecutionCategory.DOCKER,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Start Ollama Docker container"
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/docker ollama stop',
        docker_ollama_stop,
        ExecutionCategory.DOCKER,
        RiskLevel.LOW,
        requires_approval=False,
        description="Stop Ollama Docker container"
    )

    # ========================================================================
    # DEV COMMANDS
    # ========================================================================
    from commands.dev_commands import (
        debug_toggle,
        performance_monitor,
        reload_modules
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/debug',
        debug_toggle,
        ExecutionCategory.DEV,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Toggle debug mode on/off"
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/performance',
        performance_monitor,
        ExecutionCategory.DEV,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Show performance metrics"
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/reload',
        reload_modules,
        ExecutionCategory.DEV,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Reload modules (may affect running session)"
    )

    # ========================================================================
    # MODEL COMMANDS
    # ========================================================================
    from commands.model_commands import (
        model_list,
        model_switch
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/model',
        model_list,
        ExecutionCategory.MODEL,
        RiskLevel.SAFE,
        requires_approval=False,
        description="List available models"
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/model list',
        model_list,
        ExecutionCategory.MODEL,
        RiskLevel.SAFE,
        requires_approval=False,
        description="List available models"
    )

    # ========================================================================
    # PROVIDER COMMANDS
    # ========================================================================
    from commands.provider_commands import (
        provider_manage
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/provider',
        provider_manage,
        ExecutionCategory.PROVIDER,
        RiskLevel.LOW,
        requires_approval=False,
        description="Manage API providers (OpenAI, Anthropic, Google, etc.)"
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/providers',
        provider_manage,
        ExecutionCategory.PROVIDER,
        RiskLevel.LOW,
        requires_approval=False,
        description="Manage API providers (OpenAI, Anthropic, Google, etc.)"
    )

    # ========================================================================
    # LOCAL COMMANDS
    # ========================================================================
    from commands.local_commands import (
        local_setup
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/local',
        local_setup,
        ExecutionCategory.SYSTEM,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Setup local model deployment",
        estimated_duration="< 1 minute"
    )

    # ========================================================================
    # REFACTOR COMMANDS
    # ========================================================================
    from commands.refactor_commands import (
        refactor_interactive,
        autorefactor
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/refactor',
        refactor_interactive,
        ExecutionCategory.REFACTOR,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Interactive code refactoring"
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/autorefactor',
        autorefactor,
        ExecutionCategory.REFACTOR,
        RiskLevel.HIGH,
        requires_approval=True,
        description="Automated code refactoring (use with caution)"
    )

    # ========================================================================
    # SYSTEM COMMANDS
    # ========================================================================
    from commands.system_commands import (
        restart_session,
        upgrade_opencli
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/restart',
        restart_session,
        ExecutionCategory.SYSTEM,
        RiskLevel.LOW,
        requires_approval=False,
        description="Restart current session"
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/upgrade',
        upgrade_opencli,
        ExecutionCategory.SYSTEM,
        RiskLevel.HIGH,
        requires_approval=True,
        description="Upgrade OpenCLI to latest version"
    )

    # ========================================================================
    # API COMMANDS
    # ========================================================================
    from commands.api_commands import (
        api_server_control
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/api',
        api_server_control,
        ExecutionCategory.SYSTEM,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Control API server (start/stop/status)"
    )

    # ========================================================================
    # INJECTION COMMANDS
    # ========================================================================
    from commands.inject_commands import (
        code_inject
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/inject',
        code_inject,
        ExecutionCategory.DEV,
        RiskLevel.CRITICAL,
        requires_approval=True,
        description="Inject code into running process (DANGEROUS)"
    )


async def _register_tools(executor):
    """Register ALL tools - ASYNC"""

    # ========================================================================
    # FILE TOOLS
    # ========================================================================
    from tools.file_tools import (
        file_read,
        file_write,
        file_edit
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'Read',
        file_read,
        ExecutionCategory.FILE,
        RiskLevel.LOW,
        requires_approval=False,
        description="Read file contents"
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'Write',
        file_write,
        ExecutionCategory.FILE,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Write/create file (overwrites existing)"
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'Edit',
        file_edit,
        ExecutionCategory.FILE,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Edit existing file"
    )

    # ========================================================================
    # SEARCH TOOLS
    # ========================================================================
    from tools.search_tools import (
        grep_search,
        glob_search
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'Grep',
        grep_search,
        ExecutionCategory.SEARCH,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Search file contents with regex"
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'Glob',
        glob_search,
        ExecutionCategory.SEARCH,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Find files by pattern"
    )

    # ========================================================================
    # EXECUTION TOOLS
    # ========================================================================
    from tools.exec_tools import (
        bash_execute
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'Bash',
        bash_execute,
        ExecutionCategory.BASH,
        RiskLevel.HIGH,
        requires_approval=True,
        description="Execute bash commands (HIGH RISK)"
    )

    # ========================================================================
    # NETWORK TOOLS
    # ========================================================================
    from tools.network_tools import (
        web_fetch,
        web_search
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'WebFetch',
        web_fetch,
        ExecutionCategory.NETWORK,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Fetch content from URL"
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'WebSearch',
        web_search,
        ExecutionCategory.NETWORK,
        RiskLevel.LOW,
        requires_approval=False,
        description="Search the web"
    )

    # ========================================================================
    # GITHUB TOOLS
    # ========================================================================
    from tools.github_tools import (
        github_api
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'GitHub',
        github_api,
        ExecutionCategory.NETWORK,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Interact with GitHub API"
    )
