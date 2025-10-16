"""Permission buffer task management"""

from __future__ import annotations
import uuid
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable
from .enums import PromptPriority, PromptState


@dataclass
class _PromptTask:
    """Internal representation of a permission request in the buffer."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: PromptPriority = PromptPriority.NORMAL
    prompt_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    state: PromptState = PromptState.QUEUED
    
    # Callback for when the prompt is resolved
    callback: Optional[Callable[[Dict], None]] = None
    future: Optional[Any] = None  # asyncio.Future
    
    # Auto-dismiss settings
    auto_dismiss_after: Optional[float] = None
    
    def __lt__(self, other):
        """For priority queue ordering (lower number = higher priority)"""
        if not isinstance(other, _PromptTask):
            return NotImplemented
        return (self.priority.value, self.timestamp) < (other.priority.value, other.timestamp)
    
    def should_auto_dismiss(self) -> bool:
        """Check if this task should be auto-dismissed"""
        if self.auto_dismiss_after is None:
            return False
        return time.time() - self.timestamp > self.auto_dismiss_after
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization"""
        return {
            'id': self.id,
            'priority': self.priority.value,
            'prompt_data': self.prompt_data,
            'timestamp': self.timestamp,
            'state': self.state.value,
            'auto_dismiss_after': self.auto_dismiss_after
        }