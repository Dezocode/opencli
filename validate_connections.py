#!/usr/bin/env python3
"""
Validate all connection paths in the refactored TUI system.
Run this to verify end-to-end integration is working.
"""

import sys
import inspect
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

def test_multiline_input_import():
    """Test that correct MultiLineInput class is imported"""
    print("\n[TEST 1] MultiLineInput Import Validation")
    print("=" * 70)

    from modules.tui.core import MultiLineInput

    # Check module source
    module = inspect.getmodule(MultiLineInput)
    module_name = module.__name__

    expected = "modules.multiline_input"
    if module_name == expected:
        print(f"✅ PASS: MultiLineInput loaded from {module_name}")
    else:
        print(f"❌ FAIL: MultiLineInput loaded from {module_name}, expected {expected}")
        return False

    # Check action_submit has suggestions_active check
    source = inspect.getsource(MultiLineInput.action_submit)
    if 'suggestions_active' in source:
        print(f"✅ PASS: action_submit() has suggestions_active check")
    else:
        print(f"❌ FAIL: action_submit() missing suggestions_active check")
        return False

    return True


def test_message_handlers_exist():
    """Test that all message handlers are defined"""
    print("\n[TEST 2] Message Handler Existence")
    print("=" * 70)

    from modules.tui.command_handlers import CommandHandlers

    required_handlers = [
        'on_multi_line_input_submitted',
        'on_multi_line_input_show_command_suggestions',
        'on_multi_line_input_hide_command_suggestions',
        'on_multi_line_input_command_suggestion_navigate',
        'on_multi_line_input_command_suggestion_select',
    ]

    all_passed = True
    for handler_name in required_handlers:
        if hasattr(CommandHandlers, handler_name):
            handler = getattr(CommandHandlers, handler_name)
            if callable(handler):
                print(f"✅ PASS: {handler_name} exists and is callable")
            else:
                print(f"❌ FAIL: {handler_name} exists but not callable")
                all_passed = False
        else:
            print(f"❌ FAIL: {handler_name} not found")
            all_passed = False

    return all_passed


def test_execution_registry_methods():
    """Test that ExecutionRegistry has required methods"""
    print("\n[TEST 3] ExecutionRegistry Methods")
    print("=" * 70)

    from modules.execution.registry import ExecutionRegistry, ExecutionType

    registry = ExecutionRegistry()

    required_methods = [
        'search_commands',
        'record_usage',
        'get',
        'register',
    ]

    all_passed = True
    for method_name in required_methods:
        if hasattr(registry, method_name):
            method = getattr(registry, method_name)
            if callable(method):
                print(f"✅ PASS: ExecutionRegistry.{method_name}() exists")
            else:
                print(f"❌ FAIL: ExecutionRegistry.{method_name} not callable")
                all_passed = False
        else:
            print(f"❌ FAIL: ExecutionRegistry.{method_name} not found")
            all_passed = False

    return all_passed


def test_search_commands_return_format():
    """Test that search_commands returns correct format"""
    print("\n[TEST 4] ExecutionRegistry.search_commands() Return Format")
    print("=" * 70)

    from modules.execution.registry import ExecutionRegistry, ExecutionType, ExecutionCategory, RiskLevel

    registry = ExecutionRegistry()

    # Register a test command
    def test_handler(app, session, args):
        pass

    registry.register(
        type=ExecutionType.COMMAND,
        name="/test",
        handler=test_handler,
        category=ExecutionCategory.BASIC,
        risk_level=RiskLevel.SAFE,
        requires_approval=True,
        description="Test command"
    )

    # Search for it
    results = registry.search_commands("/test")

    if not results:
        print("❌ FAIL: search_commands returned empty results")
        return False

    if not isinstance(results, list):
        print(f"❌ FAIL: search_commands returned {type(results)}, expected list")
        return False

    result = results[0]

    # Check format
    required_keys = ['registration', 'name', 'score']
    all_passed = True

    for key in required_keys:
        if key in result:
            print(f"✅ PASS: Result has '{key}' key")
        else:
            print(f"❌ FAIL: Result missing '{key}' key")
            all_passed = False

    # Check registration object
    if 'registration' in result:
        reg = result['registration']
        if hasattr(reg, 'handler') and hasattr(reg, 'description') and hasattr(reg, 'usage_count'):
            print(f"✅ PASS: Registration object has required fields")
        else:
            print(f"❌ FAIL: Registration object missing required fields")
            all_passed = False

    return all_passed


