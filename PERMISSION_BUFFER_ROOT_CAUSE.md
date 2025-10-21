# Permission Buffer Display - Root Cause Analysis

## Executive Summary
**SDK commands (`/help`, `/status`, etc.) are NOT displaying permission buffers**, even though the permission flow executes correctly.

## What We Fixed
### 1. ✅ Singleton Executor Stale References (`command_router.py:49-50`)
**Problem:** ExecutionSystem is a singleton. When CommandRouter is created with new app instances (like in tests), the executor kept stale app references.

**Fix:** Always update executor references in CommandRouter.__init__():
```python
# CRITICAL: Update executor references (singleton may have stale refs)
self.executor.app = self.app
self.executor.session = self.session
```

**Verification:**
```bash
$ python3 test_executor_refs.py
✅ executor.app correctly updated to FakeApp2
```

### 2. ✅ Custom Prompt Functions Call Buffer Manager
All 6 custom prompt functions (`show_help_prompt`, `show_status_prompt`, etc.) now correctly call:
```python
buffer_manager = get_permission_buffer_manager()
return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)
```

### 3. ✅ Registry Passed to Handlers via Context
Executor adds registry to context so handlers can access command data:
```python
context['_registry'] = self.registry
```

## What's STILL Broken
### The Permission Buffer Does NOT Render Visually

**Evidence:**
1. OpenCLI Controller test shows **empty screen** (only status bar, no buffer)
2. Direct execution test **hangs forever** waiting for Future resolution
3. Real TUI shows "Permission denied" without displaying the buffer

**Test Results:**
```
❌ PERMISSION BUFFER NOT FOUND (0/6 indicators found)
```

## The Permission Flow (What's Actually Happening)

### Current Execution Path:
```
User types /help
    ↓
CommandRouter.route_command()
    ↓
ExecutionSystem.execute()
    ↓
PermissionManager.check_permission()
    ↓
    ✓ app and session are valid (FIXED!)
    ↓
PermissionManager._show_permission_prompt()
    ↓
    ✓ custom_prompt_func is found
    ↓
show_help_prompt() is called
    ↓
    ✓ Calls buffer_manager.request_permission()
    ↓
PermissionBufferManager.request_permission()
    ↓
    ✓ Creates task with asyncio.Future()
    ↓
    ✓ Sets widget.permission_prompt_data = prompt_data
    ↓
    ✓ Calls widget.refresh()
    ↓
    ✓ Sets focus
    ↓
    ⏳ await asyncio.wait_for(task.future, timeout=30.0)  # HANGS HERE!
    ↓
    ❌ Widget NEVER renders the permission buffer visually
    ↓
    ❌ Future NEVER resolves because no visual buffer to interact with
    ↓
    ⏱️ TIMEOUT after 30 seconds
    ↓
    ❌ Returns {'response': 'timeout', 'reason': 'timeout_expired'}
    ↓
    ❌ Permission denied!
```

## Why the Widget Doesn't Render

### The Widget Code (modules/multiline_input.py:126-131)
```python
def render(self) -> Text:
    """Render the current input with cursor or permission prompt"""

    # PRIORITY: Show permission prompt if active
    if self.permission_prompt_data:
        return self._render_permission_prompt()  # ← Should render buffer!
```

### Hypothesis: Widget is not re-rendering after `permission_prompt_data` is set

**Possible Causes:**
1. **Widget not mounted/visible** when `refresh()` is called
2. **Textual event loop** not processing the refresh event
3. **Widget DOM position** makes it invisible (z-index, visibility, focus issues)
4. **Permission buffer styles** hiding the content
5. **Another widget** overlaying the MultiLineInput
6. **Reactive property** not triggering render (permission_prompt_data is NOT reactive)

## The Smoking Gun: `permission_prompt_data` is NOT Reactive!

Looking at the MultiLineInput widget, `permission_prompt_data` is a **plain attribute**, NOT a **reactive property**!

In Textual, only **reactive properties** trigger automatic re-renders when changed. Plain attributes do NOT.

**Current Code:**
```python
class MultiLineInput(Widget):
    def __init__(self):
        super().__init__()
        self.permission_prompt_data = None  # ❌ Plain attribute!
```

**What We Need:**
```python
from textual.reactive import reactive

class MultiLineInput(Widget):
    permission_prompt_data = reactive(None)  # ✅ Reactive property!
```

## Next Step: Make permission_prompt_data Reactive

**File to Fix:** `modules/multiline_input.py`

**Change:**
1. Import `reactive` from `textual.reactive`
2. Convert `permission_prompt_data` from instance attribute to reactive class attribute
3. Add watcher method to trigger refresh when changed

**Expected Result:**
- When buffer manager sets `widget.permission_prompt_data = prompt_data`
- Textual will automatically call `widget.render()` because reactive property changed
- Buffer will display visually
- User can interact with options
- Message handler will resolve Future
- Permission flow completes successfully!

## Files Involved

### ✅ Fixed:
1. `/Users/dezmondhollins/opencli/modules/command_router.py` (lines 49-50)
2. `/Users/dezmondhollins/opencli/modules/commands/basic_commands.py` (all prompt functions)
3. `/Users/dezmondhollins/opencli/modules/execution/executor.py` (line 141)

### ❌ Still Needs Fix:
1. `/Users/dezmondhollins/opencli/modules/multiline_input.py` - Make permission_prompt_data reactive

## Debug Commands

### Test Executor References:
```bash
python3 test_executor_refs.py
```

### Test Permission Buffer (will hang):
```bash
python3 test_help_direct.py
```

### Test Real TUI:
```bash
python3 test_permission_buffer_fixed.py
```

## Conclusion

The permission system architecture is **CORRECT**. The buffer manager **IS** setting the data on the widget. The widget **IS** refreshing. But Textual **DOES NOT** re-render the widget because `permission_prompt_data` is not a reactive property.

**The fix is simple:** Make `permission_prompt_data` reactive in `multiline_input.py`.
