#!/usr/bin/env python3
"""
Comprehensive test to trace EXACT point where execution bypasses permission check
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


# Global trace log
execution_trace = []


def trace(location, details=""):
    """Log execution point"""
    msg = f"[TRACE] {location}"
    if details:
        msg += f": {details}"
    execution_trace.append(msg)
    print(msg, file=sys.stderr)


@pytest.fixture(autouse=True)
def reset_trace():
    """Reset trace before each test"""
    global execution_trace
    execution_trace = []
    yield
    # Print final trace
    print("\n" + "="*80, file=sys.stderr)
    print("[TRACE] === EXECUTION FLOW ===" , file=sys.stderr)
    for i, entry in enumerate(execution_trace, 1):
        print(f"  {i}. {entry}", file=sys.stderr)
    print("="*80 + "\n", file=sys.stderr)


@pytest.mark.asyncio
async def test_trace_permission_bypass():
    """Trace execution flow to find where permission check is bypassed"""

    print("\n" + "="*80)
    print("[TEST] TRACING PERMISSION SYSTEM BYPASS")
    print("="*80 + "\n")

    # Track which functions are called
    calls = {
        'action_submit': [],
        'CommandSuggestionSelect_handler': [],
        '_handle_user_message': [],
        'route_command_unified': [],
        'route_command': [],
        'execute_command': [],
        'execute': [],
        'check_permission': [],
        '_show_permission_prompt': []
    }

    # Patch action_submit in MultiLineInput
    from modules.multiline_input import MultiLineInput
    original_action_submit = MultiLineInput.action_submit

    def traced_action_submit(self):
        trace("MultiLineInput.action_submit", f"value='{self.value}', suggestions_active={self.suggestions_active}")
        calls['action_submit'].append((self.value, self.suggestions_active))
        return original_action_submit(self)

    # Patch CommandSuggestionSelect handler
    from modules.tui.command_handlers import CommandHandlers
    original_suggestion_select = CommandHandlers.on_multi_line_input_command_suggestion_select

    async def traced_suggestion_select(self, event):
        trace("CommandHandlers.on_multi_line_input_command_suggestion_select", "CALLED")
        calls['CommandSuggestionSelect_handler'].append(True)
        return await original_suggestion_select(self, event)

    # Patch message handler
    from modules.tui import message_handler_mixin
    original_handle_user_message = message_handler_mixin.MessageHandlerMixin._handle_user_message

    async def traced_handle_user_message(self, user_input: str, prompt_input):
        trace("MessageHandlerMixin._handle_user_message", f"user_input='{user_input}'")
        calls['_handle_user_message'].append(user_input)
        return await original_handle_user_message(self, user_input, prompt_input)

    # Patch command router
    from modules import command_router
    original_route_command_unified = command_router.route_command_unified

    async def traced_route_command_unified(app, session, command: str, args=None):
        trace("command_router.route_command_unified", f"command='{command}', args='{args}'")
        calls['route_command_unified'].append((command, args))
        return await original_route_command_unified(app, session, command, args)

    # Patch CommandRouter.route_command
    from modules.command_router import CommandRouter
    original_route_command = CommandRouter.route_command

    async def traced_route_command(self, command: str, args=None):
        trace("CommandRouter.route_command", f"command='{command}', args='{args}'")
        calls['route_command'].append((command, args))
        return await original_route_command(self, command, args)

    # Patch executor.execute_command
    from modules.execution.executor import ExecutionSystem
    original_execute_command = ExecutionSystem.execute_command

    async def traced_execute_command(self, name: str, app=None, session=None, args=None, **context):
        trace("ExecutionSystem.execute_command", f"name='{name}'")
        calls['execute_command'].append(name)
        return await original_execute_command(self, name, app, session, args, **context)

    # Patch executor.execute
    original_execute = ExecutionSystem.execute

    async def traced_execute(self, type, name: str, steps=None, **context):
        trace("ExecutionSystem.execute", f"type={type}, name='{name}'")
        calls['execute'].append((type, name))
        return await original_execute(self, type, name, steps, **context)

    # Patch permission manager
    from modules.execution.permission_manager import PermissionManager
    original_check_permission = PermissionManager.check_permission

    async def traced_check_permission(self, registration, context, app=None, session=None):
        trace("PermissionManager.check_permission", f"registration.name='{registration.name}'")
        calls['check_permission'].append(registration.name)
        return await original_check_permission(self, registration, context, app, session)

    original_show_prompt = PermissionManager._show_permission_prompt

    async def traced_show_prompt(self, app, session, registration, risk, context):
        trace("PermissionManager._show_permission_prompt", f"registration.name='{registration.name}'")
        calls['_show_permission_prompt'].append(registration.name)
        return await original_show_prompt(self, app, session, registration, risk, context)

    # Apply all patches
    patches = [
        patch.object(MultiLineInput, 'action_submit', traced_action_submit),
        patch.object(CommandHandlers, 'on_multi_line_input_command_suggestion_select', traced_suggestion_select),
        patch.object(message_handler_mixin.MessageHandlerMixin, '_handle_user_message', traced_handle_user_message),
        patch.object(command_router, 'route_command_unified', traced_route_command_unified),
        patch.object(CommandRouter, 'route_command', traced_route_command),
        patch.object(ExecutionSystem, 'execute_command', traced_execute_command),
        patch.object(ExecutionSystem, 'execute', traced_execute),
        patch.object(PermissionManager, 'check_permission', traced_check_permission),
        patch.object(PermissionManager, '_show_permission_prompt', traced_show_prompt)
    ]

    for p in patches:
        p.start()

    try:
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

        assert 'app' in app_container, "Failed to capture app instance"
        app_instance = app_container['app']

        trace("App instance captured", f"app={app_instance}")

        async with app_instance.run_test() as pilot:
            trace("Entering run_test context")

            # Get input widget
            input_widget = pilot.app.query_one("#prompt-input", MultiLineInput)
            trace("Got input widget", f"widget={input_widget}")

            # Type /help command
            input_widget.value = "/help"
            trace("Set input value", "value='/help'")

            # Press enter
            trace("Pressing enter key")
            await pilot.press("enter")
            trace("Enter key pressed")

            # Wait for processing
            await pilot.pause(1.5)
            trace("Waited 1.5 seconds for processing")

            # Print results
            print("\n" + "="*80, file=sys.stderr)
            print("[RESULTS] FUNCTION CALL SUMMARY", file=sys.stderr)
            print("="*80, file=sys.stderr)

            for func_name, call_list in calls.items():
                count = len(call_list)
                status = "✅" if count > 0 else "❌"
                print(f"{status} {func_name}: {count} calls", file=sys.stderr)
                if call_list:
                    for i, call_data in enumerate(call_list, 1):
                        print(f"    {i}. {call_data}", file=sys.stderr)

            print("="*80 + "\n", file=sys.stderr)

            # Analyze the bypass
            print("[ANALYSIS] BYPASS DETECTION", file=sys.stderr)
            print("-"*80, file=sys.stderr)

            if calls['action_submit']:
                print("✅ action_submit WAS called", file=sys.stderr)
            else:
                print("❌ action_submit was NOT called", file=sys.stderr)

            if calls['CommandSuggestionSelect_handler']:
                print("✅ CommandSuggestionSelect handler WAS called", file=sys.stderr)
            else:
                print("❌ CommandSuggestionSelect handler was NOT called", file=sys.stderr)

            if calls['_handle_user_message']:
                print("✅ Message handler WAS called", file=sys.stderr)
            else:
                print("❌ Message handler was NOT called", file=sys.stderr)

            if calls['route_command_unified']:
                print("✅ route_command_unified WAS called", file=sys.stderr)
            else:
                print("❌ route_command_unified was NOT called", file=sys.stderr)

            if calls['route_command']:
                print("✅ CommandRouter.route_command WAS called", file=sys.stderr)
            else:
                print("❌ CommandRouter.route_command was NOT called", file=sys.stderr)

            if calls['execute_command']:
                print("✅ ExecutionSystem.execute_command WAS called", file=sys.stderr)
            else:
                print("❌ ExecutionSystem.execute_command was NOT called", file=sys.stderr)

            if calls['execute']:
                print("✅ ExecutionSystem.execute WAS called", file=sys.stderr)
            else:
                print("❌ ExecutionSystem.execute was NOT called - BYPASS HERE!", file=sys.stderr)

            if calls['check_permission']:
                print("✅ PermissionManager.check_permission WAS called", file=sys.stderr)
            else:
                print("❌ PermissionManager.check_permission was NOT called", file=sys.stderr)

            print("-"*80 + "\n", file=sys.stderr)

            # Find the break point
            if not calls['check_permission']:
                # Walk backwards to find last successful call
                if calls['execute']:
                    print("🔍 BYPASS LOCATION: After ExecutionSystem.execute() starts", file=sys.stderr)
                    print("    → The permission check inside execute() is being skipped", file=sys.stderr)
                elif calls['execute_command']:
                    print("🔍 BYPASS LOCATION: Between execute_command() and execute()", file=sys.stderr)
                    print("    → execute_command() is not calling execute()", file=sys.stderr)
                elif calls['route_command']:
                    print("🔍 BYPASS LOCATION: Between route_command() and execute_command()", file=sys.stderr)
                    print("    → route_command() is not calling execute_command()", file=sys.stderr)
                elif calls['route_command_unified']:
                    print("🔍 BYPASS LOCATION: Between route_command_unified() and route_command()", file=sys.stderr)
                    print("    → route_command_unified() is not calling route_command()", file=sys.stderr)
                elif calls['_handle_user_message']:
                    print("🔍 BYPASS LOCATION: Inside _handle_user_message()", file=sys.stderr)
                    print("    → _handle_user_message() is not calling route_command_unified()", file=sys.stderr)
                elif calls['CommandSuggestionSelect_handler']:
                    print("🔍 BYPASS LOCATION: Inside CommandSuggestionSelect handler", file=sys.stderr)
                    print("    → Handler is not calling _handle_user_message()", file=sys.stderr)
                elif calls['action_submit']:
                    print("🔍 BYPASS LOCATION: After action_submit()", file=sys.stderr)
                    print("    → CommandSuggestionSelect message not reaching handler", file=sys.stderr)
                else:
                    print("🔍 BYPASS LOCATION: Before action_submit()", file=sys.stderr)
                    print("    → Enter key press is not triggering action_submit()", file=sys.stderr)

        # Cleanup
        startup_task.cancel()
        try:
            await startup_task
        except asyncio.CancelledError:
            pass

    finally:
        # Stop all patches
        for p in patches:
            p.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
