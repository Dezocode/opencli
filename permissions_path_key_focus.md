# Permission Buffer Navigation Investigation
**Created:** 2025-10-29 22:05 CT
**Issue:** Permission buffer displays but arrow keys don't navigate options

## Current Behavior

**What Works:**
- ✅ Permission buffer renders and displays
- ✅ Shows "▸ View all commands" option
- ✅ Focus appears to be on the input widget

**What Doesn't Work:**
- ❌ UP/DOWN arrow keys don't navigate
- ❌ ENTER key doesn't select option
- ❌ Widget shows `permission=False` in key logs

## Investigation Trail

### 1. Command Execution Path

```
User types: /help
↓
modules/tui/message_handler_mixin.py: handle_user_input()
↓
[dim]Calling routecommandunified...[/dim]
↓
modules/command_router.py: route_command_unified()
↓
Displays permission buffer in TUI
```

### 2. Key Logging Evidence

From `/tmp/opencli_keys.log`:
```
[widget.on_key] KEY=enter, permission=False
[widget.on_key] KEY=h, permission=False
[widget.on_key] KEY=i, permission=False
```

**Problem:** `permission=False` means `widget.permission_prompt_data` is NOT set!

### 3. Widget Structure

**Two Possible Widget Paths:**

**Path A - MultiLineInput (input box):**
- File: `modules/input_widget/widget.py`
- Has: `permission_prompt_data` reactive attribute
- Has: Arrow key handling in `event_handler.py:handle_permission_keys()`
- **Should be used but isn't getting data set!**

**Path B - PermissionPrompt (standalone widget):**
- File: `modules/permissions/widget.py`
- Has: `is_active` reactive attribute
- Has: Arrow key handling in `on_key()` method
- **Not being used in TUI**

### 4. Code Flow Analysis

#### Expected Flow (Not Happening):
```python
# 1. TUI sets permission prompt data
_show_permission_prompt(prompt_data)
  ↓
# 2. Sets data on MultiLineInput widget
prompt_input.permission_prompt_data = prompt_data
  ↓
# 3. Keys get routed to permission handler
handle_key_event() → handle_permission_keys()
  ↓
# 4. Arrow keys navigate, Enter selects
```

#### Actual Flow (What's Happening):
```python
# 1. Command router displays buffer directly
route_command_unified()
  ↓
# 2. Buffer renders in TUI somehow
# 3. But permission_prompt_data is NEVER SET
# 4. Keys go to normal handler, not permission handler
```

## Critical Questions

### Q1: Where is the permission buffer being rendered?
**Check:**
- Is it coming from command_router.py?
- Is it using a different widget?
- Is it bypassing _show_permission_prompt()?

### Q2: Why isn't permission_prompt_data being set?
**Possibilities:**
- _show_permission_prompt() not being called
- Wrong widget instance
- Data being cleared immediately
- Router displaying buffer differently

### Q3: Who calls _show_permission_prompt()?
**Expected caller:**
- UnifiedPermissionManager via set_ui_callback()

**Actual caller:**
- Unknown - need to trace

## Files to Investigate

### Priority 1: Command Router
- `modules/command_router.py`
- Check: route_command_unified() implementation
- Look for: How it displays permission buffers

### Priority 2: Permission System Wiring
- `modules/tui/core.py: _setup_permission_system()`
- Check: Is set_ui_callback() being called?
- Check: Is UnifiedPermissionManager initialized?

### Priority 3: Command Registration
- `modules/commands/basic_commands.py: help()`
- Check: How does /help register its permission prompt?
- Check: Does it use SDK executor or legacy system?

### Priority 4: Message Handler
- `modules/tui/message_handler_mixin.py`
- Check: handle_user_input() → command routing flow
- Look for: Where permission prompts get triggered

## Hypothesis

**Primary Hypothesis:**
The command router is displaying a permission buffer DIRECTLY in the UI without going through the proper permission system that sets `permission_prompt_data` on the MultiLineInput widget.

