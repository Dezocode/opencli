"""
Retry Manager - Exponential backoff for failed executions

Consolidates APIRetryManager from stream_manager.py
"""

import asyncio
from typing import Callable, Any


class RetryManager:
    """Handle retries with exponential backoff"""

    @staticmethod
    async def retry(
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        *args,
        **kwargs
    ) -> Any:
        """
        Retry function with exponential backoff

        Args:
            func: Function to retry
            max_retries: Maximum retry attempts
            base_delay: Base delay for exponential backoff
            max_delay: Maximum delay between retries
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries fail
        """
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                # Execute
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = await asyncio.to_thread(func, *args, **kwargs)

                return result

            except Exception as e:
                last_exception = e

                # Don't retry on last attempt
                if attempt == max_retries:
                    break

                # Calculate delay with exponential backoff
                delay = min(base_delay * (2 ** attempt), max_delay)

                # Log retry (could integrate with app.write or logging)
                print(f"⚠️  Attempt {attempt + 1}/{max_retries + 1} failed, retrying in {delay}s...")

                await asyncio.sleep(delay)

        # All retries failed
        raise Exception(
            f"Failed after {max_retries + 1} attempts. Last error: {str(last_exception)}"
        )
