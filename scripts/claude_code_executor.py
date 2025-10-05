#!/usr/bin/env python3
"""
Claude Code IPC Executor
Persistent connection with shell command execution capability
"""

import asyncio
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from opencli_ipc import IPCClient, MessageType


class ClaudeCodeExecutor:
    """Claude Code executor with IPC command handling"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.client = None
        self.connected = False
        self.cwd = str(Path.cwd())

    async def connect(self):
        """Connect to OpenCLI IPC server"""
        self.client = IPCClient(
            agent_name="Claude Code Executor",
            description="Claude Code with shell command execution",
            metadata={
                "version": "4.5",
                "model": "claude-sonnet-4-5",
                "capabilities": [
                    "shell_execution",
                    "file_operations",
                    "code_editing",
                    "code_analysis",
                    "web_search"
                ],
                "mode": "executor",
                "cwd": self.cwd
            }
        )

        try:
            await self.client.connect(self.session_id)
            self.connected = True

            # Register handlers
            self.client.register_handler(MessageType.COMMAND.value, self.handle_command)
            self.client.register_handler(MessageType.MESSAGE.value, self.handle_message)
            self.client.register_handler("injection", self.handle_injection)

            print(f"✓ Connected to OpenCLI session: {self.session_id}")
            print(f"  Agent ID: {self.client.agent_id}")
            print(f"  Working Directory: {self.cwd}\n")

            # Send ready message
            await self.send_message("🤖 Claude Code Executor ready. Send commands via /inject")

            return True

        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    async def handle_command(self, message):
        """Handle command execution request from OpenCLI"""
        payload = message.payload
        command = payload.get('command', '')
        command_type = payload.get('type', 'bash')

        print(f"\n📨 Received command request:")
        print(f"   Type: {command_type}")
        print(f"   Command: {command}\n")

        if command_type == 'bash':
            result = await self.execute_bash(command)
        elif command_type == 'read':
            result = await self.read_file(payload.get('file_path'))
        elif command_type == 'write':
            result = await self.write_file(payload.get('file_path'), payload.get('content'))
        else:
            result = {
                'success': False,
                'error': f'Unknown command type: {command_type}'
            }

        # Send result back
        await self.client.send_message(
            MessageType.RESPONSE.value,
            {
                'command_id': message.msg_id,
                'result': result
            }
        )

        print(f"✓ Result sent back to OpenCLI\n")

    async def execute_bash(self, command: str) -> dict:
        """Execute bash command and return result"""
        print(f"🔧 Executing: {command}")

        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd
            )

            stdout, stderr = await process.communicate()

            result = {
                'success': process.returncode == 0,
                'stdout': stdout.decode('utf-8'),
                'stderr': stderr.decode('utf-8'),
                'exit_code': process.returncode,
                'command': command,
                'cwd': self.cwd,
                'timestamp': datetime.now().isoformat()
            }

            print(f"   Exit code: {process.returncode}")
            if stdout:
                print(f"   Output: {stdout.decode('utf-8')[:200]}")

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': command
            }

    async def read_file(self, file_path: str) -> dict:
        """Read file and return contents"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = Path(self.cwd) / path

            content = path.read_text()

            return {
                'success': True,
                'file_path': str(path),
                'content': content,
                'size': len(content)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }

    async def write_file(self, file_path: str, content: str) -> dict:
        """Write content to file"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = Path(self.cwd) / path

            path.write_text(content)

            return {
                'success': True,
                'file_path': str(path),
                'size': len(content)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }

    async def handle_message(self, message):
        """Handle regular message from OpenCLI"""
        payload = message.payload
        content = payload.get('content', '')

        print(f"\n💬 Message from OpenCLI:")
        print(f"   {content}\n")

    async def handle_injection(self, message):
        """Handle injection message from OpenCLI"""
        payload = message.payload
        injection_type = payload.get('type', '')
        content = payload.get('content', '')

        print(f"\n💉 Injection received:")
        print(f"   Type: {injection_type}")
        print(f"   Content: {content}\n")

    async def send_message(self, content: str):
        """Send message to OpenCLI"""
        await self.client.send_message(
            MessageType.MESSAGE.value,
            {
                'role': 'assistant',
                'content': content
            }
        )

    async def heartbeat_loop(self):
        """Send periodic heartbeats"""
        while self.connected:
            await asyncio.sleep(30)
            if self.connected:
                await self.client.send_heartbeat()
                print("💓 Heartbeat sent")

    async def run(self):
        """Main run loop"""
        if not await self.connect():
            return 1

        # Start heartbeat
        heartbeat_task = asyncio.create_task(self.heartbeat_loop())

        print("🔄 Claude Code Executor running")
        print("   Listening for commands from OpenCLI")
        print("   Press Ctrl+C to disconnect\n")
        print("=" * 60 + "\n")

        try:
            while self.connected:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⏹️  Shutting down...")

        heartbeat_task.cancel()
        await self.client.disconnect()
        print("✓ Disconnected cleanly\n")

        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 claude_code_executor.py <session_id>")
        print("\nExample:")
        print("  python3 claude_code_executor.py e7694462-9189-43fb-b1e8-ff460e20e24c")
        sys.exit(1)

    session_id = sys.argv[1]
    executor = ClaudeCodeExecutor(session_id)
    exit_code = asyncio.run(executor.run())
    sys.exit(exit_code)
