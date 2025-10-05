#!/usr/bin/env python3
"""
Debug Chat Display - Diagnostic tool for OpenCLI chat area issues
Connects via IPC to diagnose why messages aren't showing
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from opencli_ipc import IPCClient, MessageType


async def diagnose_display():
    """Diagnose the chat display issue"""

    print("=" * 60)
    print("OpenCLI Chat Display Diagnostic Tool")
    print("=" * 60)

    # Check if any OpenCLI instance is running
    socket_dir = "/tmp/opencli"
    if not os.path.exists(socket_dir):
        print(f"❌ Socket directory not found: {socket_dir}")
        print("   OpenCLI IPC server may not be running")
        return

    # List available sessions
    import glob
    sockets = glob.glob(f"{socket_dir}/opencli_*.sock")

    if not sockets:
        print("❌ No OpenCLI instances found")
        print("   The IPC server needs to be started in OpenCLI")
        print("\nTo fix:")
        print("1. OpenCLI needs to initialize IPC server on startup")
        print("2. Check if session.py creates and starts IPCServer")
        return

    print(f"✓ Found {len(sockets)} OpenCLI instance(s)")

    # Get session ID from first socket
    socket_path = sockets[0]
    session_id = os.path.basename(socket_path).replace("opencli_", "").replace(".sock", "")
    print(f"✓ Connecting to session: {session_id}")

    # Try to connect
    client = IPCClient("ChatDebugger", "Diagnostic tool for chat display")

    try:
        await client.connect(session_id)
        print(f"✓ Connected successfully!")

        # Send a test message
        print("\n📤 Sending test message...")
        await client.send_message(
            MessageType.MESSAGE.value,
            {
                'role': 'assistant',
                'content': '🔧 DEBUG: This is a test message from the diagnostic tool. If you see this, message delivery works!'
            }
        )

        print("✓ Test message sent")

        # Wait a bit for any response
        print("\n⏳ Waiting for response...")
        await asyncio.sleep(2)

        await client.disconnect()
        print("\n✓ Diagnostic complete!")

        print("\n" + "=" * 60)
        print("DIAGNOSIS:")
        print("=" * 60)
        print("The IPC system is working correctly.")
        print("\nIf you don't see the test message in OpenCLI, the issue is:")
        print("1. Message handler not registered in OpenCLI")
        print("2. TUI write path is broken")
        print("3. StreamingDisplay widget not receiving messages")

        print("\nCheck these files:")
        print("- OpenCLI session.py needs to handle MESSAGE type")
        print("- TUI needs message handler that calls write()")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nThis means the IPC server is not running in OpenCLI")
        print("OpenCLI needs to be updated to start IPC server on launch")


if __name__ == "__main__":
    asyncio.run(diagnose_display())
