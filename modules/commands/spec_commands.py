"""
Spec-driven workflow commands powered by the Spec-Kit wrapper.
"""

from __future__ import annotations

from specify_wrapper import SpecifyWrapper


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


async def run_specify(app, session, **context):
    """Entry point for `/specify`."""
    content = (context.get("args") or "").strip()
    wrapper = SpecifyWrapper()
    formatted = wrapper.format_spec_for_ai("/specify", content or "(no content provided)")
    _render_result(app, {"success": True, "output": formatted}, "Specification Guidance")


async def run_constitution(app, session, **context):
    content = (context.get("args") or "").strip()
    wrapper = SpecifyWrapper()
    formatted = wrapper.format_spec_for_ai("/constitution", content or "(no content provided)")
    _render_result(app, {"success": True, "output": formatted}, "Project Principles")


async def run_plan(app, session, **context):
    content = (context.get("args") or "").strip()
    wrapper = SpecifyWrapper()
    formatted = wrapper.format_spec_for_ai("/plan", content or "(no content provided)")
    _render_result(app, {"success": True, "output": formatted}, "Implementation Plan Outline")


async def run_tasks(app, session, **context):
    wrapper = SpecifyWrapper()
    formatted = wrapper.format_spec_for_ai("/tasks", "")
    _render_result(app, {"success": True, "output": formatted}, "Task Breakdown Template")


async def run_implement(app, session, **context):
    wrapper = SpecifyWrapper()
    formatted = wrapper.format_spec_for_ai("/implement", "")
    _render_result(app, {"success": True, "output": formatted}, "Implementation Workflow")


async def run_test(app, session, **context):
    wrapper = SpecifyWrapper()
    formatted = wrapper.format_spec_for_ai("/test", "")
    _render_result(app, {"success": True, "output": formatted}, "Testing Guidance")


async def run_spec_check(app, session, **context):
    wrapper = SpecifyWrapper()
    result = wrapper.check_spec()
    _render_result(app, result, "Spec Check")
