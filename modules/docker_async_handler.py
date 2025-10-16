"""Async Docker Handler for OpenCLI

Provides async wrappers for Docker operations with:
- Thread pool execution to prevent UI blocking
- Comprehensive error handling
- Crash isolation from main application
- Proper cleanup and recovery
"""

import asyncio
import subprocess
from typing import Dict, List, Optional, Tuple, Callable
from pathlib import Path
import traceback


class DockerAsyncHandler:
    """Async handler for Docker operations with crash protection."""

    def __init__(self, docker_manager=None, debug_callback: Callable = None):
        """Initialize async Docker handler.

        Args:
            docker_manager: DockerManager instance
            debug_callback: Optional callback for debug messages
        """
        self.docker_manager = docker_manager
        self.debug = debug_callback or (lambda msg: None)
        self._running_tasks = set()

    async def _safe_thread_call(self, func, *args, timeout=10.0, **kwargs):
        """Safely execute function in thread with error handling and timeout.

        Args:
            func: Function to execute
            *args: Positional arguments
            timeout: Timeout in seconds (default 10)
            **kwargs: Keyword arguments

        Returns:
            Result or None on error
        """
        try:
            self.debug(f"[dim]Docker async: Calling {func.__name__} (timeout={timeout}s)[/dim]")
            result = await asyncio.wait_for(
                asyncio.to_thread(func, *args, **kwargs),
                timeout=timeout
            )
            self.debug(f"[dim]Docker async: {func.__name__} completed[/dim]")
            return result
        except asyncio.TimeoutError:
            self.debug(f"[red]Docker async: {func.__name__} timed out after {timeout}s[/red]")
            return None
        except asyncio.CancelledError:
            self.debug(f"[yellow]Docker async: {func.__name__} cancelled[/yellow]")
            raise
        except Exception as e:
            self.debug(f"[red]Docker async error in {func.__name__}: {str(e)}[/red]")
            if hasattr(e, '__traceback__'):
                tb = ''.join(traceback.format_tb(e.__traceback__))
                self.debug(f"[dim]{tb}[/dim]")
            return None

    async def check_docker_installed(self) -> Tuple[bool, str]:
        """Check if Docker is installed (async).

        Returns:
            (is_installed, version_or_error)
        """
        if not self.docker_manager:
            return False, "Docker manager not initialized"

        result = await self._safe_thread_call(
            self.docker_manager.is_docker_installed,
            timeout=3.0
        )

        if result is None:
            return False, "Failed to check Docker installation"

        return result

    async def check_docker_running(self) -> Tuple[bool, str]:
        """Check if Docker daemon is running (async).

        Returns:
            (is_running, message)
        """
        if not self.docker_manager:
            return False, "Docker manager not initialized"

        result = await self._safe_thread_call(
            self.docker_manager.is_docker_running,
            timeout=5.0
        )

        if result is None:
            return False, "Failed to check Docker daemon"

        return result

    async def get_ollama_container_status(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Get Ollama container status (async).

        Returns:
            (container_id, status, name) or (None, None, None)
        """
        if not self.docker_manager:
            return None, None, None

        result = await self._safe_thread_call(
            self.docker_manager.get_ollama_container_status,
            timeout=5.0
        )

        if result is None:
            return None, None, None

        return result

    async def is_ollama_running(self) -> Tuple[bool, Optional[str]]:
        """Check if Ollama container is running (async).

        Returns:
            (is_running, container_id_or_none)
        """
        if not self.docker_manager:
            return False, None

        result = await self._safe_thread_call(
            self.docker_manager.is_ollama_running,
            timeout=3.0
        )

        if result is None:
            return False, None

        return result

    async def remove_ollama_container(self, force: bool = True) -> Tuple[bool, str]:
        """Remove Ollama container (async).

        Args:
            force: Force removal even if running

        Returns:
            (success, message)
        """
        if not self.docker_manager:
            return False, "Docker manager not initialized"

        result = await self._safe_thread_call(
            self.docker_manager.remove_ollama_container,
            force
        )

        if result is None:
            return False, "Failed to remove container"

        return result

    async def create_ollama_container(
        self,
        gpu_enabled: bool = False,
        cpu_limit: Optional[str] = None,
        memory_limit: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Create Ollama container (async).

        Args:
            gpu_enabled: Enable GPU support
            cpu_limit: CPU limit
            memory_limit: Memory limit

        Returns:
            (success, message_or_container_id)
        """
        if not self.docker_manager:
            return False, "Docker manager not initialized"

        result = await self._safe_thread_call(
            self.docker_manager.create_ollama_container,
            gpu_enabled,
            cpu_limit,
            memory_limit
        )

        if result is None:
            return False, "Failed to create container"

        return result

    async def start_container(self, container_name: str) -> Tuple[bool, str]:
        """Start a container (async).

        Args:
            container_name: Name or ID of container

        Returns:
            (success, message)
        """
        if not self.docker_manager:
            return False, "Docker manager not initialized"

        result = await self._safe_thread_call(
            self.docker_manager.start_container,
            container_name
        )

        if result is None:
            return False, "Failed to start container"

        return result

    async def stop_container(self, container_name: str, timeout: int = 10) -> Tuple[bool, str]:
        """Stop a container (async).

        Args:
            container_name: Name or ID of container
            timeout: Timeout in seconds

        Returns:
            (success, message)
        """
        if not self.docker_manager:
            return False, "Docker manager not initialized"

        result = await self._safe_thread_call(
            self.docker_manager.stop_container,
            container_name,
            timeout
        )

        if result is None:
            return False, "Failed to stop container"

        return result

    async def list_containers(self, all_containers: bool = False) -> List[Dict]:
        """List Docker containers (async).

        Args:
            all_containers: Include stopped containers

        Returns:
            List of container info dicts
        """
        if not self.docker_manager:
            return []

        result = await self._safe_thread_call(
            self.docker_manager.list_containers,
            all_containers
        )

        if result is None:
            return []

        return result

    async def get_container_stats(self, container_name: str) -> Optional[Dict]:
        """Get container stats (async).

        Args:
            container_name: Name or ID of container

        Returns:
            Stats dict or None
        """
        if not self.docker_manager:
            return None

        result = await self._safe_thread_call(
            self.docker_manager.get_container_stats,
            container_name
        )

        return result

    async def pull_image(self, image: str) -> Tuple[bool, str]:
        """Pull a Docker image (async).

        Args:
            image: Image name

        Returns:
            (success, message)
        """
        if not self.docker_manager:
            return False, "Docker manager not initialized"

        result = await self._safe_thread_call(
            self.docker_manager.pull_image,
            image
        )

        if result is None:
            return False, "Failed to pull image"

        return result

    async def get_system_resources(self) -> Dict:
        """Get system resources (async).

        Returns:
            Resources dict
        """
        if not self.docker_manager:
            return {}

        result = await self._safe_thread_call(
            self.docker_manager.get_system_resources
        )

        if result is None:
            return {}

        return result

    async def check_resource_safety(
        self,
        cpu_limit: str,
        memory_limit: str
    ) -> Tuple[bool, str]:
        """Check resource safety (async).

        Args:
            cpu_limit: CPU limit
            memory_limit: Memory limit

        Returns:
            (is_safe, warning_message)
        """
        if not self.docker_manager:
            return False, "Docker manager not initialized"

        result = await self._safe_thread_call(
            self.docker_manager.check_resource_safety,
            cpu_limit,
            memory_limit
        )

        if result is None:
            return False, "Failed to check resource safety"

        return result


class OllamaAsyncHandler:
    """Async handler for Ollama operations with crash protection."""

    def __init__(self, debug_callback: Callable = None):
        """Initialize async Ollama handler.

        Args:
            debug_callback: Optional callback for debug messages
        """
        self.debug = debug_callback or (lambda msg: None)

    async def check_native_ollama(self) -> Tuple[bool, Optional[str]]:
        """Check for native Ollama installation (async with timeout).

        Returns:
            (is_installed, path_or_none)
        """
        try:
            self.debug("[dim]Checking for native Ollama...[/dim]")

            # Check common installation paths
            common_paths = [
                "/usr/local/bin/ollama",
                "/opt/homebrew/bin/ollama",
                "/usr/bin/ollama"
            ]

            for path in common_paths:
                try:
                    exists = await asyncio.wait_for(
                        asyncio.to_thread(Path(path).exists),
                        timeout=1.0
                    )
                    if exists:
                        self.debug(f"[dim]Found native Ollama at {path}[/dim]")
                        return True, path
                except asyncio.TimeoutError:
                    continue

            # Try 'which ollama'
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    subprocess.run,
                    ["which", "ollama"],
                    capture_output=True,
                    text=True,
                    timeout=2
                ),
                timeout=3.0
            )

            if result.returncode == 0:
                path = result.stdout.strip()
                self.debug(f"[dim]Found native Ollama at {path}[/dim]")
                return True, path

            self.debug("[dim]Native Ollama not found[/dim]")
            return False, None

        except asyncio.TimeoutError:
            self.debug("[yellow]Native Ollama check timed out[/yellow]")
            return False, None
        except Exception as e:
            self.debug(f"[red]Error checking native Ollama: {str(e)}[/red]")
            return False, None

    async def check_ollama_server(self, timeout: int = 2) -> Tuple[bool, str]:
        """Check if Ollama server is running (async with timeout).

        Args:
            timeout: Request timeout

        Returns:
            (is_running, message)
        """
        try:
            self.debug("[dim]Checking Ollama server status...[/dim]")

            # Try to connect to Ollama API with timeout
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    subprocess.run,
                    ["curl", "-s", "-m", str(timeout), "http://localhost:11434/api/tags"],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                ),
                timeout=float(timeout + 1)
            )

            if result.returncode == 0:
                self.debug("[dim]Ollama server is running[/dim]")
                return True, "Ollama server is running"
            else:
                self.debug("[dim]Ollama server not responding[/dim]")
                return False, "Ollama server not responding"

        except asyncio.TimeoutError:
            self.debug("[yellow]Ollama server check timed out[/yellow]")
            return False, "Ollama server check timeout"
        except Exception as e:
            self.debug(f"[red]Error checking Ollama server: {str(e)}[/red]")
            return False, f"Error: {str(e)}"

    async def list_ollama_models(self, timeout: int = 5) -> Tuple[bool, List[Dict], str]:
        """List Ollama models (async with timeout).

        Args:
            timeout: Request timeout

        Returns:
            (success, models_list, error_message)
        """
        try:
            self.debug("[dim]Listing Ollama models...[/dim]")

            result = await asyncio.wait_for(
                asyncio.to_thread(
                    subprocess.run,
                    ["ollama", "list"],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                ),
                timeout=float(timeout + 1)
            )

            if result.returncode != 0:
                return False, [], result.stderr or "Failed to list models"

            # Parse output
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return True, [], "No models installed"

            models = []
            for line in lines[1:]:  # Skip header
                parts = line.split()
                if parts:
                    models.append({
                        'name': parts[0],
                        'raw_output': line
                    })

            self.debug(f"[dim]Found {len(models)} Ollama models[/dim]")
            return True, models, ""

        except asyncio.TimeoutError:
            self.debug("[yellow]Ollama list timed out[/yellow]")
            return False, [], "Ollama list timeout"
        except Exception as e:
            self.debug(f"[red]Error listing Ollama models: {str(e)}[/red]")
            return False, [], str(e)

    async def get_ollama_process_info(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """Get Ollama process information (async with timeout).

        Returns:
            (is_running, pid, command)
        """
        try:
            self.debug("[dim]Checking Ollama process...[/dim]")

            result = await asyncio.wait_for(
                asyncio.to_thread(
                    subprocess.run,
                    ["pgrep", "-fl", "ollama"],
                    capture_output=True,
                    text=True,
                    timeout=3
                ),
                timeout=4.0
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'ollama' in line.lower():
                        parts = line.split(None, 1)
                        if len(parts) >= 2:
                            pid = parts[0]
                            command = parts[1]
                            self.debug(f"[dim]Found Ollama process: PID {pid}[/dim]")
                            return True, pid, command

            self.debug("[dim]No Ollama process found[/dim]")
            return False, None, None

        except asyncio.TimeoutError:
            self.debug("[yellow]Ollama process check timed out[/yellow]")
            return False, None, None
        except Exception as e:
            self.debug(f"[red]Error checking Ollama process: {str(e)}[/red]")
            return False, None, None
