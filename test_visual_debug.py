#!/usr/bin/env python3
"""
VISUAL debug capture - run with visual=True as the framework is designed
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.testing import TUITestFramework, TestStep

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  VISUAL DEBUG TEST - Using Framework As Designed             ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print("This will open TWO Terminal windows:")
    print("  LEFT  = opencli tui running")
    print("  RIGHT = Test controller sending commands")
    print()
    print("Watch the LEFT window to see permission buffer behavior!")
    print()

    # Create test using framework
    framework = TUITestFramework(sdk_init_wait=11)

    # Build test sequence to trigger and test permission buffer
    framework.add_step(TestStep.TYPE, "/help", "Type /help command")
    framework.add_step(TestStep.ENTER, description="Autocomplete", wait_after=1)
    framework.add_step(TestStep.ENTER, description="Show permission buffer", wait_after=5)

    # Critical test - does DOWN arrow work?
    framework.add_step(TestStep.COLLECT_STATE, description="BEFORE DOWN arrow", wait_after=2)
    framework.add_step(TestStep.DOWN, description="Press DOWN arrow", wait_after=3)
    framework.add_step(TestStep.COLLECT_STATE, description="AFTER DOWN arrow", wait_after=2)

    # Does ENTER work?
    framework.add_step(TestStep.ENTER, description="Press ENTER to confirm", wait_after=2)

    print("Starting VISUAL test...")
    print()
    print("The test will run automatically in the new windows.")
    print("Press Ctrl+C here when done to analyze results.")
    print()

    # Run with VISUAL=TRUE as the framework is designed
    result = framework.run_test(visual=True)

    # Wait for user to observe
    print()
    print("═══════════════════════════════════════════════════════════════")
    print("VISUAL TEST COMPLETED")
    print("═══════════════════════════════════════════════════════════════")
    print()

    if result.passed:
        print("✅ Test PASSED - Permission buffer is working!")
    else:
        print("❌ Test FAILED - Permission buffer has issues")
        print(f"   Message: {result.message}")

    if result.log_file:
        print(f"\n📁 Output log: {result.log_file}")

    if result.failing_functions:
        print("\n🔍 Failing Functions Detected:")
        for func in result.failing_functions:
            print(f"  → {func.get('function')}() at {func.get('file')}:{func.get('line')}")

    # Now analyze the captured output
    print("\n═══════════════════════════════════════════════════════════════")
    print("ANALYZING CAPTURED DATA")
    print("═══════════════════════════════════════════════════════════════\n")

    # Check if log file exists and analyze it
    if result.log_file and os.path.exists(result.log_file):
        with open(result.log_file, 'r') as f:
            output = f.read()

        # Look for debug messages
        print("Debug message analysis:")
        print(f"  [MultiLineInput] messages: {output.count('[MultiLineInput')}")
        print(f"  KEY EVENT messages: {output.count('KEY EVENT')}")
        print(f"  ACTION_PERMISSION calls: {output.count('ACTION_PERMISSION')}")
        print(f"  GAINED FOCUS events: {output.count('GAINED FOCUS')}")
        print(f"  has_focus=True: {output.count('has_focus=True')}")
        print(f"  has_focus=False: {output.count('has_focus=False')}")

        # Check specific issues
        print("\nIssue Detection:")
        if output.count('KEY EVENT') == 0:
            print("  ❌ NO key events received - widget not in event chain")
        elif output.count('has_focus=True') == 0:
            print("  ❌ Widget never had focus - focus() not working")
        elif output.count('ACTION_PERMISSION') == 0:
            print("  ❌ BINDINGS not triggering actions")
        else:
            print("  ✅ Basic event flow appears to be working")

        # Save a focused debug report
        debug_report = f"/tmp/debug_report_{int(time.time())}.txt"
        with open(debug_report, 'w') as f:
            f.write("═" * 70 + "\n")
            f.write("DEBUG REPORT - Permission Buffer Issues\n")
            f.write("═" * 70 + "\n\n")
            f.write(f"Test Result: {'PASSED' if result.passed else 'FAILED'}\n")
            f.write(f"Message: {result.message}\n\n")
            f.write("Key Events:\n")
            for line in output.split('\n'):
                if 'KEY EVENT' in line or 'has_focus=' in line or 'ACTION_' in line:
                    f.write(f"  {line}\n")
            f.write("\n" + "=" * 70 + "\n\n")
            f.write("Full Output:\n")
            f.write(output)

        print(f"\n📄 Debug report saved to: {debug_report}")

    return 0 if result.passed else 1

if __name__ == "__main__":
    sys.exit(main())
