#!/usr/bin/env python3
"""
Auto-Reload System - Automatically reload modules when files change
Monitors opencli modules and triggers hot reload without requiring TUI restart
"""

import sys
import time
import threading
from pathlib import Path
from typing import Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class AutoReloadHandler(FileSystemEventHandler):
    """Monitor file changes and trigger automatic reloads"""

    def __init__(self, reload_callback: Callable[[str], None]):
        """
        Args:
            reload_callback: Function to call when reload needed (receives file path)
        """
        self.reload_callback = reload_callback
        self.pending_reloads = set()
        self.reload_lock = threading.Lock()
        self.reload_timer = None
        self.debounce_seconds = 0.5  # Wait 0.5s after last change before reloading

        sys.stderr.write("[AutoReload] 🔄 Auto-reload system initialized\n")
        sys.stderr.flush()

    def on_modified(self, event):
        """File modified event"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only reload for Python source files
        if not file_path.name.endswith('.py'):
            return

        # Ignore __pycache__ and .pyc files
        if '__pycache__' in file_path.parts or file_path.name.endswith('.pyc'):
            return

        sys.stderr.write(f"\n[AutoReload] 📝 File changed: {file_path.name}\n")
        sys.stderr.flush()

        with self.reload_lock:
            self.pending_reloads.add(str(file_path))

            # Cancel existing timer
            if self.reload_timer:
                self.reload_timer.cancel()

            # Start new debounce timer
            self.reload_timer = threading.Timer(
                self.debounce_seconds,
                self._trigger_reload
            )
            self.reload_timer.start()

    def _trigger_reload(self):
        """Execute reload after debounce period"""
        with self.reload_lock:
            if not self.pending_reloads:
                return

            changed_files = list(self.pending_reloads)
            self.pending_reloads.clear()

        sys.stderr.write(f"\n[AutoReload] 🔄 Triggering reload for {len(changed_files)} file(s)\n")
        sys.stderr.flush()

        # Call the reload callback
        for file_path in changed_files:
            try:
                self.reload_callback(file_path)
            except Exception as e:
                sys.stderr.write(f"[AutoReload] ❌ Reload error: {e}\n")
                sys.stderr.flush()


class AutoReloadSystem:
    """Manages automatic module reloading based on file changes"""

    def __init__(self, app=None):
        """
        Args:
            app: TUI app instance (for displaying reload notifications)
        """
        self.app = app
        self.observer: Optional[Observer] = None
        self.handler: Optional[AutoReloadHandler] = None
        self.enabled = False

        # Paths to watch
        self.watch_paths = [
            Path.home() / '.opencli' / 'modules',
            Path.home() / '.opencli' / 'cli' / 'modules',
            Path.cwd() / 'modules',  # Development path
        ]

        sys.stderr.write("[AutoReloadSystem] 🎯 Auto-reload system created\n")
        sys.stderr.flush()

    def start(self):
        """Start watching for file changes"""
        if self.enabled:
            sys.stderr.write("[AutoReloadSystem] ⚠️ Already running\n")
            sys.stderr.flush()
            return

        sys.stderr.write("[AutoReloadSystem] 🚀 Starting auto-reload watcher...\n")
        sys.stderr.flush()

        # Create handler with reload callback
        self.handler = AutoReloadHandler(self._reload_modules)
        self.observer = Observer()

        # Schedule watchers for existing paths
        watched_count = 0
        for path in self.watch_paths:
            if path.exists():
                self.observer.schedule(self.handler, str(path), recursive=True)
                watched_count += 1
                sys.stderr.write(f"[AutoReloadSystem]   ✓ Watching: {path}\n")
                sys.stderr.flush()

        if watched_count == 0:
            sys.stderr.write("[AutoReloadSystem] ❌ No valid paths to watch!\n")
            sys.stderr.flush()
            return

        self.observer.start()
        self.enabled = True

        sys.stderr.write(f"[AutoReloadSystem] ✅ Auto-reload active ({watched_count} paths)\n")
        sys.stderr.flush()

        # Notify user if TUI available
        if self.app and hasattr(self.app, 'write'):
            self.app.write("\n[dim]🔄 Auto-reload enabled - modules will hot-reload on file changes[/dim]\n")

    def stop(self):
        """Stop watching for file changes"""
        if not self.enabled:
            return

        sys.stderr.write("[AutoReloadSystem] 🛑 Stopping auto-reload watcher...\n")
        sys.stderr.flush()

        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=2)

        self.enabled = False
        sys.stderr.write("[AutoReloadSystem] ✅ Auto-reload stopped\n")
        sys.stderr.flush()

    def _reload_modules(self, file_path: str):
        """Reload modules when file changes detected"""
        sys.stderr.write(f"\n[AutoReloadSystem._reload_modules] 🔥 RELOADING for: {file_path}\n")
        sys.stderr.flush()

        try:
            # Import cache manager
            try:
                from cache_manager import get_cache_manager
            except ImportError:
                from modules.cache_manager import get_cache_manager

            manager = get_cache_manager()

            # Determine which modules to reload based on file path
            file_path_obj = Path(file_path)
            module_patterns = self._get_module_patterns(file_path_obj)

            sys.stderr.write(f"[AutoReloadSystem] Reloading patterns: {module_patterns}\n")
            sys.stderr.flush()

            # Clear cache and reload
            manager.clear_cache(verbose=False)
            result = manager.reload_modules(module_patterns)

            sys.stderr.write(f"[AutoReloadSystem] ✅ Reloaded {result['count']} modules\n")
            sys.stderr.flush()

            # Show errors if any
            if result['errors']:
                for err in result['errors'][:3]:
                    sys.stderr.write(f"[AutoReloadSystem]   ❌ {err['module']}: {err['error']}\n")
                    sys.stderr.flush()

            # Notify user if TUI available
            if self.app and hasattr(self.app, 'write'):
                file_name = file_path_obj.name
                self.app.write(f"\n[dim]🔄 Auto-reloaded: {file_name} ({result['count']} modules)[/dim]\n")

        except Exception as e:
            sys.stderr.write(f"[AutoReloadSystem] ❌ Reload failed: {e}\n")
            import traceback
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()

    def _get_module_patterns(self, file_path: Path) -> list:
        """Determine which module patterns to reload based on changed file"""
        patterns = []

        # Extract module path from file path
        # e.g., /Users/.../opencli/modules/input_widget/widget.py -> modules.input_widget.widget

        try:
            parts = file_path.parts

            # Find 'modules' in path
            if 'modules' in parts:
                modules_idx = parts.index('modules')
                module_parts = parts[modules_idx:]

                # Remove .py extension
                module_parts = list(module_parts)
                module_parts[-1] = module_parts[-1].replace('.py', '')

                # Build module pattern
                module_pattern = '.'.join(module_parts)
                patterns.append(module_pattern)

                # Also add parent module pattern for submodules
                # e.g., modules.input_widget.widget -> also reload modules.input_widget
                if len(module_parts) > 2:
                    parent_pattern = '.'.join(module_parts[:-1])
                    patterns.append(parent_pattern)

                sys.stderr.write(f"[AutoReloadSystem] Module patterns: {patterns}\n")
                sys.stderr.flush()

        except Exception as e:
            sys.stderr.write(f"[AutoReloadSystem] ⚠️ Could not determine module pattern: {e}\n")
            sys.stderr.flush()
            # Fallback: reload all modules
            patterns = None

        return patterns


# Global auto-reload instance
_auto_reload_system: Optional[AutoReloadSystem] = None


def get_auto_reload_system(app=None) -> AutoReloadSystem:
    """Get or create the global auto-reload system"""
    global _auto_reload_system

    if _auto_reload_system is None:
        _auto_reload_system = AutoReloadSystem(app)
    elif app is not None and _auto_reload_system.app is None:
        # Update app reference if provided
        _auto_reload_system.app = app

    return _auto_reload_system


def enable_auto_reload(app=None):
    """Enable automatic module reloading"""
    system = get_auto_reload_system(app)
    system.start()


def disable_auto_reload():
    """Disable automatic module reloading"""
    system = get_auto_reload_system()
    system.stop()
