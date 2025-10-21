#!/usr/bin/env python3
"""
Test real SDK command permission buffer display using OpenCLI Controller
This sends actual commands to the TUI and verifies permission buffer appears
"""

import sys
sys.path.insert(0, '/Users/dezmondhollins/.opencli')

from opencli_controller import OpenCLIController
import time

def test_help_command_permission():
    """Test that /help command triggers permission buffer"""
    print("=" * 80)
    print("TESTING REAL /help COMMAND PERMISSION BUFFER DISPLAY")
    print("=" * 80)

    with OpenCLIController(debug=True) as controller:
        # Start TUI
        print("\n[1] Starting OpenCLI TUI...")
        success = controller.start_opencli("tui")
        if not success:
            print(f"❌ Failed to start TUI")
            return False

        print(f"✅ TUI started successfully")

        # Wait for initialization
        time.sleep(2)

        # Send /help command
        print("\n[2] Sending /help command...")
        try:
            controller.send_message("/help")
            print(f"✅ Command sent successfully")
        except Exception as e:
            print(f"❌ Failed to send /help: {e}")
            return False

        # Wait for permission buffer to appear
        print("\n[3] Waiting for permission buffer display...")
        time.sleep(1)

        # Capture current screen
        screen_text = controller.get_screen_content()

        print("\n" + "=" * 80)
        print("CURRENT SCREEN CONTENT:")
        print("=" * 80)
        print(screen_text)
        print("=" * 80)

        # Check for permission buffer indicators
        permission_indicators = [
            'System:',
            '/help',
            'Yes, allow this once',
            'Yes, and remember',
            'Yes, and auto-accept',
            'No, cancel',
            'Permission',
            'Approve',
            'Risk Level'
        ]

        found_indicators = []
        for indicator in permission_indicators:
            if indicator.lower() in screen_text.lower():
                found_indicators.append(indicator)

        print(f"\n[4] Permission buffer indicators found: {found_indicators}")

        if len(found_indicators) >= 3:
            print("✅ PERMISSION BUFFER IS DISPLAYING!")
            return True
        else:
            print("❌ PERMISSION BUFFER NOT FOUND")
            print(f"   Only found {len(found_indicators)} indicators: {found_indicators}")
            return False

if __name__ == "__main__":
    success = test_help_command_permission()
    sys.exit(0 if success else 1)
