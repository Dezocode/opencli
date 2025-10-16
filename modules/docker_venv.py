"""Docker Virtual Environment Manager for OpenCLI

Provides safe, isolated Python environments in Docker for:
- Code editing and testing
- Running untrusted code safely
- Merging changes back to worktrees/local repos
- Diff comparison before merging
"""

import subprocess
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DockerVenv:
    """Represents a Docker-based virtual environment."""

    container_id: str
    name: str
    python_version: str
    work_dir: str
    packages: List[str]
    created_at: str


class DockerVenvManager:
    """Manage Docker-based Python virtual environments for safe code editing."""

    # Base Python images
    PYTHON_IMAGES = {
        '3.11': 'python:3.11-slim',
        '3.12': 'python:3.12-slim',
        '3.13': 'python:3.13-slim',
    }

    # Container name prefix
    CONTAINER_PREFIX = "opencli-venv"

    # Resource limits (conservative)
    DEFAULT_CPU_LIMIT = "2"
    DEFAULT_MEMORY_LIMIT = "4g"

    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.venv_config_file = self.config_dir / "docker_venvs.json"
        self.venvs = self._load_venvs()

    def _load_venvs(self) -> Dict[str, DockerVenv]:
        """Load tracked virtual environments."""
        if self.venv_config_file.exists():
            try:
                with open(self.venv_config_file) as f:
                    data = json.load(f)
                return {
                    name: DockerVenv(**venv_data)
                    for name, venv_data in data.items()
                }
            except:
                pass
        return {}

    def _save_venvs(self):
        """Save tracked virtual environments."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        data = {
            name: {
                'container_id': venv.container_id,
                'name': venv.name,
                'python_version': venv.python_version,
                'work_dir': venv.work_dir,
                'packages': venv.packages,
                'created_at': venv.created_at
            }
            for name, venv in self.venvs.items()
        }
        with open(self.venv_config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_venv(
        self,
        name: str,
        python_version: str = '3.12',
        packages: List[str] = None,
        work_dir: str = '/workspace'
    ) -> Tuple[bool, str]:
        """Create a new Docker-based virtual environment.

        Args:
            name: Name for the venv
            python_version: Python version (3.11, 3.12, 3.13)
            packages: List of pip packages to install
            work_dir: Working directory in container

        Returns:
            (success, message_or_container_id)
        """
        packages = packages or []

        # Check if name already exists
        if name in self.venvs:
            return False, f"Venv '{name}' already exists"

        # Get Python image
        if python_version not in self.PYTHON_IMAGES:
            return False, f"Unsupported Python version: {python_version}"

        image = self.PYTHON_IMAGES[python_version]
        container_name = f"{self.CONTAINER_PREFIX}-{name}"

        # Build docker run command
        cmd = [
            'docker', 'run', '-d',
            '--name', container_name,
            '--cpus', self.DEFAULT_CPU_LIMIT,
            '--memory', self.DEFAULT_MEMORY_LIMIT,
            '-w', work_dir,
            '--restart', 'no',  # Manual lifecycle
        ]

        # Mount volumes for code sharing
        # Create temp directory for this venv
        venv_dir = self.config_dir / 'venvs' / name
        venv_dir.mkdir(parents=True, exist_ok=True)

        cmd.extend(['-v', f'{venv_dir}:{work_dir}'])

        # Keep container running
        cmd.extend([image, 'sleep', 'infinity'])

        try:
            # Pull image if needed
            subprocess.run(
                ['docker', 'pull', image],
                capture_output=True,
                timeout=300
            )

            # Create container
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                text=True
            )

            if result.returncode == 0:
                container_id = result.stdout.strip()

                # Install packages if specified
                if packages:
                    install_cmd = ['pip', 'install'] + packages
                    install_result = subprocess.run(
                        ['docker', 'exec', container_id] + install_cmd,
                        capture_output=True,
                        timeout=300,
                        text=True
                    )

                    if install_result.returncode != 0:
                        # Cleanup container
                        subprocess.run(['docker', 'rm', '-f', container_id], capture_output=True)
                        return False, f"Failed to install packages: {install_result.stderr}"

                # Save venv info
                import datetime
                venv = DockerVenv(
                    container_id=container_id,
                    name=name,
                    python_version=python_version,
                    work_dir=work_dir,
                    packages=packages,
                    created_at=datetime.datetime.now().isoformat()
                )
                self.venvs[name] = venv
                self._save_venvs()

                return True, container_id
            else:
                error = result.stderr.strip()
                return False, f"Failed to create container: {error}"

        except subprocess.TimeoutExpired:
            return False, "Container creation timed out"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def list_venvs(self) -> List[DockerVenv]:
        """List all tracked virtual environments."""
        return list(self.venvs.values())

    def get_venv(self, name: str) -> Optional[DockerVenv]:
        """Get venv by name."""
        return self.venvs.get(name)

    def is_venv_running(self, name: str) -> bool:
        """Check if venv container is running."""
        venv = self.venvs.get(name)
        if not venv:
            return False

        try:
            result = subprocess.run(
                ['docker', 'inspect', '-f', '{{.State.Running}}', venv.container_id],
                capture_output=True,
                timeout=5,
                text=True
            )
            return result.returncode == 0 and result.stdout.strip() == 'true'
        except:
            return False

    def start_venv(self, name: str) -> Tuple[bool, str]:
        """Start a stopped venv container."""
        venv = self.venvs.get(name)
        if not venv:
            return False, f"Venv '{name}' not found"

        try:
            result = subprocess.run(
                ['docker', 'start', venv.container_id],
                capture_output=True,
                timeout=10,
                text=True
            )

            if result.returncode == 0:
                return True, f"Started venv '{name}'"
            else:
                return False, f"Failed to start: {result.stderr}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def stop_venv(self, name: str) -> Tuple[bool, str]:
        """Stop a running venv container."""
        venv = self.venvs.get(name)
        if not venv:
            return False, f"Venv '{name}' not found"

        try:
            result = subprocess.run(
                ['docker', 'stop', venv.container_id],
                capture_output=True,
                timeout=10,
                text=True
            )

            if result.returncode == 0:
                return True, f"Stopped venv '{name}'"
            else:
                return False, f"Failed to stop: {result.stderr}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def delete_venv(self, name: str, remove_files: bool = False) -> Tuple[bool, str]:
        """Delete a venv and optionally remove its files.

        Args:
            name: Venv name
            remove_files: If True, also delete local files

        Returns:
            (success, message)
        """
        venv = self.venvs.get(name)
        if not venv:
            return False, f"Venv '{name}' not found"

        try:
            # Remove container
            result = subprocess.run(
                ['docker', 'rm', '-f', venv.container_id],
                capture_output=True,
                timeout=10,
                text=True
            )

            if result.returncode != 0:
                return False, f"Failed to remove container: {result.stderr}"

            # Remove from tracking
            del self.venvs[name]
            self._save_venvs()

            # Remove local files if requested
            if remove_files:
                venv_dir = self.config_dir / 'venvs' / name
                if venv_dir.exists():
                    import shutil
                    shutil.rmtree(venv_dir)

            return True, f"Deleted venv '{name}'"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def exec_in_venv(
        self,
        name: str,
        command: List[str],
        timeout: int = 60
    ) -> Tuple[bool, str, str]:
        """Execute a command in the venv container.

        Args:
            name: Venv name
            command: Command to execute (as list)
            timeout: Timeout in seconds

        Returns:
            (success, stdout, stderr)
        """
        venv = self.venvs.get(name)
        if not venv:
            return False, "", f"Venv '{name}' not found"

        if not self.is_venv_running(name):
            return False, "", f"Venv '{name}' is not running"

        try:
            result = subprocess.run(
                ['docker', 'exec', venv.container_id] + command,
                capture_output=True,
                timeout=timeout,
                text=True
            )

            success = result.returncode == 0
            return success, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return False, "", f"Error: {str(e)}"

    def copy_to_venv(
        self,
        name: str,
        local_path: str,
        container_path: str
    ) -> Tuple[bool, str]:
        """Copy file/directory from local to venv container.

        Args:
            name: Venv name
            local_path: Local file/directory path
            container_path: Path in container

        Returns:
            (success, message)
        """
        venv = self.venvs.get(name)
        if not venv:
            return False, f"Venv '{name}' not found"

        try:
            result = subprocess.run(
                ['docker', 'cp', local_path, f'{venv.container_id}:{container_path}'],
                capture_output=True,
                timeout=60,
                text=True
            )

            if result.returncode == 0:
                return True, f"Copied to {container_path}"
            else:
                return False, f"Failed: {result.stderr}"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def copy_from_venv(
        self,
        name: str,
        container_path: str,
        local_path: str
    ) -> Tuple[bool, str]:
        """Copy file/directory from venv container to local.

        Args:
            name: Venv name
            container_path: Path in container
            local_path: Local file/directory path

        Returns:
            (success, message)
        """
        venv = self.venvs.get(name)
        if not venv:
            return False, f"Venv '{name}' not found"

        try:
            result = subprocess.run(
                ['docker', 'cp', f'{venv.container_id}:{container_path}', local_path],
                capture_output=True,
                timeout=60,
                text=True
            )

            if result.returncode == 0:
                return True, f"Copied to {local_path}"
            else:
                return False, f"Failed: {result.stderr}"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_venv_files(self, name: str, directory: str = '/workspace') -> List[str]:
        """List files in venv directory.

        Args:
            name: Venv name
            directory: Directory to list

        Returns:
            List of file paths
        """
        success, stdout, stderr = self.exec_in_venv(
            name,
            ['find', directory, '-type', 'f'],
            timeout=30
        )

        if success:
            return [f.strip() for f in stdout.split('\n') if f.strip()]
        else:
            return []

    def run_python_code(
        self,
        name: str,
        code: str,
        timeout: int = 60
    ) -> Tuple[bool, str, str]:
        """Run Python code in the venv safely.

        Args:
            name: Venv name
            code: Python code to execute
            timeout: Timeout in seconds

        Returns:
            (success, stdout, stderr)
        """
        # Write code to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # Copy to container
            venv = self.venvs.get(name)
            if not venv:
                return False, "", f"Venv '{name}' not found"

            container_file = f'{venv.work_dir}/temp_code.py'
            success, msg = self.copy_to_venv(name, temp_file, container_file)

            if not success:
                return False, "", msg

            # Execute
            success, stdout, stderr = self.exec_in_venv(
                name,
                ['python', container_file],
                timeout=timeout
            )

            # Cleanup container file
            self.exec_in_venv(name, ['rm', container_file], timeout=5)

            return success, stdout, stderr

        finally:
            # Cleanup local temp file
            try:
                os.unlink(temp_file)
            except:
                pass
