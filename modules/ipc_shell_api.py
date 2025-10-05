"""
IPC Shell API - Bidirectional Read/Write Capabilities
Provides high-level API for subagents to interact with OpenCLI shell
"""

import asyncio
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from opencli_ipc import IPCClient, MessageType, IPCMessage


@dataclass
class ShellMessage:
    """Represents a message in the shell (user or assistant)"""
    role: str           # 'user' or 'assistant'
    content: str        # Message content
    timestamp: float    # When message was sent


class ShellAPI:
    """
    High-level API for subagents to interact with OpenCLI shell
    Provides bidirectional read/write capabilities
    """

    def __init__(self, agent_name: str, description: str = ""):
        self.client = IPCClient(agent_name, description)
        self.session_id = None
        self.message_buffer: List[ShellMessage] = []
        self.message_callback: Optional[Callable] = None

        # Register handlers
        self.client.register_handler(MessageType.MESSAGE.value, self._handle_message)
        self.client.register_handler(MessageType.RESPONSE.value, self._handle_response)

    async def connect(self, session_id: str):
        """Connect to OpenCLI instance"""
        await self.client.connect(session_id)
        self.session_id = session_id

    async def disconnect(self):
        """Disconnect from OpenCLI instance"""
        await self.client.disconnect()

    async def write_to_shell(self, message: str, role: str = "assistant"):
        """
        Write a message to the OpenCLI shell

        Args:
            message: The message content to send
            role: Either 'user' or 'assistant' (default: 'assistant')
        """
        await self.client.send_message(
            MessageType.MESSAGE.value,
            {
                'role': role,
                'content': message
            }
        )

    async def read_from_shell(self, timeout: Optional[float] = None) -> Optional[ShellMessage]:
        """
        Read the next message from the shell

        Args:
            timeout: Optional timeout in seconds

        Returns:
            ShellMessage or None if timeout
        """
        if self.message_buffer:
            return self.message_buffer.pop(0)

        # Wait for message with timeout
        if timeout:
            try:
                await asyncio.wait_for(self._wait_for_message(), timeout=timeout)
                if self.message_buffer:
                    return self.message_buffer.pop(0)
            except asyncio.TimeoutError:
                return None
        else:
            await self._wait_for_message()
            if self.message_buffer:
                return self.message_buffer.pop(0)

        return None

    async def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a command in the OpenCLI shell and get response

        Args:
            command: The command to execute

        Returns:
            Dict with 'success', 'output', 'error' keys
        """
        # Send command request
        msg_id = await self.client.send_message(
            MessageType.COMMAND.value,
            {
                'command': command
            }
        )

        # Wait for response
        response = await self._wait_for_response(msg_id)
        return response

    def on_message(self, callback: Callable[[ShellMessage], None]):
        """
        Register a callback for incoming messages

        Args:
            callback: Function that takes a ShellMessage
        """
        self.message_callback = callback

    async def stream_write(self, text_generator):
        """
        Stream text to the shell (for real-time output)

        Args:
            text_generator: Async generator yielding text chunks
        """
        async for chunk in text_generator:
            await self.client.send_message(
                MessageType.MESSAGE.value,
                {
                    'role': 'assistant',
                    'content': chunk,
                    'stream': True
                }
            )

    async def get_shell_history(self) -> List[ShellMessage]:
        """
        Get message history from the shell

        Returns:
            List of ShellMessage objects
        """
        await self.client.send_message(
            MessageType.COMMAND.value,
            {'command': 'get_history'}
        )

        response = await self._wait_for_response()
        messages = response.get('messages', [])

        return [
            ShellMessage(
                role=msg['role'],
                content=msg['content'],
                timestamp=msg['timestamp']
            )
            for msg in messages
        ]

    async def get_shell_status(self) -> Dict[str, Any]:
        """
        Get current status of the shell

        Returns:
            Dict with shell status information
        """
        await self.client.send_message(
            MessageType.STATUS.value,
            {'query': 'full_status'}
        )

        return await self._wait_for_response()

    # Internal handlers

    async def _handle_message(self, message: IPCMessage):
        """Handle incoming message from shell"""
        payload = message.payload
        shell_msg = ShellMessage(
            role=payload.get('role', 'assistant'),
            content=payload.get('content', ''),
            timestamp=message.timestamp
        )

        # Add to buffer
        self.message_buffer.append(shell_msg)

        # Call callback if registered
        if self.message_callback:
            self.message_callback(shell_msg)

    async def _handle_response(self, message: IPCMessage):
        """Handle response from shell"""
        # Store response for waiting coroutines
        self._last_response = message.payload

    async def _wait_for_message(self):
        """Wait for a message to arrive"""
        while not self.message_buffer:
            await asyncio.sleep(0.1)

    async def _wait_for_response(self, msg_id: Optional[str] = None):
        """Wait for a response message"""
        # Simple implementation - could be improved with message ID tracking
        timeout = 30
        elapsed = 0
        while elapsed < timeout:
            if hasattr(self, '_last_response'):
                response = self._last_response
                delattr(self, '_last_response')
                return response
            await asyncio.sleep(0.1)
            elapsed += 0.1

        raise TimeoutError("Response timeout")


class SubagentAPI:
    """
    Convenience wrapper for common subagent operations
    Combines ShellAPI with additional helper methods
    """

    def __init__(self, agent_name: str, description: str = ""):
        self.shell = ShellAPI(agent_name, description)
        self.connected = False

    async def connect(self, session_id: str):
        """Connect to OpenCLI instance"""
        await self.shell.connect(session_id)
        self.connected = True

    async def disconnect(self):
        """Disconnect from OpenCLI instance"""
        await self.shell.disconnect()
        self.connected = False

    async def send(self, message: str):
        """Send a message to the shell"""
        await self.shell.write_to_shell(message)

    async def receive(self, timeout: Optional[float] = None) -> Optional[str]:
        """Receive a message from the shell"""
        msg = await self.shell.read_from_shell(timeout)
        return msg.content if msg else None

    async def ask(self, question: str, timeout: float = 30.0) -> Optional[str]:
        """
        Ask a question and wait for response

        Args:
            question: Question to ask
            timeout: Max time to wait for response

        Returns:
            Response text or None if timeout
        """
        await self.send(question)
        return await self.receive(timeout)

    def on_receive(self, callback: Callable[[str], None]):
        """Register callback for received messages"""
        def wrapper(msg: ShellMessage):
            callback(msg.content)
        self.shell.on_message(wrapper)

    async def run_command(self, command: str) -> str:
        """Run a command and get output"""
        result = await self.shell.execute_command(command)
        if result.get('success'):
            return result.get('output', '')
        else:
            raise RuntimeError(result.get('error', 'Command failed'))

    async def stream_output(self, text_generator):
        """Stream output to shell"""
        await self.shell.stream_write(text_generator)

    async def __aenter__(self):
        """Context manager support"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        if self.connected:
            await self.disconnect()


# Convenience functions

async def connect_to_opencli(session_id: str, agent_name: str, description: str = "") -> SubagentAPI:
    """
    Connect to an OpenCLI instance as a subagent

    Args:
        session_id: The OpenCLI session ID to connect to
        agent_name: Name of this subagent
        description: Optional description

    Returns:
        Connected SubagentAPI instance
    """
    api = SubagentAPI(agent_name, description)
    await api.connect(session_id)
    return api


async def send_to_opencli(session_id: str, message: str, agent_name: str = "Anonymous"):
    """
    Quick send a message to OpenCLI without persistent connection

    Args:
        session_id: The OpenCLI session ID
        message: Message to send
        agent_name: Name to identify this sender
    """
    async with SubagentAPI(agent_name) as api:
        await api.connect(session_id)
        await api.send(message)
