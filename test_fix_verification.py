#!/usr/bin/env python3
"""
Test the is_active fix - verify arrow keys and ENTER work now
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.testing import TUITestFramework, TestStep

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  TESTING FIX - is_active = True Now Set                     ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    framework = TUITestFramework(sdk_init_wait=11)

    # Test sequence
    framework.add_step(TestStep.TYPE, "/help", "Type /help")
    framework.add_step(TestStep.ENTER, description="Autocomplete", wait_after=1)
    framework.add_step(TestStep.ENTER, description="Show permission buffer", wait_after=5)

    # Capture BEFORE state
    framework.add_step(TestStep.COLLECT_STATE, description="BEFORE DOWN (should be on Yes)", wait_after=2)

    # Press DOWN - should work now!
    framework.add_step(TestStep.DOWN, description="Press DOWN arrow", wait_after=2)

    # Capture AFTER state
    framework.add_step(TestStep.COLLECT_STATE, description="AFTER DOWN (should be on No)", wait_after=2)

    # Press ENTER - should work now!
    framework.add_step(TestStep.ENTER, description="Press ENTER to confirm", wait_after=2)

    print("Running HEADLESS test to check fix...")
    print()

    result = framework.run_test(visual=False)

    print()
    print("═══════════════════════════════════════════════════════════════")
    print("TEST RESULT")
    print("═══════════════════════════════════════════════════════════════")
    print()

    if result.passed:
        print("✅✅✅ TEST PASSED - FIX WORKS! ✅✅✅")
        print()
        print("Arrow keys and ENTER now work in permission buffer!")
    else:
        print("❌ TEST FAILED - Fix didn't work")
        print(f"   Message: {result.message}")

        if result.failing_functions:
            print()
            print("Failing Functions:")
            for func in result.failing_functions:
                print(f"  → {func.get('function')}() at {func.get('file')}:{func.get('line')}")

    print()
    print(f"Log file: {result.log_file}")

    # Analyze the log for is_active
    if result.log_file and os.path.exists(result.log_file):
        with open(result.log_file, 'r') as f:
            output = f.read()

        # Strip ANSI codes for analysis
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_output = ansi_escape.sub('', output)

        print()
        print("═══════════════════════════════════════════════════════════════")
        print("ANALYZING SELECTION CHANGE")
        print("═══════════════════════════════════════════════════════════════")
        print()

        # Look for selection indicators in the output
        before_section = False
        after_section = False

        lines = clean_output.split('\n')
        for i, line in enumerate(lines):
            if 'BEFORE DOWN' in line or 'before DOWN' in line:
                before_section = True
                after_section = False
                print("BEFORE DOWN arrow:")
                continue
            elif 'AFTER DOWN' in line or 'after DOWN' in line:
                before_section = False
                after_section = True
                print("\nAFTER DOWN arrow:")
                continue

            # Look for selection indicators
            if before_section or after_section:
                if '▸ Yes' in line or '❯' in line and 'Yes' in line:
                    print(f"  → Selected: YES")
                if '▸ No' in line or '❯' in line and 'No' in line:
                    print(f"  → Selected: NO")

        print()

        # Check if selection actually changed
        if '▸ Yes' in clean_output and '▸ No' in clean_output:
            print("✅ SELECTION CHANGED - DOWN arrow worked!")
        elif '▸ No' in clean_output:
            print("✅ SELECTION CHANGED to No - DOWN arrow worked!")
        else:
            print("❌ SELECTION DID NOT CHANGE - Fix didn't work")

    framework.cleanup()

    return 0 if result.passed else 1

if __name__ == "__main__":
    sys.exit(main())
