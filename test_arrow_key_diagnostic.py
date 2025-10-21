#!/usr/bin/env python3
"""
Comprehensive Arrow Key Diagnostic Test
Uses TUI Test Framework API to gather ALL data during permission buffer navigation

This test does NOT assume the cause - it captures everything:
- All key events received
- Function calls (on_key, action_permission_down, etc.)
- Reactive property changes
- Widget focus state
- Render calls
- Permission buffer state changes
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.testing import TUITestFramework, TestStep

def run_comprehensive_arrow_diagnostic():
    """
    Comprehensive diagnostic test that captures ALL data during arrow key press
    Maps directly to ARROW_KEY_DEBUG_SUMMARY.md investigation points
    """

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  ARROW KEY COMPREHENSIVE DIAGNOSTIC TEST                     ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print("This test will capture:")
    print("  ✓ All key events and their exact names")
    print("  ✓ Which functions fire (on_key vs action_permission_down)")
    print("  ✓ Reactive property changes (permission_selected_option)")
    print("  ✓ Widget focus state before/after")
    print("  ✓ Permission buffer state (prompt_data)")
    print("  ✓ Render calls and UI updates")
    print("  ✓ BINDINGS action execution")
    print()
    print("Starting comprehensive diagnostic...")
    print()

    # Create test framework
    framework = TUITestFramework(sdk_init_wait=11)

    # ===================================================================
    # CHECKPOINT 1: Initial State
    # ===================================================================
    framework.add_step(
        TestStep.COLLECT_STATE,
        description="CHECKPOINT 1: Initial TUI state (before any commands)",
        wait_after=1
    )

    # ===================================================================
    # STEP 1: Type /help command
    # ===================================================================
    framework.add_step(
        TestStep.TYPE,
        "/help",
        "Type /help command",
        wait_after=1
    )

    # ===================================================================
    # CHECKPOINT 2: After typing /help
    # ===================================================================
    framework.add_step(
        TestStep.COLLECT_STATE,
        description="CHECKPOINT 2: After typing /help (before submission)",
        wait_after=1
    )

    # ===================================================================
    # STEP 2: Autocomplete (first ENTER)
    # ===================================================================
    framework.add_step(
        TestStep.ENTER,
        description="STEP: Autocomplete /help command",
        wait_after=1
    )

    # ===================================================================
    # STEP 3: Submit command (second ENTER to show permission buffer)
    # ===================================================================
    framework.add_step(
        TestStep.ENTER,
        description="STEP: Submit /help to trigger permission buffer",
        wait_after=4  # Give time for permission buffer to appear
    )

    # ===================================================================
    # CHECKPOINT 3: Permission buffer should be visible
    # ===================================================================
    framework.add_step(
        TestStep.COLLECT_STATE,
        description="CHECKPOINT 3: Permission buffer visible (CRITICAL - check if prompt_data set)",
        wait_after=2
    )

    # ===================================================================
    # DIAGNOSTIC STEP 1: Press DOWN arrow
    # This is where we capture EVERYTHING that happens
    # ===================================================================
    print("\n" + "="*70)
    print("DIAGNOSTIC: About to press DOWN arrow")
    print("Watch for debug output showing:")
    print("  - [MultiLineInput.on_key] KEY EVENT")
    print("  - [ACTION_PERMISSION_DOWN] CALLED")
    print("  - permission_selected_option changes")
    print("="*70 + "\n")

    framework.add_step(
        TestStep.DOWN,
        description="DIAGNOSTIC: Press DOWN arrow (capture all events/functions/state changes)",
        wait_after=3  # Extra time to capture all debug output
    )

    # ===================================================================
    # CHECKPOINT 4: After DOWN arrow
    # ===================================================================
    framework.add_step(
        TestStep.COLLECT_STATE,
        description="CHECKPOINT 4: After DOWN arrow (verify selection changed)",
        wait_after=2
    )

    # ===================================================================
    # DIAGNOSTIC STEP 2: Press UP arrow (verify reverse direction)
    # ===================================================================
    framework.add_step(
        TestStep.UP,
        description="DIAGNOSTIC: Press UP arrow (verify bidirectional navigation)",
        wait_after=3
    )

    # ===================================================================
    # CHECKPOINT 5: After UP arrow
    # ===================================================================
    framework.add_step(
        TestStep.COLLECT_STATE,
        description="CHECKPOINT 5: After UP arrow (should be back to first option)",
        wait_after=2
    )

    # ===================================================================
    # DIAGNOSTIC STEP 3: Press DOWN again then ENTER
    # ===================================================================
    framework.add_step(
        TestStep.DOWN,
        description="DIAGNOSTIC: Press DOWN again",
        wait_after=2
    )

    framework.add_step(
        TestStep.ENTER,
        description="DIAGNOSTIC: Press ENTER to confirm selection (test response handling)",
        wait_after=2
    )

    # ===================================================================
    # CHECKPOINT 6: Final state after ENTER
    # ===================================================================
    framework.add_step(
        TestStep.COLLECT_STATE,
        description="CHECKPOINT 6: Final state (permission prompt should be cleared)",
        wait_after=1
    )

    print("\n" + "="*70)
    print("TEST SEQUENCE CONFIGURED - Starting visual test...")
    print("="*70 + "\n")

    # Run test in VISUAL mode to see everything
    result = framework.run_test(visual=True)

    # ===================================================================
    # ANALYZE RESULTS
    # ===================================================================
    print("\n" + "="*70)
    print("COMPREHENSIVE DIAGNOSTIC RESULTS")
    print("="*70 + "\n")

    if result.passed:
        print("✅ TEST PASSED - Arrow keys working correctly")
        print()
        print("Key findings:")
        print("  ✓ Permission buffer appeared")
        print("  ✓ DOWN arrow changed selection")
        print("  ✓ UP arrow changed selection")
        print("  ✓ ENTER confirmed selection")
    else:
        print("❌ TEST FAILED - Arrow key navigation broken")
        print()
        print("Failure Analysis:")
        print(f"  Message: {result.message}")
        print()

        if result.failing_functions:
            print("Auto-Detected Failing Functions:")
            for func_info in result.failing_functions:
                print(f"\n  📁 File: {func_info.get('file')}")
                print(f"  🎯 Function: {func_info.get('function')}")
                print(f"  📍 Line: {func_info.get('line')}")
                if func_info.get('suggestion'):
                    print(f"  💡 Suggestion: {func_info.get('suggestion')}")

    print("\n" + "="*70)
    print("DEBUG OUTPUT ANALYSIS INSTRUCTIONS")
    print("="*70)
    print()
    print("1. Check stderr output above for debug messages")
    print()
    print("2. Look for these key indicators:")
    print()
    print("   IF YOU SEE:")
    print("     [MultiLineInput.on_key] ====== KEY EVENT ======")
    print("     [MultiLineInput.on_key] KEY='down'")
    print("   THEN: on_key() IS being called")
    print()
    print("   IF YOU SEE:")
    print("     [ACTION_PERMISSION_DOWN] CALLED")
    print("   THEN: BINDINGS are firing (may be blocking on_key)")
    print()
    print("   IF YOU SEE:")
    print("     [MultiLineInput.on_key] DOWN KEY - current=0, options=2")
    print("     [MultiLineInput.on_key] DOWN - changed 0 -> 1")
    print("   THEN: Selection IS changing in code")
    print()
    print("   IF YOU SEE:")
    print("     [MultiLineInput.on_key] DOWN - refresh() called")
    print("   THEN: refresh() IS being called")
    print()
    print("3. Check tmux pane captures (BEFORE/AFTER):")
    print("   - Look at /tmp/before_down_*.txt")
    print("   - Look at /tmp/after_down_*.txt")
    print("   - Compare selection indicators (▸)")
    print()
    print("4. Common failure modes:")
    print()
    print("   MODE A: No debug output at all")
    print("     → Widget doesn't have focus OR event not reaching widget")
    print()
    print("   MODE B: Only ACTION_PERMISSION_DOWN debug")
    print("     → BINDINGS consuming event before on_key()")
    print()
    print("   MODE C: on_key() debug but selection doesn't change visually")
    print("     → refresh() not updating UI OR reactive property issue")
    print()
    print("   MODE D: Key name mismatch")
    print("     → Check if KEY='Down' vs 'down' (case mismatch)")
    print()

    if hasattr(result, 'log_file'):
        print(f"Full test log: {result.log_file}")

    print("\n" + "="*70 + "\n")

    # Cleanup
    framework.cleanup()

    return 0 if result.passed else 1


if __name__ == "__main__":
    exit_code = run_comprehensive_arrow_diagnostic()
    sys.exit(exit_code)
