"""
Shell Injection System for IPC Communication
Bidirectional message injection between OpenCLI and subagent shells
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class InjectionType(Enum):
    """Types of shell injections"""
    USER_PROMPT = "user_prompt"           # Inject into user prompt area
    ASSISTANT_RESPONSE = "assistant_response"  # Inject into assistant response
    SYSTEM_MESSAGE = "system_message"     # System-level message
    TOOL_RESULT = "tool_result"           # Tool execution result
    NAVIGATION = "navigation"             # Agent navigation update
    GOAL_PROGRESS = "goal_progress"       # Goal progress update


@dataclass
class InjectionMessage:
    """Represents a message to be injected"""
    injection_type: str                   # InjectionType value
    source_agent: str                     # Agent ID or "opencli"
    target_agent: str                     # Agent ID or "opencli"
    content: str                          # Message content
    metadata: Dict[str, Any]              # Additional metadata
    timestamp: float                      # Unix timestamp
    message_id: str                       # Unique message ID

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(data: Dict) -> 'InjectionMessage':
        """Create from dictionary"""
        return InjectionMessage(**data)

    @staticmethod
    def from_json(data: str) -> 'InjectionMessage':
        """Create from JSON"""
        return InjectionMessage.from_dict(json.loads(data))


class CommunicationLog:
    """
    Maintains a log of shell-to-shell communications
    Tracks findings, injections, and agent progress
    """

    def __init__(self, log_dir: str = None):
        self.log_dir = Path(log_dir or Path.home() / ".opencli" / "ipc_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Current session log
        self.session_log: List[InjectionMessage] = []

        # Log file path (timestamped)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"ipc_session_{timestamp}.jsonl"

    def log_injection(self, message: InjectionMessage):
        """Log an injection message"""
        # Add to in-memory log
        self.session_log.append(message)

        # Append to log file (JSON Lines format)
        try:
            with open(self.log_file, 'a') as f:
                f.write(message.to_json() + '\n')
        except Exception as e:
            print(f"[ShellInjector] Failed to write log: {e}")

    def get_recent_injections(self, limit: int = 50) -> List[InjectionMessage]:
        """Get recent injections"""
        return self.session_log[-limit:]

    def get_injections_by_agent(self, agent_id: str) -> List[InjectionMessage]:
        """Get all injections involving a specific agent"""
        return [
            msg for msg in self.session_log
            if msg.source_agent == agent_id or msg.target_agent == agent_id
        ]

    def get_injections_by_type(self, injection_type: str) -> List[InjectionMessage]:
        """Get all injections of a specific type"""
        return [
            msg for msg in self.session_log
            if msg.injection_type == injection_type
        ]

    def get_navigation_history(self, agent_id: str) -> List[InjectionMessage]:
        """Get navigation history for an agent"""
        return [
            msg for msg in self.session_log
            if msg.injection_type == InjectionType.NAVIGATION.value
            and (msg.source_agent == agent_id or msg.target_agent == agent_id)
        ]

    def get_goal_progress(self, agent_id: str) -> List[InjectionMessage]:
        """Get goal progress updates for an agent"""
        return [
            msg for msg in self.session_log
            if msg.injection_type == InjectionType.GOAL_PROGRESS.value
            and (msg.source_agent == agent_id or msg.target_agent == agent_id)
        ]

    def export_session_log(self, output_file: str = None) -> str:
        """Export session log to JSON file"""
        output_path = output_file or self.log_dir / "session_export.json"

        log_data = {
            "session_start": self.session_log[0].timestamp if self.session_log else None,
            "session_end": datetime.now().timestamp(),
            "total_messages": len(self.session_log),
            "messages": [msg.to_dict() for msg in self.session_log]
        }

        with open(output_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        return str(output_path)


class ShellInjector:
    """
    Bidirectional shell injection system
    Injects messages into OpenCLI and subagent prompt areas
    """

    def __init__(self, ipc_server=None):
        self.ipc_server = ipc_server
        self.comm_log = CommunicationLog()
        self.injection_queue: asyncio.Queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the injection processor"""
        self.processing_task = asyncio.create_task(self._process_injections())

    async def stop(self):
        """Stop the injection processor"""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass

    async def inject_to_opencli(
        self,
        injection_type: InjectionType,
        source_agent: str,
        content: str,
        metadata: Dict[str, Any] = None
    ):
        """
        Inject message into OpenCLI prompt area

        Args:
            injection_type: Type of injection
            source_agent: ID of source agent
            content: Message content
            metadata: Additional metadata
        """
        import uuid

        message = InjectionMessage(
            injection_type=injection_type.value,
            source_agent=source_agent,
            target_agent="opencli",
            content=content,
            metadata=metadata or {},
            timestamp=datetime.now().timestamp(),
            message_id=str(uuid.uuid4())
        )

        # Log the injection
        self.comm_log.log_injection(message)

        # Queue for processing
        await self.injection_queue.put(message)

    async def inject_to_agent(
        self,
        agent_id: str,
        injection_type: InjectionType,
        content: str,
        metadata: Dict[str, Any] = None
    ):
        """
        Inject message into subagent shell

        Args:
            agent_id: Target agent ID
            injection_type: Type of injection
            content: Message content
            metadata: Additional metadata
        """
        import uuid

        message = InjectionMessage(
            injection_type=injection_type.value,
            source_agent="opencli",
            target_agent=agent_id,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.now().timestamp(),
            message_id=str(uuid.uuid4())
        )

        # Log the injection
        self.comm_log.log_injection(message)

        # Send via IPC if server available
        if self.ipc_server:
            try:
                await self.ipc_server.send_to_agent(
                    agent_id,
                    "injection",
                    {
                        "type": injection_type.value,
                        "content": content,
                        "metadata": metadata or {}
                    }
                )
            except Exception as e:
                print(f"[ShellInjector] Failed to inject to agent {agent_id}: {e}")

    async def _process_injections(self):
        """Process injection queue"""
        while True:
            try:
                message = await self.injection_queue.get()

                # Process based on injection type
                if message.injection_type == InjectionType.USER_PROMPT.value:
                    # Inject into user prompt area
                    print(f"\n[Injected from {message.source_agent}]: {message.content}\n")

                elif message.injection_type == InjectionType.NAVIGATION.value:
                    # Show navigation update
                    nav_info = message.metadata.get('navigation', {})
                    current = nav_info.get('current', 'Unknown')
                    print(f"\n[Navigation - {message.source_agent}]: Now at {current}\n")

                elif message.injection_type == InjectionType.GOAL_PROGRESS.value:
                    # Show goal progress
                    progress = message.metadata.get('progress', 0)
                    goal = message.metadata.get('goal', 'Unknown')
                    print(f"\n[Progress - {message.source_agent}]: {goal} - {progress}% complete\n")

                # Mark as processed
                self.injection_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[ShellInjector] Error processing injection: {e}")

    def get_communication_log(self) -> CommunicationLog:
        """Get the communication log"""
        return self.comm_log

    def get_log_summary(self) -> Dict[str, Any]:
        """Get summary of communication log"""
        total = len(self.comm_log.session_log)

        type_counts = {}
        for msg in self.comm_log.session_log:
            type_counts[msg.injection_type] = type_counts.get(msg.injection_type, 0) + 1

        agent_counts = {}
        for msg in self.comm_log.session_log:
            agent_counts[msg.source_agent] = agent_counts.get(msg.source_agent, 0) + 1

        return {
            "total_messages": total,
            "by_type": type_counts,
            "by_agent": agent_counts,
            "log_file": str(self.comm_log.log_file)
        }


# Singleton instance
_injector_instance: Optional[ShellInjector] = None

def get_shell_injector(ipc_server=None) -> ShellInjector:
    """Get singleton shell injector instance"""
    global _injector_instance

    if _injector_instance is None:
        _injector_instance = ShellInjector(ipc_server)

    return _injector_instance
