"""
Core permission buffer manager
Main orchestrator that coordinates all permission system components
"""

import asyncio
import threading
import time
import heapq
from typing import Dict, List, Optional, Any

from .enums import PromptPriority, PromptState
from .task import _PromptTask, TaskQueue
from .i18n import I18nManager
from .validation import ValidationManager
from .analytics import AnalyticsManager
from .audit import AuditManager
from .cache import CacheManager


class PermissionBufferManager:
    """Central manager for the permission buffer (Constitution compliant)"""
    
    def __init__(self) -> None:
        # Priority queue implementation (Constitution compliant)
        self._priority_queue: List[_PromptTask] = []
        self._queue_condition = threading.Condition()  # For blocking get operations
        self._current: Optional[_PromptTask] = None
        self._lock = threading.Lock()
        self._running = True
        self._worker = threading.Thread(target=self._run, name="permission-buffer", daemon=True)
        self._worker.start()
        
        # Track active tasks for cancellation
        self._active_tasks: Dict[str, _PromptTask] = {}
        
        # Enhanced concurrent handling (Constitution Principle V)
        self._concurrent_mode = True  # Allow multiple prompts in queue
        self._max_concurrent_prompts = 5  # Limit to prevent memory issues
        self._prompt_history: List[_PromptTask] = []  # Track completed prompts
        self._max_history = 10  # Keep last 10 prompts for debugging
        
        # Initialize subsystem managers
        self._i18n = I18nManager()
        self._validator = ValidationManager()
        self._analytics = AnalyticsManager()
        self._audit = AuditManager()
        self._cache = CacheManager()
        
        # Start periodic cleanup task for orphaned prompts (Constitution compliant)
        try:
            # Only start cleanup if event loop is available
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._periodic_cleanup())
        except RuntimeError:
            # No event loop - cleanup will be manual only
            pass

    # Internationalization delegation methods
    def set_locale(self, locale: str) -> bool:
        """Set current locale for internationalization"""
        return self._i18n.set_locale(locale)

    def get_translation(self, key: str, fallback: str = None) -> str:
        """Get translated text for current locale"""
        return self._i18n.get_translation(key, fallback)

    def add_custom_translation(self, locale: str, key: str, value: str) -> None:
        """Add custom translation"""
        self._i18n.add_custom_translation(locale, key, value)

    def get_supported_locales(self) -> List[str]:
        """Get list of supported locales"""
        return self._i18n.get_supported_locales()

    # Validation delegation methods
    def validate_prompt_data(self, prompt_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate permission prompt data"""
        return self._validator.validate_prompt_data(prompt_data)

    def validate_prompt_response(self, response: Dict[str, Any], original_options: List[Dict[str, Any]] = None) -> tuple[bool, Optional[str]]:
        """Validate permission prompt response"""
        return self._validator.validate_prompt_response(response, original_options)

    # Analytics delegation methods
    def get_analytics_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        return self._analytics.get_analytics_report()

    def export_analytics(self, format: str = 'json') -> str:
        """Export analytics data in specified format"""
        return self._analytics.export_analytics(format)

    def reset_analytics(self) -> None:
        """Reset all analytics data"""
        self._analytics.reset_analytics()

    # Audit delegation methods
    def get_audit_log(self, event_type: Optional[str] = None, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit log entries with optional filtering"""
        return self._audit.get_audit_log(event_type, task_id)

    def export_audit_log(self, format: str = 'json') -> str:
        """Export audit log for security analysis"""
        return self._audit.export_audit_log(format)

    # Cache delegation methods
    def clear_prompt_cache(self) -> int:
        """Clear all cached permission responses"""
        return self._cache.clear_cache()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self._cache.get_cache_stats()

    # Priority queue methods
    def _put_priority_task(self, task: _PromptTask) -> None:
        """Add task to priority queue (Constitution compliant - thread-safe)"""
        with self._queue_condition:
            heapq.heappush(self._priority_queue, task)
            self._queue_condition.notify()  # Wake up worker thread

    def _get_priority_task(self) -> Optional[_PromptTask]:
        """Get highest priority task from queue (Constitution compliant - blocking)"""
        with self._queue_condition:
            while self._running and not self._priority_queue:
                self._queue_condition.wait()  # Block until task available
            
            if not self._running:
                return None
                
            return heapq.heappop(self._priority_queue)

    def _get_queue_size(self) -> int:
        """Get current queue size (thread-safe)"""
        with self._queue_condition:
            return len(self._priority_queue)

    def _escalate_timeout(self, task: _PromptTask) -> bool:
        """Escalate timeout by increasing priority (Constitution compliant)"""
        task.timeout_count += 1
        
        if task.timeout_count > task.max_escalations:
            import sys
            sys.stderr.write(f"[PermissionManager] Max escalations reached for task {task.task_id} ({task.timeout_count})\n")
            sys.stderr.flush()
            return False
        
        # Escalate priority
        if task.priority == PromptPriority.LOW:
            task.priority = PromptPriority.NORMAL
        elif task.priority == PromptPriority.NORMAL:
            task.priority = PromptPriority.HIGH
        elif task.priority == PromptPriority.HIGH:
            task.priority = PromptPriority.URGENT
        
        self._analytics.update_analytics('prompt_escalated', task, {'new_priority': task.priority.name})
        self._audit.log_event('ESCALATED', task.task_id, {'priority': task.priority.name, 'timeout_count': task.timeout_count})
        
        return True

    async def _periodic_cleanup(self) -> None:
        """Periodic cleanup of orphaned prompts (Constitution compliant)"""
        while self._running:
            try:
                await asyncio.sleep(30)  # Run every 30 seconds
                cleaned_count = self.cleanup_orphaned_prompts()
                if cleaned_count > 0:
                    self._analytics.update_analytics('memory_cleanup', details={'cleaned_count': cleaned_count})
            except asyncio.CancelledError:
                break
            except Exception as e:
                import sys
                sys.stderr.write(f"[PermissionManager] Cleanup error: {e}\n")
                sys.stderr.flush()

    def update(self, prompt_data: Dict[str, Any]) -> None:
        """Update current prompt display (Constitution compliant)"""
        if not self._current:
            return
        
        is_valid, error = self.validate_prompt_data(prompt_data)
        if not is_valid:
            import sys
            sys.stderr.write(f"[PermissionManager] Invalid prompt data update: {error}\n")
            sys.stderr.flush()
            return
        
        with self._lock:
            if self._current:
                self._current.prompt_data.update(prompt_data)
                self._audit.log_event('UPDATED', self._current.task_id, {'changes': list(prompt_data.keys())})

    def resolve(self, option: Dict[str, Any]) -> bool:
        """Resolve current prompt with selected option (Constitution compliant)"""
        with self._lock:
            if not self._current:
                return False
            
            task = self._current
            task.state = PromptState.RESOLVED
            
            # Store resolution data
            task.resolved_option = option
            task.resolved_at = time.time()
            
            # Complete the task
            try:
                # Check for both 'future' and 'completion_future' attribute names
                if hasattr(task, 'future') and task.future:
                    task.future.set_result(option)
                elif hasattr(task, 'completion_future') and task.completion_future:
                    task.completion_future.set_result(option)
            except Exception as e:
                import sys
                sys.stderr.write(f"[PermissionManager] Error setting future result: {e}\n")
                sys.stderr.flush()
            
            # Clean up
            if task.task_id in self._active_tasks:
                del self._active_tasks[task.task_id]
            
            # Add to history
            self._prompt_history.append(task)
            if len(self._prompt_history) > self._max_history:
                self._prompt_history.pop(0)
            
            # Update analytics and audit
            self._analytics.update_analytics('prompt_resolved', task, {'option': option})
            self._audit.log_event('RESOLVED', task.task_id, {'option': option, 'duration': task.resolved_at - task.created_at})
            
            self._current = None
            return True

    def clear(self, task: Optional[_PromptTask] = None) -> bool:
        """Clear prompt display (Constitution compliant)"""
        with self._lock:
            if task:
                # Clear specific task
                task.state = PromptState.CANCELLED
                if task.task_id in self._active_tasks:
                    del self._active_tasks[task.task_id]
                self._analytics.update_analytics('prompt_cleared', task)
                self._audit.log_event('CLEARED', task.task_id, {'reason': 'specific_clear'})
                
                if self._current and self._current.task_id == task.task_id:
                    self._current = None
                return True
            else:
                # Clear current task
                if self._current:
                    task = self._current
                    task.state = PromptState.CANCELLED
                    
                    if task.task_id in self._active_tasks:
                        del self._active_tasks[task.task_id]
                    
                    self._analytics.update_analytics('prompt_cleared', task)
                    self._audit.log_event('CLEARED', task.task_id, {'reason': 'current_clear'})
                    
                    self._current = None
                    return True
                return False

    def cancel(self, task_id: str) -> bool:
        """Cancel specific task by ID (Constitution compliant)"""
        if not self._validator.validate_task_id(task_id):
            return False
        
        with self._lock:
            if task_id in self._active_tasks:
                task = self._active_tasks[task_id]
                task.cancel()
                del self._active_tasks[task_id]
                self._analytics.update_analytics('prompt_cancelled', task)
                self._audit.log_event('CANCELLED', task_id, {'reason': 'user_request'})
                return True
        
        return False

    def get_active_task_count(self) -> int:
        """Get number of active tasks (Constitution compliant)"""
        with self._lock:
            return len(self._active_tasks)

    def get_concurrent_prompt_status(self) -> Dict[str, Any]:
        """Get status of concurrent prompt handling (Constitution compliant)"""
        with self._lock:
            return {
                'concurrent_mode': self._concurrent_mode,
                'max_concurrent': self._max_concurrent_prompts,
                'active_tasks': len(self._active_tasks),
                'queue_size': self._get_queue_size(),
                'current_task_id': self._current.task_id if self._current else None
            }

    def cancel_all_active_tasks(self) -> int:
        """Cancel all active tasks (Constitution compliant)"""
        cancelled_count = 0
        
        with self._lock:
            for task in list(self._active_tasks.values()):
                if task.cancel():
                    cancelled_count += 1
                    self._analytics.update_analytics('prompt_cancelled', task)
                    self._audit.log_event('CANCELLED', task.task_id, {'reason': 'batch_cancel'})
            
            self._active_tasks.clear()
        
        return cancelled_count

    def cancel_batch_by_prefix(self, task_id_prefix: str) -> int:
        """Cancel all tasks whose IDs start with given prefix (Constitution compliant)"""
        cancelled_count = 0
        
        with self._lock:
            tasks_to_cancel = [
                task for task_id, task in self._active_tasks.items()
                if task_id.startswith(task_id_prefix)
            ]
            
            for task in tasks_to_cancel:
                if task.cancel():
                    cancelled_count += 1
                    del self._active_tasks[task.task_id]
                    self._analytics.update_analytics('prompt_cancelled', task)
                    self._audit.log_event('CANCELLED', task.task_id, {'reason': 'prefix_batch_cancel'})
        
        return cancelled_count

    def shutdown(self) -> None:
        """Shutdown permission buffer manager (Constitution compliant)"""
        self._running = False
        
        # Cancel all active tasks
        self.cancel_all_active_tasks()
        
        # Wake up worker thread
        with self._queue_condition:
            self._queue_condition.notify_all()
        
        # Wait for worker to finish
        if self._worker.is_alive():
            self._worker.join(timeout=5.0)

    def cleanup_orphaned_prompts(self, max_age_seconds: float = 30.0) -> int:
        """Clean up orphaned prompts (Constitution compliant)"""
        current_time = time.time()
        cleaned_count = 0
        
        with self._lock:
            orphaned_tasks = []
            
            for task_id, task in list(self._active_tasks.items()):
                # Check if task is too old
                if current_time - task.created_at > max_age_seconds:
                    orphaned_tasks.append(task)
                # Check if task references are dead
                elif hasattr(task, 'is_orphaned') and task.is_orphaned():
                    orphaned_tasks.append(task)
            
            for task in orphaned_tasks:
                task.cancel()
                if task.task_id in self._active_tasks:
                    del self._active_tasks[task.task_id]
                cleaned_count += 1
                self._audit.log_event('ORPHAN_CLEANUP', task.task_id, {'age_seconds': current_time - task.created_at})
        
        return cleaned_count

    def _run(self) -> None:
        """Main worker thread loop (Constitution compliant)"""
        while self._running:
            try:
                task = self._get_priority_task()
                if not task:
                    continue
                
                with self._lock:
                    self._current = task
                    self._active_tasks[task.task_id] = task
                
                # Update analytics
                self._analytics.update_analytics('prompt_created', task)
                self._audit.log_event('CREATED', task.task_id, {'priority': task.priority.name})
                
                # Handle the task (placeholder)
                task.state = PromptState.DISPLAYING
                # ... task processing logic would go here ...
                
            except Exception as e:
                import sys
                sys.stderr.write(f"[PermissionManager] Worker error: {e}\n")
                sys.stderr.flush()

    def _resolve_current(self, selected_option: Dict[str, Any], task: Optional[_PromptTask] = None) -> bool:
        """Resolve current prompt (internal method)"""
        # Placeholder implementation
        return True

    async def request_permission(
        self,
        app,
        session,
        prompt_data: Dict[str, Any],
        timeout: float = None
    ) -> Dict[str, Any]:
        """
        Request permission and show prompt in TUI

        This is the main entry point called by execution/permission_manager.py

        Args:
            app: TUI application instance
            session: Session object
            prompt_data: Prompt data dict with title, message, options
            timeout: Timeout in seconds (default None = no timeout for interactive prompts)

        Returns:
            Dict with user's response and any selected data
        """
        import sys
        sys.stderr.write(f"\n[PermissionBufferManager.request_permission] ENTERED - title={prompt_data.get('title')}\n")
        sys.stderr.flush()

        import asyncio
        from .task import _PromptTask

        sys.stderr.write(f"[PermissionBufferManager.request_permission] Imports done\n")
        sys.stderr.flush()

        # Create task for this permission request
        task = _PromptTask(
            prompt_data=prompt_data,
            priority=PromptPriority.NORMAL
        )
        task.future = asyncio.Future()

        # Add to queue
        self._put_priority_task(task)

        # Update analytics
        self._analytics.update_analytics('prompt_created', task)
        self._audit.log_event('CREATED', task.task_id, {
            'title': prompt_data.get('title', 'Unknown'),
            'timeout': timeout
        })

        # Show in TUI if available
        if app and hasattr(app, 'query_one'):
            try:
                import sys
                sys.stderr.write(f"[PermissionBufferManager] Attempting to show prompt in TUI\n")
                sys.stderr.flush()

                # Get prompt input widget
                from ..input_widget import MultiLineInput
                prompt_input = app.query_one("#prompt-input", MultiLineInput)
                sys.stderr.write(f"[PermissionBufferManager] Got prompt_input widget: {prompt_input}\n")
                sys.stderr.flush()

                # Set permission prompt data on widget
                sys.stderr.write(f"[PermissionBufferManager] Setting permission_prompt_data with title: {prompt_data.get('title')}\n")
                sys.stderr.flush()
                prompt_input.permission_prompt_data = prompt_data
                sys.stderr.write(f"[PermissionBufferManager] permission_prompt_data set successfully\n")
                sys.stderr.flush()

                prompt_input.refresh()
                sys.stderr.write(f"[PermissionBufferManager] Widget refreshed\n")
                sys.stderr.flush()

                # Focus the input so keys work
                try:
                    app.set_focus(prompt_input)
                    sys.stderr.write(f"[PermissionBufferManager] Focus set via app.set_focus()\n")
                    sys.stderr.flush()
                except Exception as focus_err:
                    sys.stderr.write(f"[PermissionBufferManager] app.set_focus() failed: {focus_err}, trying fallback\n")
                    sys.stderr.flush()
                    prompt_input.focus()
                    sys.stderr.write(f"[PermissionBufferManager] Focus set via widget.focus()\n")
                    sys.stderr.flush()

            except Exception as e:
                import sys
                import traceback
                sys.stderr.write(f"[PermissionBufferManager] Error showing prompt in TUI: {e}\n")
                traceback.print_exc(file=sys.stderr)
                sys.stderr.flush()

        # CRITICAL: Yield control to event loop so TUI can render the prompt
        # Without this, we block the event loop before the widget can display
        await asyncio.sleep(0)
        sys.stderr.write(f"[PermissionBufferManager] Yielded to event loop for UI render\n")
        sys.stderr.flush()

        # Wait for resolution (with optional timeout)
        try:
            if timeout is None:
                # NO TIMEOUT - Wait indefinitely for user response (interactive prompts)
                sys.stderr.write(f"[PermissionBufferManager] Waiting for user response (NO TIMEOUT - will wait indefinitely)\n")
                sys.stderr.flush()
                result = await task.future
            else:
                # WITH TIMEOUT - Auto-dismiss after timeout (informational prompts only)
                sys.stderr.write(f"[PermissionBufferManager] Waiting for user response (timeout={timeout}s)\n")
                sys.stderr.flush()
                result = await asyncio.wait_for(task.future, timeout=timeout)

            self._analytics.update_analytics('prompt_resolved', task, {'result': result})
            self._audit.log_event('RESOLVED', task.task_id, {'result': result})
            return result
        except asyncio.TimeoutError:
            # Auto-dismiss on timeout (only happens if timeout was specified)
            self._analytics.update_analytics('prompt_timeout', task)
            self._audit.log_event('TIMEOUT', task.task_id, {'timeout': timeout})
            return {'response': 'timeout', 'reason': 'timeout_expired'}


def get_permission_buffer_manager():
    """
    Legacy compatibility wrapper - routes to unified permission manager

    DO NOT use this for new code - use get_unified_permission_manager() instead.
    This function exists only for backward compatibility with old code.
    """
    from . import get_unified_permission_manager
    unified_manager = get_unified_permission_manager()
    return unified_manager.get_buffer_manager()