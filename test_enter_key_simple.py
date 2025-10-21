#!/usr/bin/env python3
"""
Simple ENTER key test - just type 'hi' and press ENTER
"""

from modules.testing.tui_test_framework import TUITestFramework, TestStep

def main():
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  SIMPLE ENTER KEY TEST                                    ║")
    print("║  Type 'hi' and press ENTER to send                       ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    # Create test framework
    framework = TUITestFramework(sdk_init_wait=11)

    # Simple test: Type "hi" and press ENTER
    framework.add_step(TestStep.TYPE, "hi", "Type 'hi'")
    framework.add_step(TestStep.ENTER, description="Press ENTER to send", wait_after=2)
    framework.add_step(TestStep.COLLECT_STATE, "Check if message was sent", wait_after=1)

    # Run test in visual mode
    print("⏳ Running test...\n")
    result = framework.run_test(visual=True)

    # Print results
    print("\n" + "="*80)
    print("ENTER KEY TEST RESULTS")
    print("="*80)

    if result.passed:
        print("\n✅ ENTER KEY WORKS!")
        print("   Message 'hi' was sent successfully")
    else:
        print(f"\n❌ ENTER KEY FAILED: {result.message}")

    print("\n" + "="*80)

    return 0 if result.passed else 1

if __name__ == "__main__":
    exit(main())
