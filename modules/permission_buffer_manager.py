"""Central manager for the permission buffer.

The Textual-based UI expects changes to the input widget to happen on the
application thread. Historically, permission prompts manipulated
``permission_prompt_data`` directly from arbitrary coroutines which could
block the event loop while waiting for user input. This manager moves all
buffer mutations onto a dedicated worker thread that marshals UI updates
through ``app.call_from_thread`` and resolves asyncio futures without busy
polling.

Usage pattern::

    manager = get_permission_buffer_manager()
    result = await manager.prompt(app, session, prompt_data)
    # ``result`` is the option dict selected by the user (or ``None`` on
    # cancel/timeout)

The manager also exposes ``update`` and ``clear`` helpers so long-running
workflows can safely refresh the buffer contents without blocking the main
event loop.
"""

from __future__ import annotations

import asyncio
import threading
from dataclasses import dataclass, field
from queue import Queue
from typing import Any, Dict, Optional


@dataclass
class _PromptTask:
    """Internal representation of a queued prompt request."""

    app: Any
    session: Any
    prompt_data: Dict[str, Any]
    future: Optional[asyncio.Future]
    loop: Optional[asyncio.AbstractEventLoop]
    wait_for_response: bool = True
    done_event: threading.Event = field(default_factory=threading.Event)
    resolved: bool = False


class PermissionBufferManager:
    """Threaded controller responsible for showing and clearing prompts."""

    def __init__(self) -> None:
        self._queue: "Queue[_PromptTask]" = Queue()
        self._current: Optional[_PromptTask] = None
        self._lock = threading.Lock()
        self._running = True
        self._worker = threading.Thread(target=self._run, name="permission-buffer", daemon=True)
        self._worker.start()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def prompt(
        self,
        app: Any,
        session: Any,
        prompt_data: Dict[str, Any],
        *,
        timeout: Optional[float] = 30.0,
    ) -> Optional[Dict[str, Any]]:
        """Show a permission prompt and wait for the user's selection."""

        loop = asyncio.get_running_loop()
        future: asyncio.Future = loop.create_future()

        task = _PromptTask(
            app=app,
            session=session,
            prompt_data=prompt_data,
            future=future,
            loop=loop,
            wait_for_response=True,
        )

        self._queue.put(task)

        try:
            if timeout is None:
                return await future
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            # Force timeout resolution so worker can move on.
            self._resolve_current({'response': 'timeout'}, force=True)
            raise

    async def show_transient(
        self,
        app: Any,
        session: Any,
        prompt_data: Dict[str, Any],
        *,
        duration: float = 4.0,
    ) -> None:
        """Display a non-blocking prompt for a limited duration."""

        task = _PromptTask(
            app=app,
            session=session,
            prompt_data=prompt_data,
            future=None,
            loop=None,
            wait_for_response=False,
        )
        self._queue.put(task)

        # Schedule automatic dismissal without blocking caller.
        async def auto_clear():
            await asyncio.sleep(duration)
            self.clear()

        asyncio.create_task(auto_clear())

    def update(self, prompt_data: Dict[str, Any]) -> None:
        """Update the currently displayed prompt (if any)."""

        with self._lock:
            task = self._current
            if not task:
                return

            def _update() -> None:
                try:
                    prompt_input = task.app.query_one("#prompt-input")
                    prompt_input.permission_prompt_data = prompt_data
                    prompt_input.permission_selected_option = prompt_data.get('selected', 0)
                    prompt_input.refresh()
                except Exception:
                    pass

            task.app.call_from_thread(_update)

    def resolve(self, option: Dict[str, Any]) -> bool:
        """Resolve the active prompt with the provided option dict.

        Returns ``True`` if an active prompt was resolved, ``False`` if no
        prompt was waiting for a response.
        """

        return self._resolve_current(option, force=False)

    def clear(self) -> bool:
        """Clear the active prompt without resolving the future."""

        return self._resolve_current({'response': 'cancel'}, force=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _run(self) -> None:
        while self._running:
            task = self._queue.get()
            if task is None:
                break  # graceful shutdown

            with self._lock:
                self._current = task

            def _show() -> None:
                try:
                    prompt_input = task.app.query_one("#prompt-input")
                    prompt_input.permission_prompt_data = task.prompt_data
                    prompt_input.permission_selected_option = task.prompt_data.get('selected', 0)
                    prompt_input.refresh(layout=True)
                except Exception:
                    pass

            task.app.call_from_thread(_show)

            if task.wait_for_response:
                task.done_event.wait()
            else:
                # Non-blocking prompt; mark as resolved so queue can continue.
                task.done_event.set()
                with self._lock:
                    self._current = None

            self._queue.task_done()

    def _resolve_current(self, option: Dict[str, Any], *, force: bool) -> bool:
        with self._lock:
            task = self._current
            if not task or (task.resolved and not force):
                return False

            task.resolved = True

            def _clear() -> None:
                try:
                    prompt_input = task.app.query_one("#prompt-input")
                    prompt_input.permission_prompt_data = None
                    prompt_input.permission_selected_option = 0
                    prompt_input.refresh(layout=True)
                except Exception:
                    pass

            task.app.call_from_thread(_clear)

            if task.future and task.loop:
                if not task.future.done():
                    task.loop.call_soon_threadsafe(task.future.set_result, option)

            task.done_event.set()
            self._current = None
            return True


_MANAGER: Optional[PermissionBufferManager] = None
_MANAGER_LOCK = threading.Lock()


def get_permission_buffer_manager() -> PermissionBufferManager:
    """Return the singleton permission buffer manager."""

    global _MANAGER
    with _MANAGER_LOCK:
        if _MANAGER is None:
            _MANAGER = PermissionBufferManager()
        return _MANAGER
