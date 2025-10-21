#!/usr/bin/env python3
"""
Proper debug capture using TUI test framework template
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.testing import (
    TUITestFramework,
    TestStep,
    create_permission_buffer_test
)

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  DEBUG CAPTURE - Using TUI Test Framework Template          ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    # Create test using framework template
    framework = TUITestFramework(sdk_init_wait=11)

    # Build test sequence
    framework.add_step(TestStep.TYPE, "/help", "Type /help command")
    framework.add_step(TestStep.ENTER, description="Autocomplete", wait_after=1)
    framework.add_step(TestStep.ENTER, description="Submit and show buffer", wait_after=4)
    framework.add_step(TestStep.COLLECT_STATE, description="State before DOWN", wait_after=1)
    framework.add_step(TestStep.DOWN, description="Press DOWN arrow", wait_after=2)
    framework.add_step(TestStep.COLLECT_STATE, description="State after DOWN", wait_after=1)
    framework.add_step(TestStep.ENTER, description="Press ENTER", wait_after=2)

    print("Running headless test to capture debug output...")
    print()

    # Run headless test
    result = framework.run_test(visual=False)

    print()
    print("═══════════════════════════════════════════════════════════════")
    print("TEST RESULT")
    print("═══════════════════════════════════════════════════════════════")
    print()

    if result.passed:
        print("✅ Test PASSED")
    else:
        print("❌ Test FAILED")
        print(f"   Message: {result.message}")

    if result.log_file:
        print(f"   Log file: {result.log_file}")

    if result.failing_functions:
        print()
        print("Failing Functions Identified:")
        for func in result.failing_functions:
            print(f"  → {func.get('function')}()")
            print(f"    File: {func.get('file')}")
            print(f"    Line: {func.get('line')}")

    # Now check for debug output in session logs
    print()
    print("═══════════════════════════════════════════════════════════════")
    print("CHECKING FOR DEBUG OUTPUT")
    print("═══════════════════════════════════════════════════════════════")
    print()

    session_name = framework.session_name
    print(f"Session name: {session_name}")

    # Check for tmux output capture
    import subprocess
    try:
        # Try to capture pane content from tmux session
        tmux_output = subprocess.run(
            ['tmux', 'capture-pane', '-t', session_name, '-p'],
            capture_output=True,
            text=True
        )
        if tmux_output.returncode == 0:
            print("✅ Captured tmux pane output")
            output = tmux_output.stdout

            # Analyze output
            if "[MultiLineInput" in output:
                print("✅ Found MultiLineInput debug output")
            else:
                print("❌ NO MultiLineInput debug output found")

            if "KEY EVENT" in output:
                print("✅ Found KEY EVENT messages")
                count = output.count("KEY EVENT")
                print(f"   Total key events: {count}")
            else:
                print("❌ NO KEY EVENT messages found")

            if "ACTION_PERMISSION" in output:
                print("✅ Found ACTION_PERMISSION calls")
            else:
                print("❌ NO ACTION_PERMISSION calls found")

            if "GAINED FOCUS" in output:
                print("✅ Widget gained focus")
            else:
                print("❌ Widget did NOT gain focus")

            # Save full output
            debug_file = f"/tmp/debug_output_{session_name}.txt"
            with open(debug_file, 'w') as f:
                f.write(output)
            print(f"\n📁 Full output saved to: {debug_file}")

        else:
            print("❌ Could not capture tmux pane")
    except Exception as e:
        print(f"❌ Error capturing tmux: {e}")

    # Cleanup
    framework.cleanup()

    return 0 if result.passed else 1

if __name__ == "__main__":
    sys.exit(main())
