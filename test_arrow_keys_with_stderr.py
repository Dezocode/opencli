#!/usr/bin/env python3
"""
Arrow Key Debug Test - Uses TUI Test Framework API
Captures stderr logs to answer critical questions about focus and event routing
"""

import sys
import os
import time

# Add modules to path
sys.path.insert(0, os.path.expanduser("~/opencli"))

from modules.testing.tui_test_framework import TUITestFramework, TestStep, TestResult

def analyze_stderr_logs(log_file: str) -> dict:
    """
    Analyze stderr logs to answer critical questions

    Returns dict with answers to:
    1. Was permission buffer shown?
    2. Was permission_prompt_data set?
    3. Did widget gain focus?
    4. Was on_key() called for arrows?
    5. Were BINDINGS action methods called?
    6. Did selection change?
    """
    if not os.path.exists(log_file):
        return {
            "error": f"Log file not found: {log_file}",
            "all_questions_answered": False
        }

    with open(log_file, 'r') as f:
        log_content = f.read()

    results = {
        "log_file": log_file,
        "log_length": len(log_content),
        "all_questions_answered": True
    }

    # QUESTION 1: Was permission buffer shown?
    if "[TUI._show_permission_prompt]" in log_content:
        results["q1_buffer_shown"] = True
        results["q1_details"] = "✅ _show_permission_prompt was called"
    else:
        results["q1_buffer_shown"] = False
        results["q1_details"] = "❌ _show_permission_prompt was NOT called"

    # QUESTION 2: Was permission_prompt_data set?
    if "PERMISSION ACTIVE" in log_content:
        results["q2_data_set"] = True
        results["q2_details"] = "✅ permission_prompt_data was set"
        # Extract which permission
        for line in log_content.split('\n'):
            if "PERMISSION ACTIVE:" in line:
                results["q2_permission_type"] = line.split("PERMISSION ACTIVE:")[1].strip()
                break
    else:
        results["q2_data_set"] = False
        results["q2_details"] = "❌ permission_prompt_data was NOT set"

    # QUESTION 3: Did widget gain focus?
    focus_gained = "[MultiLineInput.on_focus] GAINED FOCUS" in log_content
    if focus_gained:
        results["q3_focus_gained"] = True
        # Check if focus was with permission buffer
        focus_lines = [line for line in log_content.split('\n') if "on_focus] GAINED FOCUS" in line]
        has_prompt = any("prompt=True" in line for line in focus_lines)
        results["q3_details"] = f"✅ Widget gained focus (with prompt={has_prompt})"

        # Check if focus was immediately lost
        blur_count = log_content.count("[MultiLineInput.on_blur] LOST FOCUS")
        if blur_count > 0:
            results["q3_focus_lost"] = True
            results["q3_details"] += f" ⚠️ BUT lost focus {blur_count} times!"
    else:
        results["q3_focus_gained"] = False
        results["q3_details"] = "❌ Widget NEVER gained focus"

    # QUESTION 4: Was on_key() called for arrows?
    down_key_logs = [line for line in log_content.split('\n') if "on_key]" in line and "KEY='down'" in line]
    up_key_logs = [line for line in log_content.split('\n') if "on_key]" in line and "KEY='up'" in line]

    if down_key_logs:
        results["q4_on_key_down"] = True
        results["q4_down_details"] = f"✅ on_key() received DOWN ({len(down_key_logs)} times)"
        # Check focus state when DOWN was pressed
        for line in down_key_logs:
            if "focused=" in line:
                focused = "focused=True" in line
                results["q4_down_focused"] = focused
                if not focused:
                    results["q4_down_details"] += " ⚠️ BUT widget was NOT focused!"
                break
    else:
        results["q4_on_key_down"] = False
        results["q4_down_details"] = "❌ on_key() NEVER received DOWN key"

    if up_key_logs:
        results["q4_on_key_up"] = True
        results["q4_up_details"] = f"✅ on_key() received UP ({len(up_key_logs)} times)"
    else:
        results["q4_on_key_up"] = False
        results["q4_up_details"] = "❌ on_key() NEVER received UP key"

    # QUESTION 5: Were BINDINGS action methods called?
    action_down_logs = [line for line in log_content.split('\n') if "action_permission_down] ENTERED" in line]
    action_up_logs = [line for line in log_content.split('\n') if "action_permission_up] ENTERED" in line]

    if action_down_logs:
        results["q5_action_down"] = True
        results["q5_down_action_details"] = f"✅ action_permission_down called ({len(action_down_logs)} times)"
    else:
        results["q5_action_down"] = False
        results["q5_down_action_details"] = "❌ action_permission_down was NEVER called"

    if action_up_logs:
        results["q5_action_up"] = True
        results["q5_up_action_details"] = f"✅ action_permission_up called ({len(action_up_logs)} times)"
    else:
        results["q5_action_up"] = False
        results["q5_up_action_details"] = "❌ action_permission_up was NEVER called"

    # QUESTION 6: Did selection change?
    selection_changes = [line for line in log_content.split('\n') if "watch_permission_selected_option]" in line and "->" in line]

    if selection_changes:
        results["q6_selection_changed"] = True
        results["q6_details"] = f"✅ Selection changed ({len(selection_changes)} times)"
        results["q6_changes"] = selection_changes[:5]  # First 5 changes
    else:
        results["q6_selection_changed"] = False
        results["q6_details"] = "❌ Selection NEVER changed"

    # DIAGNOSIS: Determine scenario
    if not results.get("q3_focus_gained"):
        results["diagnosis"] = "Scenario A: FOCUS NEVER GAINED"
        results["fix_needed"] = "Force focus after render completes (use call_after_refresh or set_timer)"
    elif results.get("q3_focus_lost"):
        results["diagnosis"] = "Scenario B: FOCUS GAINED BUT IMMEDIATELY LOST"
        results["fix_needed"] = "Prevent focus stealing - check what's calling on_blur"
    elif not results.get("q4_on_key_down"):
        results["diagnosis"] = "Scenario C: FOCUS WORKS, on_key() NOT CALLED"
        results["fix_needed"] = "Check Textual event routing, app configuration"
    elif results.get("q4_on_key_down") and results.get("q4_down_focused") == False:
        results["diagnosis"] = "Scenario D: on_key() CALLED BUT WIDGET NOT FOCUSED"
        results["fix_needed"] = "Fix focus state tracking or event routing"
    elif results.get("q5_action_down") and not results.get("q4_on_key_down"):
        results["diagnosis"] = "Scenario E: BINDINGS OVERRIDE on_key()"
        results["fix_needed"] = "Remove on_key() handling, rely only on BINDINGS"
    elif results.get("q4_on_key_down") and not results.get("q6_selection_changed"):
        results["diagnosis"] = "Scenario F: on_key() CALLED, LOGIC FAILS"
        results["fix_needed"] = "Debug on_key() logic - check permission_prompt_data checks"
    else:
        results["diagnosis"] = "Unknown scenario - need manual analysis"
        results["fix_needed"] = "Review full logs"

    return results


