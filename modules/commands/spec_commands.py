"""
Spec-driven workflow commands powered by the Spec-Kit wrapper - SDK COMPLIANT

SDK-COMPLIANT: All commands use interactive permission buffer pages.
User interaction happens in buffer, handlers execute based on selections.
"""

from __future__ import annotations

from modules.specify_wrapper import SpecifyWrapper

# SDK-compliant imports only
from modules.permissions import PermissionResponse
# Legacy import removed - using unified_permission_manager via SDK executor


def _render_result(app, result, heading: str):
    """Helper to render Spec-Kit command output."""
    app.write(f"[bold cyan]{heading}[/bold cyan]\n")
    if not result:
        app.write("[red]Spec-Kit integration is unavailable.[/red]\n\n")
        return

    if result.get("success"):
        output = result.get("output") or "Command executed."
        app.write(f"{output}\n\n")
    else:
        error = result.get("error") or "Unknown failure."
        app.write(f"[red]{error}[/red]\n\n")


# ============================================================================
# /specify - Define project specification
# ============================================================================

def run_specify_prompt(app, session, registration, context):
    """Interactive prompt for /specify command"""

    content = (context.get("args") or "").strip()
    has_content = bool(content)

    prompt_data = {
        'title': 'System: /specify',
        'message': f"""# Specification Workflow

**Content Provided:** {'Yes' if has_content else 'No (will use defaults)'}
**Estimated Duration:** 2-3 minutes

**Workflow Steps:**
1. Define project specification
2. Establish requirements
3. Document constraints
4. Save specification to .specify/

**Select action:**""",
        'options': [
            {
                'text': 'Execute specification workflow',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute', 'content': content}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def run_specify(app, session, **context):
    """Entry point for `/specify` - SDK COMPLIANT"""

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

    # Execute - run specify
    content = user_selection.get('content', '') or "(no content provided)"
    wrapper = SpecifyWrapper()
    formatted = wrapper.format_spec_for_ai("/specify", content)
    _render_result(app, {"success": True, "output": formatted}, "Specification Guidance")


# ============================================================================
# /constitution - Define project principles
# ============================================================================

def run_constitution_prompt(app, session, registration, context):
    """Interactive prompt for /constitution command"""

    content = (context.get("args") or "").strip()
    has_content = bool(content)

    prompt_data = {
        'title': 'System: /constitution',
        'message': f"""# Constitution Workflow

**Content Provided:** {'Yes' if has_content else 'No (will use defaults)'}
**Estimated Duration:** 1-2 minutes

**Workflow Steps:**
1. Define project principles
2. Establish coding standards
3. Document architectural guidelines

**Select action:**""",
        'options': [
            {
                'text': 'Execute constitution workflow',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute', 'content': content}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def run_constitution(app, session, **context):
    """Run constitution command - SDK COMPLIANT"""

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

    # Execute - run constitution
    content = user_selection.get('content', '') or "(no content provided)"
    wrapper = SpecifyWrapper()
    formatted = wrapper.format_spec_for_ai("/constitution", content)
    _render_result(app, {"success": True, "output": formatted}, "Project Principles")


# ============================================================================
# /plan - Create implementation plan
# ============================================================================

def run_plan_prompt(app, session, registration, context):
    """Interactive prompt for /plan command"""

    content = (context.get("args") or "").strip()
    has_content = bool(content)

    prompt_data = {
        'title': 'System: /plan',
        'message': f"""# Plan Workflow

**Content Provided:** {'Yes' if has_content else 'No (will use defaults)'}
**Estimated Duration:** 2-4 minutes

**Workflow Steps:**
1. Create implementation plan
2. Break down technical approach
3. Document dependencies

**Select action:**""",
        'options': [
            {
                'text': 'Execute plan workflow',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute', 'content': content}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def run_plan(app, session, **context):
    """Run plan command - SDK COMPLIANT"""

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

    # Execute - run plan
    content = user_selection.get('content', '') or "(no content provided)"
    wrapper = SpecifyWrapper()
    formatted = wrapper.format_spec_for_ai("/plan", content)
    _render_result(app, {"success": True, "output": formatted}, "Implementation Plan Outline")


# ============================================================================
# /tasks - Break plan into tasks
# ============================================================================

def run_tasks_prompt(app, session, registration, context):
    """Interactive prompt for /tasks command"""

    prompt_data = {
        'title': 'System: /tasks',
        'message': """# Tasks Workflow

**Estimated Duration:** 1-2 minutes

**Workflow Steps:**
1. Break plan into tasks
2. Prioritize task list
3. Generate task breakdown template

**Select action:**""",
        'options': [
            {
                'text': 'Execute tasks workflow',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def run_tasks(app, session, **context):
    """Run tasks command - SDK COMPLIANT"""

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

    # Execute - run tasks
    wrapper = SpecifyWrapper()
    formatted = wrapper.format_spec_for_ai("/tasks", "")
    _render_result(app, {"success": True, "output": formatted}, "Task Breakdown Template")


# ============================================================================
# /implement - Execute development workflow
# ============================================================================

def run_implement_prompt(app, session, registration, context):
    """Interactive prompt for /implement command"""

    prompt_data = {
        'title': 'System: /implement',
        'message': """# Implement Workflow

**Estimated Duration:** Varies by task

**Workflow Steps:**
1. Review implementation plan
2. Execute development workflow
3. Follow architectural guidelines

**Select action:**""",
        'options': [
            {
                'text': 'Execute implement workflow',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def run_implement(app, session, **context):
    """Run implement command - SDK COMPLIANT"""

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

    # Execute - run implement
    wrapper = SpecifyWrapper()
    formatted = wrapper.format_spec_for_ai("/implement", "")
    _render_result(app, {"success": True, "output": formatted}, "Implementation Workflow")


# ============================================================================
# /test - Generate testing strategy
# ============================================================================

def run_test_prompt(app, session, registration, context):
    """Interactive prompt for /test command"""

    prompt_data = {
        'title': 'System: /test',
        'message': """# Test Workflow

**Estimated Duration:** 1-2 minutes

**Workflow Steps:**
1. Generate testing strategy
2. Define test coverage requirements
3. Create test plan template

**Select action:**""",
        'options': [
            {
                'text': 'Execute test workflow',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'execute'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def run_test(app, session, **context):
    """Run test command - SDK COMPLIANT"""

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

    # Execute - run test
    wrapper = SpecifyWrapper()
    formatted = wrapper.format_spec_for_ai("/test", "")
    _render_result(app, {"success": True, "output": formatted}, "Testing Guidance")


# ============================================================================
# /spec-check - Check spec completeness
# ============================================================================

def run_spec_check_prompt(app, session, registration, context):
    """Interactive prompt for /spec-check command"""

    prompt_data = {
        'title': 'System: /spec-check',
        'message': """# Spec Check

**Type:** Specification validation
**Action:** Check spec completeness and consistency

**Select action:**""",
        'options': [
            {
                'text': 'Run spec check',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'check'}
            },
            {
                'text': 'Run and export to file',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'export'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def run_spec_check(app, session, **context):
    """Run spec check command - SDK COMPLIANT"""

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

    # Execute - run spec check
    wrapper = SpecifyWrapper()
    result = wrapper.check_spec()
    _render_result(app, result, "Spec Check")

    # Handle export if selected
    if action == 'export' and result.get('success'):
        from pathlib import Path
        export_path = Path.cwd() / "spec-check-result.txt"
        with open(export_path, 'w') as f:
            f.write("Spec Check Result\n")
            f.write("=" * 40 + "\n\n")
            f.write(result.get("output", "No output") + "\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")
