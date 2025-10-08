"""
Automatic Refactoring with File Watching
Monitors Python files and triggers refactoring when they exceed size limits
"""

import os
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from .code_analyzer import CodeAnalyzer, FunctionCluster
from .refactor_executor import RefactoringExecutor, RefactoringPlan, RefactoringResult


@dataclass
class AutoRefactorConfig:
    """Configuration for auto-refactoring"""
    max_file_lines: int = 500
    min_cluster_size: int = 3
    min_cluster_lines: int = 100
    watch_paths: List[str] = None
    exclude_patterns: List[str] = None
    enabled: bool = False

    def __post_init__(self):
        if self.watch_paths is None:
            self.watch_paths = ['modules/', 'agents/']
        if self.exclude_patterns is None:
            self.exclude_patterns = ['__pycache__', '.git', 'test_', 'venv', 'node_modules']


class RefactoringFileHandler(FileSystemEventHandler):
    """Handles file system events for auto-refactoring"""

    def __init__(self, config: AutoRefactorConfig, on_refactor_needed: Callable):
        self.config = config
        self.on_refactor_needed = on_refactor_needed
        self._cooldown: Dict[str, float] = {}  # Prevent duplicate triggers
        self._cooldown_seconds = 5.0

    def on_modified(self, event):
        """Called when a file is modified"""
        if event.is_directory:
            return

        if not event.src_path.endswith('.py'):
            return

        # Check exclude patterns
        for pattern in self.config.exclude_patterns:
            if pattern in event.src_path:
                return

        # Check cooldown to prevent duplicate triggers
        now = time.time()
        if event.src_path in self._cooldown:
            if now - self._cooldown[event.src_path] < self._cooldown_seconds:
                return

        self._cooldown[event.src_path] = now

        # Check file size
        try:
            with open(event.src_path, 'r') as f:
                line_count = sum(1 for _ in f)

            if line_count > self.config.max_file_lines:
                self.on_refactor_needed(event.src_path, line_count)

        except Exception as e:
            print(f"Error checking file {event.src_path}: {e}")


