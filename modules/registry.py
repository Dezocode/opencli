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

from .execution.registry import ExecutionType, ExecutionCategory, RiskLevel
from .sdk.enforcement import enforce_handler, EnforcementAction
from .sdk.validation import validate_full_coverage


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

    # ========================================================================
    # COVERAGE VALIDATION
    # ========================================================================
    print("[SDK] Validating registration coverage…")
    validate_full_coverage(executor)


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

    # Update SDK loading dropdown (if app available)
    if hasattr(executor, 'app') and executor.app:
        try:
            from sdk import get_enforcement
            enforcement = get_enforcement()

            # Update live count in dropdown
            cmd_count = len(executor.registry.commands)
            tool_count = len(executor.registry.tools)

            # Update SDK loading dropdown
            sdk_buffer = executor.app.query_one("#sdk-loading")
            sdk_buffer.update_progress(
                command_count=cmd_count,
                tool_count=tool_count,
                accepted_count=enforcement.accepted_count,
                converted_count=enforcement.converted_count,
                rejected_count=enforcement.rejected_count,
                latest_module=name
            )
        except Exception as e:
            # Silently fail - don't break registration
            pass


async def _register_commands(executor):
    """Register ALL commands - ASYNC"""

    # BASIC COMMANDS
    from commands.basic_commands import (
        show_help,
        show_status,
        clear_history,
        list_background_tasks,
        show_command_overview,
        show_permissions,
        exit_session,
        quit_session,
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/help',
        show_help,
        ExecutionCategory.BASIC,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Show available commands with descriptions",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/status',
        show_status,
        ExecutionCategory.BASIC,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Display current session status",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/clear',
        clear_history,
        ExecutionCategory.BASIC,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Clear chat history for this session",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/bashes',
        list_background_tasks,
        ExecutionCategory.BASIC,
        RiskLevel.SAFE,
        requires_approval=False,
        description="List background shell tasks",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/commands',
        show_command_overview,
        ExecutionCategory.SYSTEM,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Show enabled/disabled command permissions",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/permissions',
        show_permissions,
        ExecutionCategory.SYSTEM,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Show stored permission decisions",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/exit',
        exit_session,
        ExecutionCategory.SYSTEM,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Exit the OpenCLI session",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/quit',
        quit_session,
        ExecutionCategory.SYSTEM,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Exit the OpenCLI session",
    )

    # AGENT COMMANDS
    from commands.agent_commands import (
        agent_main,
        list_agents,
        agent_assistant,
        agent_debugger,
        agent_reviewer,
        agent_refactor,
        agent_tester,
        agent_documenter,
        agent_architect,
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/agent',
        agent_main,
        ExecutionCategory.BASIC,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Switch to a specific agent",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/agents',
        list_agents,
        ExecutionCategory.BASIC,
        RiskLevel.SAFE,
        requires_approval=False,
        description="List available agents",
    )

    for name, handler in [
        ('/agent assistant', agent_assistant),
        ('/agent debugger', agent_debugger),
        ('/agent reviewer', agent_reviewer),
        ('/agent refactor', agent_refactor),
        ('/agent tester', agent_tester),
        ('/agent documenter', agent_documenter),
        ('/agent architect', agent_architect),
    ]:
        await _safe_register(
            executor,
            ExecutionType.COMMAND,
            name,
            handler,
            ExecutionCategory.BASIC,
            RiskLevel.SAFE,
            requires_approval=False,
            description=f"Switch to the {name.split()[-1]} agent",
        )

    # DIFF COMMANDS
    from commands.diff_commands import (
        diff_overview,
        diff_git,
        diff_worktree,
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/diff',
        diff_overview,
        ExecutionCategory.DEV,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Show working tree summary diff",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/diff git',
        diff_git,
        ExecutionCategory.DEV,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Show git diff against HEAD",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/diff worktree',
        diff_worktree,
        ExecutionCategory.DEV,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Compare worktree with environment",
    )

    # DOCKER COMMANDS
    from docker_commands import (
        docker_main,
        docker_ollama_setup,
        docker_ollama_start,
        docker_ollama_stop,
        docker_status,
        docker_ps,
        docker_stats,
        docker_ollama_status,
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/docker',
        docker_main,
        ExecutionCategory.DOCKER,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Docker operations and management",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/docker status',
        docker_status,
        ExecutionCategory.DOCKER,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Show Docker daemon status",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/docker ps',
        docker_ps,
        ExecutionCategory.DOCKER,
        RiskLevel.SAFE,
        requires_approval=False,
        description="List running Docker containers",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/docker stats',
        docker_stats,
        ExecutionCategory.DOCKER,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Show resource usage for containers",
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
        estimated_duration="2-3 minutes",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/docker ollama start',
        docker_ollama_start,
        ExecutionCategory.DOCKER,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Start Ollama Docker container",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/docker ollama stop',
        docker_ollama_stop,
        ExecutionCategory.DOCKER,
        RiskLevel.LOW,
        requires_approval=False,
        description="Stop Ollama Docker container",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/docker ollama status',
        docker_ollama_status,
        ExecutionCategory.DOCKER,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Show Ollama container status",
    )

    # DEV COMMANDS
    from commands.dev_commands import (
        debug_toggle,
        performance_monitor,
        reload_modules,
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/debug',
        debug_toggle,
        ExecutionCategory.DEV,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Toggle debug mode on/off",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/performance',
        performance_monitor,
        ExecutionCategory.DEV,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Show performance metrics",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/reload',
        reload_modules,
        ExecutionCategory.DEV,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Reload modules (may affect running session)",
    )

    # MODEL COMMANDS
    from commands.model_commands import (
        model_list,
        model_switch,
        model_list_providers,
        model_switch_recent_1,
        model_switch_recent_2,
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/model',
        model_list,
        ExecutionCategory.MODEL,
        RiskLevel.SAFE,
        requires_approval=False,
        description="List available models",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/model list',
        model_list,
        ExecutionCategory.MODEL,
        RiskLevel.SAFE,
        requires_approval=False,
        description="List available models",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/model providers',
        model_list_providers,
        ExecutionCategory.MODEL,
        RiskLevel.SAFE,
        requires_approval=False,
        description="List configured providers",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/model r1',
        model_switch_recent_1,
        ExecutionCategory.MODEL,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Switch to most recent model",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/model r2',
        model_switch_recent_2,
        ExecutionCategory.MODEL,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Switch to second most recent model",
    )

    # PROVIDER COMMANDS
    from commands.provider_commands import (
        provider_manage,
        provider_list,
        provider_add,
        provider_add_ollama,
        provider_remove,
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/provider',
        provider_manage,
        ExecutionCategory.PROVIDER,
        RiskLevel.LOW,
        requires_approval=False,
        description="Manage API providers (OpenAI, Anthropic, Google, etc.)",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/providers',
        provider_manage,
        ExecutionCategory.PROVIDER,
        RiskLevel.LOW,
        requires_approval=False,
        description="Manage API providers (OpenAI, Anthropic, Google, etc.)",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/providers list',
        provider_list,
        ExecutionCategory.PROVIDER,
        RiskLevel.SAFE,
        requires_approval=False,
        description="List configured providers",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/providers add',
        provider_add,
        ExecutionCategory.PROVIDER,
        RiskLevel.MEDIUM,
        requires_approval=False,
        description="Add provider API key",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/providers add ollama',
        provider_add_ollama,
        ExecutionCategory.PROVIDER,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Register local Ollama provider",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/providers remove',
        provider_remove,
        ExecutionCategory.PROVIDER,
        RiskLevel.LOW,
        requires_approval=False,
        description="Remove stored provider API key",
    )

    # LOCAL COMMANDS
    from commands.local_commands import (
        local_setup,
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
        estimated_duration="< 1 minute",
    )

    # SPEC COMMANDS
    from commands.spec_commands import (
        run_specify,
        run_constitution,
        run_plan,
        run_tasks,
        run_implement,
        run_test,
        run_spec_check,
    )

    for name, handler, desc in [
        ('/specify', run_specify, "Create a project specification"),
        ('/constitution', run_constitution, "Create project principles and guidelines"),
        ('/plan', run_plan, "Create a technical implementation plan"),
        ('/tasks', run_tasks, "Break plan into actionable tasks"),
        ('/implement', run_implement, "Implementation workflow guidance"),
        ('/test', run_test, "Testing strategy guidance"),
        ('/spec-check', run_spec_check, "Validate spec completeness"),
    ]:
        await _safe_register(
            executor,
            ExecutionType.COMMAND,
            name,
            handler,
            ExecutionCategory.SPEC,
            RiskLevel.SAFE,
            requires_approval=False,
            description=desc,
        )

    # REFACTOR COMMANDS
    from commands.refactor_commands import (
        refactor_interactive,
        autorefactor,
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/refactor',
        refactor_interactive,
        ExecutionCategory.REFACTOR,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Interactive code refactoring",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/autorefactor',
        autorefactor,
        ExecutionCategory.REFACTOR,
        RiskLevel.HIGH,
        requires_approval=True,
        description="Automated code refactoring (use with caution)",
    )

    # SYSTEM COMMANDS
    from commands.system_commands import (
        restart_session,
        upgrade_opencli,
        rollback_opencli,
        api_server_control,
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/restart',
        restart_session,
        ExecutionCategory.SYSTEM,
        RiskLevel.LOW,
        requires_approval=False,
        description="Restart current session",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/upgrade',
        upgrade_opencli,
        ExecutionCategory.SYSTEM,
        RiskLevel.HIGH,
        requires_approval=True,
        description="Upgrade OpenCLI to latest version",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/rollback',
        rollback_opencli,
        ExecutionCategory.SYSTEM,
        RiskLevel.MEDIUM,
        requires_approval=False,
        description="Show available OpenCLI backups",
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/api',
        api_server_control,
        ExecutionCategory.SYSTEM,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Control API server (start/stop/status)",
    )

    for sub_name in ['start', 'stop', 'status']:
        await _safe_register(
            executor,
            ExecutionType.COMMAND,
            f'/api {sub_name}',
            api_server_control,
            ExecutionCategory.SYSTEM,
            RiskLevel.MEDIUM,
            requires_approval=True,
            description=f"{sub_name.title()} the API server",
        )

    # INJECTION COMMANDS
    from commands.inject_commands import (
        code_inject,
    )

    await _safe_register(
        executor,
        ExecutionType.COMMAND,
        '/inject',
        code_inject,
        ExecutionCategory.DEV,
        RiskLevel.CRITICAL,
        requires_approval=True,
        description="Inject code into running process (DANGEROUS)",
    )


