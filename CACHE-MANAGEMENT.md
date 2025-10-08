# OpenCLI Cache Management

## The Problem

Python creates `.pyc` bytecode cache files to speed up module loading. However, when you update OpenCLI code (via git pull, editing files, etc.), the cached `.pyc` files can become **stale** - meaning they're older than the source `.py` files.

This causes:
- ❌ "Unknown slash command" errors for newly added commands
- ❌ Old behavior even after updating code
- ❌ Outdated function implementations running instead of new code

## Solutions

### Quick Fix: Use `/reload` Command

**In a running OpenCLI session:**

```
/reload
```

This will:
1. Check for stale cache (shows which modules are outdated)
2. Clear all `.pyc` files and `__pycache__` directories
3. Hot-reload all OpenCLI modules
4. Apply changes WITHOUT restarting the CLI

**Example output:**
```
▸ Reloading OpenCLI modules...

! Found 3 modules with stale cache
  modules.command_registry (source 120s newer)
  modules.async_interactive (source 45s newer)
  modules.simple_tui (source 30s newer)

Clearing Python bytecode cache...
✓ Removed 47 .pyc files, 12 __pycache__ dirs

Reloading modules...
✓ Reloaded 23 modules successfully

Modules reloaded. Changes to command handlers, utilities, etc. are now active.
```

### Solution 1: Development Mode (Recommended for Contributors)

Run OpenCLI in development mode to **prevent .pyc creation entirely**:

```bash
# Option A: Use the dev-mode script
./dev-mode.sh

# Option B: Set environment variable
export OPENCLI_DEV=1
python opencli.py
```

**Benefits:**
- ✓ No `.pyc` files created
- ✓ Always runs latest code
- ✓ No cache issues
- ✓ Auto-clears old cache on startup

**When to use:** Active development, testing new features, debugging

### Solution 2: Manual Cache Clear

**Before starting OpenCLI:**

```bash
# From opencli directory
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
```

**Or use the convenience script:**

```bash
./dev-mode.sh  # Clears cache and runs in dev mode
```

### Solution 3: Startup Warning (Automatic)

OpenCLI now **automatically detects** stale cache on startup and warns you:

```
⚠️  WARNING: Found 3 modules with stale bytecode cache
   Your .pyc files are older than source files.
   This can cause 'Unknown command' errors or outdated behavior.

   Recommended: Type '/reload' in the CLI to fix this
   Or run: find ~/opencli -name '*.pyc' -delete
```

Just type `/reload` when you see this.

## How Cache Works

### Normal Python Caching

1. Python compiles `.py` → `.pyc` (bytecode)
2. `.pyc` stored in `__pycache__/` directory
3. Next run uses `.pyc` for faster loading
4. Python checks timestamps - if `.py` newer, recompiles

### The Problem with OpenCLI

OpenCLI uses dynamic imports and module reloading, which can bypass Python's normal timestamp checks. This means:

- Git pull updates `.py` files
- Python still loads old `.pyc` files
- New commands/features don't work

### The Fix

Our cache manager:
- **Detects** stale cache by comparing source vs bytecode timestamps
- **Clears** old `.pyc` files
- **Reloads** modules using `importlib.reload()`
- **Prevents** cache creation in dev mode

## Cache Manager API

### Python API

```python
from modules.cache_manager import get_cache_manager

manager = get_cache_manager()

# Check for stale cache
stale = manager.find_all_stale_cache()
for s in stale:
    print(f"{s['module']}: {s['age_seconds']}s stale")

# Clear cache
result = manager.clear_cache(verbose=True)
print(f"Removed {result['pyc_files']} files")

# Reload modules
reload_result = manager.reload_modules()
print(f"Reloaded {reload_result['count']} modules")

# Enable dev mode
manager.enable_dev_mode()  # Prevents .pyc creation
```

### Command Line

```bash
# In OpenCLI session
/reload                    # Hot-reload everything

# In terminal
./dev-mode.sh             # Run in dev mode (no cache)
export OPENCLI_DEV=1      # Set dev mode env var
python opencli.py

# Manual cleanup
find ~/opencli -name "*.pyc" -delete
find ~/opencli -type d -name __pycache__ -exec rm -rf {} +
```

## Best Practices

### For Contributors

1. **Always use dev mode** during active development:
   ```bash
   export OPENCLI_DEV=1
   # Add to ~/.bashrc or ~/.zshrc
   ```

2. **Run /reload** after git pull:
   ```
   git pull
   # In running OpenCLI session:
   /reload
   ```

3. **Clear cache** before reporting bugs:
   ```bash
   ./dev-mode.sh
   ```

### For Users

1. **Use /reload** if commands don't work after update:
   ```
   /reload
   ```

2. **Watch for startup warnings** about stale cache

3. **Restart OpenCLI** after major updates:
   ```bash
   exit
   python opencli.py
   ```

## Troubleshooting

### "Unknown slash command: local"

**Cause:** Stale cache - `command_registry.py` cache is old

**Fix:**
```
/reload
```

### New features don't work after git pull

**Cause:** `.pyc` files from before the update

**Fix:**
```bash
find ~/opencli -name "*.pyc" -delete
python opencli.py
```

### /reload shows errors

**Cause:** Some modules can't be hot-reloaded

**Fix:** Restart OpenCLI completely:
```bash
exit
python opencli.py
```

### Modules still outdated after /reload

**Cause:** Deep dependency issues

**Fix:** Full restart in dev mode:
```bash
./dev-mode.sh
```

## Technical Details

### Cache Location

```
opencli/
├── modules/
│   ├── __pycache__/          ← Bytecode cache
│   │   ├── async_interactive.cpython-311.pyc
│   │   ├── command_registry.cpython-311.pyc
│   │   └── ...
│   ├── async_interactive.py   ← Source
│   └── command_registry.py    ← Source
```

### Timestamp Checking

```python
# Cache manager checks:
source_mtime = Path("async_interactive.py").stat().st_mtime
pyc_mtime = Path("__pycache__/async_interactive.cpython-311.pyc").stat().st_mtime

if source_mtime > pyc_mtime:
    print("STALE - source is newer!")
```

### Module Reloading

```python
import importlib
import sys

# Reload a module
module = sys.modules['modules.async_interactive']
importlib.reload(module)
```

### Dev Mode

```python
# Prevent .pyc creation
import sys
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
```

## Related Files

- `modules/cache_manager.py` - Cache management utilities
- `opencli.py` - Startup cache check (lines 1976-1990)
- `modules/async_interactive.py` - `/reload` command (lines 1319-1359)
- `dev-mode.sh` - Development mode launcher
- `modules/command_registry.py` - Command registration

## FAQ

**Q: Should I always use dev mode?**
A: Only when developing. Normal users don't need it.

**Q: Does /reload work for all changes?**
A: Yes, but some deep changes may require full restart.

**Q: Will this delete my data?**
A: No - only removes `.pyc` cache files, not user data.

**Q: Why not just disable caching permanently?**
A: Cache improves startup performance. Dev mode only needed when editing code.

**Q: What if /reload is slow?**
A: It reloads ~20-30 modules. Takes 1-2 seconds. Faster than full restart.
