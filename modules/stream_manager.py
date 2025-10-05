"""
Stream Manager - Handles async streaming with timeouts and cancellation
Prevents UI freezes and provides robust error handling
"""

import asyncio
import time
from typing import Optional, Callable
from datetime import datetime


class StreamTimeoutError(Exception):
    """Raised when stream exceeds timeout"""
    pass


class StreamManager:
    """Manages streaming with timeout, cancellation, and heartbeat monitoring"""

    def __init__(self, timeout: int = 300, heartbeat_interval: float = 2.0):
        """
        Args:
            timeout: Max seconds for stream (default 5min)
            heartbeat_interval: Seconds between heartbeat checks
        """
        self.timeout = timeout
        self.heartbeat_interval = heartbeat_interval
        self.cancel_token = asyncio.Event()
        self.last_activity = time.time()
        self.heartbeat_task: Optional[asyncio.Task] = None

    async def stream_with_timeout(self, coro, on_heartbeat: Optional[Callable] = None):
        """
        Execute coroutine with timeout protection

        Args:
            coro: Async coroutine to execute
            on_heartbeat: Optional callback when stream appears frozen

        Returns:
            Result from coroutine

        Raises:
            StreamTimeoutError: If stream exceeds timeout
        """
        # Start heartbeat monitor if callback provided
        if on_heartbeat:
            self.heartbeat_task = asyncio.create_task(
                self._heartbeat_monitor(on_heartbeat)
            )

        try:
            result = await asyncio.wait_for(coro, timeout=self.timeout)
            return result
        except asyncio.TimeoutError:
            self.cancel_token.set()
            raise StreamTimeoutError(f"Stream exceeded {self.timeout}s timeout")
        finally:
            # Cancel heartbeat monitor
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass

    async def _heartbeat_monitor(self, callback: Callable):
        """Monitor for frozen streams and alert via callback"""
        frozen_threshold = 30  # Alert if no activity for 30s

        while not self.cancel_token.is_set():
            await asyncio.sleep(self.heartbeat_interval)

            inactive_time = time.time() - self.last_activity
            if inactive_time > frozen_threshold:
                await callback(inactive_time)

    def update_activity(self):
        """Update last activity timestamp (call on stream progress)"""
        self.last_activity = time.time()

    def cancel(self):
        """Cancel the stream"""
        self.cancel_token.set()

    def is_cancelled(self) -> bool:
        """Check if stream was cancelled"""
        return self.cancel_token.is_set()


class AsyncToolExecutor:
    """Execute tools asynchronously with timeout protection"""

    @staticmethod
    async def execute_bash_async(command: str, description: Optional[str] = None, timeout: int = 30):
        """
        Non-blocking bash execution with timeout

        Args:
            command: Shell command to execute
            description: Optional description
            timeout: Max execution time in seconds

        Returns:
            Command output as string
        """
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )

            output = stdout.decode() + stderr.decode()
            return output if output else f"✓ Command executed: {command}"

        except asyncio.TimeoutError:
            if proc:
                proc.kill()
                await proc.wait()
            return f"⏱ Command timed out after {timeout}s"
        except Exception as e:
            return f"Error executing command: {str(e)}"

    @staticmethod
    async def execute_read_async(file_path: str):
        """Async file read"""
        try:
            # Use thread executor for file I/O
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: open(file_path, 'r').read()
            )
        except Exception as e:
            return f"Error reading {file_path}: {str(e)}"

    @staticmethod
    async def execute_write_async(file_path: str, content: str):
        """Async file write"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: open(file_path, 'w').write(content)
            )
            return f"✓ Written to {file_path}"
        except Exception as e:
            return f"Error writing to {file_path}: {str(e)}"


class APIRetryManager:
    """Handles API calls with exponential backoff"""

    @staticmethod
    async def call_with_retry(client, max_retries: int = 3, base_delay: float = 1.0, **kwargs):
        """
        Retry API calls with exponential backoff

        Args:
            client: OpenAI async client
            max_retries: Maximum retry attempts
            base_delay: Base delay for exponential backoff
            **kwargs: Arguments for chat.completions.create()

        Returns:
            API response

        Raises:
            Exception: If all retries fail
        """
        for attempt in range(max_retries):
            try:
                return await client.chat.completions.create(**kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise

                delay = base_delay * (2 ** attempt)
                print(f"⚠️ API call failed (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                await asyncio.sleep(delay)


class ToolCircuitBreaker:
    """Prevent cascading failures in tool execution"""

    def __init__(self, failure_threshold: int = 3, timeout: int = 60):
        """
        Args:
            failure_threshold: Failures before opening circuit
            timeout: Seconds before attempting reset (half-open state)
        """
        self.failures = 0
        self.threshold = failure_threshold
        self.timeout = timeout
        self.state = 'closed'  # closed, open, half_open
        self.last_failure: Optional[float] = None

    async def execute(self, tool_func, *args, **kwargs):
        """
        Execute tool with circuit breaker protection

        Raises:
            CircuitOpenError: If circuit is open
        """
        if self.state == 'open':
            if self.last_failure and time.time() - self.last_failure > self.timeout:
                self.state = 'half_open'
            else:
                raise CircuitOpenError("Tool execution circuit is open - too many failures")

        try:
            result = await tool_func(*args, **kwargs)

            # Success in half_open state closes the circuit
            if self.state == 'half_open':
                self.state = 'closed'
                self.failures = 0

            return result

        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()

            if self.failures >= self.threshold:
                self.state = 'open'

            raise


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass
