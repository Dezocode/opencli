#!/usr/bin/env python3
"""
Claude Code Persistent IPC Connection
Maintains an active connection to OpenCLI for real-time bidirectional communication
"""

import asyncio
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from opencli_ipc import IPCClient, MessageType


async def persistent_connection(session_id: str):
    """Maintain persistent connection to OpenCLI"""

    client = IPCClient(
        agent_name="Claude Code",
        description="Anthropic's Claude Code assistant - Persistent Mode",
        metadata={
            "version": "4.5",
            "model": "claude-sonnet-4-5",
            "capabilities": [
                "code_editing",
                "file_operations",
                "bash_execution",
                "code_analysis",
                "web_search"
            ],
            "mode": "persistent"
        }
    )

    try:
        print(f"🔗 Connecting to OpenCLI session: {session_id}")
        await client.connect(session_id)
        print("✓ Connected successfully!")
        print(f"  Agent ID: {client.agent_id}")
        print(f"  Session ID: {client.session_id}\n")

        # Send initial message
        await client.send_message(
            MessageType.MESSAGE.value,
            {
                "role": "assistant",
                "content": "🤖 Claude Code connected in persistent mode. Ready to assist!"
            }
        )
        print("✓ Initial message sent\n")

        # Register message handler
        async def handle_message(message):
            print(f"\n📨 Received message:")
            print(f"   Type: {message.msg_type}")
            print(f"   From: {message.sender_id}")
            print(f"   Payload: {message.payload}\n")

            # Echo back for testing
            if message.msg_type == MessageType.MESSAGE.value:
                await client.send_message(
                    MessageType.MESSAGE.value,
                    {
                        "role": "assistant",
                        "content": f"Echo: Received your message"
                    }
                )

        client.register_handler(MessageType.MESSAGE.value, handle_message)
        client.register_handler(MessageType.COMMAND.value, handle_message)
        client.register_handler("injection", handle_message)

        # Send heartbeat every 30 seconds
        async def heartbeat_loop():
            while client.connected:
                await asyncio.sleep(30)
                if client.connected:
                    await client.send_heartbeat()
                    print("💓 Heartbeat sent")

        heartbeat_task = asyncio.create_task(heartbeat_loop())

        print("🔄 Persistent connection active")
        print("   Press Ctrl+C to disconnect\n")
        print("=" * 60)

        # Keep connection alive
        try:
            while client.connected:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⏹️  Shutting down...")

        heartbeat_task.cancel()
        await client.disconnect()
        print("✓ Disconnected cleanly\n")

    except ConnectionError as e:
        print(f"✗ Connection failed: {e}")
        print("\nPossible issues:")
        print("  1. IPC server not running (run `/api start` in OpenCLI)")
        print("  2. Wrong session ID")
        print("  3. Socket file doesn't exist")
        return 1

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 claude_code_persistent.py <session_id>")
        print("\nExample:")
        print("  python3 claude_code_persistent.py e7694462-9189-43fb-b1e8-ff460e20e24c")
        sys.exit(1)

    session_id = sys.argv[1]
    exit_code = asyncio.run(persistent_connection(session_id))
    sys.exit(exit_code)
