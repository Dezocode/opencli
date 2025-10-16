"""
Permission task data structures and management
Task objects, priority queue handling
"""

import asyncio
import threading
import time
import uuid
import weakref
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable, List

from .enums import PromptPriority, PromptState


@dataclass
class _PromptTask:
    """Internal task representation for permission prompts (Constitution compliant)"""
    
    # Core identification
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: PromptPriority = PromptPriority.NORMAL
    
    # Request data
    app: Any = None
    session: Any = None  
    prompt_data: Dict[str, Any] = field(default_factory=dict)
    
    # Execution context
    future: Optional[asyncio.Future] = None
    loop: Optional[asyncio.AbstractEventLoop] = None
    
    # State tracking
    state: PromptState = PromptState.QUEUED
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    # Timeout and cancellation
    timeout: Optional[float] = 30.0
    cancellation_token: Optional[asyncio.Event] = field(default_factory=asyncio.Event)
    auto_dismiss_timer: Optional[threading.Timer] = None
    
    # Caching
    use_cache: bool = True
    cache_key: Optional[str] = None
    
    # Analytics and tracking
    escalated: bool = False
    escalation_count: int = 0
    response_data: Optional[Dict[str, Any]] = None
    error_info: Optional[str] = None
    
    # Weak references for cleanup
    _app_ref: Optional[weakref.ref] = None
    _session_ref: Optional[weakref.ref] = None
    
    def __post_init__(self):
        """Post-initialization setup"""
        # Create weak references to prevent memory leaks
        if self.app:
            self._app_ref = weakref.ref(self.app)
        if self.session:
            self._session_ref = weakref.ref(self.session)
    
    def __lt__(self, other):
        """Comparison for priority queue (lower priority value = higher priority)"""
        if not isinstance(other, _PromptTask):
            return NotImplemented
        
        # Primary sort: priority (URGENT=0 comes first)
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        
        # Secondary sort: creation time (older first)
        return self.created_at < other.created_at
    
    def get_age_seconds(self) -> float:
        """Get task age in seconds"""
        return time.time() - self.created_at
    
    def get_duration_seconds(self) -> Optional[float]:
        """Get task duration if completed"""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None
    
    def is_expired(self) -> bool:
        """Check if task has expired"""
        if not self.timeout:
            return False
        return self.get_age_seconds() > self.timeout
    
    def is_orphaned(self) -> bool:
        """Check if task is orphaned (references are dead)"""
        if self._app_ref and self._app_ref() is None:
            return True
        if self._session_ref and self._session_ref() is None:
            return True
        return False
    
    def escalate_priority(self) -> bool:
        """Escalate task priority (Constitution compliant)"""
        if self.priority == PromptPriority.URGENT:
            return False  # Already at highest priority
        
        # Escalate one level
        if self.priority == PromptPriority.LOW:
            self.priority = PromptPriority.NORMAL
        elif self.priority == PromptPriority.NORMAL:
            self.priority = PromptPriority.HIGH
        elif self.priority == PromptPriority.HIGH:
            self.priority = PromptPriority.URGENT
        
        self.escalated = True
        self.escalation_count += 1
        return True
    
    def cancel(self) -> bool:
        """Cancel the task (Constitution compliant <100ms)"""
        if self.state in [PromptState.RESOLVED, PromptState.CANCELLED]:
            return False
        
        self.state = PromptState.CANCELLED
        self.completed_at = time.time()
        
        # Signal cancellation
        if self.cancellation_token:
            self.cancellation_token.set()
        
        # Cancel auto-dismiss timer
        if self.auto_dismiss_timer:
            self.auto_dismiss_timer.cancel()
            self.auto_dismiss_timer = None
        
        # Cancel future if exists
        if self.future and not self.future.done():
            self.future.cancel()
        
        return True
    
    def resolve(self, response_data: Dict[str, Any]) -> bool:
        """Resolve the task with response data"""
        if self.state in [PromptState.RESOLVED, PromptState.CANCELLED]:
            return False
        
        self.state = PromptState.RESOLVED
        self.completed_at = time.time()
        self.response_data = response_data
        
        # Cancel auto-dismiss timer
        if self.auto_dismiss_timer:
            self.auto_dismiss_timer.cancel()
            self.auto_dismiss_timer = None
        
        # Complete future if exists
        if self.future and not self.future.done():
            self.future.set_result(response_data)
        
        return True
    
    def auto_dismiss(self) -> bool:
        """Auto-dismiss the task (timeout)"""
        if self.state in [PromptState.RESOLVED, PromptState.CANCELLED]:
            return False
        
        self.state = PromptState.AUTO_DISMISSED
        self.completed_at = time.time()
        self.error_info = "Auto-dismissed due to timeout"
        
        # Complete future with timeout
        if self.future and not self.future.done():
            self.future.set_exception(asyncio.TimeoutError("Permission prompt timed out"))
        
        return True
    
    def set_error(self, error_message: str) -> None:
        """Set error information for the task"""
        self.error_info = error_message
        if self.future and not self.future.done():
            self.future.set_exception(Exception(error_message))
    
    def start_auto_dismiss_timer(self) -> None:
        """Start auto-dismiss timer"""
        if not self.timeout or self.auto_dismiss_timer:
            return
        
        self.auto_dismiss_timer = threading.Timer(self.timeout, self.auto_dismiss)
        self.auto_dismiss_timer.start()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization"""
        return {
            'task_id': self.task_id,
            'priority': self.priority.name,
            'state': self.state.value,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'timeout': self.timeout,
            'escalated': self.escalated,
            'escalation_count': self.escalation_count,
            'age_seconds': self.get_age_seconds(),
            'duration_seconds': self.get_duration_seconds(),
            'error_info': self.error_info,
            'prompt_data': self.prompt_data,
            'response_data': self.response_data
        }
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return (f"PromptTask(id={self.task_id[:8]}..., "
                f"priority={self.priority.name}, "
                f"state={self.state.value}, "
                f"age={self.get_age_seconds():.1f}s)")


class TaskQueue:
    """Priority queue for permission tasks"""
    
    def __init__(self, max_size: Optional[int] = None):
        self.max_size = max_size
        self._queue: List[_PromptTask] = []
        self._lock = threading.Lock()
        
    def put(self, task: _PromptTask) -> bool:
        """Add task to queue"""
        with self._lock:
            if self.max_size and len(self._queue) >= self.max_size:
                return False
            
            heapq.heappush(self._queue, task)
            return True
    
    def get(self) -> Optional[_PromptTask]:
        """Get highest priority task"""
        with self._lock:
            if not self._queue:
                return None
            return heapq.heappop(self._queue)
    
    def peek(self) -> Optional[_PromptTask]:
        """Peek at highest priority task without removing"""
        with self._lock:
            if not self._queue:
                return None
            return self._queue[0]
    
    def remove(self, task_id: str) -> bool:
        """Remove specific task by ID"""
        with self._lock:
            for i, task in enumerate(self._queue):
                if task.task_id == task_id:
                    self._queue.pop(i)
                    heapq.heapify(self._queue)  # Restore heap property
                    return True
            return False
    
    def clear(self) -> List[_PromptTask]:
        """Clear all tasks and return them"""
        with self._lock:
            tasks = self._queue.copy()
            self._queue.clear()
            return tasks
    
    def size(self) -> int:
        """Get queue size"""
        with self._lock:
            return len(self._queue)
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        with self._lock:
            return len(self._queue) == 0
    
    def get_all_tasks(self) -> List[_PromptTask]:
        """Get all tasks (for debugging/monitoring)"""
        with self._lock:
            return self._queue.copy()
    
    def cleanup_expired(self) -> List[_PromptTask]:
        """Remove and return expired tasks"""
        with self._lock:
            expired = []
            remaining = []
            
            for task in self._queue:
                if task.is_expired() or task.is_orphaned():
                    expired.append(task)
                else:
                    remaining.append(task)
            
            self._queue = remaining
            heapq.heapify(self._queue)  # Restore heap property
            return expired