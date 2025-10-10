# SDK Enforcement System

**Automatic validation and conversion of handlers at registration time**

## 🛡️ What It Does

The SDK Enforcement system **automatically validates every handler** when it's registered and:

1. ✅ **ACCEPTS** compliant handlers (use as-is)
2. ⚠️ **CONVERTS** handlers with minor issues (auto-wrap to add **context)
3. ✗ **REJECTS** handlers that violate SDK (cannot be fixed)

**Result:** No module can load unless it complies with the SDK!

## 📋 Enforcement Rules

### ✅ COMPLIANT Handler
```python
async def my_handler(app, session, **context):
    """Perfect! Will be accepted"""
    app.write("Doing work...\n")
    return "result"
```

### ⚠️ AUTO-CONVERTED Handler
```python
async def old_handler(app, session):  # Missing **context
    """Will be auto-wrapped to add **context"""
    app.write("This still works!\n")

# Enforcement wraps it:
async def wrapped(app, session, **context):
    return await old_handler(app, session)
```

### ✗ REJECTED Handler
```python
def sync_handler(app, session):  # Not async!
    """REJECTED - cannot convert sync to async"""
    pass

async def wrong_sig(foo, bar):  # Wrong params!
    """REJECTED - must be (app, session, **context)"""
    pass
```

## 🚀 Startup Buffer Display

When you start OpenCLI and type first command, you'll see:

```
┌─────────────────────────────────────────────────────────┐
│ 🚀 OpenCLI Startup - Module Registration               │
│                                                         │
│ Registration Summary                                    │
│ Commands: 17 | Tools: 8                                │
│                                                         │
│ SDK Enforcement                                         │
│ ✓ Compliant: 24 | ⚠ Converted: 1 | ✗ Rejected: 0      │
│                                                         │
│ Modules by Category                                    │
│                                                         │
│ ▸ DOCKER (3)                                           │
│   ✓ /docker ollama setup                              │
│   ✓ /docker ollama start                              │
│   ✓ /docker ollama stop                               │
│                                                         │
│ ▸ DEV (3)                                              │
│   ✓ /debug                                             │
│   ✓ /performance                                       │
│   ⚠ /reload (auto-fixed)                              │
│                                                         │
│ ▸ FILE (3)                                             │
│   ✓ Read                                               │
│   ✓ Write                                              │
│   ✓ Edit                                               │
│   ... and 15 more                                      │
│                                                         │
│ [Auto-closes in 4s or press Enter]                     │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Shows in **permission buffer** (non-blocking dropdown)
- Categorizes by module type (DOCKER, DEV, FILE, etc.)
- Shows status: ✓ ⚠ ✗
- Auto-dismisses after 4 seconds
- User can press Enter to dismiss early

## 🔧 How It Works

### Registration Flow

```
Handler → enforce_handler() → Validate → Convert if needed → Register
                                ↓
                        ✓ ACCEPT
                        ⚠ CONVERT (wrap)
                        ✗ REJECT (raise ValueError)
```

### Code Flow

1. **Handler defined:**
   ```python
   async def my_command(app, session, **context):
       pass
   ```

2. **Registration in `commands/registry.py`:**
   ```python
   _safe_register(
       executor,
       ExecutionType.COMMAND,
       '/mycommand',
       my_command,
       ExecutionCategory.SYSTEM,
       RiskLevel.MEDIUM,
       requires_approval=True,
       description="My command"
   )
   ```

3. **`_safe_register()` enforces SDK:**
   ```python
   # Validate handler
   result = enforce_handler(name, handler, category)

   # Use converted/wrapped handler if needed
   final_handler = result.final_handler

   # Register (or raise ValueError if rejected)
   executor.registry.register(...)
   ```

4. **On first command, startup buffer shows results**

## 📊 Enforcement Actions

### ACCEPTED
- Handler is already compliant
- No changes needed
- Used as-is

### CONVERTED
- Handler missing **context parameter
- Automatically wrapped:
  ```python
  async def wrapper(app, session, **context):
      return await original_handler(app, session)
  ```
- Preserves original functionality
- Adds SDK compliance

### REJECTED
- Handler cannot be auto-fixed
- Not async (must rewrite)
- Wrong signature (must rewrite)
- Raises `ValueError` with details
- **Module will not load!**

## 🎯 Terminal Output

When enforcement runs, you'll see in terminal:

```
[CommandRouter] SDK Enforcement Complete:
  Commands: 17 | Tools: 8
  ✓ Accepted: 24
  ⚠ Converted: 1
  ✗ Rejected: 0
```

If any handlers are rejected:
```
[CommandRouter] SDK Violation: /badcommand - Handler must be async
Traceback...
ValueError: SDK Violation: /badcommand
```

**Application will not start with violations!**

## 🔍 Files

- `sdk/enforcement.py` - Main enforcement engine
- `sdk/startup_buffer.py` - Startup buffer display
- `commands/registry.py` - Uses `_safe_register()` for all registrations
- `command_router.py` - Shows startup buffer on first command

## 🚦 Violation Handling

### Block on Violations (Optional)
```python
await show_startup_status(
    app,
    executor,
    block_on_violations=True  # Wait for user decision
)
```

Shows blocking prompt:
```
┌─────────────────────────────────────────────────────────┐
│ ⚠ OpenCLI Startup - Enforcement Violations             │
│                                                         │
│ ... status ...                                          │
│                                                         │
│ ⚠ WARNING: Some modules failed to load!                │
│ Check enforcement report above for details.             │
│                                                         │
│ Press Enter to continue                                 │
│                                                         │
│ > Continue anyway                                       │
│   Exit and fix violations                               │
└─────────────────────────────────────────────────────────┘
```

## ✅ Benefits

1. **No Silent Failures** - Violations caught at load time
2. **Auto-Conversion** - Compatible handlers auto-upgraded
3. **Clear Feedback** - Visual buffer shows what loaded
4. **Categorized Display** - See modules by type
5. **Non-Blocking** - Auto-dismisses, doesn't slow startup
6. **Terminal + Buffer** - Info in both places

---

**The SDK enforcement ensures EVERY handler is compliant before it can run!**
