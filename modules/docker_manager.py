"""
Docker Manager for OpenCLI
Manages Docker containers for local model serving (Ollama, etc.)
Provides safety checks, resource monitoring, and permission-based automation
"""

import subprocess
import json
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class DockerManager:
    """Manage Docker containers for local AI models with safety checks."""

    # Ollama Docker image configuration
    OLLAMA_IMAGE = "ollama/ollama:latest"
    OLLAMA_CONTAINER_NAME = "opencli-ollama"
    OLLAMA_PORT = 11434

    # Resource limits (conservative defaults)
    DEFAULT_CPU_LIMIT = "4"  # 4 CPUs max
    DEFAULT_MEMORY_LIMIT = "8g"  # 8GB RAM max

    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.docker_config_file = self.config_dir / "docker_config.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load Docker configuration."""
        if self.docker_config_file.exists():
            try:
                with open(self.docker_config_file) as f:
                    return json.load(f)
            except:
                pass

        return {
            "enabled": True,
            "cpu_limit": self.DEFAULT_CPU_LIMIT,
            "memory_limit": self.DEFAULT_MEMORY_LIMIT,
            "auto_pull_images": False,  # Ask permission first
            "monitored_containers": []
        }

    def _save_config(self):
        """Save Docker configuration."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.docker_config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def is_docker_installed(self) -> Tuple[bool, str]:
        """Check if Docker is installed.

        Returns:
            (is_installed, version_or_error)
        """
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=2,
                text=True
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, version
            return False, "Docker command failed"
        except FileNotFoundError:
            return False, "Docker not found in PATH"
        except Exception as e:
            return False, str(e)

    def is_docker_running(self) -> Tuple[bool, str]:
        """Check if Docker daemon is running.

        Returns:
            (is_running, message)
        """
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=5,
                text=True
            )
            if result.returncode == 0:
                return True, "Docker daemon is running"
            return False, "Docker daemon not responding"
        except subprocess.TimeoutExpired:
            return False, "Docker daemon timeout (may be starting)"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_system_resources(self) -> Dict:
        """Get system resource information for safety checks.

        Returns:
            Dict with cpu_count, memory_gb, disk_gb
        """
        resources = {}

        # CPU count
        try:
            import multiprocessing
            resources['cpu_count'] = multiprocessing.cpu_count()
        except:
            resources['cpu_count'] = 0

        # Memory
        try:
            if os.uname().sysname == 'Darwin':  # macOS
                result = subprocess.run(
                    ["sysctl", "-n", "hw.memsize"],
                    capture_output=True,
                    timeout=2,
                    text=True
                )
                if result.returncode == 0:
                    mem_bytes = int(result.stdout.strip())
                    resources['memory_gb'] = mem_bytes / (1024**3)
            else:  # Linux
                with open('/proc/meminfo') as f:
                    for line in f:
                        if line.startswith('MemTotal:'):
                            kb = int(line.split()[1])
                            resources['memory_gb'] = kb / (1024**2)
                            break
        except:
            resources['memory_gb'] = 0

        # Disk space
        try:
            result = subprocess.run(
                ["df", "-BG", str(Path.home())],
                capture_output=True,
                timeout=2,
                text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 4:
                        avail = parts[3].rstrip('G')
                        resources['disk_gb'] = int(avail)
        except:
            resources['disk_gb'] = 0

        return resources

    def check_resource_safety(self, cpu_limit: str, memory_limit: str) -> Tuple[bool, str]:
        """Check if requested resources are safe.

        Args:
            cpu_limit: CPU limit (e.g., "4" or "2.5")
            memory_limit: Memory limit (e.g., "8g" or "4096m")

        Returns:
            (is_safe, warning_message)
        """
        resources = self.get_system_resources()
        warnings = []

        # Parse CPU limit
        try:
            requested_cpus = float(cpu_limit)
            available_cpus = resources.get('cpu_count', 0)

            if available_cpus > 0:
                if requested_cpus > available_cpus:
                    warnings.append(f"CPU limit ({requested_cpus}) exceeds available CPUs ({available_cpus})")
                elif requested_cpus > available_cpus * 0.8:
                    warnings.append(f"CPU limit ({requested_cpus}) is >80% of available CPUs ({available_cpus})")
        except:
            warnings.append(f"Invalid CPU limit format: {cpu_limit}")

        # Parse memory limit
        try:
            mem_value = memory_limit.lower()
            if mem_value.endswith('g'):
                requested_gb = float(mem_value[:-1])
            elif mem_value.endswith('m'):
                requested_gb = float(mem_value[:-1]) / 1024
            else:
                requested_gb = float(mem_value) / (1024**3)

            available_gb = resources.get('memory_gb', 0)

            if available_gb > 0:
                if requested_gb > available_gb:
                    warnings.append(f"Memory limit ({requested_gb:.1f}GB) exceeds available memory ({available_gb:.1f}GB)")
                elif requested_gb > available_gb * 0.75:
                    warnings.append(f"Memory limit ({requested_gb:.1f}GB) is >75% of available memory ({available_gb:.1f}GB)")
        except:
            warnings.append(f"Invalid memory limit format: {memory_limit}")

        if warnings:
            return False, "; ".join(warnings)
        return True, "Resource limits are safe"

    def list_containers(self, all_containers: bool = False) -> List[Dict]:
        """List Docker containers.

        Args:
            all_containers: If True, include stopped containers

        Returns:
            List of container info dicts
        """
        try:
            cmd = ["docker", "ps", "--format", "json"]
            if all_containers:
                cmd.append("-a")

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=5,
                text=True
            )

            if result.returncode != 0:
                return []

            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        container = json.loads(line)
                        containers.append(container)
                    except:
                        pass

            return containers
        except:
            return []

    def get_container_stats(self, container_name: str) -> Optional[Dict]:
        """Get real-time stats for a container.

        Args:
            container_name: Name or ID of container

        Returns:
            Dict with cpu_percent, memory_usage, memory_limit, network stats
        """
        try:
            result = subprocess.run(
                ["docker", "stats", container_name, "--no-stream", "--format", "json"],
                capture_output=True,
                timeout=5,
                text=True
            )

            if result.returncode == 0 and result.stdout.strip():
                stats = json.loads(result.stdout.strip())
                return {
                    'cpu_percent': stats.get('CPUPerc', '0%').rstrip('%'),
                    'memory_usage': stats.get('MemUsage', 'N/A'),
                    'memory_percent': stats.get('MemPerc', '0%').rstrip('%'),
                    'network_io': stats.get('NetIO', 'N/A'),
                    'block_io': stats.get('BlockIO', 'N/A')
                }
        except:
            pass

        return None

    def is_ollama_running(self) -> Tuple[bool, Optional[str]]:
        """Check if Ollama container is running.

        Returns:
            (is_running, container_id_or_none)
        """
        containers = self.list_containers(all_containers=False)

        for container in containers:
            name = container.get('Names', '')
            image = container.get('Image', '')

            # Check if it's our Ollama container or any Ollama container
            if self.OLLAMA_CONTAINER_NAME in name or 'ollama' in image.lower():
                return True, container.get('ID')

        return False, None

    def get_ollama_container_status(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Check status of OpenCLI Ollama container (running or stopped).

        Returns:
            (container_id, status, name) or (None, None, None)
            status: 'running', 'exited', 'created', 'paused', etc.
        """
        # Check all containers including stopped ones
        containers = self.list_containers(all_containers=True)

        for container in containers:
            name = container.get('Names', '')

            # Check for our specific OpenCLI branded container
            if self.OLLAMA_CONTAINER_NAME in name:
                return (
                    container.get('ID'),
                    container.get('State', 'unknown'),
                    name
                )

        return None, None, None

    def remove_ollama_container(self, force: bool = True) -> Tuple[bool, str]:
        """Remove OpenCLI Ollama container (including stopped/failed ones).

        Args:
            force: Force removal even if running

        Returns:
            (success, message)
        """
        container_id, status, name = self.get_ollama_container_status()

        if not container_id:
            return False, "No OpenCLI Ollama container found"

        try:
            cmd = ["docker", "rm"]
            if force:
                cmd.append("-f")
            cmd.append(container_id)

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                text=True
            )

            if result.returncode == 0:
                return True, f"Removed container {name} (was {status})"
            else:
                return False, f"Failed to remove container: {result.stderr}"

        except Exception as e:
            return False, f"Error removing container: {str(e)}"

    def create_ollama_container(
        self,
        gpu_enabled: bool = False,
        cpu_limit: Optional[str] = None,
        memory_limit: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Create and start Ollama Docker container.

        Args:
            gpu_enabled: Enable GPU support (requires nvidia-docker)
            cpu_limit: CPU limit (default from config)
            memory_limit: Memory limit (default from config)

        Returns:
            (success, message_or_container_id)
        """
        cpu_limit = cpu_limit or self.config.get('cpu_limit', self.DEFAULT_CPU_LIMIT)
        memory_limit = memory_limit or self.config.get('memory_limit', self.DEFAULT_MEMORY_LIMIT)

        # Safety check
        is_safe, warning = self.check_resource_safety(cpu_limit, memory_limit)
        if not is_safe:
            return False, f"Resource safety check failed: {warning}"

        # Build docker run command
        cmd = [
            "docker", "run", "-d",
            "--name", self.OLLAMA_CONTAINER_NAME,
            "-p", f"{self.OLLAMA_PORT}:{self.OLLAMA_PORT}",
            "--cpus", cpu_limit,
            "--memory", memory_limit,
            "--restart", "unless-stopped"  # Auto-restart policy
        ]

        # Add GPU support if requested
        if gpu_enabled:
            cmd.extend(["--gpus", "all"])

        # Add volume for model persistence
        volume_path = self.config_dir / "ollama_models"
        volume_path.mkdir(parents=True, exist_ok=True)
        cmd.extend(["-v", f"{volume_path}:/root/.ollama"])

        cmd.append(self.OLLAMA_IMAGE)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                text=True
            )

            if result.returncode == 0:
                container_id = result.stdout.strip()
                return True, container_id
            else:
                error = result.stderr.strip() or result.stdout.strip()
                return False, f"Failed to create container: {error}"
        except subprocess.TimeoutExpired:
            return False, "Container creation timed out"
        except Exception as e:
            return False, f"Error creating container: {str(e)}"

    def start_container(self, container_name: str) -> Tuple[bool, str]:
        """Start a stopped container.

        Args:
            container_name: Name or ID of container

        Returns:
            (success, message)
        """
        try:
            result = subprocess.run(
                ["docker", "start", container_name],
                capture_output=True,
                timeout=10,
                text=True
            )

            if result.returncode == 0:
                return True, f"Started container {container_name}"
            else:
                error = result.stderr.strip()
                return False, f"Failed to start: {error}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def stop_container(self, container_name: str, timeout: int = 10) -> Tuple[bool, str]:
        """Stop a running container gracefully.

        Args:
            container_name: Name or ID of container
            timeout: Seconds to wait before force kill

        Returns:
            (success, message)
        """
        try:
            result = subprocess.run(
                ["docker", "stop", "-t", str(timeout), container_name],
                capture_output=True,
                timeout=timeout + 5,
                text=True
            )

            if result.returncode == 0:
                return True, f"Stopped container {container_name}"
            else:
                error = result.stderr.strip()
                return False, f"Failed to stop: {error}"
        except subprocess.TimeoutExpired:
            return False, f"Stop command timed out after {timeout}s"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def remove_container(self, container_name: str, force: bool = False) -> Tuple[bool, str]:
        """Remove a container.

        Args:
            container_name: Name or ID of container
            force: Force remove (kill if running)

        Returns:
            (success, message)
        """
        cmd = ["docker", "rm"]
        if force:
            cmd.append("-f")
        cmd.append(container_name)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=10,
                text=True
            )

            if result.returncode == 0:
                return True, f"Removed container {container_name}"
            else:
                error = result.stderr.strip()
                return False, f"Failed to remove: {error}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def pull_image(self, image: str) -> Tuple[bool, str]:
        """Pull a Docker image.

        Args:
            image: Image name (e.g., "ollama/ollama:latest")

        Returns:
            (success, message)
        """
        try:
            # Run in foreground so we can see progress
            result = subprocess.run(
                ["docker", "pull", image],
                capture_output=False,  # Show progress
                timeout=300,  # 5 minutes
                text=True
            )

            if result.returncode == 0:
                return True, f"Pulled image {image}"
            else:
                return False, f"Failed to pull image {image}"
        except subprocess.TimeoutExpired:
            return False, "Image pull timed out (large image or slow connection)"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_ollama_container_status(self) -> Dict:
        """Get detailed status of Ollama container.

        Returns:
            Dict with status, id, stats, ports, etc.
        """
        is_running, container_id = self.is_ollama_running()

        status = {
            'running': is_running,
            'container_id': container_id,
            'container_name': self.OLLAMA_CONTAINER_NAME,
            'port': self.OLLAMA_PORT,
            'stats': None
        }

        if is_running and container_id:
            stats = self.get_container_stats(container_id)
            status['stats'] = stats

        return status
