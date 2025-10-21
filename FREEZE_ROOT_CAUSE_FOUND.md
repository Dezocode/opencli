# Permission Buffer Freeze - ROOT CAUSE IDENTIFIED

## The Problem

Commands freeze instead of showing the permission buffer because there are **TWO SEPARATE permission manager instances** that aren't communicating with each other.

## The Disconnect

### Instance 1: ExecutionSystem's PermissionManager
**Location**: `modules/execution/executor.py:102`
```python
class ExecutionSystem:
    def __init__(self, app, session):
        self.permission_manager = PermissionManager()  # ← Creates its own instance
```

**What it does**:
- Handles permission checks when commands execute
- Calls `buffer_manager.request_permission()`
- Creates an `asyncio.Future()` and waits for it to resolve
- **This is the one that FREEZES** waiting for the Future

### Instance 2: TUI's UnifiedPermissionManager
**Location**: `modules/tui/core.py:225`
```python
class OpenCLITUI:
    def _setup_permission_system(self):
        self.permission_manager = get_unified_permission_manager()  # ← Different instance!
        self.permission_manager.set_ui_callback(self._show_permission_prompt)
        self.permission_manager.register_response_handler(...)
```

**What it does**:
- Receives permission responses from user interactions
- Calls `handle_permission_response()` when user selects an option
- **This is where responses GO** but ExecutionSystem never sees them!

## The Freeze Flow

```
User types /help
    ↓
ExecutionSystem.execute() calls executor.permission_manager.check_permission()
    ↓
executor.permission_manager._show_permission_prompt()
    ↓
buffer_manager.request_permission(app, session, prompt_data)
    ├─ Creates Future #1
    ├─ Sets prompt_input.permission_prompt_data = prompt_data
    ├─ Buffer displays ✓
    └─ await future  ← WAITING HERE
        ↓
User sees buffer, selects option
        ↓
PermissionHandlers.on_multi_line_input_permission_response(event)
        ↓
tui.permission_manager.handle_permission_response(response, data)
        ↓
tui.permission_manager._buffer_manager.resolve(response_data)
        ├─ Tries to resolve Future #2 (WRONG FUTURE!)
        └─ Future #1 is still waiting ← NEVER RESOLVES!
            ↓
        FREEZE ❌
```

## Why This Happens

1. ExecutionSystem creates its own PermissionManager instance
2. TUI creates a separate UnifiedPermissionManager instance
3. When ExecutionSystem needs permission:
   - Uses its own PermissionManager
   - Calls buffer_manager.request_permission()
   - Future created in ExecutionSystem's context
4. When user responds:
   - Response goes to TUI's PermissionManager
   - TUI's manager tries to resolve its own buffer manager's future
   - ExecutionSystem's future NEVER gets resolved
5. ExecutionSystem waits forever → FREEZE

## The Fix

ExecutionSystem should **NOT create its own PermissionManager**. Instead, it should use the same instance that TUI created.

### Option 1: Share the Instance (Recommended)

Modify `ExecutionSystem.__init__()` to accept a permission_manager parameter:

```python
class ExecutionSystem:
    def __init__(self, app, session, permission_manager=None):
        self.app = app
        self.session = session

        # Use provided permission manager or create default
        self.permission_manager = permission_manager or PermissionManager()
```

Then in TUI:
```python
class OpenCLITUI:
    def _init_command_router(self):
        # Create unified permission manager first
        unified_manager = get_unified_permission_manager()
        unified_manager.set_ui_callback(self._show_permission_prompt)

        # Pass it to ExecutionSystem
        executor = ExecutionSystem(
            app=self,
            session=self.session,
            permission_manager=unified_manager  # ← Share the instance!
        )
```

### Option 2: Use get_unified_permission_manager() in ExecutionSystem

Change executor.py to use the singleton:
```python
class ExecutionSystem:
    def __init__(self, app, session):
        self.app = app
        self.session = session

        # Use unified permission manager
        from ..permissions import get_unified_permission_manager
        self.permission_manager = get_unified_permission_manager()
```

## Verification Test

After fix, the flow should be:
```
User types /help
    ↓
ExecutionSystem.execute() → SHARED permission_manager.check_permission()
    ↓
buffer_manager.request_permission()
    ├─ Creates Future
    ├─ Buffer displays
    └─ await future
        ↓
User selects option
        ↓
SAME permission_manager.handle_permission_response()
        ↓
buffer_manager.resolve(response_data)
        ├─ Resolves THE SAME Future ✓
        └─ await completes
            ↓
        SUCCESS ✅
```

## Files That Need Changes

1. ✅ `modules/execution/executor.py` - Accept permission_manager parameter OR use get_unified_permission_manager()
2. ✅ `modules/tui/core.py` - Pass unified manager to ExecutionSystem

---

**Root Cause**: Disconnected permission manager instances
**Impact**: All permission-required commands freeze
**Solution**: Share single UnifiedPermissionManager instance
**Priority**: CRITICAL - Blocks all SDK commands
