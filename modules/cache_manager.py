"""
Cache Manager - Handle Python bytecode cache for OpenCLI

Provides utilities to clear .pyc files and reload modules during development.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Optional
import importlib


class CacheManager:
    """Manage Python bytecode cache for development workflow"""

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize cache manager

        Args:
            base_dir: Base directory to manage (defaults to opencli dir)
        """
        if base_dir is None:
            # Auto-detect opencli directory
            base_dir = Path(__file__).parent.parent

        self.base_dir = Path(base_dir)

    def clear_cache(self, verbose: bool = False) -> dict:
        """
        Clear all .pyc files and __pycache__ directories

        Args:
            verbose: Print detailed information

        Returns:
            dict with counts of files/dirs removed
        """
        pyc_files = []
        pycache_dirs = []

        # Find all .pyc files
        for pyc in self.base_dir.rglob("*.pyc"):
            try:
                pyc.unlink()
                pyc_files.append(str(pyc))
                if verbose:
                    print(f"  Removed: {pyc.relative_to(self.base_dir)}")
            except Exception as e:
                if verbose:
                    print(f"  Failed to remove {pyc}: {e}")

        # Find all __pycache__ directories
        for pycache in self.base_dir.rglob("__pycache__"):
            try:
                shutil.rmtree(pycache)
                pycache_dirs.append(str(pycache))
                if verbose:
                    print(f"  Removed: {pycache.relative_to(self.base_dir)}/")
            except Exception as e:
                if verbose:
                    print(f"  Failed to remove {pycache}: {e}")

        return {
            "pyc_files": len(pyc_files),
            "pycache_dirs": len(pycache_dirs),
            "files": pyc_files,
            "dirs": pycache_dirs
        }

    def reload_modules(self, module_patterns: Optional[List[str]] = None) -> dict:
        """
        Reload Python modules that match patterns

        Args:
            module_patterns: List of module name patterns to reload
                            (e.g., ['modules.async_interactive', 'modules.command_registry'])
                            If None, reloads all opencli modules

        Returns:
            dict with reloaded modules and any errors
        """
        reloaded = []
        errors = []

        if module_patterns is None:
            # Reload all modules that start with 'modules.'
            module_patterns = []
            for name in list(sys.modules.keys()):
                if name.startswith('modules.') or name == 'opencli':
                    module_patterns.append(name)

        for pattern in module_patterns:
            # Handle both exact matches and wildcards
            matching_modules = [
                name for name in sys.modules.keys()
                if name == pattern or name.startswith(f"{pattern}.")
            ]

            for module_name in matching_modules:
                try:
                    module = sys.modules[module_name]
                    importlib.reload(module)
                    reloaded.append(module_name)
                except Exception as e:
                    errors.append({
                        "module": module_name,
                        "error": str(e)
                    })

        return {
            "reloaded": reloaded,
            "count": len(reloaded),
            "errors": errors
        }

    def check_stale_cache(self, module_name: str) -> Optional[dict]:
        """
        Check if a module's .pyc file is stale (older than .py source)

        Args:
            module_name: Module name to check

        Returns:
            dict with staleness info, or None if not stale
        """
        if module_name not in sys.modules:
            return None

        module = sys.modules[module_name]

        # Get source file path
        if not hasattr(module, '__file__') or module.__file__ is None:
            return None

        source_file = Path(module.__file__)

        # Find corresponding .pyc file
        if source_file.suffix == '.py':
            # Check __pycache__ directory
            pycache_dir = source_file.parent / '__pycache__'
            pyc_pattern = f"{source_file.stem}.cpython-*.pyc"
            pyc_files = list(pycache_dir.glob(pyc_pattern))

            if pyc_files:
                pyc_file = pyc_files[0]
                source_mtime = source_file.stat().st_mtime
                pyc_mtime = pyc_file.stat().st_mtime

                if source_mtime > pyc_mtime:
                    return {
                        "module": module_name,
                        "source": str(source_file),
                        "pyc": str(pyc_file),
                        "source_mtime": source_mtime,
                        "pyc_mtime": pyc_mtime,
                        "age_seconds": source_mtime - pyc_mtime
                    }

        return None

    def find_all_stale_cache(self) -> List[dict]:
        """
        Find all modules with stale .pyc cache

        Returns:
            List of stale module info dicts
        """
        stale = []

        for module_name in list(sys.modules.keys()):
            if module_name.startswith('modules.') or module_name == 'opencli':
                stale_info = self.check_stale_cache(module_name)
                if stale_info:
                    stale.append(stale_info)

        return stale

    def enable_dev_mode(self):
        """
        Enable development mode - prevents .pyc creation

        Sets PYTHONDONTWRITEBYTECODE environment variable
        """
        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
        sys.dont_write_bytecode = True

    def disable_dev_mode(self):
        """
        Disable development mode - allows .pyc creation
        """
        if 'PYTHONDONTWRITEBYTECODE' in os.environ:
            del os.environ['PYTHONDONTWRITEBYTECODE']
        sys.dont_write_bytecode = False


def get_cache_manager() -> CacheManager:
    """Get singleton cache manager instance"""
    if not hasattr(get_cache_manager, '_instance'):
        get_cache_manager._instance = CacheManager()
    return get_cache_manager._instance


def clear_opencli_cache(verbose: bool = False) -> dict:
    """
    Convenience function to clear OpenCLI cache

    Args:
        verbose: Print detailed information

    Returns:
        dict with cleanup results
    """
    manager = get_cache_manager()
    return manager.clear_cache(verbose=verbose)
