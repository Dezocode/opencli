"""
Unified Display Manager - Coordinates StreamBuffer and direct writes
Ensures smooth coexistence of buffered AI responses and system messages
"""

import asyncio
from typing import Optional, Callable
from collections import deque


class WriteQueue:
    """
    Serializes all writes to prevent interleaving between buffer and direct writes.

    Usage:
        queue = WriteQueue(app)
        await queue.write("system message")  # Queued
        await queue.write_buffered(chunk)    # Goes to buffer, drained smoothly
    """

    def __init__(self, app):
        self.app = app
        self._queue = asyncio.Queue()
        self._worker_task = None
        self._buffer_active = False

    async def start_worker(self):
        """Start background worker that processes writes in order"""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._process_writes())

    async def stop_worker(self):
        """Stop the write worker"""
        if self._worker_task and not self._worker_task.done():
            await self._queue.put(None)  # Sentinel to stop
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

    async def _process_writes(self):
        """Background worker that processes queued writes"""
        while True:
            item = await self._queue.get()

            # Sentinel to stop
            if item is None:
                break

            write_type, content, kwargs = item

            if write_type == "direct":
                # Direct write
                self.app.write(content, **kwargs)
                await asyncio.sleep(0)  # Yield

            elif write_type == "markdown":
                # Render as markdown
                try:
                    from markdown_renderer import get_markdown_renderer
                    renderer = get_markdown_renderer()
                    rendered = renderer.render(content)

                    widget = self.app._resolve_content_widget()
                    if widget and hasattr(widget, '_lines'):
                        widget._lines.append(rendered)
                        if hasattr(widget, 'update'):
                            from rich.text import Text
                            display = Text()
                            for line in widget._lines:
                                if isinstance(line, Text):
                                    display.append_text(line)
                                else:
                                    display.append(str(line))
                                display.append("\n")
                            widget.update(display)
                    else:
                        self.app.write(content)
                except:
                    self.app.write(content)

                await asyncio.sleep(0)  # Yield

            self._queue.task_done()

    async def write(self, text: str, markdown: bool = False, **kwargs):
        """
        Queue a write operation.

        Args:
            text: Text to write
            markdown: Render as markdown
            **kwargs: Additional args for app.write()
        """
        write_type = "markdown" if markdown else "direct"
        await self._queue.put((write_type, text, kwargs))

    async def wait_empty(self):
        """Wait for all queued writes to complete"""
        await self._queue.join()


class UnifiedDisplay:
    """
    Coordinates all TUI writes to prevent blocking between streams.

    - AI responses go through StreamBuffer for smooth rendering
    - System messages write through queue to prevent interleaving
    - All writes are serialized for clean output
    """

    def __init__(self, app, stream_buffer=None):
        """
        Args:
            app: TUI app instance
            stream_buffer: Optional StreamBuffer for AI responses
        """
        self.app = app
        self.stream_buffer = stream_buffer
        self.drain_task: Optional[asyncio.Task] = None
        self.is_draining = False
        self.write_queue = WriteQueue(app)

    async def start(self):
        """Start the unified display system"""
        await self.write_queue.start_worker()

    async def stop(self):
        """Stop the display system"""
        await self.write_queue.stop_worker()

    async def start_draining(self, write_callback: Callable):
        """
        Start draining the stream buffer in background.

        Args:
            write_callback: Async function to call with text chunks
        """
        if not self.stream_buffer:
            return

        self.is_draining = True
        self.write_queue._buffer_active = True
        self.drain_task = asyncio.create_task(
            self._drain_loop(write_callback)
        )

    async def _drain_loop(self, write_callback: Callable):
        """Background task that drains buffer smoothly"""
        try:
            await self.stream_buffer.drain_smooth(write_callback)
        finally:
            self.is_draining = False
            self.write_queue._buffer_active = False

    async def stop_draining(self):
        """Stop the drain task gracefully"""
        if self.drain_task and not self.drain_task.done():
            # Wait for drain to finish naturally
            try:
                await self.drain_task
            except asyncio.CancelledError:
                pass
        self.is_draining = False

    async def write(self, text: str, markdown: bool = False, **kwargs):
        """
        Write text through queue (respects buffer state).

        Args:
            text: Text to write
            markdown: Render as markdown
            **kwargs: Additional args for app.write()
        """
        await self.write_queue.write(text, markdown=markdown, **kwargs)

    async def write_to_buffer(self, chunk: str):
        """
        Add chunk to stream buffer.

        Args:
            chunk: Text chunk to buffer
        """
        if self.stream_buffer:
            await self.stream_buffer.add_chunk(chunk)
