#!/usr/bin/env python3
"""
Send a message from Claude Code to OpenCLI's prompt area via IPC
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "modules"))

from opencli_ipc import IPCClient, MessageType


async def send_message(session_id: str, message: str):
    """Send message to OpenCLI"""

    client = IPCClient(
        agent_name="Claude Code Message Sender",
        description="Sending message to OpenCLI",
        metadata={"mode": "message_sender"}
    )

    try:
        print(f"🔗 Connecting to session: {session_id}")
        await client.connect(session_id)
        print("✓ Connected\n")

        print(f"📤 Sending message to OpenCLI prompt area...")
        await client.send_message(
            MessageType.MESSAGE.value,
            {
                "role": "assistant",
                "content": message
            }
        )
        print("✓ Message sent!\n")

        await asyncio.sleep(1)
        await client.disconnect()
        print("✓ Disconnected\n")

        return 0

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 send_message_to_opencli.py <session_id> <message>")
        print("\nExample:")
        print('  python3 send_message_to_opencli.py 6816b680-24cd-430e-8594-f675f53c13d9 "Hello from Claude Code!"')
        sys.exit(1)

    session_id = sys.argv[1]
    message = " ".join(sys.argv[2:])

    exit_code = asyncio.run(send_message(session_id, message))
    sys.exit(exit_code)