async def _register_tools(executor):
    """Register ALL tools - ASYNC"""

    from tools.core_tools import (
        tool_read,
        tool_write,
        tool_edit,
        tool_bash,
        tool_glob,
        tool_grep,
        tool_github,
        tool_configure_headers,
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'Read',
        tool_read,
        ExecutionCategory.FILE,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Read file contents",
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'Write',
        tool_write,
        ExecutionCategory.FILE,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Write or create a file",
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'Edit',
        tool_edit,
        ExecutionCategory.FILE,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Edit an existing file",
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'Glob',
        tool_glob,
        ExecutionCategory.SEARCH,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Find files by glob pattern",
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'Grep',
        tool_grep,
        ExecutionCategory.SEARCH,
        RiskLevel.SAFE,
        requires_approval=False,
        description="Search file contents via grep",
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'Bash',
        tool_bash,
        ExecutionCategory.BASH,
        RiskLevel.HIGH,
        requires_approval=True,
        description="Execute shell commands",
        timeout=120,
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'GitHub',
        tool_github,
        ExecutionCategory.NETWORK,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Perform authenticated GitHub operations",
    )

    await _safe_register(
        executor,
        ExecutionType.TOOL,
        'ConfigureHeaders',
        tool_configure_headers,
        ExecutionCategory.SYSTEM,
        RiskLevel.MEDIUM,
        requires_approval=True,
        description="Auto-configure API request headers for models",
    )
