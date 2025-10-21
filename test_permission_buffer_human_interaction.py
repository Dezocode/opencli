#!/usr/bin/env python3
"""
Test /help permission buffer with human-like interaction
Simulates: Type /help, press DOWN arrow to select "No", press ENTER
"""

import pytest
import pexpect
import sys
import time
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))


class TestPermissionBufferHumanInteraction:
    """Test permission buffer with realistic human interaction"""

    def test_help_permission_buffer_down_arrow_no(self):
        """
        Test /help command with permission buffer interaction:
        1. Start opencli tui
        2. Type /help
        3. Wait for permission buffer
        4. Press DOWN arrow to select "No"
        5. Press ENTER to confirm
        """

        print("\n" + "="*80)
        print("🧪 TESTING /help PERMISSION BUFFER - HUMAN INTERACTION")
        print("="*80)
        print("")
        print("Actions to simulate:")
        print("  1. Start opencli tui")
        print("  2. Type: /help")
        print("  3. Wait for permission buffer")
        print("  4. Press DOWN ARROW (select 'No')")
        print("  5. Press ENTER (confirm)")
        print("")
        print("="*80)
        print("")

        # Start opencli tui with visible output
        print("▶ Starting opencli tui...")
        child = pexpect.spawn(
            'opencli tui',
            encoding='utf-8',
            timeout=10,
            dimensions=(50, 150)  # rows, cols
        )

        # Enable logging to see everything
        child.logfile_read = sys.stdout

        try:
            # Wait for TUI to be ready (look for welcome banner or prompt)
            print("\n⏳ Waiting for TUI to initialize...")
            time.sleep(2)  # Give TUI time to start

            # Look for ready indicators
            index = child.expect([
                'OPENCLI',  # Welcome banner
                'Ready',
                pexpect.TIMEOUT
            ], timeout=5)

            if index == 2:
                print("⚠️  Timeout waiting for TUI - continuing anyway")
            else:
                print("✅ TUI ready!")

            time.sleep(1)

            # Type /help command
            print("\n" + "-"*80)
            print("📝 ACTION 1: Typing '/help' command...")
            print("-"*80)
            child.send('/help')
            time.sleep(0.5)
            child.send('\r')  # Enter key

            print("✅ Sent: /help")
            time.sleep(2)  # Wait for permission buffer to render

            # Look for permission buffer
            print("\n" + "-"*80)
            print("👀 Looking for permission buffer...")
            print("-"*80)

            # The permission buffer should appear with options
            # Let's wait a moment and then send the down arrow
            time.sleep(1)

            # Send DOWN arrow key to select "No" (2nd option)
            print("\n" + "-"*80)
            print("📝 ACTION 2: Pressing DOWN ARROW (select 'No')...")
            print("-"*80)
            child.send('\x1b[B')  # ANSI escape code for down arrow
            print("✅ Sent: DOWN ARROW")
            time.sleep(1)

            # Send ENTER to confirm selection
            print("\n" + "-"*80)
            print("📝 ACTION 3: Pressing ENTER (confirm selection)...")
            print("-"*80)
            child.send('\r')
            print("✅ Sent: ENTER")
            time.sleep(2)

            # Check what happened
            print("\n" + "-"*80)
            print("📊 Checking result...")
            print("-"*80)

            # Read remaining output
            try:
                child.expect(pexpect.TIMEOUT, timeout=1)
            except:
                pass

            print("\n" + "="*80)
            print("🎬 INTERACTION COMPLETE")
            print("="*80)
            print("\nExpected behavior:")
            print("  ✓ Permission buffer appeared")
            print("  ✓ Down arrow moved selection to 'No'")
            print("  ✓ Enter confirmed 'No' selection")
            print("  ✓ Command was denied")
            print("")

            # Exit TUI (Ctrl+C)
            print("Sending Ctrl+C to exit...")
            child.sendcontrol('c')
            time.sleep(1)

        except pexpect.TIMEOUT as e:
            print(f"\n❌ TIMEOUT: {e}")
            print("\nCurrent buffer:")
            print(child.before)
            raise

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            raise

        finally:
            # Cleanup
            try:
                child.sendcontrol('c')
                time.sleep(0.5)
                child.close()
            except:
                pass

            if child.isalive():
                child.kill(9)

        print("\n✅ Test completed!")


def test_help_permission_buffer_visual():
    """
    Visual test - runs in new terminal window
    """
    import subprocess
    import os

    print("\n" + "="*80)
    print("🖥️  VISUAL TEST - OPENING NEW TERMINAL")
    print("="*80)
    print("")

    # Create a script to run
    script = '''#!/bin/bash
echo "=================================="
echo "VISUAL PERMISSION BUFFER TEST"
echo "=================================="
echo ""
echo "Watch for:"
echo "  1. TUI starts"
echo "  2. /help is typed"
echo "  3. Permission buffer appears"
echo "  4. DOWN arrow selects 'No'"
echo "  5. ENTER confirms"
echo ""
echo "Press any key to start..."
read -n 1

# Start opencli and send commands
(
    sleep 2
    echo "/help"
    sleep 2
    # Send down arrow (ESC[B)
    printf "\\x1b[B"
    sleep 1
    # Send enter
    echo ""
    sleep 2
    # Exit with Ctrl+C
    printf "\\x03"
) | opencli tui

echo ""
echo "=================================="
echo "Test completed!"
echo "Press any key to close..."
read -n 1
'''

    script_path = '/tmp/opencli_visual_test.sh'
    with open(script_path, 'w') as f:
        f.write(script)

    os.chmod(script_path, 0o755)

    # Open in new terminal window (macOS)
    try:
        subprocess.Popen([
            'osascript',
            '-e',
            f'tell application "Terminal" to do script "{script_path}"'
        ])
        print("✅ New terminal window opened!")
        print(f"   Script: {script_path}")
        print("")
        print("Watch the new terminal window for the test!")

    except Exception as e:
        print(f"❌ Could not open new terminal: {e}")
        print(f"\nRun manually: {script_path}")


if __name__ == "__main__":
    # Run the visual test
    test_help_permission_buffer_visual()

    # Also run the automated test
    print("\n\nRunning automated test in 3 seconds...")
    time.sleep(3)

    test = TestPermissionBufferHumanInteraction()
    test.test_help_permission_buffer_down_arrow_no()
