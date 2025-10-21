#!/usr/bin/env python3
"""
Pytest to identify EXACTLY where the permission flow is freezing
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, str(Path(__file__).parent))

from modules.execution.registry import ExecutionRegistry, ExecutionType
from modules.execution.executor import ExecutionSystem
from cli.session import Session


class TraceApp:
    """App that logs all method calls"""

    def __init__(self):
        self.writes = []
        self._command_router = None

    def write(self, text, end="\n"):
        self.writes.append(f"APP.write: {text[:100]}")
        print(f"[TRACE] APP.write: {text[:100]}")

    def query_one(self, selector, expect_type=None):
        print(f"[TRACE] APP.query_one({selector})")

        # Return mock widget
        mock_widget = MagicMock()
        mock_widget.id = selector.lstrip('#')
        mock_widget.visible = True
        mock_widget.is_mounted = True
        mock_widget.permission_prompt_data = None

        def set_permission_data(value):
            print(f"[TRACE] Widget.permission_prompt_data = {value.get('title') if value else None}")
            mock_widget.permission_prompt_data = value

        type(mock_widget).permission_prompt_data = property(
            lambda self: self._perm_data,
            set_permission_data
        )
        mock_widget._perm_data = None

        mock_widget.refresh = MagicMock()
        mock_widget.focus = MagicMock()

        return mock_widget

    def set_focus(self, widget):
        print(f"[TRACE] APP.set_focus({widget})")


@pytest.mark.asyncio
async def test_permission_flow_trace():
    """
    Trace the EXACT execution path to find where it freezes
    """
    print("\n" + "="*80)
    print("PERMISSION FLOW FREEZE TRACE")
    print("="*80 + "\n")

    # Create components
    session = Session(model='test-model')
    app = TraceApp()
    executor = ExecutionSystem(app=app, session=session)

    print("Step 1: Registering all commands...")
    from modules.commands.registry import register_all
    await register_all(executor)
    print(f"  ✓ Registered {len(executor.registry.commands)} commands\n")

    # Get /help registration
    help_reg = executor.registry.get(ExecutionType.COMMAND, '/help')
    print("Step 2: /help registration details:")
    print(f"  Name: {help_reg.name}")
    print(f"  Requires approval: {help_reg.requires_approval}")
    print(f"  Has metadata: {help_reg.metadata is not None}")
    if help_reg.metadata:
        print(f"  Has custom_prompt_func: {'custom_prompt_func' in help_reg.metadata}")
    print()

    print("Step 3: Starting execution with detailed tracing...")
    print("-" * 80)

    # Instrument PermissionManager to trace calls
    original_check_permission = executor.permission_manager.check_permission

    async def traced_check_permission(registration, context, app, session):
        print(f"\n[TRACE] PermissionManager.check_permission() ENTERED")
        print(f"[TRACE]   registration.name = {registration.name}")
        print(f"[TRACE]   requires_approval = {registration.requires_approval}")
        print(f"[TRACE]   app = {app is not None}")
        print(f"[TRACE]   session = {session is not None}")

        try:
            result = await original_check_permission(registration, context, app, session)
            print(f"[TRACE] PermissionManager.check_permission() RETURNED {result}")
            return result
        except Exception as e:
            print(f"[TRACE] PermissionManager.check_permission() RAISED {type(e).__name__}: {e}")
            raise

    executor.permission_manager.check_permission = traced_check_permission

    # Instrument _show_permission_prompt to trace
    original_show_prompt = executor.permission_manager._show_permission_prompt

    async def traced_show_prompt(app, session, registration, risk, context):
        print(f"\n[TRACE] PermissionManager._show_permission_prompt() ENTERED")
        print(f"[TRACE]   registration.name = {registration.name}")
        print(f"[TRACE]   registration.metadata = {registration.metadata}")

        if registration.metadata:
            custom_func = registration.metadata.get('custom_prompt_func')
            print(f"[TRACE]   custom_prompt_func = {custom_func}")

            if custom_func:
                print(f"[TRACE]   Calling custom_prompt_func...")
                try:
                    prompt_data = custom_func(app, session, registration, context)
                    print(f"[TRACE]   custom_prompt_func returned: {prompt_data.get('title') if prompt_data else None}")
                except Exception as e:
                    print(f"[TRACE]   custom_prompt_func RAISED {type(e).__name__}: {e}")
                    raise

        print(f"[TRACE]   About to call original _show_permission_prompt...")
        try:
            result = await original_show_prompt(app, session, registration, risk, context)
            print(f"[TRACE] _show_permission_prompt() RETURNED {result}")
            return result
        except Exception as e:
            print(f"[TRACE] _show_permission_prompt() RAISED {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise

    executor.permission_manager._show_permission_prompt = traced_show_prompt

    # Instrument buffer manager
    try:
        from modules.permission_buffer_manager import get_permission_buffer_manager
        buffer_manager = get_permission_buffer_manager()

        original_request_permission = buffer_manager.request_permission

        async def traced_request_permission(app, session, prompt_data, timeout=30.0):
            print(f"\n[TRACE] PermissionBufferManager.request_permission() ENTERED")
            print(f"[TRACE]   title = {prompt_data.get('title')}")
            print(f"[TRACE]   timeout = {timeout}")
            print(f"[TRACE]   Creating asyncio.Future()...")

            try:
                print(f"[TRACE]   Calling original request_permission...")
                # Use a shorter timeout for testing
                result = await asyncio.wait_for(
                    original_request_permission(app, session, prompt_data, timeout=2.0),
                    timeout=3.0
                )
                print(f"[TRACE] request_permission() RETURNED {result}")
                return result
            except asyncio.TimeoutError:
                print(f"[TRACE] request_permission() TIMED OUT (expected - no user interaction)")
                print(f"[TRACE] This means the buffer is waiting for user input")
                return {'response': 'timeout', 'reason': 'test_timeout'}
            except Exception as e:
                print(f"[TRACE] request_permission() RAISED {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                raise

        buffer_manager.request_permission = traced_request_permission

    except ImportError as e:
        print(f"[TRACE] Could not import buffer manager: {e}")

    # Execute the command with timeout
    print(f"[TRACE] Executing command: /help")
    print(f"[TRACE] Setting 5 second timeout...")

    try:
        result = await asyncio.wait_for(
            executor.execute(ExecutionType.COMMAND, '/help', context={}),
            timeout=5.0
        )
        print(f"\n[TRACE] executor.execute() COMPLETED")
        print(f"[TRACE] Result: {result}")
    except asyncio.TimeoutError:
        print(f"\n[TRACE] ✗ FREEZE DETECTED - executor.execute() timed out after 5 seconds")
        print(f"[TRACE] Last trace output shows where it froze")

        # Print summary
        print("\n" + "="*80)
        print("FREEZE LOCATION IDENTIFIED")
        print("="*80)
        print("Check the LAST [TRACE] message above to see where execution stopped.")
        print("This is the blocking point causing the freeze.")

    except Exception as e:
        print(f"\n[TRACE] executor.execute() RAISED {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)
    print("TRACE COMPLETE")
    print("="*80)


@pytest.mark.asyncio
async def test_buffer_manager_isolation():
    """
    Test buffer manager request_permission in isolation
    """
    print("\n" + "="*80)
    print("BUFFER MANAGER ISOLATION TEST")
    print("="*80 + "\n")

    try:
        from modules.permission_buffer_manager import get_permission_buffer_manager

        buffer_manager = get_permission_buffer_manager()
        print(f"✓ Buffer manager type: {type(buffer_manager)}")
        print(f"✓ Has request_permission: {hasattr(buffer_manager, 'request_permission')}")

        session = Session(model='test-model')
        app = TraceApp()

        prompt_data = {
            'title': 'TEST',
            'message': 'Test message',
            'options': [
                {'text': 'Option 1', 'response': 'allow_once', 'data': {}},
                {'text': 'Cancel', 'response': 'cancel'}
            ]
        }

        print(f"\nCalling buffer_manager.request_permission() with 2s timeout...")

        try:
            result = await asyncio.wait_for(
                buffer_manager.request_permission(app, session, prompt_data, timeout=2.0),
                timeout=3.0
            )
            print(f"✓ Returned: {result}")
        except asyncio.TimeoutError:
            print(f"⏱ TIMEOUT - buffer is waiting for user input (expected)")
            print(f"✓ This means request_permission() is working correctly")
            print(f"✓ It's awaiting Future.set_result() from user interaction")
        except Exception as e:
            print(f"✗ ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    except ImportError as e:
        print(f"✗ Could not import buffer manager: {e}")


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "-s", "--tb=short"])
