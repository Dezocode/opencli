"""
Trace EXACTLY which functions fire when /help is executed
Shows the complete call stack and where it gets stuck
"""

import sys
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import traceback

# Add modules to path - need to import as package
opencli_dir = Path(__file__).parent
sys.path.insert(0, str(opencli_dir))

# Import using direct module loading to avoid relative import issues
import importlib.util

def load_module(name, filepath):
    spec = importlib.util.spec_from_file_location(name, filepath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Load modules directly
modules_dir = opencli_dir / "modules"
sys.path.insert(0, str(modules_dir))

# Now import
from modules.command_router import CommandRouter, route_command_unified
from modules.execution.executor import ExecutionSystem, get_executor
from modules.permissions import get_unified_permission_manager


# Global trace log
TRACE_LOG = []

def trace(msg):
    """Log and print trace message"""
    TRACE_LOG.append(msg)
    print(f"  {msg}")


# Monkey-patch key functions to trace execution
original_functions = {}

def setup_tracing():
    """Patch all key functions to trace their execution"""

    # 1. CommandRouter.route_command
    if hasattr(CommandRouter, 'route_command'):
        original_functions['CommandRouter.route_command'] = CommandRouter.route_command
        async def traced_route_command(self, command, args=None):
            trace(f"✓ CommandRouter.route_command('{command}', {args})")
            try:
                result = await original_functions['CommandRouter.route_command'](self, command, args)
                trace(f"  → route_command returned: {result}")
                return result
            except Exception as e:
                trace(f"  ✗ route_command raised: {type(e).__name__}: {e}")
                raise
        CommandRouter.route_command = traced_route_command

    # 2. ExecutionSystem.execute_command
    if hasattr(ExecutionSystem, 'execute_command'):
        original_functions['ExecutionSystem.execute_command'] = ExecutionSystem.execute_command
        async def traced_execute_command(self, name, **kwargs):
            trace(f"✓ ExecutionSystem.execute_command('{name}')")
            try:
                result = await original_functions['ExecutionSystem.execute_command'](self, name, **kwargs)
                trace(f"  → execute_command returned: {result}")
                return result
            except Exception as e:
                trace(f"  ✗ execute_command raised: {type(e).__name__}: {e}")
                raise
        ExecutionSystem.execute_command = traced_execute_command

    # 3. ExecutionSystem.execute
    if hasattr(ExecutionSystem, 'execute'):
        original_functions['ExecutionSystem.execute'] = ExecutionSystem.execute
        async def traced_execute(self, type, name, steps=None, **context):
            trace(f"✓ ExecutionSystem.execute({type}, '{name}')")
            try:
                result = await original_functions['ExecutionSystem.execute'](self, type, name, steps, **context)
                trace(f"  → execute returned: {result}")
                return result
            except Exception as e:
                trace(f"  ✗ execute raised: {type(e).__name__}: {e}")
                traceback.print_exc()
                raise
        ExecutionSystem.execute = traced_execute

    # 4. UnifiedPermissionManager.check_permission
    from permissions.integration import UnifiedPermissionManager
    if hasattr(UnifiedPermissionManager, 'check_permission'):
        original_functions['UPM.check_permission'] = UnifiedPermissionManager.check_permission
        async def traced_check_permission(self, registration, context, app=None, session=None):
            trace(f"✓ UnifiedPermissionManager.check_permission('{registration.name}')")
            try:
                result = await original_functions['UPM.check_permission'](self, registration, context, app, session)
                trace(f"  → check_permission returned: {result}")
                return result
            except Exception as e:
                trace(f"  ✗ check_permission raised: {type(e).__name__}: {e}")
                traceback.print_exc()
                raise
        UnifiedPermissionManager.check_permission = traced_check_permission

    # 5. UnifiedPermissionManager.request_permission
    if hasattr(UnifiedPermissionManager, 'request_permission'):
        original_functions['UPM.request_permission'] = UnifiedPermissionManager.request_permission
        async def traced_request_permission(self, app, session, prompt_data, timeout=30.0):
            trace(f"✓ UnifiedPermissionManager.request_permission(timeout={timeout})")
            trace(f"  prompt_data title: {prompt_data.get('title')}")
            trace(f"  prompt_data options: {len(prompt_data.get('options', []))} options")
            try:
                # SIMULATE USER SELECTING FIRST OPTION
                trace(f"  [SIMULATING] User selects option 1")
                result = {
                    'response': 'allow_once',
                    'data': prompt_data.get('options', [{}])[0].get('data', {})
                }
                trace(f"  → request_permission returned: {result}")
                return result
            except Exception as e:
                trace(f"  ✗ request_permission raised: {type(e).__name__}: {e}")
                traceback.print_exc()
                raise
        UnifiedPermissionManager.request_permission = traced_request_permission

    # 6. Custom prompt function
    from commands.basic_commands import show_help_prompt
    original_functions['show_help_prompt'] = show_help_prompt
    def traced_show_help_prompt(app, session, registration, context):
        trace(f"✓ show_help_prompt() called")
        result = original_functions['show_help_prompt'](app, session, registration, context)
        trace(f"  → show_help_prompt returned: {type(result).__name__} with {len(result.get('options', []))} options")
        return result
    import commands.basic_commands
    commands.basic_commands.show_help_prompt = traced_show_help_prompt

    # 7. Handler function
    from commands.basic_commands import show_help
    original_functions['show_help'] = show_help
    async def traced_show_help(app, session, **context):
        trace(f"✓ show_help() handler called")
        trace(f"  context keys: {list(context.keys())}")
        trace(f"  _command_selection: {context.get('_command_selection')}")
        try:
            result = await original_functions['show_help'](app, session, **context)
            trace(f"  → show_help returned: {result}")
            return result
        except Exception as e:
            trace(f"  ✗ show_help raised: {type(e).__name__}: {e}")
            traceback.print_exc()
            raise
    commands.basic_commands.show_help = traced_show_help


async def test_help_command_execution_trace():
    """Test /help execution with complete tracing"""

    print("\n" + "="*80)
    print("TRACING /help EXECUTION - COMPLETE CALL STACK")
    print("="*80)

    # Setup tracing
    setup_tracing()

    # Create mock app and session
    class MockApp:
        def __init__(self):
            self.output = []
            self._command_router = None

        def write(self, text):
            trace(f"  [APP.WRITE] {text[:80]}")
            self.output.append(text)

        def query_one(self, selector):
            trace(f"  [APP.QUERY_ONE] {selector}")
            if selector == "#prompt-input":
                return Mock()  # Simulate TUI mode
            raise Exception(f"Widget {selector} not found")

    class MockSession:
        pass

    app = MockApp()
    session = MockSession()

    trace("=" * 80)
    trace("STEP 1: Create CommandRouter")
    trace("=" * 80)

    # Create router (this initializes ExecutionSystem)
    router = CommandRouter(app, session)
    app._command_router = router

    trace("")
    trace("=" * 80)
    trace("STEP 2: Initialize registrations")
    trace("=" * 80)

    # Initialize registrations
    await router._initialize_registrations()

    trace("")
    trace("=" * 80)
    trace("STEP 3: Execute /help command")
    trace("=" * 80)

    # Execute /help
    try:
        result = await route_command_unified(app, session, '/help')
        trace("")
        trace(f"✅ FINAL RESULT: {result}")
    except Exception as e:
        trace("")
        trace(f"❌ EXECUTION FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()

    trace("")
    trace("=" * 80)
    trace("EXECUTION TRACE COMPLETE")
    trace("=" * 80)

    # Print full trace
    print("\n" + "="*80)
    print("COMPLETE TRACE LOG:")
    print("="*80)
    for i, msg in enumerate(TRACE_LOG, 1):
        print(f"{i:3d}. {msg}")

    # Print app output
    print("\n" + "="*80)
    print("APP OUTPUT:")
    print("="*80)
    for output in app.output:
        print(output)

    print("\n" + "="*80)
    print("TRACE SUMMARY:")
    print("="*80)

    # Analyze trace
    functions_called = [msg for msg in TRACE_LOG if msg.startswith("✓")]
    print(f"Functions called: {len(functions_called)}")
    for func in functions_called:
        print(f"  {func}")

    errors = [msg for msg in TRACE_LOG if "✗" in msg]
    if errors:
        print(f"\n❌ Errors encountered: {len(errors)}")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ No errors in trace")


if __name__ == "__main__":
    asyncio.run(test_help_command_execution_trace())
