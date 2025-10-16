# IMPORT PATH FIX - cli.modules.async_interactive

## The Problem

**Error**: `No module named 'cli.modules.async_interactive.streaming'`

### Root Cause

The issue was a **sys.path conflict** caused by the modular CLI refactoring:

1. **opencli.py** (launcher) adds TWO directories to sys.path:
   ```python
   # Line 23-24: Add root directory
   sys.path.insert(0, str(ROOT_DIR))  # /Users/xxx/.opencli

   # Line 27-28: Add CLI directory
   sys.path.insert(0, str(CLI_DIR))   # /Users/xxx/.opencli/cli
   ```

2. **cli/modules/initialization.py** line 41 had:
   ```python
   from modules.async_interactive import interactive_async, run_interactive_async
   ```

3. **Python's import resolution**:
   - With CLI_DIR in sys.path FIRST (inserted at index 0)
   - Python tries to resolve `modules.async_interactive` relative to CLI_DIR
   - Looks for: `cli/modules/async_interactive/` (doesn't exist!)
   - Should look for: `modules/async_interactive/` (at root level)

### Why This Happened

The modular refactor created TWO `modules/` directories:
- `/Users/xxx/.opencli/modules/` - **Root-level modules** (contains async_interactive, tui, etc.)
- `/Users/xxx/.opencli/cli/modules/` - **CLI-specific modules** (contains initialization, execution_flow, etc.)

When `cli/modules/initialization.py` tries to import from `modules.async_interactive`, Python first checks `cli/modules/async_interactive` (because CLI_DIR is in sys.path first), which doesn't exist.

## The Fix

Updated **cli/modules/initialization.py** line 34-61 to explicitly ensure the root directory is in sys.path BEFORE importing:

```python
def initialize_async_tui(self) -> bool:
    """Initialize async TUI system with fallback detection

    Returns:
        True if TUI is available, False if fallback needed
    """
    try:
        # CRITICAL: Import from root-level modules, not cli/modules
        # sys.path has both ROOT_DIR and CLI_DIR, so we need absolute import
        import sys
        from pathlib import Path

        # Get root opencli directory (parent of cli/)
        root_dir = Path(__file__).parent.parent.parent
        if str(root_dir) not in sys.path:
            sys.path.insert(0, str(root_dir))

        from modules.async_interactive import interactive_async, run_interactive_async
        self.features['ASYNC_TUI'] = True
        self.initialized_components['async_tui'] = {
            'interactive_async': interactive_async,
            'run_interactive_async': run_interactive_async
        }
        return True
    except ImportError as e:
        self.features['ASYNC_TUI'] = False
        print(f"\033[2mTUI not available, using fallback mode: {e}\033[0m")
        return False
```

### What Changed

1. **Explicitly get root directory**: `Path(__file__).parent.parent.parent`
   - `__file__` = `/Users/xxx/.opencli/cli/modules/initialization.py`
   - `.parent` = `/Users/xxx/.opencli/cli/modules/`
   - `.parent.parent` = `/Users/xxx/.opencli/cli/`
   - `.parent.parent.parent` = `/Users/xxx/.opencli/` ✓

2. **Ensure root in sys.path first**: `sys.path.insert(0, str(root_dir))`
   - This guarantees `modules.async_interactive` resolves to root-level modules

3. **Import proceeds as before**: `from modules.async_interactive import ...`

## Files Changed

1. `/Users/dezmondhollins/opencli/cli/modules/initialization.py`
   - Lines 34-61: Updated `initialize_async_tui()` method

2. Cleared all Python caches:
   ```bash
   find /Users/dezmondhollins/.opencli -type d -name "__pycache__" -exec rm -rf {} +
   find /Users/dezmondhollins/.opencli -name "*.pyc" -delete
   find /Users/dezmondhollins/opencli -type d -name "__pycache__" -exec rm -rf {} +
   find /Users/dezmondhollins/opencli -name "*.pyc" -delete
   ```

## Directory Structure

```
/Users/xxx/.opencli/
├── opencli.py                  # Launcher (adds both paths to sys.path)
├── modules/                    # ROOT-LEVEL MODULES
│   ├── async_interactive/      # ← This is what we need to import
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── streaming.py        # ← The file that caused the error
│   │   └── ...
│   ├── tui/
│   └── ...
└── cli/                        # CLI DIRECTORY
    ├── main.py
    ├── modules/                # CLI-SPECIFIC MODULES
    │   ├── initialization.py   # ← This file needed the fix
    │   ├── execution_flow.py
    │   └── ...
    └── ...
```

## Test Now

```bash
opencli tui
```

Should launch without the import error!

## Similar Issues

If you see other import errors like:
- `No module named 'cli.modules.X'` where X is a root-level module
- Follow the same pattern: explicitly add root_dir to sys.path before importing

## Prevention

For future imports in `cli/modules/` that need root-level modules:
1. Always explicitly ensure root directory is in sys.path first
2. Or use fully qualified imports with the root directory name
3. Or restructure to avoid having two `modules/` directories
