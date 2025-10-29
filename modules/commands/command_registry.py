"""Command Registration - All command handlers registered here

Imports and registers all slash commands with SDK enforcement.
Called by main registry.py during initialization.
"""

from modules.execution.registry import ExecutionType, ExecutionCategory, RiskLevel


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
        show_help, show_help_prompt,
        show_status, show_status_prompt,
        clear_history, clear_history_prompt,
        list_background_tasks, list_background_tasks_prompt,
        show_command_overview, show_command_overview_prompt,
        show_permissions, show_permissions_prompt,
        exit_session, exit_session_prompt,
        quit_session, quit_session_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/help', show_help,
        ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
        description="Show available commands with descriptions",
        custom_prompt_func=show_help_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/status', show_status,
        ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
        description="Display current session status",
        custom_prompt_func=show_status_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/clear', clear_history,
        ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
        description="Clear chat history for this session",
        custom_prompt_func=clear_history_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/bashes', list_background_tasks,
        ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
        description="List background shell tasks",
        custom_prompt_func=list_background_tasks_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/commands', show_command_overview,
        ExecutionCategory.SYSTEM, RiskLevel.SAFE, requires_approval=True,
        description="Show enabled/disabled command permissions",
        custom_prompt_func=show_command_overview_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/permissions', show_permissions,
        ExecutionCategory.SYSTEM, RiskLevel.SAFE, requires_approval=True,
        description="Show stored permission decisions",
        custom_prompt_func=show_permissions_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/exit', exit_session,
        ExecutionCategory.SYSTEM, RiskLevel.SAFE, requires_approval=True,
        description="Exit the OpenCLI session",
        custom_prompt_func=exit_session_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/quit', quit_session,
        ExecutionCategory.SYSTEM, RiskLevel.SAFE, requires_approval=True,
        description="Exit the OpenCLI session",
        custom_prompt_func=quit_session_prompt,
    )

    # ========================================================================
    # AGENT COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering agent commands", current_file="agent_commands.py", cmd_count=len(executor.registry.commands))
    from .agent_commands import (
        agent_main, agent_main_prompt,
        list_agents, list_agents_prompt,
        agent_assistant, agent_assistant_prompt,
        agent_debugger, agent_debugger_prompt,
        agent_reviewer, agent_reviewer_prompt,
        agent_refactor, agent_refactor_prompt,
        agent_tester, agent_tester_prompt,
        agent_documenter, agent_documenter_prompt,
        agent_architect, agent_architect_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/agent', agent_main,
        ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
        description="Switch to a specific agent",
        custom_prompt_func=agent_main_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/agents', list_agents,
        ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
        description="List available agents",
        custom_prompt_func=list_agents_prompt,
    )

    for name, handler, prompt_func in [
        ('/agent assistant', agent_assistant, agent_assistant_prompt),
        ('/agent debugger', agent_debugger, agent_debugger_prompt),
        ('/agent reviewer', agent_reviewer, agent_reviewer_prompt),
        ('/agent refactor', agent_refactor, agent_refactor_prompt),
        ('/agent tester', agent_tester, agent_tester_prompt),
        ('/agent documenter', agent_documenter, agent_documenter_prompt),
        ('/agent architect', agent_architect, agent_architect_prompt),
    ]:
        await _safe_register(
            executor, ExecutionType.COMMAND, name, handler,
            ExecutionCategory.BASIC, RiskLevel.SAFE, requires_approval=True,
            description=f"Switch to the {name.split()[-1]} agent",
            custom_prompt_func=prompt_func,
        )

    # ========================================================================
    # DIFF COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering diff commands", current_file="diff_commands.py", cmd_count=len(executor.registry.commands))
    from .diff_commands import (
        diff_overview, diff_overview_prompt,
        diff_git, diff_git_prompt,
        diff_worktree, diff_worktree_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/diff', diff_overview,
        ExecutionCategory.DEV, RiskLevel.SAFE, requires_approval=True,
        description="Show working tree summary diff",
        custom_prompt_func=diff_overview_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/diff git', diff_git,
        ExecutionCategory.DEV, RiskLevel.SAFE, requires_approval=True,
        description="Show git diff against HEAD",
        custom_prompt_func=diff_git_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/diff worktree', diff_worktree,
        ExecutionCategory.DEV, RiskLevel.SAFE, requires_approval=True,
        description="Compare worktree with environment",
        custom_prompt_func=diff_worktree_prompt,
    )

    # ========================================================================
    # DOCKER COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering docker commands", current_file="docker_commands.py", cmd_count=len(executor.registry.commands))
    from modules.docker_commands import (
        docker_main, docker_main_prompt,
        docker_ollama_setup, docker_ollama_setup_prompt,
        docker_ollama_start, docker_ollama_start_prompt,
        docker_ollama_stop, docker_ollama_stop_prompt,
        docker_status, docker_status_prompt,
        docker_ps, docker_ps_prompt,
        docker_stats, docker_stats_prompt,
        docker_ollama_status, docker_ollama_status_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker', docker_main,
        ExecutionCategory.DOCKER, RiskLevel.SAFE, requires_approval=True,
        description="Docker operations and management",
        custom_prompt_func=docker_main_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker status', docker_status,
        ExecutionCategory.DOCKER, RiskLevel.SAFE, requires_approval=True,
        description="Show Docker daemon status",
        custom_prompt_func=docker_status_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker ps', docker_ps,
        ExecutionCategory.DOCKER, RiskLevel.SAFE, requires_approval=True,
        description="List running Docker containers",
        custom_prompt_func=docker_ps_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker stats', docker_stats,
        ExecutionCategory.DOCKER, RiskLevel.SAFE, requires_approval=True,
        description="Show resource usage for containers",
        custom_prompt_func=docker_stats_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker ollama setup', docker_ollama_setup,
        ExecutionCategory.DOCKER, RiskLevel.HIGH, requires_approval=True,
        description="Setup Ollama in Docker with resource configuration",
        estimated_duration="2-3 minutes",
        custom_prompt_func=docker_ollama_setup_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker ollama start', docker_ollama_start,
        ExecutionCategory.DOCKER, RiskLevel.MEDIUM, requires_approval=True,
        description="Start Ollama Docker container",
        custom_prompt_func=docker_ollama_start_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker ollama stop', docker_ollama_stop,
        ExecutionCategory.DOCKER, RiskLevel.LOW, requires_approval=True,
        description="Stop Ollama Docker container",
        custom_prompt_func=docker_ollama_stop_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/docker ollama status', docker_ollama_status,
        ExecutionCategory.DOCKER, RiskLevel.SAFE, requires_approval=True,
        description="Show Ollama container status",
        custom_prompt_func=docker_ollama_status_prompt,
    )

    # ========================================================================
    # DEV COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering dev commands", current_file="dev_commands.py", cmd_count=len(executor.registry.commands))
    from .dev_commands import (
        debug_toggle, debug_toggle_prompt,
        performance_monitor, performance_monitor_prompt,
        reload_modules, reload_modules_prompt,
        test_tui, test_tui_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/debug', debug_toggle,
        ExecutionCategory.DEV, RiskLevel.SAFE, requires_approval=True,
        description="Toggle debug mode on/off",
        custom_prompt_func=debug_toggle_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/performance', performance_monitor,
        ExecutionCategory.DEV, RiskLevel.SAFE, requires_approval=True,
        description="Show performance metrics",
        custom_prompt_func=performance_monitor_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/reload', reload_modules,
        ExecutionCategory.DEV, RiskLevel.MEDIUM, requires_approval=True,
        description="Reload modules (may affect running session)",
        custom_prompt_func=reload_modules_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/test-tui', test_tui,
        ExecutionCategory.DEV, RiskLevel.SAFE, requires_approval=True,
        description="Generate TUI test template script with API examples",
        custom_prompt_func=test_tui_prompt,
    )

    # ========================================================================
    # MODEL COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering model commands", current_file="model_commands.py", cmd_count=len(executor.registry.commands))
    from .model_commands import (
        model_list, model_list_prompt,
        model_switch, model_switch_prompt,
        model_list_providers, model_list_providers_prompt,
        model_switch_recent_1, model_switch_recent_1_prompt,
        model_switch_recent_2, model_switch_recent_2_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/model', model_list,
        ExecutionCategory.MODEL, RiskLevel.SAFE, requires_approval=True,
        description="List available models",
        custom_prompt_func=model_list_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/model list', model_list,
        ExecutionCategory.MODEL, RiskLevel.SAFE, requires_approval=True,
        description="List available models",
        custom_prompt_func=model_list_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/model providers', model_list_providers,
        ExecutionCategory.MODEL, RiskLevel.SAFE, requires_approval=True,
        description="List configured providers",
        custom_prompt_func=model_list_providers_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/model r1', model_switch_recent_1,
        ExecutionCategory.MODEL, RiskLevel.SAFE, requires_approval=True,
        description="Switch to most recent model",
        custom_prompt_func=model_switch_recent_1_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/model r2', model_switch_recent_2,
        ExecutionCategory.MODEL, RiskLevel.SAFE, requires_approval=True,
        description="Switch to second most recent model",
        custom_prompt_func=model_switch_recent_2_prompt,
    )

    # ========================================================================
    # PROVIDER COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering provider commands", current_file="provider_commands.py", cmd_count=len(executor.registry.commands))
    from .provider_commands import (
        provider_manage, provider_manage_prompt,
        provider_list, provider_list_prompt,
        provider_add, provider_add_prompt,
        provider_add_ollama, provider_add_ollama_prompt,
        provider_remove, provider_remove_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/provider', provider_manage,
        ExecutionCategory.PROVIDER, RiskLevel.LOW, requires_approval=True,
        description="Manage API providers (OpenAI, Anthropic, Google, etc.)",
        custom_prompt_func=provider_manage_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/providers', provider_manage,
        ExecutionCategory.PROVIDER, RiskLevel.LOW, requires_approval=True,
        description="Manage API providers (OpenAI, Anthropic, Google, etc.)",
        custom_prompt_func=provider_manage_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/providers list', provider_list,
        ExecutionCategory.PROVIDER, RiskLevel.SAFE, requires_approval=True,
        description="List configured providers",
        custom_prompt_func=provider_list_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/providers add', provider_add,
        ExecutionCategory.PROVIDER, RiskLevel.MEDIUM, requires_approval=True,
        description="Add provider API key",
        custom_prompt_func=provider_add_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/providers add ollama', provider_add_ollama,
        ExecutionCategory.PROVIDER, RiskLevel.SAFE, requires_approval=True,
        description="Register local Ollama provider",
        custom_prompt_func=provider_add_ollama_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/providers remove', provider_remove,
        ExecutionCategory.PROVIDER, RiskLevel.LOW, requires_approval=True,
        description="Remove stored provider API key",
        custom_prompt_func=provider_remove_prompt,
    )

    # ========================================================================
    # LOCAL COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering local commands", current_file="local_commands.py", cmd_count=len(executor.registry.commands))
    from .local_commands import (
        local_setup, local_setup_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/local', local_setup,
        ExecutionCategory.SYSTEM, RiskLevel.MEDIUM, requires_approval=True,
        description="Setup local model deployment",
        estimated_duration="< 1 minute",
        custom_prompt_func=local_setup_prompt,
    )

    # ========================================================================
    # SPEC COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering spec commands", current_file="spec_commands.py", cmd_count=len(executor.registry.commands))
    from .spec_commands import (
        run_specify, run_specify_prompt,
        run_constitution, run_constitution_prompt,
        run_plan, run_plan_prompt,
        run_tasks, run_tasks_prompt,
        run_implement, run_implement_prompt,
        run_test, run_test_prompt,
        run_spec_check, run_spec_check_prompt,
    )

    for name, handler, prompt_func, desc in [
        ('/specify', run_specify, run_specify_prompt, "Create a project specification"),
        ('/constitution', run_constitution, run_constitution_prompt, "Create project principles and guidelines"),
        ('/plan', run_plan, run_plan_prompt, "Create a technical implementation plan"),
        ('/tasks', run_tasks, run_tasks_prompt, "Break plan into actionable tasks"),
        ('/implement', run_implement, run_implement_prompt, "Implementation workflow guidance"),
        ('/test', run_test, run_test_prompt, "Testing strategy guidance"),
        ('/spec-check', run_spec_check, run_spec_check_prompt, "Validate spec completeness"),
    ]:
        await _safe_register(
            executor, ExecutionType.COMMAND, name, handler,
            ExecutionCategory.SPEC, RiskLevel.SAFE, requires_approval=True,
            description=desc,
            custom_prompt_func=prompt_func,
        )

    # ========================================================================
    # REFACTOR COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering refactor commands", current_file="refactor_commands.py", cmd_count=len(executor.registry.commands))
    from .refactor_commands import (
        refactor_interactive, refactor_interactive_prompt,
        autorefactor, autorefactor_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/refactor', refactor_interactive,
        ExecutionCategory.REFACTOR, RiskLevel.MEDIUM, requires_approval=True,
        description="Interactive code refactoring",
        custom_prompt_func=refactor_interactive_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/autorefactor', autorefactor,
        ExecutionCategory.REFACTOR, RiskLevel.HIGH, requires_approval=True,
        description="Automated code refactoring (use with caution)",
        custom_prompt_func=autorefactor_prompt,
    )

    # ========================================================================
    # SYSTEM COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering system commands", current_file="system_commands.py", cmd_count=len(executor.registry.commands))
    from .system_commands import (
        restart_session, restart_session_prompt,
        upgrade_opencli, upgrade_opencli_prompt,
        rollback_opencli, rollback_opencli_prompt,
        api_server_control, api_server_control_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/restart', restart_session,
        ExecutionCategory.SYSTEM, RiskLevel.LOW, requires_approval=True,
        description="Restart current session",
        custom_prompt_func=restart_session_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/upgrade', upgrade_opencli,
        ExecutionCategory.SYSTEM, RiskLevel.HIGH, requires_approval=True,
        description="Upgrade OpenCLI to latest version",
        custom_prompt_func=upgrade_opencli_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/rollback', rollback_opencli,
        ExecutionCategory.SYSTEM, RiskLevel.MEDIUM, requires_approval=True,
        description="Show available OpenCLI backups",
        custom_prompt_func=rollback_opencli_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/api', api_server_control,
        ExecutionCategory.SYSTEM, RiskLevel.MEDIUM, requires_approval=True,
        description="Control API server (start/stop/status)",
        custom_prompt_func=api_server_control_prompt,
    )

    for sub_name in ['start', 'stop', 'status']:
        await _safe_register(
            executor, ExecutionType.COMMAND, f'/api {sub_name}', api_server_control,
            ExecutionCategory.SYSTEM, RiskLevel.MEDIUM, requires_approval=True,
            description=f"{sub_name.title()} the API server",
            custom_prompt_func=api_server_control_prompt,
        )

    # ========================================================================
    # INJECTION COMMANDS
    # ========================================================================
    _update_sdk_buffer(executor.app, current_step="Registering injection commands", current_file="inject_commands.py", cmd_count=len(executor.registry.commands))
    from .inject_commands import (
        code_inject, code_inject_prompt,
    )

    await _safe_register(
        executor, ExecutionType.COMMAND, '/inject', code_inject,
        ExecutionCategory.DEV, RiskLevel.CRITICAL, requires_approval=True,
        description="Inject code into running process (DANGEROUS)",
        custom_prompt_func=code_inject_prompt,
    )
