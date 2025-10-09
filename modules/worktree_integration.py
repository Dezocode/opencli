"""Git Worktree Integration for OpenCLI

Manages git worktrees for parallel development and safe merging:
- Create/manage worktrees
- Merge changes from Docker venv to worktrees
- Diff comparison before merging
- Safe code isolation
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Worktree:
    """Represents a git worktree."""

    path: str
    branch: str
    commit_hash: str
    is_bare: bool
    is_detached: bool


class WorktreeManager:
    """Manage git worktrees for parallel development."""

    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path or os.getcwd())

    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            result = subprocess.run(
                ['git', '-C', str(self.repo_path), 'rev-parse', '--git-dir'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def list_worktrees(self) -> List[Worktree]:
        """List all worktrees in the repository."""
        if not self.is_git_repo():
            return []

        try:
            result = subprocess.run(
                ['git', '-C', str(self.repo_path), 'worktree', 'list', '--porcelain'],
                capture_output=True,
                timeout=10,
                text=True
            )

            if result.returncode != 0:
                return []

            # Parse porcelain output
            worktrees = []
            current_worktree = {}

            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line:
                    if current_worktree:
                        worktrees.append(Worktree(
                            path=current_worktree.get('worktree', ''),
                            branch=current_worktree.get('branch', ''),
                            commit_hash=current_worktree.get('HEAD', ''),
                            is_bare=current_worktree.get('bare', False),
                            is_detached=current_worktree.get('detached', False)
                        ))
                        current_worktree = {}
                    continue

                if line.startswith('worktree '):
                    current_worktree['worktree'] = line[9:]
                elif line.startswith('HEAD '):
                    current_worktree['HEAD'] = line[5:]
                elif line.startswith('branch '):
                    current_worktree['branch'] = line[7:]
                elif line == 'bare':
                    current_worktree['bare'] = True
                elif line == 'detached':
                    current_worktree['detached'] = True

            # Add last worktree if exists
            if current_worktree:
                worktrees.append(Worktree(
                    path=current_worktree.get('worktree', ''),
                    branch=current_worktree.get('branch', ''),
                    commit_hash=current_worktree.get('HEAD', ''),
                    is_bare=current_worktree.get('bare', False),
                    is_detached=current_worktree.get('detached', False)
                ))

            return worktrees

        except Exception:
            return []

    def create_worktree(
        self,
        path: str,
        branch: str = None,
        new_branch: bool = False
    ) -> Tuple[bool, str]:
        """Create a new worktree.

        Args:
            path: Path for new worktree
            branch: Branch name (creates new if new_branch=True)
            new_branch: Create new branch

        Returns:
            (success, message)
        """
        if not self.is_git_repo():
            return False, "Not a git repository"

        cmd = ['git', '-C', str(self.repo_path), 'worktree', 'add']

        if new_branch and branch:
            cmd.extend(['-b', branch])
        elif branch:
            cmd.append(branch)

        cmd.append(path)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                text=True
            )

            if result.returncode == 0:
                return True, f"Created worktree at {path}"
            else:
                return False, f"Failed: {result.stderr}"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def remove_worktree(self, path: str, force: bool = False) -> Tuple[bool, str]:
        """Remove a worktree.

        Args:
            path: Path to worktree
            force: Force removal even with uncommitted changes

        Returns:
            (success, message)
        """
        if not self.is_git_repo():
            return False, "Not a git repository"

        cmd = ['git', '-C', str(self.repo_path), 'worktree', 'remove']

        if force:
            cmd.append('--force')

        cmd.append(path)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                text=True
            )

            if result.returncode == 0:
                return True, f"Removed worktree at {path}"
            else:
                return False, f"Failed: {result.stderr}"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_worktree_diff(
        self,
        worktree_path: str,
        ref: str = 'HEAD'
    ) -> Tuple[bool, str]:
        """Get diff for a worktree.

        Args:
            worktree_path: Path to worktree
            ref: Git reference to compare against

        Returns:
            (success, diff_text)
        """
        try:
            result = subprocess.run(
                ['git', '-C', worktree_path, 'diff', ref],
                capture_output=True,
                timeout=30,
                text=True
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr

        except Exception as e:
            return False, f"Error: {str(e)}"

    def merge_venv_to_worktree(
        self,
        venv_file_path: str,
        worktree_file_path: str,
        commit_message: str = None
    ) -> Tuple[bool, str, str]:
        """Merge changes from Docker venv file to worktree file.

        Args:
            venv_file_path: Local path to venv file (copied from container)
            worktree_file_path: Path to file in worktree
            commit_message: Commit message (if provided, auto-commits)

        Returns:
            (success, diff_text, message)
        """
        try:
            # First, check if files exist
            if not os.path.exists(venv_file_path):
                return False, "", f"Venv file not found: {venv_file_path}"

            if not os.path.exists(worktree_file_path):
                return False, "", f"Worktree file not found: {worktree_file_path}"

            # Get diff before merging
            diff_result = subprocess.run(
                ['diff', '-u', worktree_file_path, venv_file_path],
                capture_output=True,
                text=True
            )

            # diff returns 0 for identical, 1 for differences, 2 for errors
            if diff_result.returncode == 0:
                return True, "", "Files are identical - no changes to merge"
            elif diff_result.returncode == 2:
                return False, "", f"Diff error: {diff_result.stderr}"

            diff_text = diff_result.stdout

            # Copy venv file to worktree (merging changes)
            import shutil
            shutil.copy2(venv_file_path, worktree_file_path)

            # Auto-commit if message provided
            if commit_message:
                worktree_dir = os.path.dirname(worktree_file_path)
                file_name = os.path.basename(worktree_file_path)

                # Stage file
                subprocess.run(
                    ['git', '-C', worktree_dir, 'add', file_name],
                    capture_output=True,
                    timeout=10
                )

                # Commit
                commit_result = subprocess.run(
                    ['git', '-C', worktree_dir, 'commit', '-m', commit_message],
                    capture_output=True,
                    timeout=10,
                    text=True
                )

                if commit_result.returncode == 0:
                    return True, diff_text, f"Merged and committed: {commit_message}"
                else:
                    return True, diff_text, f"Merged but commit failed: {commit_result.stderr}"

            return True, diff_text, "Merged successfully (not committed)"

        except Exception as e:
            return False, "", f"Error: {str(e)}"

    def get_current_branch(self, worktree_path: str = None) -> Optional[str]:
        """Get current branch name.

        Args:
            worktree_path: Path to worktree (defaults to main repo)

        Returns:
            Branch name or None
        """
        path = worktree_path or str(self.repo_path)

        try:
            result = subprocess.run(
                ['git', '-C', path, 'branch', '--show-current'],
                capture_output=True,
                timeout=5,
                text=True
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None

        except:
            return None

    def has_uncommitted_changes(self, worktree_path: str = None) -> bool:
        """Check if worktree has uncommitted changes.

        Args:
            worktree_path: Path to worktree (defaults to main repo)

        Returns:
            True if uncommitted changes exist
        """
        path = worktree_path or str(self.repo_path)

        try:
            result = subprocess.run(
                ['git', '-C', path, 'status', '--porcelain'],
                capture_output=True,
                timeout=5,
                text=True
            )

            if result.returncode == 0:
                return bool(result.stdout.strip())
            else:
                return False

        except:
            return False

    def create_worktree_for_venv(
        self,
        venv_name: str,
        base_branch: str = 'main'
    ) -> Tuple[bool, str, str]:
        """Create a worktree specifically for a Docker venv.

        Args:
            venv_name: Name of Docker venv
            base_branch: Base branch to branch from

        Returns:
            (success, worktree_path, message)
        """
        # Generate worktree path
        worktree_path = str(self.repo_path.parent / f"{self.repo_path.name}-{venv_name}")

        # Generate branch name
        branch_name = f"venv/{venv_name}"

        # Create worktree
        success, msg = self.create_worktree(
            worktree_path,
            branch=branch_name,
            new_branch=True
        )

        if success:
            return True, worktree_path, f"Created worktree at {worktree_path} on branch {branch_name}"
        else:
            return False, "", msg


def merge_docker_venv_to_worktree(
    venv_manager,
    worktree_manager,
    venv_name: str,
    container_file: str,
    worktree_file: str,
    commit_message: str = None
) -> Tuple[bool, str, str]:
    """High-level function to merge Docker venv file to worktree with diff.

    Args:
        venv_manager: DockerVenvManager instance
        worktree_manager: WorktreeManager instance
        venv_name: Docker venv name
        container_file: File path in container
        worktree_file: File path in worktree
        commit_message: Optional commit message

    Returns:
        (success, diff_text, message)
    """
    import tempfile

    # Copy file from venv to temp location
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = os.path.join(tmpdir, os.path.basename(container_file))

        success, msg = venv_manager.copy_from_venv(
            venv_name,
            container_file,
            temp_file
        )

        if not success:
            return False, "", f"Failed to copy from venv: {msg}"

        # Merge to worktree
        return worktree_manager.merge_venv_to_worktree(
            temp_file,
            worktree_file,
            commit_message
        )