**Evidence:**
1. Buffer displays correctly (visual rendering works)
2. But `permission=False` in key logs (data not set)
3. "Using fallback handler" message suggests execution manager isn't wired
4. Permission navigation code is perfect but never gets called

**Root Cause:**
Commands are being executed through a fallback path that bypasses the proper permission system.

## 🔥 ROOT CAUSE FOUND!

**File:** `modules/permissions/integration.py:52-84`
**Function:** `show_permission_prompt()`

### The Bug

Lines 66-71 create a **standalone PermissionPrompt widget**:
```python
self._current_widget = PermissionPrompt(
    title=prompt_data.get('title', 'Permission Required'),
    message=prompt_data.get('message', 'Allow this operation?'),
    options=prompt_data.get('options', []),
    details=prompt_data.get('details', {})
)
```

Then line 84 calls the UI callback:
```python
self._ui_callback(prompt_data)
```

### The Problem

**What SHOULD happen:**
1. Call `_ui_callback(prompt_data)` which is `TUI._show_permission_prompt()`
2. `_show_permission_prompt()` sets `prompt_input.permission_prompt_data = prompt_data`
3. MultiLineInput widget gets the data
4. Arrow keys route to `handle_permission_keys()`

**What ACTUALLY happens:**
1. Creates standalone PermissionPrompt widget (lines 66-71)
2. Calls `_ui_callback(prompt_data)` which renders buffer
3. BUT permission_prompt_data is NEVER set on MultiLineInput!
4. Arrow keys go to normal handler (permission=False)

### Why It Displays But Doesn't Navigate

The buffer **renders** because `_ui_callback` is rendering the prompt data.
But the MultiLineInput widget **never gets** `permission_prompt_data` set.
So when arrow keys are pressed, the check `if widget.permission_prompt_data` is False.

### The Fix

**Option 1:** Remove lines 66-82 (widget creation)
Let _ui_callback handle everything including setting permission_prompt_data on MultiLineInput.

**Option 2:** Have _ui_callback accept the widget
Pass self._current_widget to _ui_callback so it can be displayed properly.

**Option 3 (Best):** Don't create PermissionPrompt widget at all
The PermissionPrompt widget is for standalone display.
MultiLineInput already has permission rendering built in.
Just call _ui_callback(prompt_data) and let it handle everything.

## ✅ FIX APPLIED

**File Modified:** `modules/permissions/integration.py:63-78`

**What Changed:**
Removed lines 66-82 that created standalone PermissionPrompt widget.
Now just calls `_ui_callback(prompt_data)` directly.

**Before:**
```python
with self._lock:
    self._current_widget = PermissionPrompt(...)  # ❌ Created widget
    self._current_widget.show()
    self._current_widget.focus()
self._ui_callback(prompt_data)  # Then called callback
```

**After:**
```python
if self._ui_callback:
    if handler_name:
        prompt_data['_handler_name'] = handler_name
    self._ui_callback(prompt_data)  # ✅ Just call callback
```

**Expected Result:**
1. `_ui_callback` (which is `TUI._show_permission_prompt()`) gets called
2. Sets `prompt_input.permission_prompt_data = prompt_data`
3. MultiLineInput widget now has the data
4. Arrow keys detected: `if widget.permission_prompt_data:` → TRUE
5. Keys route to `handle_permission_keys()`
6. Arrow navigation works!

## Next Steps

1. ✅ Add traceback logging to execution manager init (DONE)
2. ✅ Found root cause - PermissionPrompt widget created but not used (DONE)
3. ✅ Fix show_permission_prompt() to not create unused widget (DONE)
4. ⏳ Test opencli tui - run `/help` and try arrow keys
5. ⏳ Verify ENTER key selects option and executes command

## Log Files

- `/tmp/opencli_keys.log` - Key press events with permission status
- `/tmp/opencli_stderr.log` - Debug output and errors
- `/tmp/tui-trace.log` - TUI lifecycle events
- `/tmp/opencli_focus.log` - Focus state tracking
