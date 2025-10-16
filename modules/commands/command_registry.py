"""Command Registration - All command handlers registered here

Imports and registers all slash commands with SDK enforcement.
Called by main registry.py during initialization.
"""

from ..execution.registry import ExecutionType, ExecutionCategory, RiskLevel


async def register_all_commands(executor, _safe_register, _update_sdk_buffer):
    """Register ALL commands - ASYNC

    Args:
        executor: ExecutionSystem instance
        _safe_register: SDK-enforced registration function
        _update_sdk_buffer: Live progress update function
    """

    # ========================================================================
    # BASIC COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering basic commands", current_file="basic_commands.py")
    from .basic_commands import (
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
        executor, ExecutionType.COMMAND, '/help', show_help,
        ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
        description="Show available commands with descriptions",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/status', show_status,
        ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
        description="Display current session status",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/clear', clear_history,
        ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
        description="Clear chat history for this session",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/bashes', list_background_tasks,
        ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
        description="List background shell tasks",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/commands', show_command_overview,
        ExecutionCategory.SYSTEM, RiskLevel.SAFE, requires_approval=True,
        description="Show enabled/disabled command permissions",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/permissions', show_permissions,
        ExecutionCategory.SYSTEM, RiskLevel.SAFE, requires_approval=True,
        description="Show stored permission decisions",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/exit', exit_session,
        ExecutionCategory.SYSTEM, RiskLevel.SAFE, requires_approval=True,
        description="Exit the OpenCLI session",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/quit', quit_session,
        ExecutionCategory.SYSTEM, RiskLevel.SAFE, requires_approval=True,
        description="Exit the OpenCLI session",
    )

    # ========================================================================
    # AGENT COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering agent commands", current_file="agent_commands.py", cmd_count=len(executor.registry.commands))
    from .agent_commands import (
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
        executor, ExecutionType.COMMAND, '/agent', agent_main,
        ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
        description="Switch to a specific agent",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/agents', list_agents,
        ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
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
            executor, ExecutionType.COMMAND, name, handler,
            ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
            description=f"Switch to the {name.split()[-1]} agent",
        )

    # ========================================================================
    # DIFF COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering diff commands", current_file="diff_commands.py", cmd_count=len(executor.registry.commands))
    from .diff_commands import (
        diff_overview,
        diff_git,
        diff_worktree,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/diff', diff_overview,
        ExecutionCategory.DEV, RiskLevel.SAFE, requires_approval=True,
        description="Show working tree summary diff",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/diff git', diff_git,
        ExecutionCategory.DEV, RiskLevel.SAFE, requires_approval=True,
        description="Show git diff against HEAD",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/diff worktree', diff_worktree,
        ExecutionCategory.DEV, RiskLevel.SAFE, requires_approval=True,
        description="Compare worktree with environment",
    )

    # ========================================================================
    # DOCKER COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering docker commands", current_file="docker_commands.py", cmd_count=len(executor.registry.commands))
    from ..docker_commands import (
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
        executor, ExecutionType.COMMAND, '/docker', docker_main,
        ExecutionCategory.DOCKER, RiskLevel.SAFE, requires_approval=True,
        description="Docker operations and management",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker status', docker_status,
        ExecutionCategory.DOCKER, RiskLevel.SAFE, requires_approval=True,
        description="Show Docker daemon status",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker ps', docker_ps,
        ExecutionCategory.DOCKER, RiskLevel.SAFE, requires_approval=True,
        description="List running Docker containers",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker stats', docker_stats,
        ExecutionCategory.DOCKER, RiskLevel.SAFE, requires_approval=True,
        description="Show resource usage for containers",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker ollama setup', docker_ollama_setup,
        ExecutionCategory.DOCKER, RiskLevel.HIGH, requires_approval=True,
        description="Setup Ollama in Docker with resource configuration",
        estimated_duration="2-3 minutes",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker ollama start', docker_ollama_start,
        ExecutionCategory.DOCKER, RiskLevel.MEDIUM, requires_approval=True,
        description="Start Ollama Docker container",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker ollama stop', docker_ollama_stop,
        ExecutionCategory.DOCKER, RiskLevel.LOW, requires_approval=True,
        description="Stop Ollama Docker container",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker ollama status', docker_ollama_status,
        ExecutionCategory.DOCKER, RiskLevel.SAFE, requires_approval=True,
        description="Show Ollama container status",
    )

    # ========================================================================
    # DEV COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering dev commands", current_file="dev_commands.py", cmd_count=len(executor.registry.commands))
    from .dev_commands import (
        debug_toggle,
        performance_monitor,
        reload_modules,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/debug', debug_toggle,
        ExecutionCategory.DEV, RiskLevel.SAFE, requires_approval=True,
        description="Toggle debug mode on/off",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/performance', performance_monitor,
        ExecutionCategory.DEV, RiskLevel.SAFE, requires_approval=True,
        description="Show performance metrics",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/reload', reload_modules,
        ExecutionCategory.DEV, RiskLevel.MEDIUM, requires_approval=True,
        description="Reload modules (may affect running session)",
    )

    # ========================================================================
    # MODEL COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering model commands", current_file="model_commands.py", cmd_count=len(executor.registry.commands))
    from .model_commands import (
        model_list,
        model_switch,
        model_list_providers,
        model_switch_recent_1,
        model_switch_recent_2,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/model', model_list,
        ExecutionCategory.MODEL, RiskLevel.SAFE, requires_approval=True,
        description="List available models",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/model list', model_list,
        ExecutionCategory.MODEL, RiskLevel.SAFE, requires_approval=True,
        description="List available models",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/model providers', model_list_providers,
        ExecutionCategory.MODEL, RiskLevel.SAFE, requires_approval=True,
        description="List configured providers",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/model r1', model_switch_recent_1,
        ExecutionCategory.MODEL, RiskLevel.SAFE, requires_approval=True,
        description="Switch to most recent model",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/model r2', model_switch_recent_2,
        ExecutionCategory.MODEL, RiskLevel.SAFE, requires_approval=True,
        description="Switch to second most recent model",
    )

    # ========================================================================
    # PROVIDER COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering provider commands", current_file="provider_commands.py", cmd_count=len(executor.registry.commands))
    from .provider_commands import (
        provider_manage,
        provider_list,
        provider_add,
        provider_add_ollama,
        provider_remove,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/provider', provider_manage,
        ExecutionCategory.PROVIDER, RiskLevel.LOW, requires_approval=True,
        description="Manage API providers (OpenAI, Anthropic, Google, etc.)",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/providers', provider_manage,
        ExecutionCategory.PROVIDER, RiskLevel.LOW, requires_approval=True,
        description="Manage API providers (OpenAI, Anthropic, Google, etc.)",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/providers list', provider_list,
        ExecutionCategory.PROVIDER, RiskLevel.SAFE, requires_approval=True,
        description="List configured providers",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/providers add', provider_add,
        ExecutionCategory.PROVIDER, RiskLevel.MEDIUM, requires_approval=True,
        description="Add provider API key",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/providers add ollama', provider_add_ollama,
        ExecutionCategory.PROVIDER, RiskLevel.SAFE, requires_approval=True,
        description="Register local Ollama provider",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/providers remove', provider_remove,
        ExecutionCategory.PROVIDER, RiskLevel.LOW, requires_approval=True,
        description="Remove stored provider API key",
    )

    # ========================================================================
    # LOCAL COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering local commands", current_file="local_commands.py", cmd_count=len(executor.registry.commands))
    from .local_commands import (
        local_setup,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/local', local_setup,
        ExecutionCategory.SYSTEM, RiskLevel.MEDIUM, requires_approval=True,
        description="Setup local model deployment",
        estimated_duration="< 1 minute",
    )

    # ========================================================================
    # SPEC COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering spec commands", current_file="spec_commands.py", cmd_count=len(executor.registry.commands))
    from .spec_commands import (
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
            executor, ExecutionType.COMMAND, name, handler,
            ExecutionCategory.SPEC, RiskLevel.SAFE, requires_approval=True,
            description=desc,
        )

    # ========================================================================
    # REFACTOR COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering refactor commands", current_file="refactor_commands.py", cmd_count=len(executor.registry.commands))
    from .refactor_commands import (
        refactor_interactive,
        autorefactor,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/refactor', refactor_interactive,
        ExecutionCategory.REFACTOR, RiskLevel.MEDIUM, requires_approval=True,
        description="Interactive code refactoring",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/autorefactor', autorefactor,
        ExecutionCategory.REFACTOR, RiskLevel.HIGH, requires_approval=True,
        description="Automated code refactoring (use with caution)",
    )

    # ========================================================================
    # SYSTEM COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering system commands", current_file="system_commands.py", cmd_count=len(executor.registry.commands))
    from .system_commands import (
        restart_session,
        upgrade_opencli,
        rollback_opencli,
        api_server_control,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/restart', restart_session,
        ExecutionCategory.SYSTEM, RiskLevel.LOW, requires_approval=True,
        description="Restart current session",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/upgrade', upgrade_opencli,
        ExecutionCategory.SYSTEM, RiskLevel.HIGH, requires_approval=True,
        description="Upgrade OpenCLI to latest version",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/rollback', rollback_opencli,
        ExecutionCategory.SYSTEM, RiskLevel.MEDIUM, requires_approval=True,
        description="Show available OpenCLI backups",
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/api', api_server_control,
        ExecutionCategory.SYSTEM, RiskLevel.MEDIUM, requires_approval=True,
        description="Control API server (start/stop/status)",
    )

    for sub_name in ['start', 'stop', 'status']:
        await _safe_register(
            executor, ExecutionType.COMMAND, f'/api {sub_name}', api_server_control,
            ExecutionCategory.SYSTEM, RiskLevel.MEDIUM, requires_approval=True,
            description=f"{sub_name.title()} the API server",
        )

    # ========================================================================
    # INJECTION COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering injection commands", current_file="inject_commands.py", cmd_count=len(executor.registry.commands))
    from .inject_commands import (
        code_inject,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/inject', code_inject,
        ExecutionCategory.DEV, RiskLevel.CRITICAL, requires_approval=True,
        description="Inject code into running process (DANGEROUS)",
    )
