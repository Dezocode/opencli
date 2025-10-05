#!/usr/bin/env python3
"""
Claude Code IPC Bridge
Enables Claude Code to communicate with OpenCLI via IPC
"""

import asyncio
import sys
import os
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from opencli_ipc import IPCClient, MessageType


class ClaudeCodeBridge:
    """Bridge between Claude Code and OpenCLI"""

    def __init__(self, session_id: str = None):
        self.session_id = session_id
        self.client = None
        self.connected = False

    async def connect(self, session_id: str = None):
        """Connect to OpenCLI IPC server"""
        if session_id:
            self.session_id = session_id

        if not self.session_id:
            raise ValueError("Session ID required for IPC connection")

        self.client = IPCClient(
            agent_name="Claude Code",
            description="Anthropic's Claude Code assistant",
            metadata={
                "version": "4.5",
                "model": "claude-sonnet-4-5",
                "capabilities": [
                    "code_editing",
                    "file_operations",
                    "bash_execution",
                    "code_analysis",
                    "web_search"
                ]
            }
        )

        try:
            await self.client.connect(self.session_id)
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            raise ConnectionError(f"Failed to connect to OpenCLI: {e}")

    async def send_message(self, content: str, role: str = "assistant"):
        """Send message to OpenCLI"""
        if not self.connected:
            raise RuntimeError("Not connected to OpenCLI. Call connect() first.")

        await self.client.send_message(
            MessageType.MESSAGE.value,
            {
                "role": role,
                "content": content
            }
        )

    async def send_tool_use(self, tool_name: str, parameters: dict, result: str):
        """Send tool usage notification to OpenCLI"""
        if not self.connected:
            raise RuntimeError("Not connected to OpenCLI. Call connect() first.")

        await self.client.send_message(
            MessageType.TOOL_USE.value,
            {
                "tool": tool_name,
                "parameters": parameters,
                "result": result
            }
        )

    async def send_status(self, status: str, details: dict = None):
        """Send status update to OpenCLI"""
        if not self.connected:
            raise RuntimeError("Not connected to OpenCLI. Call connect() first.")

        await self.client.send_message(
            MessageType.STATUS.value,
            {
                "status": status,
                "details": details or {}
            }
        )

    async def disconnect(self):
        """Disconnect from OpenCLI"""
        if self.connected and self.client:
            await self.client.disconnect()
            self.connected = False

    def __del__(self):
        """Cleanup on deletion"""
        if self.connected:
            # Try to disconnect gracefully
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.disconnect())
                else:
                    loop.run_until_complete(self.disconnect())
            except:
                pass


# Singleton instance for easy access
_bridge_instance = None

def get_claude_bridge(session_id: str = None) -> ClaudeCodeBridge:
    """Get singleton Claude Code bridge instance"""
    global _bridge_instance

    if _bridge_instance is None:
        _bridge_instance = ClaudeCodeBridge(session_id)
    elif session_id and _bridge_instance.session_id != session_id:
        # Different session, create new instance
        _bridge_instance = ClaudeCodeBridge(session_id)

    return _bridge_instance


async def test_connection(session_id: str):
    """Test IPC connection to OpenCLI"""
    bridge = get_claude_bridge(session_id)

    try:
        print(f"🔗 Connecting to OpenCLI session: {session_id}")
        await bridge.connect()
        print("✓ Connected successfully!")

        print("\n📤 Sending test message...")
        await bridge.send_message(
            "🤖 Hello from Claude Code! IPC bridge is working."
        )
        print("✓ Message sent!")

        print("\n📊 Sending status update...")
        await bridge.send_status("ready", {
            "capabilities": ["code_editing", "file_operations", "bash_execution"]
        })
        print("✓ Status sent!")

        print("\n⏳ Waiting 5 seconds for responses...")
        await asyncio.sleep(5)

        await bridge.disconnect()
        print("\n✓ Disconnected cleanly")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 claude_code_bridge.py <session_id>")
        print("\nExample:")
        print("  python3 claude_code_bridge.py 77dc8cc8-e8ed-4111-ae5a-76bb1975b606")
        sys.exit(1)

    session_id = sys.argv[1]
    success = asyncio.run(test_connection(session_id))
    sys.exit(0 if success else 1)
