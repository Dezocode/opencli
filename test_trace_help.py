"""
Simple trace test - run with: python3 -m pytest test_trace_help.py -v -s
"""

import pytest
import asyncio
import sys

# Trace log
TRACE = []

def trace(msg):
    """Log trace message"""
    TRACE.append(msg)
    print(f"🔍 {msg}")


@pytest.mark.asyncio
async def test_trace_help_execution():
    """Trace what happens when /help is executed"""

    trace("="*80)
    trace("STARTING /help EXECUTION TRACE")
    trace("="*80)

    # Import modules (will work when run as pytest module)
    from modules.command_router import CommandRouter, route_command_unified
    from modules.execution.executor import ExecutionSystem
    from modules.execution.registry import ExecutionType
    from modules.permissions import get_unified_permission_manager

    trace("")
    trace("STEP 1: Creating mock app and session")

    class MockApp:
        def __init__(self):
            self.output = []
            self._command_router = None

        def write(self, text):
            self.output.append(text)
            trace(f"  APP.WRITE: {text[:60]}")

        def query_one(self, selector):
            trace(f"  APP.QUERY_ONE: {selector}")
            if selector == "#prompt-input":
                # Return mock widget to simulate TUI mode
                class MockWidget:
                    pass
                return MockWidget()
            raise Exception(f"Widget not found: {selector}")

    class MockSession:
        pass

    app = MockApp()
    session = MockSession()

    trace("")
    trace("STEP 2: Creating CommandRouter")

    router = CommandRouter(app, session)
    app._command_router = router

    trace(f"  ✓ Router created")
    trace(f"  ✓ Router.executor type: {type(router.executor).__name__}")
    trace(f"  ✓ Router._initialized: {router._initialized}")

    trace("")
    trace("STEP 3: Initializing registrations")

    try:
        await router._initialize_registrations()
        trace(f"  ✓ Registrations initialized")
        trace(f"  ✓ Router._initialized: {router._initialized}")

        # Check if /help is registered
        from modules.execution.registry import ExecutionType
        help_reg = router.executor.registry.get(ExecutionType.COMMAND, '/help')
        if help_reg:
            trace(f"  ✓ /help is registered")
            trace(f"    - requires_approval: {help_reg.requires_approval}")
            trace(f"    - has custom_prompt_func: {'custom_prompt_func' in (help_reg.metadata or {})}")
        else:
            trace(f"  ✗ /help NOT registered!")
            return

    except Exception as e:
        trace(f"  ✗ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return

    trace("")
    trace("STEP 4: Attempting to execute /help")

    try:
        # Call route_command_unified directly
        trace("  Calling route_command_unified(app, session, '/help')")

        # Set a timeout
        result = await asyncio.wait_for(
            route_command_unified(app, session, '/help'),
            timeout=5.0  # 5 second timeout
        )

        trace(f"  ✓ Command completed successfully!")
        trace(f"  Result: {result}")

    except asyncio.TimeoutError:
        trace(f"  ⏱️  TIMEOUT after 5 seconds!")
        trace(f"  Command did NOT complete")
        trace(f"  This indicates a blocking operation or deadlock")

    except Exception as e:
        trace(f"  ✗ Execution failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    trace("")
    trace("="*80)
    trace("TRACE COMPLETE")
    trace("="*80)

    # Print summary
    print("\n" + "="*80)
    print("EXECUTION TRACE SUMMARY")
    print("="*80)
    for i, msg in enumerate(TRACE, 1):
        print(f"{i:3d}. {msg}")

    print("\n" + "="*80)
    print("APP OUTPUT:")
    print("="*80)
    for output in app.output:
        print(output)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
