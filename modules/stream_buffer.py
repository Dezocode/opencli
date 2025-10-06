"""
Stream Buffer - Smooth token streaming with animated status
Buffers incoming API chunks and releases at controlled pace
"""

import asyncio
import time
from collections import deque


class StreamBuffer:
    """Buffers API response chunks for smooth, controlled streaming"""

    def __init__(self, chars_per_batch=20, batch_delay_ms=50):
        """
        Args:
            chars_per_batch: Characters to release per batch
            batch_delay_ms: Delay between batches in milliseconds
        """
        self.buffer = asyncio.Queue()
        self.total_tokens = 0
        self.start_time = None
        self.receiving = False
        self.complete = False
        self.interrupted = False

        # Pacing configuration
        self.chars_per_batch = chars_per_batch
        self.batch_delay = batch_delay_ms / 1000.0  # Convert to seconds

        # For assembled output
        self.full_text = ""

    def start(self):
        """Start buffer reception"""
        self.start_time = time.time()
        self.receiving = True
        self.complete = False
        self.interrupted = False
        self.total_tokens = 0
        self.full_text = ""

    async def add_chunk(self, text):
        """Add text chunk to buffer (called from streaming loop)"""
        if not text:
            return
        await self.buffer.put(text)
        self.total_tokens += len(text)  # Approximate token count
        self.full_text += text

    def finish_receiving(self):
        """Mark reception complete"""
        self.receiving = False

    def interrupt(self):
        """User interrupted with ESC"""
        self.interrupted = True
        self.receiving = False

    def get_status_message(self, spinner_char="✢"):
        """Get current spinner status message"""
        if not self.start_time:
            return ""

        elapsed = int(time.time() - self.start_time)

        # Different messages based on state
        if self.interrupted:
            return f"⏸ Interrupted (↓ {self.total_tokens} tokens received)"
        elif self.receiving:
            return f"{spinner_char} Synthesizing… (esc to interrupt · {elapsed}s · ↓ {self.total_tokens} tokens)"
        elif not self.complete:
            return f"{spinner_char} Rendering… ({self.total_tokens} tokens · {elapsed}s)"
        else:
            return f"✓ Complete ({self.total_tokens} tokens · {elapsed}s)"

    def get_elapsed(self):
        """Get elapsed time in seconds"""
        if not self.start_time:
            return 0
        return int(time.time() - self.start_time)

    async def drain_smooth(self, write_callback):
        """
        Drain buffer with smooth pacing

        Args:
            write_callback: async function to call with text chunks
        """
        accumulated = ""

        while self.receiving or not self.buffer.empty():
            if self.interrupted:
                break

            try:
                # Get chunk from buffer (with timeout to check receiving status)
                chunk = await asyncio.wait_for(self.buffer.get(), timeout=0.1)
                accumulated += chunk

                # Release in batches for smooth rendering
                while len(accumulated) >= self.chars_per_batch:
                    batch = accumulated[:self.chars_per_batch]
                    accumulated = accumulated[self.chars_per_batch:]

                    await write_callback(batch)
                    await asyncio.sleep(self.batch_delay)

            except asyncio.TimeoutError:
                # No chunk available, continue waiting
                continue

        # Flush any remaining text
        if accumulated and not self.interrupted:
            await write_callback(accumulated)

        self.complete = True


class BufferStatusDisplay:
    """Manages the animated buffer status inline in chat area"""

    # Braille spinner animation frames
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, app, buffer):
        """
        Args:
            app: TUI app instance
            buffer: StreamBuffer instance
        """
        self.app = app
        self.buffer = buffer
        self.status_task = None
        self.content_widget = None
        self._spinner_frame = 0

    async def start(self):
        """Start animated status display in chat"""
        # Get content widget (StreamingDisplay)
        self.content_widget = self.app._resolve_content_widget()

        if self.content_widget and hasattr(self.content_widget, 'add_buffer_status'):
            # Add buffer status line to chat
            self.content_widget.add_buffer_status(
                tokens=self.buffer.total_tokens,
                elapsed=self.buffer.get_elapsed()
            )

        # Start update task
        self.status_task = asyncio.create_task(self._update_loop())

    async def stop(self):
        """Stop status updates and remove from chat"""
        if self.status_task:
            self.status_task.cancel()
            try:
                await self.status_task
            except asyncio.CancelledError:
                pass

        # Remove buffer status from display
        if self.content_widget and hasattr(self.content_widget, 'remove_buffer_status'):
            self.content_widget.remove_buffer_status()

    async def _update_loop(self):
        """Background task to update buffer status inline"""
        try:
            while not self.buffer.complete:
                if self.buffer.interrupted:
                    break

                # Update spinner frame
                self._spinner_frame = (self._spinner_frame + 1) % len(self.SPINNER_FRAMES)
                spinner = self.SPINNER_FRAMES[self._spinner_frame]

                # Update buffer status in chat
                if self.content_widget and hasattr(self.content_widget, 'update_buffer_status'):
                    self.content_widget.update_buffer_status(
                        tokens=self.buffer.total_tokens,
                        elapsed=self.buffer.get_elapsed(),
                        spinner_frame=spinner
                    )

                await asyncio.sleep(0.1)  # Update 10 times per second

        except asyncio.CancelledError:
            pass

    def write_final_status(self):
        """Write final status message (optional - widget removal handles display)"""
        # Widget is removed by stop(), so we can optionally write a completion message
        # For now, just let the markdown response replace the widget
        pass