def print_results(results: dict):
    """Pretty print analysis results"""
    print("\n" + "="*80)
    print("STDERR LOG ANALYSIS RESULTS")
    print("="*80)

    if "error" in results:
        print(f"\n❌ ERROR: {results['error']}")
        return

    print(f"\n📁 Log File: {results['log_file']}")
    print(f"📊 Log Size: {results['log_length']:,} bytes")
    print("\n" + "-"*80)
    print("CRITICAL QUESTIONS")
    print("-"*80)

    print(f"\n1. Was permission buffer shown?")
    print(f"   {results['q1_details']}")

    print(f"\n2. Was permission_prompt_data set?")
    print(f"   {results['q2_details']}")
    if results.get('q2_data_set') and 'q2_permission_type' in results:
        print(f"   Type: {results['q2_permission_type']}")

    print(f"\n3. Did widget gain focus?")
    print(f"   {results['q3_details']}")

    print(f"\n4. Was on_key() called for arrows?")
    print(f"   DOWN: {results['q4_down_details']}")
    print(f"   UP: {results['q4_up_details']}")

    print(f"\n5. Were BINDINGS action methods called?")
    print(f"   DOWN: {results['q5_down_action_details']}")
    print(f"   UP: {results['q5_up_action_details']}")

    print(f"\n6. Did selection change?")
    print(f"   {results['q6_details']}")
    if results.get('q6_selection_changed') and 'q6_changes' in results:
        print(f"   Changes:")
        for change in results['q6_changes']:
            print(f"     {change.strip()}")

    print("\n" + "="*80)
    print("DIAGNOSIS")
    print("="*80)
    print(f"\n🔍 {results['diagnosis']}")
    print(f"\n💡 FIX NEEDED:")
    print(f"   {results['fix_needed']}")
    print("\n" + "="*80)


def main():
    """Run arrow key test with stderr analysis"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  ARROW KEY DEBUG TEST - TUI Test Framework API            ║")
    print("║  Capturing stderr to diagnose focus/event routing issues  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

    # Create test using framework API
    print("▶ Configuring test...")
    framework = TUITestFramework(sdk_init_wait=11)

    # Add test steps
    framework.add_step(
        TestStep.TYPE,
        "/help",
        "Type /help command",
        wait_after=1
    )

    framework.add_step(
        TestStep.ENTER,
        description="Autocomplete /help",
        wait_after=2
    )

    framework.add_step(
        TestStep.ENTER,
        description="Submit /help command - permission buffer should show",
        wait_after=4
    )

    framework.add_step(
        TestStep.COLLECT_STATE,
        description="Collect permission buffer state",
        wait_after=1
    )

    framework.add_step(
        TestStep.DOWN,
        description="Press DOWN arrow - should move to 'No'",
        wait_after=2
    )

    framework.add_step(
        TestStep.UP,
        description="Press UP arrow - should move back to 'Yes'",
        wait_after=2
    )

    print("✅ Test configured with 6 steps")
    print()
    print("▶ Running visual test (dual terminal windows)...")
    print("   LEFT window: opencli tui")
    print("   RIGHT window: Test controller")
    print()
    print("⏳ Test will run automatically...")
    print("   Waiting for results...")
    print()

    # Run test in visual mode
    result = framework.run_test(visual=True)

    print("\n" + "="*80)
    print("TUI TEST FRAMEWORK RESULT")
    print("="*80)
    print(f"\nTest Status: {'✅ PASSED' if result.passed else '❌ FAILED'}")
    print(f"Message: {result.message}")

    if result.log_file:
        print(f"\n▶ Analyzing stderr logs from: {result.log_file}")

        # Wait a bit for log file to be fully written
        time.sleep(2)

        # Analyze stderr logs
        analysis = analyze_stderr_logs(result.log_file)

        # Print results
        print_results(analysis)

        print(f"\n📄 Full logs available at: {result.log_file}")
        print(f"   View with: cat {result.log_file}")
        print(f"   Search: cat {result.log_file} | grep -i 'on_key\\|focus\\|permission'")
    else:
        print("\n⚠️ No log file available")

    # Cleanup
    print("\n▶ Cleaning up...")
    framework.cleanup()

    print("\n✅ Test complete!")

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
