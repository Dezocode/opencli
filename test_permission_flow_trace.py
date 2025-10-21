#!/usr/bin/env python3
"""
Comprehensive test to trace permission system flow and identify bypass
"""
import pytest
import asyncio
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

from textual.pilot import Pilot
from modules.tui.core import OpenCLITUI
from modules.multiline_input import MultiLineInput
from cli.session import Session
from modules.async_interactive.core import interactive_async


# Track execution flow
execution_trace = []


def trace_call(location, *args, **kwargs):
    """Track function calls"""
    execution_trace.append({
        'location': location,
        'args': args,
        'kwargs': kwargs
    })
    print(f"[TRACE] {location}", file=sys.stderr)


@pytest.fixture(autouse=True)
def reset_trace():
    """Reset execution trace before each test"""
    global execution_trace
    execution_trace = []
    yield
    # Print final trace
    print("\n[TRACE] === EXECUTION FLOW ===", file=sys.stderr)
    for i, entry in enumerate(execution_trace):
        print(f"[TRACE] {i+1}. {entry['location']}", file=sys.stderr)


@pytest.mark.asyncio
async def test_permission_system_flow():
    """Test complete permission system flow for SDK commands"""

    print("\n[TEST] ========== PERMISSION SYSTEM FLOW TEST ==========")

    # Setup patches to trace execution
    original_check_permission = None
    original_execute = None
    original_show_permission_prompt = None

    # Import modules to patch
    from modules.execution import permission_manager
    from modules.execution import executor

    # Store originals
    if hasattr(permission_manager, 'PermissionManager'):
        PM = permission_manager.PermissionManager
        original_check_permission = PM.check_permission
        original_show_permission_prompt = PM._show_permission_prompt

    check_permission_called = []
    show_prompt_called = []
    execute_called = []

    async def traced_check_permission(self, registration, context, app=None, session=None):
        """Traced check_permission"""
        trace_call(f"PermissionManager.check_permission(registration.name={registration.name})")
        check_permission_called.append({
            'registration': registration,
            'context': context,
            'requires_approval': registration.requires_approval
        })
        print(f"[TRACE] check_permission called for {registration.name}, requires_approval={registration.requires_approval}", file=sys.stderr)
        # Call original
        return await original_check_permission(self, registration, context, app, session)

    async def traced_show_prompt(self, app, session, registration, risk, context):
        """Traced _show_permission_prompt"""
        trace_call(f"PermissionManager._show_permission_prompt(registration.name={registration.name})")
        show_prompt_called.append({
            'registration': registration,
            'risk': risk,
            'has_custom_prompt': registration.metadata.get('custom_prompt_func') if registration.metadata else None
        })
        print(f"[TRACE] _show_permission_prompt called for {registration.name}", file=sys.stderr)
        print(f"[TRACE] custom_prompt_func = {registration.metadata.get('custom_prompt_func') if registration.metadata else None}", file=sys.stderr)
        # Call original
        return await original_show_permission_prompt(self, app, session, registration, risk, context)

    # Apply patches
    if original_check_permission:
        PM.check_permission = traced_check_permission
        PM._show_permission_prompt = traced_show_prompt

    # Setup app
    session = Session(model='test_model')
    config = {'model': 'test_model', 'baseURL': 'https://api.example.com/v1'}

    app_container = {}
    original_set_message_handler = OpenCLITUI.set_message_handler

    def new_set_message_handler(self, handler):
        app_container['app'] = self
        trace_call("OpenCLITUI.set_message_handler")
        original_set_message_handler(self, handler)

    with patch.object(OpenCLITUI, 'set_message_handler', new_set_message_handler):
        with patch.object(OpenCLITUI, 'run_async', return_value=None):
            startup_task = asyncio.create_task(interactive_async(config, session))
            await asyncio.sleep(0.3)

    assert 'app' in app_container, "Failed to capture app instance"
    app_instance = app_container['app']

    print(f"[TEST] App instance captured: {app_instance}")

    async with app_instance.run_test() as pilot:
        print("[TEST] Entering run_test context")

        # Get input widget
        input_widget = pilot.app.query_one("#prompt-input", MultiLineInput)
        print(f"[TEST] Got input widget: {input_widget}")

        # Type /help command
        input_widget.value = "/help"
        trace_call("input_widget.value = '/help'")
        print("[TEST] Set input value to /help")

        # Press enter
        trace_call("pilot.press('enter')")
        print("[TEST] Pressing enter...")
        await pilot.press("enter")
        print("[TEST] Enter pressed")

        # Wait for processing
        await pilot.pause(1.0)
        print("[TEST] Waited 1 second for processing")

        # Check results
        print(f"\n[TEST] ===== RESULTS =====")
        print(f"[TEST] check_permission called: {len(check_permission_called)} times")
        print(f"[TEST] show_prompt called: {len(show_prompt_called)} times")
        print(f"[TEST] permission_prompt_data: {input_widget.permission_prompt_data}")

        if check_permission_called:
            for i, call in enumerate(check_permission_called):
                print(f"[TEST] check_permission[{i}]: {call['registration'].name}, requires_approval={call['requires_approval']}")
        else:
            print("[TEST] ❌ check_permission WAS NEVER CALLED!")

        if show_prompt_called:
            for i, call in enumerate(show_prompt_called):
                print(f"[TEST] show_prompt[{i}]: {call['registration'].name}, custom_prompt={call['has_custom_prompt']}")
        else:
            print("[TEST] ❌ show_prompt WAS NEVER CALLED!")

        # Verify permission system was used
        assert len(check_permission_called) > 0, (
            "Permission system was bypassed! check_permission was never called. "
            "This means SDK commands are executing without permission checks."
        )

        assert len(show_prompt_called) > 0, (
            "Permission prompt was never shown! _show_permission_prompt was never called. "
            "This means the permission buffer is not being displayed."
        )

        assert input_widget.permission_prompt_data is not None, (
            "Permission buffer was never populated! permission_prompt_data is still None. "
            "This means the widget is not receiving prompt data from the permission manager."
        )

        print("[TEST] ✅ All permission system checks passed!")

    # Cleanup
    if original_check_permission:
        PM.check_permission = original_check_permission
        PM._show_permission_prompt = original_show_permission_prompt

    startup_task.cancel()
    try:
        await startup_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_trace_command_router():
    """Trace how CommandRouter handles /help command"""

    print("\n[TEST] ========== COMMAND ROUTER TRACE TEST ==========")

    from modules.command_router import CommandRouter

    original_route = CommandRouter.route_command
    route_called = []

    async def traced_route(self, command_text):
        """Traced route_command"""
        trace_call(f"CommandRouter.route_command(command_text='{command_text}')")
        route_called.append(command_text)
        print(f"[TRACE] route_command called with: {command_text}", file=sys.stderr)
        result = await original_route(self, command_text)
        print(f"[TRACE] route_command returned: {result}", file=sys.stderr)
        return result

    CommandRouter.route_command = traced_route

    # Setup app
    session = Session(model='test_model')
    config = {'model': 'test_model', 'baseURL': 'https://api.example.com/v1'}

    app_container = {}
    original_set_message_handler = OpenCLITUI.set_message_handler

    def new_set_message_handler(self, handler):
        app_container['app'] = self
        original_set_message_handler(self, handler)

    with patch.object(OpenCLITUI, 'set_message_handler', new_set_message_handler):
        with patch.object(OpenCLITUI, 'run_async', return_value=None):
            startup_task = asyncio.create_task(interactive_async(config, session))
            await asyncio.sleep(0.3)

    app_instance = app_container['app']

    async with app_instance.run_test() as pilot:
        input_widget = pilot.app.query_one("#prompt-input", MultiLineInput)

        input_widget.value = "/help"
        await pilot.press("enter")
        await pilot.pause(1.0)

        print(f"\n[TEST] ===== ROUTER RESULTS =====")
        print(f"[TEST] route_command called: {len(route_called)} times")
        if route_called:
            for i, cmd in enumerate(route_called):
                print(f"[TEST] route_command[{i}]: '{cmd}'")
        else:
            print("[TEST] ⚠️  route_command was never called - command may be handled elsewhere")

    # Restore
    CommandRouter.route_command = original_route

    startup_task.cancel()
    try:
        await startup_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
