"""Central manager for the permission buffer"""

from __future__ import annotations
import asyncio
import threading
import heapq
import time
from typing import Any, Dict, Optional, Callable, List
from .enums import PromptPriority, PromptState
from .task import _PromptTask


class PermissionBufferManager:
    """Manages permission prompts with priority-based queuing and UI integration"""
    
    def __init__(self):
        self._prompt_queue = []
        self._lock = threading.Lock()
        self._current_task: Optional[_PromptTask] = None
        self._is_active = False
        self._auto_dismiss_enabled = True
        
        # UI integration
        self._app = None
        self._prompt_input = None
        
        # Performance tracking
        self._stats = {
            'total_prompts': 0,
            'auto_dismissed': 0,
            'user_resolved': 0,
            'cancelled': 0
        }
    
    def set_app_context(self, app, prompt_input=None):
        """Set the TUI application context for UI integration"""
        self._app = app
        self._prompt_input = prompt_input
    
    async def request_permission(
        self, 
        prompt_data: Dict[str, Any],
        priority: PromptPriority = PromptPriority.NORMAL,
        auto_dismiss_after: Optional[float] = None,
        callback: Optional[Callable[[Dict], None]] = None
    ) -> Dict[str, Any]:
        """Request permission with priority-based queuing"""
        
        task = _PromptTask(
            priority=priority,
            prompt_data=prompt_data,
            auto_dismiss_after=auto_dismiss_after,
            callback=callback,
            future=asyncio.Future()
        )
        
        with self._lock:
            heapq.heappush(self._prompt_queue, task)
            self._stats['total_prompts'] += 1
        
        # Start processing if not already active
        if not self._is_active:
            asyncio.create_task(self._process_queue())
        
        # Wait for resolution
        return await task.future
    
    async def _process_queue(self):
        """Process the permission prompt queue"""
        if self._is_active:
            return
        
        self._is_active = True
        
        try:
            while True:
                # Get next task
                with self._lock:
                    if not self._prompt_queue:
                        break
                    task = heapq.heappop(self._prompt_queue)
                
                # Check for auto-dismiss
                if task.should_auto_dismiss():
                    self._auto_dismiss_task(task)
                    continue
                
                # Process the task
                await self._process_task(task)
                
        finally:
            self._is_active = False
    
    async def _process_task(self, task: _PromptTask):
        """Process a single permission task"""
        self._current_task = task
        task.state = PromptState.DISPLAYING
        
        try:
            # Show in UI if available
            if self._app and self._prompt_input:
                await self._show_in_ui(task)
            else:
                # Fallback: auto-approve for non-UI contexts
                result = {'response': 'auto_approved', 'reason': 'no_ui_context'}
                self._resolve_task(task, result)
                
        except Exception as e:
            # Handle errors gracefully
            error_result = {'response': 'error', 'error': str(e)}
            self._resolve_task(task, error_result)
    
    async def _show_in_ui(self, task: _PromptTask):
        """Display the permission prompt in the UI"""
        try:
            if hasattr(self._prompt_input, 'permission_prompt_data'):
                self._prompt_input.permission_prompt_data = task.prompt_data
                task.state = PromptState.AWAITING_INPUT
            else:
                # Fallback if UI doesn't support permission prompts
                result = {'response': 'auto_approved', 'reason': 'ui_not_supported'}
                self._resolve_task(task, result)
                
        except Exception as e:
            error_result = {'response': 'error', 'error': str(e)}
            self._resolve_task(task, error_result)
    
    def _resolve_task(self, task: _PromptTask, result: Dict[str, Any]):
        """Resolve a permission task with the given result"""
        task.state = PromptState.RESOLVED
        
        # Update stats
        if result.get('response') == 'auto_dismissed':
            self._stats['auto_dismissed'] += 1
        elif result.get('response') == 'cancelled':
            self._stats['cancelled'] += 1
        else:
            self._stats['user_resolved'] += 1
        
        # Call callback if provided
        if task.callback:
            try:
                task.callback(result)
            except Exception:
                pass  # Ignore callback errors
        
        # Resolve the future
        if task.future and not task.future.done():
            task.future.set_result(result)
        
        # Clear UI if this was the current task
        if self._current_task == task:
            self._clear_ui()
            self._current_task = None
    
    def _auto_dismiss_task(self, task: _PromptTask):
        """Auto-dismiss a task that has expired"""
        task.state = PromptState.AUTO_DISMISSED
        result = {'response': 'auto_dismissed', 'reason': 'timeout'}
        self._resolve_task(task, result)
    
    def _clear_ui(self):
        """Clear the permission prompt from the UI"""
        try:
            if self._prompt_input and hasattr(self._prompt_input, 'permission_prompt_data'):
                self._prompt_input.permission_prompt_data = None
        except Exception:
            pass  # Ignore UI errors
    
    def handle_user_response(self, response: Dict[str, Any]):
        """Handle user response to the current permission prompt"""
        if self._current_task and self._current_task.state == PromptState.AWAITING_INPUT:
            self._resolve_task(self._current_task, response)
    
    def cancel_current_prompt(self):
        """Cancel the currently displayed prompt"""
        if self._current_task:
            result = {'response': 'cancelled', 'reason': 'user_cancelled'}
            self._resolve_task(self._current_task, result)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self._stats.copy()
    
    def clear_queue(self):
        """Clear all pending prompts"""
        with self._lock:
            while self._prompt_queue:
                task = heapq.heappop(self._prompt_queue)
                if task.future and not task.future.done():
                    result = {'response': 'cancelled', 'reason': 'queue_cleared'}
                    task.future.set_result(result)


# Global instance
_global_buffer_manager = None

def get_permission_buffer_manager() -> PermissionBufferManager:
    """Get the global permission buffer manager instance"""
    global _global_buffer_manager
    if _global_buffer_manager is None:
        _global_buffer_manager = PermissionBufferManager()
    return _global_buffer_manager