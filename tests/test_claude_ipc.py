#!/usr/bin/env python3
"""
Test IPC Communication from Claude Code
Attempts to connect to OpenCLI IPC server and register as a subagent
"""

import asyncio
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from opencli_ipc import IPCClient, MessageType


async def test_claude_code_connection():
    """Test connecting as Claude Code subagent"""

    # Session ID from the IPC server output
    session_id = "77dc8cc8-e8ed-4111-ae5a-76bb1975b606"

    print("=" * 60)
    print("Claude Code → OpenCLI IPC Test")
    print("=" * 60)
    print(f"\nAttempting to connect to session: {session_id}\n")

    # Create IPC client
    client = IPCClient(
        agent_name="Claude Code",
        description="Anthropic's Claude Code assistant",
        metadata={
            "version": "4.5",
            "model": "claude-sonnet-4-5",
            "capabilities": ["code_editing", "file_operations", "bash", "analysis"]
        }
    )

    try:
        # Connect to OpenCLI
        await client.connect(session_id)
        print(f"✓ Connected successfully!")
        print(f"  Agent ID: {client.agent_id}")
        print(f"  Agent Name: {client.agent_name}\n")

        # Send a test message
        print("Sending test message to OpenCLI...")
        await client.send_message(
            MessageType.MESSAGE.value,
            {
                "role": "assistant",
                "content": "🤖 Hello from Claude Code! I've successfully connected via IPC and registered as a subagent."
            }
        )
        print("✓ Message sent!\n")

        # Listen for responses for a few seconds
        print("Listening for responses (5 seconds)...")
        await asyncio.sleep(5)

        # Disconnect
        await client.disconnect()
        print("\n✓ Disconnected cleanly")

        print("\n" + "=" * 60)
        print("SUCCESS: IPC communication working!")
        print("=" * 60)

    except ConnectionError as e:
        print(f"✗ Connection failed: {e}")
        print("\nPossible issues:")
        print("  1. IPC server not running (run `/api start` in OpenCLI)")
        print("  2. Wrong session ID")
        print("  3. Socket file doesn't exist")

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_claude_code_connection())
