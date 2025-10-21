#!/usr/bin/env python3
"""
Test permission buffer arrow key navigation
"""

from modules.testing.tui_test_framework import TUITestFramework, TestStep

def main():
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  PERMISSION BUFFER ARROW KEY TEST                        ║")
    print("║  Test /help command with UP/DOWN arrows                  ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    # Create test framework
    framework = TUITestFramework(sdk_init_wait=11)

    # Type /help
    framework.add_step(TestStep.TYPE, "/help", "Type /help command")
    framework.add_step(TestStep.ENTER, description="Submit /help", wait_after=5)

    # Test DOWN arrow
    framework.add_step(TestStep.DOWN, description="Press DOWN arrow", wait_after=1)

    # Test UP arrow
    framework.add_step(TestStep.UP, description="Press UP arrow", wait_after=1)

    # Collect final state
    framework.add_step(TestStep.COLLECT_STATE, "Check final state", wait_after=1)

    # Run test in visual mode
    print("⏳ Running permission buffer navigation test...\n")
    result = framework.run_test(visual=True)

    # Print results
    print("\n" + "="*80)
    print("PERMISSION BUFFER ARROW KEY TEST RESULTS")
    print("="*80)

    if result.passed:
        print("\n✅ ARROW KEYS WORK IN PERMISSION BUFFER!")
        print("   UP/DOWN arrows navigate the options")
    else:
        print(f"\n❌ ARROW KEYS FAILED: {result.message}")
        if result.failing_functions:
            print("\nFailing functions:")
            for func in result.failing_functions:
                print(f"  • {func['function']} at {func['file']}:{func['line']}")

    print("\n" + "="*80)

    return 0 if result.passed else 1

if __name__ == "__main__":
    exit(main())
