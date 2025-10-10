"""Central manager for the permission buffer."""

from __future__ import annotations

import asyncio
import threading
from dataclasses import dataclass, field
from queue import Queue
from typing import Any, Dict, Optional


@dataclass
class _PromptTask:
    app: Any
    session: Any
    prompt_data: Dict[str, Any]
    future: Optional[asyncio.Future]
    loop: Optional[asyncio.AbstractEventLoop]
    wait_for_response: bool = True
    done_event: threading.Event = field(default_factory=threading.Event)
    resolved: bool = False


class PermissionBufferManager:
    def __init__(self) -> None:
        self._queue: "Queue[_PromptTask]" = Queue()
        self._current: Optional[_PromptTask] = None
        self._lock = threading.Lock()
        self._running = True
        self._worker = threading.Thread(target=self._run, name="permission-buffer", daemon=True)
        self._worker.start()

    async def prompt(
        self,
        app: Any,
        session: Any,
        prompt_data: Dict[str, Any],
        *,
        timeout: Optional[float] = 30.0,
    ) -> Optional[Dict[str, Any]]:
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
        task = _PromptTask(
            app=app,
            session=session,
            prompt_data=prompt_data,
            future=None,
            loop=None,
            wait_for_response=False,
        )
        self._queue.put(task)

        async def auto_clear():
            await asyncio.sleep(duration)
            self.clear()

        asyncio.create_task(auto_clear())

    def update(self, prompt_data: Dict[str, Any]) -> None:
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
        return self._resolve_current(option, force=False)

    def clear(self) -> bool:
        return self._resolve_current({'response': 'cancel'}, force=True)

    def _run(self) -> None:
        while self._running:
            task = self._queue.get()
            if task is None:
                break

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

            if task.future and task.loop and not task.future.done():
                task.loop.call_soon_threadsafe(task.future.set_result, option)

            task.done_event.set()
            self._current = None
            return True


_MANAGER: Optional[PermissionBufferManager] = None
_MANAGER_LOCK = threading.Lock()


def get_permission_buffer_manager() -> PermissionBufferManager:
    global _MANAGER
    with _MANAGER_LOCK:
        if _MANAGER is None:
            _MANAGER = PermissionBufferManager()
        return _MANAGER
