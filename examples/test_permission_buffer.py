#!/usr/bin/env python3
"""
Example: Test Permission Buffer Functionality

This example demonstrates how to use the TUI Test Framework to test
permission buffer behavior with automated data collection and failure analysis.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.testing import (
    TUITestFramework,
    TestStep,
    create_permission_buffer_test
)


def example_1_quick_test():
    """
    Example 1: Quick Permission Buffer Test
    Uses pre-configured test for /help command
    """
    print("=" * 60)
    print("Example 1: Quick Permission Buffer Test")
    print("=" * 60)
    print()

    # Create pre-configured test
    test = create_permission_buffer_test(command="/help")

    # Run with visual windows
    print("Running visual test (two Terminal windows will open)...")
    print("Watch the TUI window for permission buffer!")
    print()

    result = test.run_test(visual=True)

    print()
    print("Test Result:", "✅ PASSED" if result.passed else "❌ FAILED")
    print("Output log:", result.log_file)

    if result.failing_functions:
        print("\nFailing Functions:")
        for func in result.failing_functions:
            print(f"  - {func.get('function')} at {func.get('file')}:{func.get('line')}")


def example_2_custom_test():
    """
    Example 2: Custom Test Sequence
    Build a custom test from scratch
    """
    print("=" * 60)
    print("Example 2: Custom Test Sequence")
    print("=" * 60)
    print()

    # Create framework
    framework = TUITestFramework(sdk_init_wait=11)

    # Build custom test sequence
    framework.add_step(
        TestStep.TYPE,
        "/help",
        "Type /help command",
        wait_after=1
    )

    framework.add_step(
        TestStep.ENTER,
        description="Autocomplete command",
        wait_after=1
    )

    framework.add_step(
        TestStep.ENTER,
        description="Submit command",
        wait_after=4
    )

    framework.add_step(
        TestStep.COLLECT_STATE,
        description="Collect permission buffer state",
        wait_after=2
    )

    framework.add_step(
        TestStep.DOWN,
        description="Press DOWN arrow (select No)",
        wait_after=2
    )

    framework.add_step(
        TestStep.VERIFY_SELECTION,
        description="Verify 'No' is selected",
        expected_state={"selected": "No"},
        wait_after=1
    )

    framework.add_step(
        TestStep.ENTER,
        description="Confirm selection",
        wait_after=2
    )

    print("Running custom test sequence...")
    result = framework.run_test(visual=True)

    print()
    print("Test Result:", "✅ PASSED" if result.passed else "❌ FAILED")

    # Cleanup
    framework.cleanup()


def example_3_headless_test():
    """
    Example 3: Headless Testing (for CI/CD)
    Run without visual windows
    """
    print("=" * 60)
    print("Example 3: Headless Test (CI/CD Mode)")
    print("=" * 60)
    print()

    # Create test
    test = create_permission_buffer_test("/help")

    print("Running headless test (no visual windows)...")
    result = test.run_test(visual=False)

    print()
    if result.passed:
        print("✅ Test PASSED")
        print("   Permission buffer works correctly")
    else:
        print("❌ Test FAILED")
        print("   Message:", result.message)

        if result.failing_functions:
            print()
            print("   Failing Functions Identified:")
            for func in result.failing_functions:
                print(f"     → {func.get('function')}()")
                print(f"       File: {func.get('file')}")
                print(f"       Line: {func.get('line')}")

    print()
    print("Output log:", result.log_file)

    test.cleanup()

    return result.passed


def example_4_multiple_commands():
    """
    Example 4: Test Multiple Commands
    Test different commands sequentially
    """
    print("=" * 60)
    print("Example 4: Test Multiple Commands")
    print("=" * 60)
    print()

    commands = ["/help", "/agent", "/model"]

    results = {}

    for cmd in commands:
        print(f"Testing command: {cmd}")
        test = create_permission_buffer_test(command=cmd)
        result = test.run_test(visual=False)
        results[cmd] = result
        print(f"  {'✅ PASSED' if result.passed else '❌ FAILED'}")
        test.cleanup()

    print()
    print("Summary:")
    passed = sum(1 for r in results.values() if r.passed)
    total = len(results)
    print(f"  {passed}/{total} commands passed")

    return all(r.passed for r in results.values())


def example_5_navigation_test():
    """
    Example 5: Test Navigation (UP/DOWN arrows)
    Specifically test arrow key navigation
    """
    print("=" * 60)
    print("Example 5: Navigation Test (Arrow Keys)")
    print("=" * 60)
    print()

    framework = TUITestFramework()

    # Submit command to get permission buffer
    framework.add_step(TestStep.TYPE, "/help")
    framework.add_step(TestStep.ENTER)
    framework.add_step(TestStep.ENTER, wait_after=4)

    # Test DOWN arrow
    framework.add_step(
        TestStep.DOWN,
        description="Test DOWN arrow navigation",
        wait_after=1
    )

    framework.add_step(
        TestStep.VERIFY_SELECTION,
        description="Verify moved to 'No'",
        expected_state={"selected": "No"}
    )

    # Test UP arrow
    framework.add_step(
        TestStep.UP,
        description="Test UP arrow navigation",
        wait_after=1
    )

    framework.add_step(
        TestStep.VERIFY_SELECTION,
        description="Verify moved back to 'Yes'",
        expected_state={"selected": "Yes"}
    )

    print("Running navigation test...")
    result = framework.run_test(visual=True)

    print()
    print("Navigation Test:", "✅ PASSED" if result.passed else "❌ FAILED")

    framework.cleanup()


def main():
    """Run all examples"""
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  OpenCLI TUI Test Framework Examples                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

    print("Choose an example to run:")
    print("  1. Quick Permission Buffer Test (visual)")
    print("  2. Custom Test Sequence (visual)")
    print("  3. Headless Test (CI/CD mode)")
    print("  4. Test Multiple Commands")
    print("  5. Navigation Test (Arrow Keys)")
    print("  6. Run ALL examples")
    print()

    choice = input("Enter choice (1-6): ").strip()

    print()

    if choice == "1":
        example_1_quick_test()
    elif choice == "2":
        example_2_custom_test()
    elif choice == "3":
        success = example_3_headless_test()
        sys.exit(0 if success else 1)
    elif choice == "4":
        success = example_4_multiple_commands()
        sys.exit(0 if success else 1)
    elif choice == "5":
        example_5_navigation_test()
    elif choice == "6":
        print("Running all examples...\n")
        example_1_quick_test()
        print("\n" + "="*60 + "\n")
        example_2_custom_test()
        print("\n" + "="*60 + "\n")
        example_3_headless_test()
        print("\n" + "="*60 + "\n")
        example_4_multiple_commands()
        print("\n" + "="*60 + "\n")
        example_5_navigation_test()
    else:
        print("Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    main()
