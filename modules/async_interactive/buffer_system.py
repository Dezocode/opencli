"""
Buffer system for managing streaming content
Coordinates stream buffer and display widgets
"""

import asyncio
import time
from typing import Optional, Callable


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

                # Release in batches for smooth display
                while len(accumulated) >= self.chars_per_batch:
                    batch = accumulated[:self.chars_per_batch]
                    accumulated = accumulated[self.chars_per_batch:]
                    
                    await write_callback(batch)
                    await asyncio.sleep(self.batch_delay)

            except asyncio.TimeoutError:
                # No new data, but maybe we have accumulated text to flush
                if accumulated and not self.receiving:
                    await write_callback(accumulated)
                    accumulated = ""
                continue

        # Flush any remaining text
        if accumulated:
            await write_callback(accumulated)

        self.complete = True


class BufferManager:
    """Manages multiple buffers for different purposes"""
    
    def __init__(self):
        self.stream_buffer = StreamBuffer()
        self.permission_buffer = None  # For permission prompts
        self.status_widget = None  # Reference to status widget
        
    def create_stream_buffer(self, **kwargs) -> StreamBuffer:
        """Create a new stream buffer with given parameters"""
        self.stream_buffer = StreamBuffer(**kwargs)
        return self.stream_buffer
    
    def set_status_widget(self, widget):
        """Set reference to status widget for updates"""
        self.status_widget = widget
    
    async def update_status(self):
        """Update status widget if available"""
        if self.status_widget and self.stream_buffer:
            self.status_widget.update_progress(
                self.stream_buffer.total_tokens,
                self.stream_buffer.get_elapsed()
            )
    
    def interrupt_all(self):
        """Interrupt all active buffers"""
        if self.stream_buffer:
            self.stream_buffer.interrupt()