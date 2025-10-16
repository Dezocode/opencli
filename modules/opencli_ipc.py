"""
OpenCLI IPC (Inter-Process Communication) Module
Enables bidirectional communication between OpenCLI instances and subagents

Architecture:
- Unix domain sockets for fast local IPC
- JSON-based message protocol
- Async/await for non-blocking operations
- Subagent registration and lifecycle management
"""

import asyncio
import json
import os
import socket
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Callable, Any, List
from dataclasses import dataclass, asdict
from enum import Enum


class MessageType(Enum):
    """Types of IPC messages"""
    REGISTER = "register"           # Subagent registration
    UNREGISTER = "unregister"       # Subagent deregistration
    MESSAGE = "message"             # Chat message from user/assistant
    COMMAND = "command"             # Command execution request
    RESPONSE = "response"           # Response to a command
    STATUS = "status"               # Status update
    HEARTBEAT = "heartbeat"         # Keep-alive ping
    ERROR = "error"                 # Error notification
    INJECTION = "injection"         # Shell injection message
    TOOL_USE = "tool_use"           # Tool usage notification
    NAVIGATION = "navigation"       # Navigation update
    GOAL_PROGRESS = "goal_progress" # Goal progress update


@dataclass
class IPCMessage:
    """Structure for IPC messages"""
    msg_type: str                   # MessageType value
    sender_id: str                  # UUID of sender
    recipient_id: Optional[str]     # UUID of recipient (None for broadcast)
    payload: Dict[str, Any]         # Message payload
    timestamp: float                # Unix timestamp
    msg_id: str                     # Unique message ID

    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(data: str) -> 'IPCMessage':
        """Deserialize from JSON"""
        obj = json.loads(data)
        return IPCMessage(**obj)


@dataclass
class SubagentInfo:
    """Information about a registered subagent"""
    agent_id: str                   # Unique agent ID
    name: str                       # Human-readable name
    description: str                # Agent description
    registered_at: float            # Registration timestamp
    last_heartbeat: float           # Last heartbeat timestamp
    metadata: Dict[str, Any]        # Additional metadata


