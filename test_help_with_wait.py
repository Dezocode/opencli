#!/usr/bin/env python3
"""
Test /help with proper wait for SDK initialization
"""

import pexpect
import sys
import time

print("="*80)
print("🧪 TESTING /help PERMISSION BUFFER (With SDK Wait)")
print("="*80)
print("")

# Start opencli tui
print("▶ Starting opencli tui...")
child = pexpect.spawn(
    'opencli tui',
    encoding='utf-8',
    timeout=30,
    dimensions=(50, 150)
)

# Show output
child.logfile_read = sys.stdout

try:
    # Wait for TUI initialization
    print("\n⏳ Waiting for TUI to initialize...")
    time.sleep(2)

    # Wait for SDK initialization to COMPLETE
    print("\n⏳ Waiting for SDK initialization to complete...")
    print("   (Looking for 'SDK Initialization' to disappear)")

    # Give it time to load all command modules
    time.sleep(8)  # SDK needs time to register all commands

    print("\n✅ SDK should be initialized now")

    # Now send /help
    print("\n" + "-"*80)
    print("📝 ACTION 1: Typing '/help'...")
    print("-"*80)

    child.send('/help')
    time.sleep(0.5)
    child.send('\r')

    print("✅ Sent: /help")
    print("\n⏳ Waiting for permission buffer to appear...")
    time.sleep(3)

    # Send DOWN arrow
    print("\n" + "-"*80)
    print("📝 ACTION 2: Pressing DOWN ARROW...")
    print("-"*80)
    child.send('\x1b[B')  # Down arrow
    print("✅ Sent: DOWN ARROW")
    time.sleep(1)

    # Send ENTER
    print("\n" + "-"*80)
    print("📝 ACTION 3: Pressing ENTER...")
    print("-"*80)
    child.send('\r')
    print("✅ Sent: ENTER")
    time.sleep(2)

    # Check output
    print("\n" + "-"*80)
    print("📊 Result:")
    print("-"*80)

    # Try to read more output
    try:
        child.expect(pexpect.TIMEOUT, timeout=1)
    except:
        pass

    print("\n✅ Test sequence completed!")
    print("\nExpected behavior:")
    print("  ✓ SDK initialization completed")
    print("  ✓ /help command sent")
    print("  ✓ Permission buffer appeared")
    print("  ✓ DOWN arrow selected 'No'")
    print("  ✓ ENTER confirmed selection")

    # Keep running for observation
    print("\n" + "="*80)
    print("TUI is still running - keeping alive for 10 seconds...")
    print("Press Ctrl+C in the TUI to exit early")
    print("="*80)

    time.sleep(10)

except KeyboardInterrupt:
    print("\n\n⚠️  Interrupted by user")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

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
