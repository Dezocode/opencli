"""Dev Commands - debug, performance, reload - SDK COMPLIANT

SDK-COMPLIANT: All commands use interactive permission buffer pages.
User interaction happens in buffer, handlers execute based on selections.
"""

# SDK-compliant imports only
from modules.permissions import PermissionResponse
# Legacy import removed - using unified_permission_manager via SDK executor


# ============================================================================
# /debug - Toggle debug mode
# ============================================================================

def debug_toggle_prompt(app, session, registration, context):
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
    return prompt_data


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

def performance_monitor_prompt(app, session, registration, context):
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
    return prompt_data


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

def reload_modules_prompt(app, session, registration, context):
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
    return prompt_data


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


# ============================================================================
# /test-tui - Generate TUI test template script
# ============================================================================

def test_tui_prompt(app, session, registration, context):
    """Interactive prompt for /test-tui command"""

    prompt_data = {
        'title': 'System: /test-tui',
        'message': """# Generate TUI Test Template

Creates a shell script template showing how to configure and run TUI tests via the API.

**What gets created:**
• Shell script with TUI test API examples
• Pre-configured test patterns
• Visual and headless test modes
• Function detection examples

**File:** `test_tui_template.sh`

**Confirm action:**""",
        'options': [
            {
                'text': 'Generate test template script',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'generate'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def test_tui(app, session, **context):
    """Generate TUI test template script - SDK COMPLIANT"""

    # Get user selection
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[red]Error: No selection made[/red]\n\n")
        return

    data = prompt_data.get('data', {})
    action = data.get('action')

    if action != 'generate':
        app.write("[yellow]» Test template generation cancelled[/yellow]\n\n")
        return

    # Create template script
    template_path = "test_tui_template.sh"

    template_content = '''#!/bin/bash
# ============================================================================
# TUI Test Framework - API Template
# Generated by opencli /test-tui command
# ============================================================================
#
# IMPORTANT: Framework automatically cleans up old tests before starting new ones!
# - Kills old tmux sessions (tui_test_*)
# - Kills old controller processes
# - Removes stale temp files
# This means each test run starts fresh - no manual cleanup needed!
#
# ============================================================================

# PATTERN 1: Quick Permission Buffer Test
# Tests if permission buffer appears for a command
python3 << 'PYTHON_EOF'
from modules.testing import create_permission_buffer_test

# Create pre-configured test for /help command
test = create_permission_buffer_test("/help")

# Run with visual windows (opens LEFT=TUI, RIGHT=Controller)
# Framework will auto-cleanup old tests before running
result = test.run_test(visual=True)

print()
print("Test Result:", "✅ PASSED" if result.passed else "❌ FAILED")

# Check if any functions failed
if result.failing_functions:
    print("\\nFailing Functions Found:")
    for func in result.failing_functions:
        print(f"  - {func.get('function')} at {func.get('file')}:{func.get('line')}")
PYTHON_EOF


# PATTERN 2: Custom Navigation Test
# Build a custom test sequence with arrow key validation
python3 << 'PYTHON_EOF'
from modules.testing import TUITestFramework, TestStep

# Create framework instance
framework = TUITestFramework(sdk_init_wait=11)

# Build test sequence
framework.add_step(TestStep.TYPE, "/help", "Type /help command")
framework.add_step(TestStep.ENTER, description="Autocomplete", wait_after=1)
framework.add_step(TestStep.ENTER, description="Submit command", wait_after=4)

# Test navigation with BEFORE/AFTER comparison
framework.add_step(TestStep.DOWN, description="Press DOWN arrow", wait_after=2)
framework.add_step(TestStep.VERIFY_SELECTION,
                  description="Verify 'No' selected",
                  expected_state={"selected": "No"})

framework.add_step(TestStep.UP, description="Press UP arrow", wait_after=2)
framework.add_step(TestStep.VERIFY_SELECTION,
                  description="Verify back to 'Yes'",
                  expected_state={"selected": "Yes"})

# Run test
result = framework.run_test(visual=True)
print("Navigation Test:", "✅ PASSED" if result.passed else "❌ FAILED")
PYTHON_EOF


# PATTERN 3: Headless Test (CI/CD Mode)
# Run test without visual windows, just get results
python3 << 'PYTHON_EOF'
from modules.testing import create_permission_buffer_test
import sys

# Create test
test = create_permission_buffer_test("/help")

# Run headless (no windows opened)
result = test.run_test(visual=False)

# Exit with appropriate code for CI/CD
if result.passed:
    print("✅ Test PASSED - Permission buffer working")
    sys.exit(0)
else:
    print("❌ Test FAILED")
    if result.failing_functions:
        print("Failing functions:")
        for func in result.failing_functions:
            print(f"  {func['function']} at {func['file']}:{func['line']}")
    sys.exit(1)
PYTHON_EOF


# PATTERN 4: Test Multiple Commands
# Loop through commands and test each one
python3 << 'PYTHON_EOF'
from modules.testing import create_permission_buffer_test

commands_to_test = ["/help", "/agent", "/model", "/provider"]
failed_tests = []

for cmd in commands_to_test:
    print(f"\\nTesting {cmd}...")
    test = create_permission_buffer_test(cmd)
    result = test.run_test(visual=False)

    if result.passed:
        print(f"  ✅ {cmd} PASSED")
    else:
        print(f"  ❌ {cmd} FAILED")
        failed_tests.append(cmd)

print("\\n" + "="*60)
if not failed_tests:
    print("✅ ALL TESTS PASSED")
else:
    print(f"❌ {len(failed_tests)} tests failed: {', '.join(failed_tests)}")
PYTHON_EOF


# PATTERN 5: Custom Validation
# Use custom verification function for specific checks
python3 << 'PYTHON_EOF'
from modules.testing import TUITestFramework, TestStep

def custom_verify(state):
    """Custom verification function"""
    output = state.get('output', '')
    return 'Expected text' in output

framework = TUITestFramework()
framework.add_step(TestStep.TYPE, "/custom_command")
framework.add_step(TestStep.ENTER)
framework.add_step(
    TestStep.COLLECT_STATE,
    description="Verify custom condition",
    verify_fn=custom_verify,
    wait_after=2
)

result = framework.run_test(visual=True)
print("Custom Validation:", "✅ PASSED" if result.passed else "❌ FAILED")
PYTHON_EOF


# PATTERN 6: State Collection and Analysis
# Collect TUI state at different points for analysis
python3 << 'PYTHON_EOF'
from modules.testing import TUITestFramework, TestStep

framework = TUITestFramework()

# Execute command
framework.add_step(TestStep.TYPE, "/help")
framework.add_step(TestStep.ENTER, wait_after=4)

# Collect state before navigation
framework.add_step(TestStep.COLLECT_STATE, description="State before DOWN")

# Navigate
framework.add_step(TestStep.DOWN, wait_after=1)

# Collect state after navigation
framework.add_step(TestStep.COLLECT_STATE, description="State after DOWN")

result = framework.run_test(visual=True)

# Analyze collected states
print("\\nState Analysis:")
for detail in result.details.get('states', []):
    print(f"  {detail}")
PYTHON_EOF


echo ""
echo "============================================================================"
echo "TUI Test Template Complete"
echo "============================================================================"
echo ""
echo "Available Test Steps:"
echo "  - TestStep.TYPE        # Type text"
echo "  - TestStep.ENTER       # Press Enter"
echo "  - TestStep.DOWN        # DOWN arrow (auto BEFORE/AFTER detection)"
echo "  - TestStep.UP          # UP arrow (auto BEFORE/AFTER detection)"
echo "  - TestStep.ESCAPE      # ESC key"
echo "  - TestStep.WAIT        # Wait seconds"
echo "  - TestStep.COLLECT_STATE      # Capture TUI state"
echo "  - TestStep.VERIFY_SELECTION   # Verify selection state"
echo ""
echo "Auto-Detection Features:"
echo "  ✓ Permission buffer presence"
echo "  ✓ Yes/No options displayed"
echo "  ✓ Navigation (arrow keys working)"
echo "  ✓ Selection changes (BEFORE/AFTER)"
echo "  ✓ Failing functions (exact file + line number)"
echo ""
echo "Visual Mode (development):"
echo "  • LEFT window: Shows actual opencli tui"
echo "  • RIGHT window: Shows test commands & data collection"
echo "  • Use: run_test(visual=True)"
echo ""
echo "Headless Mode (CI/CD):"
echo "  • No windows opened"
echo "  • Returns TestResult object"
echo "  • Use: run_test(visual=False)"
echo ""
'''

    try:
        with open(template_path, 'w') as f:
            f.write(template_content)

        import os
        os.chmod(template_path, 0o755)

        app.write(f"[green]✓ Test template created: {template_path}[/green]\n\n")
        app.write("[dim]The template contains 6 patterns:\n")
        app.write("  1. Quick Permission Buffer Test\n")
        app.write("  2. Custom Navigation Test\n")
        app.write("  3. Headless Test (CI/CD)\n")
        app.write("  4. Test Multiple Commands\n")
        app.write("  5. Custom Validation\n")
        app.write("  6. State Collection & Analysis\n\n")
        app.write(f"Run with: [cyan]bash {template_path}[/cyan]\n")
        app.write(f"Or execute individual patterns from the file\n\n")

    except Exception as e:
        app.write(f"[red]Error creating template: {e}[/red]\n\n")
