#!/usr/bin/env python3
"""
Claude Code Interactive IPC Terminal
Press hotkey to type message, sends to OpenCLI AI, shows response
"""

import asyncio
import sys
import termios
import tty
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "modules"))

from opencli_ipc import IPCClient, MessageType


class InteractiveIPCTerminal:
    """Interactive terminal with hotkey for sending messages to OpenCLI AI"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.client = None
        self.connected = False
        self.responses = []
        self.message_queue = asyncio.Queue()

    async def connect(self):
        """Connect to OpenCLI IPC server"""
        self.client = IPCClient(
            agent_name="Claude Code Interactive Terminal",
            description="Interactive terminal with hotkey message sending",
            metadata={
                "mode": "interactive",
                "capabilities": ["message_sending", "response_receiving"]
            }
        )

        try:
            await self.client.connect(self.session_id)
            self.connected = True

            # Register response handler
            self.client.register_handler(MessageType.MESSAGE.value, self.handle_response)
            self.client.register_handler(MessageType.RESPONSE.value, self.handle_response)

            print(f"✓ Connected to OpenCLI session")
            print(f"  Session ID: {self.session_id}\n")

            return True

        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    async def handle_response(self, message):
        """Handle response from OpenCLI"""
        payload = message.payload

        if 'content' in payload:
            content = payload['content']
            print(f"\n{'='*60}")
            print(f"📨 AI Response from OpenCLI:")
            print(f"{'='*60}")
            print(f"{content}")
            print(f"{'='*60}\n")
            print("Press [Ctrl+M] to send another message, [Ctrl+C] to quit")
            print("> ", end="", flush=True)

    async def send_message_to_ai(self, user_message: str):
        """Send message to OpenCLI to be processed by AI"""
        print(f"\n📤 Sending to OpenCLI AI: {user_message}")

        # Send as user message to trigger AI response
        await self.client.send_message(
            MessageType.MESSAGE.value,
            {
                "role": "user",
                "content": user_message,
                "from_ipc": True,
                "agent_id": self.client.agent_id
            }
        )

        print("✓ Message sent to AI, waiting for response...\n")

    def get_input_nonblocking(self):
        """Get keyboard input in raw mode"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    async def input_loop(self):
        """Main input loop for hotkey detection"""
        print("\n" + "="*60)
        print("🎹 HOTKEY MODE ACTIVE")
        print("="*60)
        print("Press [Ctrl+M] (or Enter) to type a message")
        print("Press [Ctrl+C] to quit")
        print("="*60 + "\n")
        print("> ", end="", flush=True)

        while self.connected:
            try:
                await asyncio.sleep(0.1)

                # Check for input in non-blocking mode
                import select
                if select.select([sys.stdin], [], [], 0)[0]:
                    char = sys.stdin.read(1)

                    # Ctrl+M or Enter (newline)
                    if char == '\r' or char == '\n':
                        print()  # New line
                        message = input("💬 Type your message: ").strip()

                        if message:
                            await self.send_message_to_ai(message)

                        print("\n> ", end="", flush=True)

            except KeyboardInterrupt:
                print("\n\n⏹️  Shutting down...")
                break

    async def heartbeat_loop(self):
        """Send periodic heartbeats"""
        while self.connected:
            await asyncio.sleep(30)
            if self.connected:
                await self.client.send_heartbeat()

    async def run(self):
        """Main run loop"""
        if not await self.connect():
            return 1

        # Start heartbeat
        heartbeat_task = asyncio.create_task(self.heartbeat_loop())

        # Send initial ready message
        await self.client.send_message(
            MessageType.MESSAGE.value,
            {
                "role": "assistant",
                "content": "🎹 Claude Code Interactive Terminal connected! Press Ctrl+M to send messages."
            }
        )

        # Run input loop
        try:
            await self.input_loop()
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()

        # Cleanup
        heartbeat_task.cancel()
        await self.client.disconnect()
        print("✓ Disconnected\n")

        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 claude_code_interactive.py <session_id>")
        print("\nExample:")
        print("  python3 claude_code_interactive.py 6816b680-24cd-430e-8594-f675f53c13d9")
        sys.exit(1)

    session_id = sys.argv[1]
    terminal = InteractiveIPCTerminal(session_id)
    exit_code = asyncio.run(terminal.run())
    sys.exit(exit_code)
