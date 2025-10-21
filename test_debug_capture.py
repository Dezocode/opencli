#!/usr/bin/env python3
"""
Automated Debug Capture Test
Uses TUI Test Framework to capture debug output and analyze root cause
"""

import sys
import os
import time

# Add modules to path
sys.path.insert(0, '/Users/dezmondhollins/opencli')

from modules.testing import TUITestFramework, TestStep

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  AUTOMATED DEBUG CAPTURE - Permission Buffer Analysis       ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    # Create test framework with debug capture
    framework = TUITestFramework(
        sdk_init_wait=11
    )

    # Test sequence to trigger permission buffer
    print("📋 Test Sequence:")
    print("  1. Type /help")
    print("  2. Press ENTER to submit")
    print("  3. Press ENTER to show permission buffer")
    print("  4. Press DOWN arrow")
    print("  5. Press ENTER to confirm")
    print()

    # Add test steps
    framework.add_step(TestStep.TYPE, "/help", "Type /help command")
    framework.add_step(TestStep.ENTER, description="Submit /help", wait_after=2)
    framework.add_step(TestStep.ENTER, description="Show permission buffer", wait_after=4)

    # Capture state BEFORE DOWN arrow
    framework.add_step(TestStep.COLLECT_STATE, description="CHECKPOINT 1: Before DOWN arrow", wait_after=1)

    # Press DOWN arrow
    framework.add_step(TestStep.DOWN, description="Press DOWN arrow", wait_after=2)

    # Capture state AFTER DOWN arrow
    framework.add_step(TestStep.COLLECT_STATE, description="CHECKPOINT 2: After DOWN arrow", wait_after=1)

    # Press ENTER
    framework.add_step(TestStep.ENTER, description="Press ENTER to confirm", wait_after=2)

    # Run test in HEADLESS mode (no visual windows)
    print("🚀 Running automated test...")
    print()

    result = framework.run_test(visual=False)

    print("═══════════════════════════════════════════════════════════════")
    print("TEST COMPLETED")
    print("═══════════════════════════════════════════════════════════════")
    print()

    # Now analyze the debug log
    debug_log = f"/tmp/opencli_debug_{framework.session_name}.log"

    if not os.path.exists(debug_log):
        print(f"❌ No debug log found at: {debug_log}")
        print()
        print("Checking for stderr output in test result...")
        if hasattr(result, 'raw_output'):
            print(result.raw_output)
        return 1

    print(f"✅ Debug log found: {debug_log}")
    print(f"   Size: {os.path.getsize(debug_log)} bytes")
    print()

    # Read the debug log
    with open(debug_log, 'r') as f:
        debug_output = f.read()

    # Analyze the output
    print("═══════════════════════════════════════════════════════════════")
    print("ANALYSIS - Permission Prompt Setup")
    print("═══════════════════════════════════════════════════════════════")

    if "[TUI._show_permission_prompt]" in debug_output:
        print("✅ _show_permission_prompt() WAS called")
        lines = [line for line in debug_output.split('\n') if '[TUI._show_permission_prompt]' in line]
        for line in lines[:5]:
            print(f"   {line}")
    else:
        print("❌ _show_permission_prompt() was NOT called - SETUP ISSUE!")
    print()

    print("═══════════════════════════════════════════════════════════════")
    print("ANALYSIS - Widget Focus")
    print("═══════════════════════════════════════════════════════════════")

    if "GAINED FOCUS" in debug_output:
        print("✅ Widget GAINED focus")
        lines = [line for line in debug_output.split('\n') if 'GAINED FOCUS' in line]
        for line in lines[:3]:
            print(f"   {line}")
    else:
        print("❌ Widget DID NOT gain focus - FOCUS ISSUE!")

    if "LOST FOCUS" in debug_output:
        print("⚠️  Widget LOST focus during test")
        lines = [line for line in debug_output.split('\n') if 'LOST FOCUS' in line]
        for line in lines[:3]:
            print(f"   {line}")
    print()

    print("═══════════════════════════════════════════════════════════════")
    print("ANALYSIS - Key Events Received")
    print("═══════════════════════════════════════════════════════════════")

    key_events = debug_output.count("====== KEY EVENT ======")
    print(f"Total key events received: {key_events}")

    if key_events > 0:
        print("✅ Widget IS receiving key events")
        print()
        print("Sample key events:")
        lines = debug_output.split('\n')
        for i, line in enumerate(lines):
            if "====== KEY EVENT ======" in line:
                # Print this line and next 5 lines
                for j in range(min(6, len(lines) - i)):
                    print(f"   {lines[i + j]}")
                print()
                if lines[i:i+6].count("====== KEY EVENT ======") >= 3:
                    break  # Show max 3 key events
    else:
        print("❌ Widget is NOT receiving ANY key events - EVENT ROUTING ISSUE!")
    print()

    print("═══════════════════════════════════════════════════════════════")
    print("ANALYSIS - has_focus During Key Events")
    print("═══════════════════════════════════════════════════════════════")

    has_focus_true = debug_output.count("has_focus=True")
    has_focus_false = debug_output.count("has_focus=False")

    print(f"has_focus=True:  {has_focus_true} times")
    print(f"has_focus=False: {has_focus_false} times")

    if has_focus_true > 0:
        print("✅ Widget had focus during some events")
    else:
        print("❌ Widget NEVER had focus during key events - FOCUS ISSUE!")
    print()

    print("═══════════════════════════════════════════════════════════════")
    print("ANALYSIS - Action Methods Called")
    print("═══════════════════════════════════════════════════════════════")

    action_down = debug_output.count("[ACTION_PERMISSION_DOWN]")
    action_up = debug_output.count("[ACTION_PERMISSION_UP]")
    action_submit = debug_output.count("[ACTION_SUBMIT]")

    print(f"action_permission_down() called: {action_down} times")
    print(f"action_permission_up() called:   {action_up} times")
    print(f"action_submit() called:          {action_submit} times")
    print()

    if action_down > 0:
        print("✅ DOWN action WAS called - checking if it worked...")
        lines = [line for line in debug_output.split('\n') if 'ACTION_PERMISSION_DOWN' in line]
        for line in lines[:5]:
            print(f"   {line}")
    else:
        print("❌ DOWN action was NEVER called - BINDING NOT WORKING!")

    if action_submit > 0:
        print("✅ SUBMIT action WAS called")
    else:
        print("❌ SUBMIT action was NEVER called - BINDING NOT WORKING!")
    print()

    print("═══════════════════════════════════════════════════════════════")
    print("ANALYSIS - Permission Data State")
    print("═══════════════════════════════════════════════════════════════")

    if "PERMISSION DATA CHANGED" in debug_output:
        print("✅ permission_prompt_data WAS set")
        lines = [line for line in debug_output.split('\n') if 'PERMISSION' in line and 'selected_option' in line]
        for line in lines[:5]:
            print(f"   {line}")
    else:
        print("❌ permission_prompt_data was NEVER set - DATA ISSUE!")
    print()

    print("═══════════════════════════════════════════════════════════════")
    print("ROOT CAUSE DIAGNOSIS")
    print("═══════════════════════════════════════════════════════════════")
    print()

    # Determine root cause
    if "[TUI._show_permission_prompt]" not in debug_output:
        print("🔴 ROOT CAUSE: Permission prompt setup function never called")
        print("   → Check permission manager integration")
        print("   → Check if /help command triggers permission request")
    elif "GAINED FOCUS" not in debug_output:
        print("🔴 ROOT CAUSE: Widget never gained focus")
        print("   → Check focus() call in _show_permission_prompt()")
        print("   → Check if widget is focusable (can_focus=True)")
    elif key_events == 0:
        print("🔴 ROOT CAUSE: Widget not receiving ANY key events")
        print("   → Check parent widget consuming events")
        print("   → Check event routing in Textual app")
        print("   → Check if widget is in focus chain")
    elif has_focus_true == 0:
        print("🔴 ROOT CAUSE: Widget receives events but has_focus=False")
        print("   → Focus is lost between setup and key press")
        print("   → Check for focus-stealing widgets")
        print("   → Check on_blur() events")
    elif action_down == 0 and action_submit == 0:
        print("🔴 ROOT CAUSE: Key events received but BINDINGS not firing")
        print("   → Check BINDINGS declaration matches action method names")
        print("   → Check if BINDINGS are being overridden")
        print("   → Check priority attribute on BINDINGS")
    elif action_down > 0:
        print("🔴 ROOT CAUSE: Action methods called but UI not updating")
        print("   → Check refresh() implementation")
        print("   → Check reactive property updates")
        print("   → Check render() method")
    else:
        print("🟡 UNCLEAR: Multiple issues detected, need manual analysis")
        print(f"   → Full debug log: {debug_log}")

    print()
    print("═══════════════════════════════════════════════════════════════")
    print(f"Full debug output saved to: {debug_log}")
    print("═══════════════════════════════════════════════════════════════")
    print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
