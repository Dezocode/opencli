#!/usr/bin/env python3
"""Test that permission buffer displays after fix"""

import sys
sys.path.insert(0, '/Users/dezmondhollins/.opencli')

from opencli_controller import OpenCLIController
import time

print("=" * 80)
print("TESTING PERMISSION BUFFER DISPLAY AFTER FIX")
print("=" * 80)

with OpenCLIController(debug=True) as controller:
    # Start TUI
    print("\n[1] Starting OpenCLI TUI...")
    success = controller.start_opencli("tui")
    if not success:
        print("❌ Failed to start TUI")
        sys.exit(1)

    print("✅ TUI started successfully")

    # Wait for initialization
    time.sleep(3)

    # Send /help command
    print("\n[2] Sending /help command...")
    try:
        controller.send_message("/help")
        print("✅ Command sent")
    except Exception as e:
        print(f"❌ Failed to send /help: {e}")
        sys.exit(1)

    # Wait for permission buffer to appear
    print("\n[3] Waiting for permission buffer...")
    time.sleep(2)

    # Capture screen
    screen_text = controller.get_screen_content()

    print("\n" + "=" * 80)
    print("SCREEN CONTENT:")
    print("=" * 80)
    print(screen_text[-1000:] if len(screen_text) > 1000 else screen_text)  # Last 1000 chars
    print("=" * 80)

    # Check for permission buffer indicators
    indicators = {
        'title': 'System:' in screen_text or '/help' in screen_text,
        'command_help': 'Command Help' in screen_text,
        'view_all': 'View all commands' in screen_text,
        'view_by_category': 'View by category' in screen_text,
        'export': 'Export to file' in screen_text,
        'cancel': 'Cancel' in screen_text or 'cancel' in screen_text.lower(),
    }

    print(f"\n[4] Permission buffer indicators:")
    for key, found in indicators.items():
        status = "✅" if found else "❌"
        print(f"   {status} {key}: {found}")

    total_found = sum(indicators.values())

    if total_found >= 3:
        print(f"\n✅ PERMISSION BUFFER IS DISPLAYING! ({total_found}/6 indicators found)")
        sys.exit(0)
    else:
        print(f"\n❌ PERMISSION BUFFER NOT FOUND ({total_found}/6 indicators found)")
        sys.exit(1)