class IPCServer:
    """
    IPC Server for OpenCLI main instance
    Manages subagent connections and message routing
    """

    def __init__(self, session_id: str, socket_dir: str = "/tmp/opencli"):
        self.session_id = session_id
        self.socket_path = os.path.join(socket_dir, f"opencli_{session_id}.sock")
        self.server = None
        self.subagents: Dict[str, SubagentInfo] = {}
        self.connections: Dict[str, asyncio.StreamWriter] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.running = False

        # Ensure socket directory exists
        Path(socket_dir).mkdir(parents=True, exist_ok=True)

        # Clean up old socket if exists
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

    async def start(self):
        """Start the IPC server"""
        self.server = await asyncio.start_unix_server(
            self._handle_client,
            path=self.socket_path
        )
        self.running = True
        print(f"[IPC] Server started on {self.socket_path}")

    async def stop(self):
        """Stop the IPC server"""
        self.running = False

        # Close all client connections
        for writer in self.connections.values():
            writer.close()
            await writer.wait_closed()

        # Stop server
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        # Clean up socket
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

        print("[IPC] Server stopped")

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle a client connection"""
        client_id = None

        try:
            while self.running:
                # Read message (length-prefixed protocol)
                length_bytes = await reader.readexactly(4)
                length = int.from_bytes(length_bytes, 'big')

                data = await reader.readexactly(length)
                message = IPCMessage.from_json(data.decode('utf-8'))

                # Handle message based on type
                if message.msg_type == MessageType.REGISTER.value:
                    client_id = await self._handle_registration(message, writer)
                elif message.msg_type == MessageType.UNREGISTER.value:
                    await self._handle_unregistration(message)
                    break
                elif message.msg_type == MessageType.HEARTBEAT.value:
                    await self._handle_heartbeat(message)
                else:
                    # Route message to handler
                    await self._route_message(message)

        except asyncio.IncompleteReadError:
            # Client disconnected
            pass
        except Exception as e:
            print(f"[IPC] Error handling client: {e}")
        finally:
            # Clean up connection
            if client_id:
                self.connections.pop(client_id, None)
                self.subagents.pop(client_id, None)

            writer.close()
            await writer.wait_closed()

    async def _handle_registration(self, message: IPCMessage, writer: asyncio.StreamWriter) -> str:
        """Handle subagent registration"""
        payload = message.payload
        agent_id = message.sender_id

        # Create subagent info
        info = SubagentInfo(
            agent_id=agent_id,
            name=payload.get('name', 'Unknown'),
            description=payload.get('description', ''),
            registered_at=message.timestamp,
            last_heartbeat=message.timestamp,
            metadata=payload.get('metadata', {})
        )

        self.subagents[agent_id] = info
        self.connections[agent_id] = writer

        # Send acknowledgment
        response = IPCMessage(
            msg_type=MessageType.RESPONSE.value,
            sender_id=self.session_id,
            recipient_id=agent_id,
            payload={'status': 'registered', 'session_id': self.session_id},
            timestamp=datetime.now().timestamp(),
            msg_id=str(uuid.uuid4())
        )
        await self._send_message(writer, response)

        print(f"[IPC] Registered subagent: {info.name} ({agent_id[:8]})")

        return agent_id

    async def _handle_unregistration(self, message: IPCMessage):
        """Handle subagent unregistration"""
        agent_id = message.sender_id
        if agent_id in self.subagents:
            info = self.subagents[agent_id]
            print(f"[IPC] Unregistered subagent: {info.name} ({agent_id[:8]})")
            self.subagents.pop(agent_id, None)
            self.connections.pop(agent_id, None)

    async def _handle_heartbeat(self, message: IPCMessage):
        """Handle heartbeat from subagent"""
        agent_id = message.sender_id
        if agent_id in self.subagents:
            self.subagents[agent_id].last_heartbeat = message.timestamp

    async def _route_message(self, message: IPCMessage):
        """Route message to appropriate handler"""
        handler = self.message_handlers.get(message.msg_type)
        if handler:
            await handler(message)

    async def _send_message(self, writer: asyncio.StreamWriter, message: IPCMessage):
        """Send a message to a client"""
        data = message.to_json().encode('utf-8')
        length = len(data).to_bytes(4, 'big')

        writer.write(length + data)
        await writer.drain()

    async def broadcast(self, msg_type: str, payload: Dict[str, Any], exclude: Optional[str] = None):
        """Broadcast message to all subagents"""
        message = IPCMessage(
            msg_type=msg_type,
            sender_id=self.session_id,
            recipient_id=None,
            payload=payload,
            timestamp=datetime.now().timestamp(),
            msg_id=str(uuid.uuid4())
        )

        for agent_id, writer in self.connections.items():
            if agent_id != exclude:
                await self._send_message(writer, message)

    async def send_to_agent(self, agent_id: str, msg_type: str, payload: Dict[str, Any]):
        """Send message to specific subagent"""
        if agent_id not in self.connections:
            raise ValueError(f"Subagent {agent_id} not connected")

        message = IPCMessage(
            msg_type=msg_type,
            sender_id=self.session_id,
            recipient_id=agent_id,
            payload=payload,
            timestamp=datetime.now().timestamp(),
            msg_id=str(uuid.uuid4())
        )

        writer = self.connections[agent_id]
        await self._send_message(writer, message)

    def register_handler(self, msg_type: str, handler: Callable):
        """Register a message handler"""
        self.message_handlers[msg_type] = handler

    def get_subagent_count(self) -> int:
        """Get number of registered subagents"""
        return len(self.subagents)

    def get_subagents(self) -> List[SubagentInfo]:
        """Get list of all subagents"""
        return list(self.subagents.values())


class IPCClient:
    """
    IPC Client for subagents
    Connects to OpenCLI main instance
    """

    def __init__(self, agent_name: str, description: str = "", metadata: Optional[Dict] = None):
        self.agent_id = str(uuid.uuid4())
        self.agent_name = agent_name
        self.description = description
        self.metadata = metadata or {}
        self.session_id = None
        self.reader = None
        self.writer = None
        self.connected = False
        self.message_handlers: Dict[str, Callable] = {}
        self._receive_task = None

    async def connect(self, session_id: str, socket_dir: str = "/tmp/opencli"):
        """Connect to OpenCLI instance"""
        socket_path = os.path.join(socket_dir, f"opencli_{session_id}.sock")

        if not os.path.exists(socket_path):
            raise ConnectionError(f"OpenCLI instance {session_id} not found")

        # Connect to Unix socket
        self.reader, self.writer = await asyncio.open_unix_connection(socket_path)

        # Send registration
        reg_message = IPCMessage(
            msg_type=MessageType.REGISTER.value,
            sender_id=self.agent_id,
            recipient_id=None,
            payload={
                'name': self.agent_name,
                'description': self.description,
                'metadata': self.metadata
            },
            timestamp=datetime.now().timestamp(),
            msg_id=str(uuid.uuid4())
        )

        await self._send_message(reg_message)

        # Wait for acknowledgment
        response = await self._receive_message()
        if response.payload.get('status') == 'registered':
            self.session_id = response.payload.get('session_id')
            self.connected = True

            # Start receive loop
            self._receive_task = asyncio.create_task(self._receive_loop())

            print(f"[IPC Client] Connected to session {session_id}")
        else:
            raise ConnectionError("Registration failed")

    async def disconnect(self):
        """Disconnect from OpenCLI instance"""
        if not self.connected:
            return

        # Send unregister message
        unreg_message = IPCMessage(
            msg_type=MessageType.UNREGISTER.value,
            sender_id=self.agent_id,
            recipient_id=None,
            payload={},
            timestamp=datetime.now().timestamp(),
            msg_id=str(uuid.uuid4())
        )

        await self._send_message(unreg_message)

        # Stop receive task
        if self._receive_task:
            self._receive_task.cancel()

        # Close connection
        self.writer.close()
        await self.writer.wait_closed()

        self.connected = False
        print("[IPC Client] Disconnected")

    async def _send_message(self, message: IPCMessage):
        """Send message to server"""
        data = message.to_json().encode('utf-8')
        length = len(data).to_bytes(4, 'big')

        self.writer.write(length + data)
        await self.writer.drain()

    async def _receive_message(self) -> IPCMessage:
        """Receive a message from server"""
        length_bytes = await self.reader.readexactly(4)
        length = int.from_bytes(length_bytes, 'big')

        data = await self.reader.readexactly(length)
        return IPCMessage.from_json(data.decode('utf-8'))

    async def _receive_loop(self):
        """Continuously receive messages"""
        try:
            while self.connected:
                message = await self._receive_message()

                # Route to handler
                handler = self.message_handlers.get(message.msg_type)
                if handler:
                    await handler(message)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[IPC Client] Receive error: {e}")

    async def send_message(self, msg_type: str, payload: Dict[str, Any]):
        """Send message to OpenCLI main instance"""
        if not self.connected:
            raise RuntimeError("Not connected to OpenCLI instance")

        message = IPCMessage(
            msg_type=msg_type,
            sender_id=self.agent_id,
            recipient_id=self.session_id,
            payload=payload,
            timestamp=datetime.now().timestamp(),
            msg_id=str(uuid.uuid4())
        )

        await self._send_message(message)

    async def send_heartbeat(self):
        """Send heartbeat to maintain connection"""
        await self.send_message(MessageType.HEARTBEAT.value, {})

    def register_handler(self, msg_type: str, handler: Callable):
        """Register a message handler"""
        self.message_handlers[msg_type] = handler


# Convenience function for creating IPC server
def create_ipc_server(session_id: str) -> IPCServer:
    """Create and return an IPC server instance"""
    return IPCServer(session_id)


# Convenience function for creating IPC client
def create_ipc_client(agent_name: str, description: str = "", metadata: Optional[Dict] = None) -> IPCClient:
    """Create and return an IPC client instance"""
    return IPCClient(agent_name, description, metadata)
