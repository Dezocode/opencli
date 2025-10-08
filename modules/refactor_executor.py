"""
Refactoring Executor with Git Worktree Sandbox
Safely performs refactorings with permission system integration
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from rope.base.project import Project
from rope.refactor.extract import ExtractMethod, ExtractVariable
from rope.refactor.move import MoveModule
from rope.base import libutils


@dataclass
class RefactoringPlan:
    """Plan for a code refactoring"""
    action: str  # "extract_module", "split_file", "move_functions"
    source_file: str
    target_file: str
    functions_to_move: List[str]
    estimated_lines: int
    rationale: str


@dataclass
class RefactoringResult:
    """Result of a refactoring operation"""
    success: bool
    worktree_path: Optional[str]
    changes: List[str]  # List of changed files
    diff: str
    test_results: Optional[str]
    error: Optional[str] = None


class WorktreeManager:
    """Manage git worktrees for safe refactoring"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.active_worktrees: List[str] = []

    def create_worktree(self, branch_name: str = "refactor-temp") -> Optional[str]:
        """Create a new git worktree for refactoring"""
        try:
            # Create temporary directory
            worktree_dir = tempfile.mkdtemp(prefix="opencli_refactor_")

            # Create worktree
            result = subprocess.run(
                ["git", "worktree", "add", "-b", branch_name, worktree_dir],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            self.active_worktrees.append(worktree_dir)
            return worktree_dir

        except subprocess.CalledProcessError as e:
            print(f"Failed to create worktree: {e.stderr}")
            return None

    def remove_worktree(self, worktree_path: str):
        """Remove a git worktree"""
        try:
            # Get branch name
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=worktree_path,
                capture_output=True,
                text=True
            )
            branch_name = result.stdout.strip()

            # Remove worktree
            subprocess.run(
                ["git", "worktree", "remove", worktree_path, "--force"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )

            # Delete branch
            if branch_name and branch_name != "main" and branch_name != "master":
                subprocess.run(
                    ["git", "branch", "-D", branch_name],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )

            # Remove from active list
            if worktree_path in self.active_worktrees:
                self.active_worktrees.remove(worktree_path)

            # Clean up directory if it still exists
            if os.path.exists(worktree_path):
                shutil.rmtree(worktree_path, ignore_errors=True)

        except Exception as e:
            print(f"Error removing worktree: {e}")

    def cleanup_all(self):
        """Clean up all active worktrees"""
        for worktree in self.active_worktrees[:]:
            self.remove_worktree(worktree)


class RefactoringExecutor:
    """Execute refactorings safely in git worktree sandbox"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.worktree_manager = WorktreeManager(repo_path)

    def execute_extraction(self, plan: RefactoringPlan) -> RefactoringResult:
        """
        Execute a function extraction refactoring

        This creates a worktree, performs the refactoring, runs tests,
        and returns the results for permission approval
        """
        worktree_path = None

        try:
            # Create worktree sandbox
            worktree_path = self.worktree_manager.create_worktree()
            if not worktree_path:
                return RefactoringResult(
                    success=False,
                    worktree_path=None,
                    changes=[],
                    diff="",
                    test_results=None,
                    error="Failed to create git worktree"
                )

            # Perform refactoring in worktree
            changes = self._perform_extraction(worktree_path, plan)

            if not changes:
                self.worktree_manager.remove_worktree(worktree_path)
                return RefactoringResult(
                    success=False,
                    worktree_path=None,
                    changes=[],
                    diff="",
                    test_results=None,
                    error="Refactoring failed - no changes made"
                )

            # Generate diff
            diff = self._generate_diff(worktree_path, changes)

            # Run tests
            test_results = self._run_tests(worktree_path)

            # Return result - worktree is kept for permission review
            return RefactoringResult(
                success=True,
                worktree_path=worktree_path,
                changes=changes,
                diff=diff,
                test_results=test_results
            )

        except Exception as e:
            if worktree_path:
                self.worktree_manager.remove_worktree(worktree_path)

            return RefactoringResult(
                success=False,
                worktree_path=None,
                changes=[],
                diff="",
                test_results=None,
                error=f"Refactoring error: {str(e)}"
            )

    def _perform_extraction(self, worktree_path: str, plan: RefactoringPlan) -> List[str]:
        """
        Perform the actual code extraction using rope library

        Extracts specified functions from source file to target file
        """
        changes = []

        try:
            # Create rope project in worktree
            project = Project(worktree_path)

            source_path = Path(worktree_path) / plan.source_file
            target_path = Path(worktree_path) / plan.target_file

            if not source_path.exists():
                project.close()
                return changes

            # Get rope resource for source file
            source_resource = libutils.path_to_resource(project, str(source_path))

            # Read source to find function definitions
            with open(source_path, 'r') as f:
                source_code = f.read()

            # Create target module if it doesn't exist
            target_path.parent.mkdir(parents=True, exist_ok=True)

            if not target_path.exists():
                # Create new module with docstring
                module_name = Path(plan.target_file).stem
                with open(target_path, 'w') as f:
                    f.write(f'"""\n')
                    f.write(f'Extracted from {plan.source_file}\n')
                    f.write(f'"""\n\n')
                changes.append(plan.target_file)

            # Extract each function using rope
            for func_name in plan.functions_to_move:
                try:
                    # Find function in source code
                    import ast
                    tree = ast.parse(source_code)
                    func_node = None
                    func_lineno = None

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.name == func_name:
                            func_node = node
                            func_lineno = node.lineno
                            break

                    if not func_node:
                        print(f"Function {func_name} not found in {plan.source_file}")
                        continue

                    # Read current source (may have been modified)
                    with open(source_path, 'r') as f:
                        current_source = f.read()

                    # Find function text
                    lines = current_source.split('\n')
                    func_start = func_lineno - 1
                    func_end = func_node.end_lineno
                    func_text = '\n'.join(lines[func_start:func_end])

                    # Append to target file
                    with open(target_path, 'a') as f:
                        f.write('\n\n')
                        f.write(func_text)
                        f.write('\n')

                    # Remove from source file
                    lines = lines[:func_start] + lines[func_end:]

                    # Add import if not already present
                    target_module = Path(plan.target_file).stem
                    import_line = f"from .{target_module} import {func_name}"

                    # Check if import already exists
                    if import_line not in '\n'.join(lines):
                        # Insert after docstring and existing imports
                        insert_pos = 0
                        in_docstring = False
                        for i, line in enumerate(lines):
                            stripped = line.strip()
                            if '"""' in stripped or "'''" in stripped:
                                in_docstring = not in_docstring
                            elif not in_docstring and not stripped.startswith('#') and not stripped.startswith('import') and not stripped.startswith('from') and stripped:
                                insert_pos = i
                                break

                        lines.insert(insert_pos, import_line)

                    # Write back source
                    with open(source_path, 'w') as f:
                        f.write('\n'.join(lines))

                    source_code = '\n'.join(lines)

                except Exception as e:
                    print(f"Error extracting {func_name}: {e}")
                    continue

            changes.append(plan.source_file)

            # Close rope project
            project.close()

            return changes

        except Exception as e:
            print(f"Error performing extraction: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _generate_diff(self, worktree_path: str, changes: List[str]) -> str:
        """Generate diff of changes"""
        try:
            result = subprocess.run(
                ["git", "diff", "--", *changes],
                cwd=worktree_path,
                capture_output=True,
                text=True
            )
            return result.stdout

        except Exception as e:
            return f"Error generating diff: {e}"

    def _run_tests(self, worktree_path: str) -> str:
        """Run test suite in worktree"""
        try:
            # Try to run pytest
            result = subprocess.run(
                ["pytest", "-v"],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            return f"Exit code: {result.returncode}\n\n{result.stdout}\n{result.stderr}"

        except subprocess.TimeoutExpired:
            return "Tests timed out after 60 seconds"
        except FileNotFoundError:
            return "pytest not found - skipping tests"
        except Exception as e:
            return f"Error running tests: {e}"

    def apply_refactoring(self, result: RefactoringResult) -> bool:
        """
        Apply approved refactoring to main branch

        Called after user grants permission
        """
        if not result.worktree_path or not os.path.exists(result.worktree_path):
            return False

        try:
            # Copy changed files to main repo
            for changed_file in result.changes:
                src = Path(result.worktree_path) / changed_file
                dst = self.repo_path / changed_file

                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)

            # Clean up worktree
            self.worktree_manager.remove_worktree(result.worktree_path)

            return True

        except Exception as e:
            print(f"Error applying refactoring: {e}")
            return False

    def reject_refactoring(self, result: RefactoringResult):
        """
        Reject refactoring and clean up worktree

        Called when user denies permission
        """
        if result.worktree_path:
            self.worktree_manager.remove_worktree(result.worktree_path)

    def cleanup(self):
        """Clean up all active worktrees"""
        self.worktree_manager.cleanup_all()
