#!/usr/bin/env python3
"""
Test script to send /upgrade command via IPC to reload modules
"""
import asyncio
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.expanduser("~/.opencli/modules"))

from opencli_ipc import IPCClient, MessageType


async def send_upgrade_command():
    """Connect to OpenCLI IPC server and send /upgrade command"""

    # Extract session_id from socket path
    session_id = "542a55b6-aacb-42b8-a74e-59179d1cdb62"
    socket_dir = "/tmp/opencli"

    print(f"🔌 Connecting to OpenCLI IPC server...")
    print(f"📍 Session ID: {session_id}")

    client = IPCClient(socket_dir, "claude_code_upgrade_client")

    try:
        # Connect to server
        await client.connect(session_id)
        print("✅ Connected to OpenCLI IPC server")

        # Send /upgrade command to reload modules
        print("\n📤 Sending /upgrade command...")
        await client.send_message(
            MessageType.MESSAGE.value,
            {
                "content": "/upgrade",
                "sender": "claude_code_client",
                "timestamp": asyncio.get_event_loop().time()
            }
        )
        print("✅ /upgrade command sent")
        print("\n💡 After upgrade completes, manually type: /restart")

        # Wait a bit for response
        print("\n⏳ Waiting for response...")
        await asyncio.sleep(2)

        print("\n✅ Module upgrade initiated via IPC")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()
        print("\n🔌 Disconnected from IPC server")


if __name__ == "__main__":
    asyncio.run(send_upgrade_command())
