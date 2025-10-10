"""
Async Execution Runner - Non-blocking execution with timeouts

Consolidates AsyncToolExecutor from stream_manager.py
"""

import asyncio
from typing import Callable, Any, Optional


class AsyncExecutionRunner:
    """Execute functions asynchronously with timeout protection"""

    @staticmethod
    async def run_async(
        func: Callable,
        timeout: int = 120,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function asynchronously with timeout

        Args:
            func: Function to execute
            timeout: Max execution time in seconds
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            asyncio.TimeoutError: If execution exceeds timeout
        """
        try:
            # If func is already async
            if asyncio.iscoroutinefunction(func):
                try:
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout
                    )
                except TypeError as te:
                    # Parameter mismatch - ROBUST RECOVERY
                    print(f"[AsyncRunner] WARNING: Parameter mismatch: {te}")
                    print(f"[AsyncRunner] Args: {args}, Kwargs keys: {list(kwargs.keys())}")
                    print(f"[AsyncRunner] Attempting minimal call...")

                    # Try with just app, session
                    if 'app' in kwargs and 'session' in kwargs:
                        result = await asyncio.wait_for(
                            func(kwargs['app'], kwargs['session']),
                            timeout=timeout
                        )
                        print(f"[AsyncRunner] Recovery successful")
                    else:
                        print(f"[AsyncRunner] Recovery failed - no app/session in kwargs")
                        raise
            else:
                # Run sync function in thread pool
                result = await asyncio.wait_for(
                    asyncio.to_thread(func, *args, **kwargs),
                    timeout=timeout
                )

            return result

        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Execution timed out after {timeout}s")
        except Exception as e:
            print(f"[AsyncRunner] ERROR: {e}")
            import traceback
            traceback.print_exc()
            raise

    @staticmethod
    async def run_bash_async(
        command: str,
        timeout: int = 30,
        description: Optional[str] = None
    ) -> str:
        """
        Non-blocking bash execution with timeout

        Args:
            command: Shell command to execute
            timeout: Max execution time in seconds
            description: Optional description

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
            raise asyncio.TimeoutError(f"Command timed out after {timeout}s")
        except Exception as e:
            raise Exception(f"Error executing command: {str(e)}")