class AutoRefactorManager:
    """Manages automatic refactoring with file watching"""

    def __init__(self, repo_path: str = ".", permission_handler=None):
        self.repo_path = Path(repo_path).resolve()
        self.config = AutoRefactorConfig()
        self.executor = RefactoringExecutor(repo_path)
        self.permission_handler = permission_handler  # AsyncPermissionHandler instance

        self.observer: Optional[Observer] = None
        self.is_running = False
        self._refactor_thread: Optional[threading.Thread] = None
        self._refactor_queue: List[tuple] = []
        self._queue_lock = threading.Lock()

    def start(self, config: Optional[AutoRefactorConfig] = None):
        """Start file watching and auto-refactoring"""
        if self.is_running:
            return {"status": "already_running"}

        if config:
            self.config = config

        self.config.enabled = True

        # Set up file watcher
        event_handler = RefactoringFileHandler(
            self.config,
            self._on_refactor_needed
        )

        self.observer = Observer()

        # Watch each configured path
        for watch_path in self.config.watch_paths:
            full_path = self.repo_path / watch_path
            if full_path.exists():
                self.observer.schedule(event_handler, str(full_path), recursive=True)

        self.observer.start()

        # Start refactoring worker thread
        self._refactor_thread = threading.Thread(target=self._refactor_worker, daemon=True)
        self._refactor_thread.start()

        self.is_running = True

        return {
            "status": "started",
            "watching": [str(self.repo_path / p) for p in self.config.watch_paths],
            "max_file_lines": self.config.max_file_lines
        }

    def stop(self):
        """Stop file watching and auto-refactoring"""
        if not self.is_running:
            return {"status": "not_running"}

        self.config.enabled = False

        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=2.0)
            self.observer = None

        self.is_running = False

        return {
            "status": "stopped",
            "queued_refactorings": len(self._refactor_queue)
        }

    def status(self) -> Dict:
        """Get current status of auto-refactoring"""
        return {
            "running": self.is_running,
            "enabled": self.config.enabled,
            "watching": [str(self.repo_path / p) for p in self.config.watch_paths] if self.is_running else [],
            "max_file_lines": self.config.max_file_lines,
            "queued_refactorings": len(self._refactor_queue),
            "queue": [
                {"file": item[0], "lines": item[1]}
                for item in self._refactor_queue
            ]
        }

    def _on_refactor_needed(self, file_path: str, line_count: int):
        """Called when a file needs refactoring"""
        with self._queue_lock:
            # Check if already in queue
            if any(item[0] == file_path for item in self._refactor_queue):
                return

            self._refactor_queue.append((file_path, line_count))

    def _refactor_worker(self):
        """Worker thread that processes refactoring queue"""
        while self.config.enabled:
            # Get next item from queue
            item = None
            with self._queue_lock:
                if self._refactor_queue:
                    item = self._refactor_queue.pop(0)

            if item:
                file_path, line_count = item
                self._process_refactoring(file_path, line_count)

            time.sleep(1.0)  # Check queue every second

    def _process_refactoring(self, file_path: str, line_count: int):
        """Process a file that needs refactoring"""
        try:
            # Analyze file for clusters
            analyzer = CodeAnalyzer(file_path)
            if not analyzer.analyze():
                print(f"Failed to analyze {file_path}")
                return

            clusters = analyzer.identify_clusters(
                min_cluster_size=self.config.min_cluster_size,
                min_lines=self.config.min_cluster_lines
            )

            if not clusters:
                print(f"No suitable clusters found in {file_path}")
                return

            # Take the best cluster
            best_cluster = clusters[0]

            # Create refactoring plan
            source_file = str(Path(file_path).relative_to(self.repo_path))
            target_file = str(Path(source_file).parent / f"{best_cluster.suggested_module_name}.py")

            plan = RefactoringPlan(
                action="extract_module",
                source_file=source_file,
                target_file=target_file,
                functions_to_move=best_cluster.functions,
                estimated_lines=best_cluster.total_lines,
                rationale=best_cluster.rationale
            )

            # Execute refactoring in worktree sandbox
            result = self.executor.execute_extraction(plan)

            if not result.success:
                print(f"Refactoring failed: {result.error}")
                return

            # Request permission via permission handler
            if self.permission_handler:
                # Convert plan to dict for permission template
                plan_dict = {
                    'source_file': plan.source_file,
                    'target_file': plan.target_file,
                    'functions_to_move': plan.functions_to_move,
                    'estimated_lines': plan.estimated_lines,
                    'rationale': plan.rationale
                }

                result_dict = {
                    'test_results': result.test_results,
                    'changes': result.changes,
                    'diff': result.diff
                }

                # Request permission using async handler
                # This will be called from worker thread, so we need to schedule it on the event loop
                import asyncio
                try:
                    # Get the running event loop from the main thread
                    loop = asyncio.get_event_loop()

                    # Schedule the permission check on the event loop and wait for it
                    future = asyncio.run_coroutine_threadsafe(
                        self.permission_handler.check_and_prompt(
                            "Refactoring",
                            {"plan": plan_dict, "result": result_dict}
                        ),
                        loop
                    )

                    # Wait for the result with timeout
                    approved, reason = future.result(timeout=300)  # 5 minute timeout

                    if approved:
                        # Apply refactoring
                        if self.executor.apply_refactoring(result):
                            print(f"✅ Auto-refactored {source_file} -> {target_file}")
                        else:
                            print(f"❌ Failed to apply refactoring for {source_file}")
                    else:
                        # Rejected - cleanup worktree
                        self.executor.reject_refactoring(result)
                        print(f"⚠️ Refactoring rejected for {source_file}: {reason}")

                except Exception as e:
                    print(f"❌ Permission request failed: {e}")
                    self.executor.reject_refactoring(result)
            else:
                # No permission handler - just show what would be done
                print(f"\n📋 REFACTORING SUGGESTION:")
                print(f"   File: {source_file} ({line_count} lines)")
                print(f"   Extract {len(plan.functions_to_move)} functions to {target_file}")
                print(f"   Reduce by ~{plan.estimated_lines} lines")
                print(f"   Rationale: {plan.rationale}")
                print(f"\n   Use '/refactor suggest-split {source_file}' to review")

                # Cleanup worktree
                self.executor.reject_refactoring(result)

        except Exception as e:
            print(f"Error processing refactoring for {file_path}: {e}")
            import traceback
            traceback.print_exc()

    def suggest_split(self, file_path: str) -> Dict:
        """
        Analyze a file and suggest how to split it

        Returns detailed information about potential extractions
        """
        try:
            # Resolve file path
            if not Path(file_path).is_absolute():
                file_path = str(self.repo_path / file_path)

            # Analyze file
            analyzer = CodeAnalyzer(file_path)
            if not analyzer.analyze():
                return {
                    "success": False,
                    "error": f"Failed to analyze {file_path}"
                }

            # Get file stats
            stats = analyzer.get_file_stats()

            # Get clusters
            clusters = analyzer.identify_clusters(
                min_cluster_size=self.config.min_cluster_size,
                min_lines=self.config.min_cluster_lines
            )

            return {
                "success": True,
                "file": file_path,
                "stats": stats,
                "clusters": [
                    {
                        "functions": cluster.functions,
                        "cohesion": cluster.cohesion_score,
                        "coupling": cluster.coupling_score,
                        "lines": cluster.total_lines,
                        "suggested_name": cluster.suggested_module_name,
                        "rationale": cluster.rationale
                    }
                    for cluster in clusters
                ]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def cleanup(self):
        """Clean up resources"""
        self.stop()
        self.executor.cleanup()


# Global instance
_auto_refactor_manager: Optional[AutoRefactorManager] = None


def get_auto_refactor_manager() -> AutoRefactorManager:
    """Get or create global auto-refactor manager instance"""
    global _auto_refactor_manager
    if _auto_refactor_manager is None:
        _auto_refactor_manager = AutoRefactorManager()
    return _auto_refactor_manager
