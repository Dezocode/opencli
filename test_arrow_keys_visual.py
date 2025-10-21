#!/usr/bin/env python3
"""
Arrow Key Test - Simple Visual Test Using TUI Framework API
Uses the convenience API for visual dual-window testing
"""

import sys
import os

# Add modules to path
sys.path.insert(0, os.path.expanduser("~/opencli"))

from modules.testing.tui_test_framework import create_permission_buffer_test

def main():
    """Run visual arrow key test"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  ARROW KEY VISUAL TEST - TUI Test Framework              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("▶ Creating permission buffer test for /help command...")

    # Use convenience API to create pre-configured test
    test = create_permission_buffer_test("/help")

    print("✅ Test configured")
    print()
    print("▶ Running VISUAL test (dual terminal windows)...")
    print("   • LEFT window: opencli tui (actual running instance)")
    print("   • RIGHT window: Test controller (sends commands)")
    print()
    print("   The test will:")
    print("   1. Type /help")
    print("   2. Press ENTER twice (autocomplete + submit)")
    print("   3. Wait for permission buffer")
    print("   4. Press DOWN arrow (should select 'No')")
    print("   5. Press UP arrow (should select 'Yes')")
    print("   6. Verify selection state")
    print()
    print("⏳ Launching test windows...")
    print()

    # Run test in visual mode - framework handles everything
    result = test.run_test(visual=True)

    # Print results
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)
    print(f"\nStatus: {'✅ PASSED' if result.passed else '❌ FAILED'}")
    print(f"Message: {result.message}")

    if result.log_file:
        print(f"\n📄 Full output log: {result.log_file}")
        print(f"   View: cat {result.log_file}")
        print(f"   Search stderr: cat {result.log_file} | grep -E '\\[MultiLineInput|\\[TUI'")
        print(f"   Search focus: cat {result.log_file} | grep -i focus")
        print(f"   Search keys: cat {result.log_file} | grep -i 'KEY='")

    if result.failing_functions:
        print(f"\n🔍 Failing Functions Detected:")
        for func in result.failing_functions:
            print(f"   • {func.get('function')} at {func.get('file')}:{func.get('line')}")

    if result.details:
        output = result.details.get('output', '')
        if '❌ FAIL' in output:
            print(f"\n📋 Failures:")
            for line in output.split('\n'):
                if '❌ FAIL' in line or '❌' in line:
                    print(f"   {line.strip()}")

    print("\n" + "="*80)

    # Cleanup
    print("\n▶ Cleaning up...")
    test.cleanup()

    print("✅ Test complete!")
    print()

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
