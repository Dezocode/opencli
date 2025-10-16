"""Dev Commands - debug, performance, reload - SDK COMPLIANT

SDK-COMPLIANT: All commands use interactive permission buffer pages.
User interaction happens in buffer, handlers execute based on selections.
"""

# SDK-compliant imports only
from ..permission_prompt import PermissionResponse
from ..permission_buffer_manager import get_permission_buffer_manager


# ============================================================================
# /debug - Toggle debug mode
# ============================================================================

async def debug_toggle_prompt(app, session, registration, context):
    """Interactive prompt for /debug command"""

    current_debug_mode = getattr(session, 'debug_mode', False)
    new_state = not current_debug_mode

    prompt_data = {
        'title': 'System: /debug',
        'message': f"""# Toggle Debug Mode

**Current Mode:** {'Enabled' if current_debug_mode else 'Disabled'}
**New Mode:** {'Enabled' if new_state else 'Disabled'}

**Confirm action:**""",
        'options': [
            {
                'text': f'{"Enable" if new_state else "Disable"} debug mode',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'toggle', 'new_state': new_state}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }

    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def debug_toggle(app, session, **context):
    """Toggle debug mode - SDK COMPLIANT"""

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

    # Execute - toggle debug mode
    new_state = user_selection.get('new_state', False)
    session.debug_mode = new_state
    status = "enabled" if session.debug_mode else "disabled"
    color = "green" if session.debug_mode else "yellow"
    app.write(f"[{color}]✓ Debug mode {status}[/{color}]\n\n")


# ============================================================================
# /performance - Performance monitoring controls
# ============================================================================

async def performance_monitor_prompt(app, session, registration, context):
    """Interactive prompt for /performance command"""

    args = context.get('args', '')
    subcommand = args.strip() if args else None

    if subcommand == "report":
        action_desc = "Generate detailed performance report"
    elif subcommand == "fast":
        fast_mode = getattr(session, 'fast_mode', False)
        action_desc = f"Toggle fast mode (currently {'enabled' if fast_mode else 'disabled'})"
    else:
        action_desc = "Toggle performance monitoring statusline"

    prompt_data = {
        'title': 'System: /performance',
        'message': f"""# Performance Monitor

**Action:** {action_desc}
**Subcommand:** {subcommand if subcommand else 'toggle statusline'}

**Confirm action:**""",
        'options': [
            {
                'text': 'Execute performance command',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute', 'subcommand': subcommand}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }

    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def performance_monitor(app, session, **context):
    """Performance monitoring controls - SDK COMPLIANT"""

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

    subcommand = user_selection.get('subcommand')

    # Execute based on subcommand
    try:
        from performance_monitor import get_monitor
    except ImportError:
        try:
            from modules.performance_monitor import get_monitor
        except ImportError:
            app.write("[red]Error: performance_monitor module not available[/red]\n\n")
            return

    perf_monitor = get_monitor()

    if subcommand == "report":
        # Show detailed report
        app.write(perf_monitor.get_detailed_report())
        return

    if subcommand == "fast":
        # Toggle fast mode (skip markdown rendering for speed)
        if not hasattr(session, 'fast_mode'):
            session.fast_mode = False

        session.fast_mode = not session.fast_mode
        status = "enabled" if session.fast_mode else "disabled"
        color = "green" if session.fast_mode else "yellow"

        app.write(f"[{color}]» Fast mode {status}[/{color}]\n\n")
        if session.fast_mode:
            app.write("[dim]Optimizations enabled:\n")
            app.write("  • Skipped markdown post-processing\n")
            app.write("  • Raw text rendering only\n")
            app.write("  • Maximum token throughput\n\n")
            app.write("! Note: Markdown formatting will not render\n\n")
        else:
            app.write("[dim]Markdown rendering restored\n\n")
        return

    # Toggle monitoring via statusline widget
    try:
        from simple_tui import PerformanceStatusLine
    except ImportError:
        try:
            from modules.simple_tui import PerformanceStatusLine
        except ImportError:
            app.write("[red]Error: PerformanceStatusLine not available[/red]\n\n")
            return

    try:
        perf_statusline = app.query_one(PerformanceStatusLine)
        is_enabled = perf_statusline.toggle()

        if is_enabled:
            app.write("[green]▪ Performance monitoring enabled[/green]\n\n")
            app.write("[dim]Live statusline active beneath prompt showing:\n")
            app.write("  • CPU usage and trend (↗️↘️→)\n")
            app.write("  • Memory usage (MB)\n")
            app.write("  • Thread count\n")
            app.write("  • » Token streaming speed (tok/s)\n")
            app.write("  • Bottlenecks (if any)\n\n")
            app.write("Use [cyan]/performance report[/cyan] for detailed analysis\n")
            app.write("Use [cyan]/performance fast[/cyan] to toggle fast mode\n\n")
        else:
            app.write("[yellow]▪ Performance monitoring disabled[/yellow]\n\n")
    except Exception as e:
        app.write(f"[red]Error: Could not toggle performance monitor: {e}[/red]\n\n")


# ============================================================================
# /reload - Hot-reload modules
# ============================================================================

async def reload_modules_prompt(app, session, registration, context):
    """Interactive prompt for /reload command"""

    prompt_data = {
        'title': 'System: /reload',
        'message': """# Reload Modules

**Action:** Clear cache and reload all modules
**Impact:** Changes to command handlers, utilities, etc. will be active

**Warning:** This clears Python bytecode cache

**Confirm action:**""",
        'options': [
            {
                'text': 'Reload all modules',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'reload'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }

    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def reload_modules(app, session, **context):
    """Hot-reload modules - SDK COMPLIANT"""

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

    # Execute - reload modules
    try:
        from cache_manager import get_cache_manager
    except ImportError:
        try:
            from modules.cache_manager import get_cache_manager
        except ImportError:
            app.write("[red]Error: cache_manager module not available[/red]\n\n")
            return

    app.write("[cyan]▸ Reloading OpenCLI modules...[/cyan]\n\n")

    manager = get_cache_manager()

    # Check for stale cache first
    stale = manager.find_all_stale_cache()
    if stale:
        app.write(f"[yellow]! Found {len(stale)} modules with stale cache[/yellow]\n")
        for s in stale[:5]:  # Show first 5
            age = int(s['age_seconds'])
            app.write(f"  [dim]{s['module']} (source {age}s newer)[/dim]\n")
        if len(stale) > 5:
            app.write(f"  [dim]... and {len(stale) - 5} more[/dim]\n")
        app.write("\n")

    # Clear cache
    app.write("[dim]Clearing Python bytecode cache...[/dim]\n")
    result_clear = manager.clear_cache(verbose=False)
    app.write(f"[green]✓ Removed {result_clear['pyc_files']} .pyc files, {result_clear['pycache_dirs']} __pycache__ dirs[/green]\n\n")

    # Reload modules
    app.write("[dim]Reloading modules...[/dim]\n")
    reload_result = manager.reload_modules()

    if reload_result['errors']:
        app.write(f"[yellow]⚠ Reloaded {reload_result['count']} modules with {len(reload_result['errors'])} errors[/yellow]\n")
        for err in reload_result['errors'][:3]:
            app.write(f"  [red]{err['module']}: {err['error']}[/red]\n")
    else:
        app.write(f"[green]✓ Reloaded {reload_result['count']} modules successfully[/green]\n")

    app.write("\n[dim]Modules reloaded. Changes to command handlers, utilities, etc. are now active.[/dim]\n\n")