def test_command_router_import():
    """Test that route_command_unified can be imported"""
    print("\n[TEST 5] Command Router Import")
    print("=" * 70)

    try:
        from modules.command_router import route_command_unified, CommandRouter
        print(f"✅ PASS: route_command_unified imported successfully")
        print(f"✅ PASS: CommandRouter imported successfully")

        # Check it's a coroutine
        import asyncio
        if asyncio.iscoroutinefunction(route_command_unified):
            print(f"✅ PASS: route_command_unified is async function")
        else:
            print(f"❌ FAIL: route_command_unified is not async")
            return False

        return True
    except ImportError as e:
        print(f"❌ FAIL: Import error: {e}")
        return False


def test_widget_message_classes():
    """Test that all Message classes are defined"""
    print("\n[TEST 6] MultiLineInput Message Classes")
    print("=" * 70)

    from modules.multiline_input import MultiLineInput

    required_messages = [
        'Submitted',
        'ShowCommandSuggestions',
        'HideCommandSuggestions',
        'CommandSuggestionNavigate',
        'CommandSuggestionSelect',
        'PermissionResponse',
        'PermissionCancelled',
        'NavigationEvent',
    ]

    all_passed = True
    for msg_name in required_messages:
        if hasattr(MultiLineInput, msg_name):
            msg_class = getattr(MultiLineInput, msg_name)
            if inspect.isclass(msg_class):
                print(f"✅ PASS: MultiLineInput.{msg_name} exists")
            else:
                print(f"❌ FAIL: MultiLineInput.{msg_name} is not a class")
                all_passed = False
        else:
            print(f"❌ FAIL: MultiLineInput.{msg_name} not found")
            all_passed = False

    return all_passed


def test_tui_composition():
    """Test that OpenCLITUI can be instantiated"""
    print("\n[TEST 7] OpenCLITUI Composition")
    print("=" * 70)

    try:
        from modules.tui.core import OpenCLITUI
        from modules.session import Session
        from modules.config import Config

        # Create mock session and config
        session = Session()
        config = Config()

        # Try to instantiate
        app = OpenCLITUI(session, config)

        print(f"✅ PASS: OpenCLITUI instantiated successfully")

        # Check it has required methods
        if hasattr(app, '_handle_user_message'):
            print(f"✅ PASS: OpenCLITUI has _handle_user_message method")
        else:
            print(f"❌ FAIL: OpenCLITUI missing _handle_user_message method")
            return False

        # Check mixin inheritance
        from modules.tui.command_handlers import CommandHandlers
        if isinstance(app, CommandHandlers):
            print(f"✅ PASS: OpenCLITUI inherits from CommandHandlers")
        else:
            print(f"❌ FAIL: OpenCLITUI does not inherit from CommandHandlers")
            return False

        return True

    except Exception as e:
        print(f"❌ FAIL: Could not instantiate OpenCLITUI: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests"""
    print("\n" + "=" * 70)
    print("OPENCLI TUI REFACTOR - CONNECTION VALIDATION")
    print("=" * 70)

    tests = [
        test_multiline_input_import,
        test_message_handlers_exist,
        test_execution_registry_methods,
        test_search_commands_return_format,
        test_command_router_import,
        test_widget_message_classes,
        test_tui_composition,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR in {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test.__name__, False))

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL CONNECTIONS VALIDATED - REFACTOR COMPLETE!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
