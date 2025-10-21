#!/usr/bin/env python3
"""
Test to trace /help registration and verify custom_prompt_func is set
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.execution.registry import ExecutionRegistry, ExecutionType
from modules.execution.executor import ExecutionSystem
from cli.session import Session


async def test_help_registration():
    """Trace /help registration step by step"""

    print("\n" + "="*80)
    print("HELP REGISTRATION TRACE")
    print("="*80 + "\n")

    # Create minimal components
    session = Session(model='test-model')

    class FakeApp:
        pass

    executor = ExecutionSystem(app=FakeApp(), session=session)

    print("Step 1: Registering all commands...")
    from modules.commands.registry import register_all
    await register_all(executor)
    print(f"  ✓ Registry has {len(executor.registry.commands)} commands\n")

    # Check if /help is registered
    print("Step 2: Looking up /help registration...")
    help_registration = executor.registry.get(ExecutionType.COMMAND, '/help')

    if not help_registration:
        print("  ✗ FAILURE: /help not found in registry!")
        return

    print(f"  ✓ Found /help registration")
    print(f"  Name: {help_registration.name}")
    print(f"  Type: {help_registration.type}")
    print(f"  Category: {help_registration.category}")
    print(f"  Risk Level: {help_registration.risk_level}")
    print(f"  Requires Approval: {help_registration.requires_approval}")
    print(f"  Description: {help_registration.description}")
    print()

    # Check metadata
    print("Step 3: Checking metadata...")
    print(f"  Metadata type: {type(help_registration.metadata)}")
    print(f"  Metadata value: {help_registration.metadata}")
    print()

    if help_registration.metadata is None:
        print("  ✗ FAILURE: metadata is None!")
        return

    if not isinstance(help_registration.metadata, dict):
        print(f"  ✗ FAILURE: metadata is not a dict, it's {type(help_registration.metadata)}")
        return

    print(f"  ✓ Metadata is a dict with {len(help_registration.metadata)} keys:")
    for key, value in help_registration.metadata.items():
        print(f"    - {key}: {type(value).__name__} = {value if not callable(value) else f'{value.__name__}()'}")
    print()

    # Check for custom_prompt_func
    print("Step 4: Checking for custom_prompt_func...")
    if 'custom_prompt_func' not in help_registration.metadata:
        print("  ✗ FAILURE: 'custom_prompt_func' key NOT in metadata!")
        print(f"  Available keys: {list(help_registration.metadata.keys())}")
        return

    custom_prompt_func = help_registration.metadata.get('custom_prompt_func')
    print(f"  ✓ custom_prompt_func found!")
    print(f"    Type: {type(custom_prompt_func)}")
    print(f"    Name: {custom_prompt_func.__name__ if hasattr(custom_prompt_func, '__name__') else 'N/A'}")
    print(f"    Callable: {callable(custom_prompt_func)}")
    print()

    # Test calling it
    print("Step 5: Testing custom_prompt_func call...")
    try:
        class FakeApp:
            pass

        result = custom_prompt_func(FakeApp(), session, help_registration, {})
        print(f"  ✓ Function returned successfully")
        print(f"    Return type: {type(result)}")
        if isinstance(result, dict):
            print(f"    Keys: {list(result.keys())}")
            print(f"    Title: {result.get('title', 'N/A')}")
            print(f"    Options count: {len(result.get('options', []))}")
    except Exception as e:
        print(f"  ✗ FAILURE calling custom_prompt_func: {e}")
        import traceback
        traceback.print_exc()
        return

    print()
    print("="*80)
    print("SUCCESS: /help registration is correct!")
    print("="*80)


async def test_runtime_registration():
    """Test if runtime uses correct modules"""

    print("\n" + "="*80)
    print("RUNTIME MODULES CHECK")
    print("="*80 + "\n")

    # Check which permission_manager is being used
    print("Checking permission_manager module path...")
    from modules.execution import permission_manager as pm_module
    print(f"  Module file: {pm_module.__file__}")
    print()

    # Check if it has the expected structure
    print("Checking PermissionManager class...")
    from modules.execution.permission_manager import PermissionManager
    import inspect

    # Get the _show_permission_prompt method
    method = getattr(PermissionManager, '_show_permission_prompt', None)
    if not method:
        print("  ✗ FAILURE: _show_permission_prompt method not found!")
        return

    print(f"  ✓ Method found")
    print(f"    File: {inspect.getfile(method)}")
    print(f"    Line: {inspect.getsourcelines(method)[1]}")

    # Check source code for custom_prompt_func handling
    source = inspect.getsource(method)
    if 'custom_prompt_func' in source:
        print(f"  ✓ Method contains 'custom_prompt_func' handling")

        # Check if it awaits the function
        if 'await custom_prompt_func' in source:
            print(f"    ⚠️  WARNING: Method AWAITs custom_prompt_func (should be sync!)")
        else:
            print(f"    ✓ Method calls custom_prompt_func synchronously")
    else:
        print(f"  ✗ FAILURE: Method does NOT contain 'custom_prompt_func' handling!")

    print()
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_help_registration())
    asyncio.run(test_runtime_registration())
