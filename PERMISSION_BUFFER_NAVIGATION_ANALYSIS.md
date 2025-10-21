# Permission Buffer Navigation Analysis
**Investigation Date**: 2025-10-21
**Issue**: Arrow keys (UP/DOWN) don't work in permission buffer when typing `/help` and pressing ENTER

---

## Architecture Overview

### Permission Buffer Is NOT a Separate Widget

**CRITICAL DISCOVERY**: The "permission buffer" is NOT a standalone widget. It's a **display mode** of the `MultiLineInput` widget controlled by the `permission_prompt_data` reactive property.

```python
# Location: cli/modules/multiline_input.py

class MultiLineInput(Widget):
    permission_prompt_data = reactive(None)  # When set, widget shows permission UI
    permission_selected_option = reactive(0)

    def render(self) -> Text:
        # Line 89: PRIORITY check
        if self.permission_prompt_data:
            return render_permission_prompt(...)  # Show permission UI

        # Otherwise show normal input
        return normal_input_display
```

**Key Insight**: There is no `PermissionBuffer` widget class. The same `MultiLineInput` widget switches between:
1. **Normal Mode**: Text input with cursor
2. **Permission Mode**: Permission prompt with options (when `permission_prompt_data` is set)

---

## Event Flow Architecture

### 1. Permission Prompt Display Flow

```
User types: /help + ENTER
    ↓
command_handlers.py → _handle_user_message()
    ↓
permission_handlers.py → _show_permission_prompt(prompt_data)
    ↓
Line 401: prompt_input.permission_prompt_data = prompt_data
    ↓
watch_permission_prompt_data() TRIGGERS (Line 646)
    ↓
Lines 662-691: Attempts to call focus()
    - self.focus()
    - self.app.set_focus(self)
    ↓
Widget re-renders with permission UI (render() line 89)
```

**File**: `cli/modules/tui/permission_handlers.py:390-420`
**File**: `cli/modules/multiline_input.py:646-692`

---

### 2. Key Event Propagation Flow

When user presses arrow key:

```
User presses: UP or DOWN
    ↓
ActionMixin.on_key() CALLED FIRST (TUI/App level)
    ├─ File: cli/modules/tui/action_mixin.py:43-78
    ├─ Logs: "[ActionMixin.on_key] 🔥 KEY=up 🔥"
    ├─ Checks if key is shortcut (Ctrl+C, F11, etc)
    └─ Line 76: "Allowing key 'up' to propagate"

    ↓ (event propagates to focused widget)

MultiLineInput.on_key() SHOULD BE CALLED
    ├─ File: cli/modules/multiline_input.py:336-415
    ├─ Line 342: Logs: "[MultiLineInput.on_key] 🔥 KEY='up' prompt=True focused=True 🔥"
    ├─ Line 348: Check if permission_prompt_data is set
    ├─ Lines 362-373: Handle UP/DOWN arrows
    │   ├─ UP: permission_selected_option -= 1
    │   ├─ DOWN: permission_selected_option += 1
    │   └─ refresh() to update display
    └─ event.prevent_default()
```

---

## The Code IS Correct

### ✅ Permission Handling Code Exists

**File**: `cli/modules/multiline_input.py:347-384`

```python
def on_key(self, event) -> None:
    if self.permission_prompt_data:  # Line 348
        options = self.permission_prompt_data.get('options', [])

        # Handle UP arrow
        if key == "up":  # Line 362
            if self.permission_selected_option > 0:
                self.permission_selected_option -= 1
                self.refresh()
            event.prevent_default()
            return

        # Handle DOWN arrow
        elif key == "down":  # Line 368
            if self.permission_selected_option < len(options) - 1:
                self.permission_selected_option += 1
                self.refresh()
            event.prevent_default()
            return
```

**Status**: ✅ Code is correct and complete

---

### ✅ Focus Handling Code Exists

**File**: `cli/modules/multiline_input.py:646-692`

```python
def watch_permission_prompt_data(self, old_value, new_value) -> None:
    if new_value:  # Permission prompt set
        # Line 658: Set initial selected option
        self.permission_selected_option = new_value.get('selected', 0)

        # Lines 662-666: Try to focus if not focused
        if not self.has_focus:
            self.focus()

        # Lines 682-690: FORCE focus immediately
        try:
            self.app.set_focus(self)  # Line 683
            print(f"[MultiLineInput]   ✓ FORCED FOCUS IMMEDIATELY")
        except Exception as e:
            self.focus()  # Fallback
```

**Status**: ✅ Focus code exists and tries multiple methods

---

### ✅ Event Propagation Allows Keys Through

**File**: `cli/modules/tui/action_mixin.py:43-78`

```python
def on_key(self, event) -> None:
    # Only intercept specific shortcuts
    if event.key == "ctrl+c":
        self.action_quit_app()
        event.prevent_default()
        event.stop()
        return

    # Lines 74-77: CRITICAL - Let ALL other keys propagate!
    sys.stderr.write(f"[ActionMixin.on_key] Allowing key '{event.key}' to propagate\n")
    # NOTE: Does NOT call prevent_default() or stop()
```

**Status**: ✅ Non-shortcut keys are allowed to propagate to focused widget

---

## Why It's NOT Working: The Focus Problem

### The Hypothesis

Even though the code calls `focus()` and `self.app.set_focus(self)`, the `MultiLineInput` widget may **not actually receive focus** when the permission prompt is displayed.

### Evidence for Focus Issue

1. **watch_permission_prompt_data** (Line 646) is called when `permission_prompt_data` is set
2. **Lines 662-691**: Code tries to focus the widget
3. **BUT**: Focus may fail silently if:
   - App is not mounted yet
   - Widget is not in DOM tree
   - Another widget steals focus
   - Textual event loop timing issue

### Missing Debug Evidence

**We need to see in logs**:
- ✅ `[MultiLineInput.watch_permission_prompt_data]` - Called when prompt set
- ✅ `[MultiLineInput] FORCED FOCUS IMMEDIATELY` - Focus attempted
- ❌ `[MultiLineInput.on_focus]` - **NOT CALLED** = Widget never received focus!
- ❌ `[MultiLineInput.on_key] 🔥 KEY='up'` - **NOT CALLED** = Keys not reaching widget!

**File**: `cli/modules/input_widget/widget.py:52-57`

```python
def on_focus(self) -> None:
    """Track when widget receives focus"""
    sys.stderr.write(f"\n[MultiLineInput.on_focus] GAINED FOCUS - prompt={bool(self.permission_prompt_data)}\n")
    sys.stderr.flush()
```

**This log should appear after focus() is called, but it doesn't!**

---

## Why Focus Fails

### Textual Focus Requirements

For a widget to receive focus in Textual:

1. **Widget must be mounted** - Added to DOM tree and compose() complete
2. **Widget must have `can_focus = True`** - ✅ Set in `__init__` line 48
3. **Widget must be visible** - ✅ Always visible in layout
4. **No other widget can intercept focus** - ⚠️ **POTENTIAL ISSUE**
5. **App must be in focus mode** - ⚠️ **POTENTIAL ISSUE**

### Potential Focus Blockers

#### 1. **StreamingDisplay Widget Stealing Focus**

**File**: `cli/modules/tui/core.py` (layout)

```python
# Content area (scrollable)
with Vertical(id="content-container"):
    yield StreamingDisplay(id="content")  # Can this steal focus?

# Command suggestions (hidden by default)
yield CommandSuggestionBuffer(id="command-suggestions", classes="hidden")

# Prompt area (fixed)
with Horizontal(id="prompt-container"):
    yield MultiLineInput(id="prompt-input", placeholder="Type your message...")
```

**Question**: Does `StreamingDisplay` or `CommandSuggestionBuffer` have `can_focus = True`?

#### 2. **Focus Called Before Mount Complete**

**File**: `cli/modules/multiline_input.py:682-690`

```python
try:
    self.app.set_focus(self)  # What if self.app is None?
    print("FORCED FOCUS IMMEDIATELY")
except Exception as e:
    print(f"Focus error: {e}, trying fallback")  # Silent failure!
    try:
        self.focus()  # What if widget not mounted?
    except Exception as e2:
        print(f"Fallback focus also failed: {e2}")  # Swallowed!
```

**Problem**: Exceptions are caught and logged to `print()` (which goes to TUI), not `sys.stderr`. User never sees these errors!

#### 3. **Asynchronous Focus Timing**

**File**: `cli/modules/tui/permission_handlers.py:401-413`

```python
prompt_input.permission_prompt_data = prompt_data  # Line 401 - Sets reactive
# This triggers watch_permission_prompt_data ASYNCHRONOUSLY

# Lines 410-413: Meanwhile, THIS code tries to focus synchronously
prompt_input.focus()  # Called before watch handler completes?
```

**Race Condition**: The handler sets data, then immediately tries to focus. But the `watch_permission_prompt_data()` is called async, so it may try to focus AGAIN, creating a conflict.

---

## The Missing Link: on_key Never Receives Events

### Why MultiLineInput.on_key Isn't Called

Even if focus is set, **on_key() may not receive events** if:

1. **Event is consumed by parent** - ActionMixin logs show it propagates, so this is OK
2. **Widget doesn't have focus** - Most likely cause
3. **Textual bindings intercept** - Check BINDINGS on MultiLineInput
4. **Event handler is overridden** - Check if another mixin overrides on_key

### Check: Does MultiLineInput Have Bindings?

**File**: `cli/modules/multiline_input.py:29-35`

```python
BINDINGS = [
    Binding("enter", "submit", "Submit message"),
    Binding("ctrl+c", "cancel", "Cancel input"),
    # Permission buffer navigation
    Binding("up", "permission_up", "Navigate up in permission options", show=False),
    Binding("down", "permission_down", "Navigate down in permission options", show=False),
]
```

**PROBLEM FOUND!** ⚠️

The widget defines `Binding("up", "permission_up", ...)` which means Textual will:
1. Intercept UP key
2. Call `action_permission_up()` method
3. **NOT call on_key() at all**

**But**: There is NO `action_permission_up()` method defined!

**File**: Search for `def action_permission_up` - **NOT FOUND**

---

## ROOT CAUSE IDENTIFIED

### The Bindings vs on_key Conflict

**How Textual Handles Keys**:

1. **Bindings First**: If widget has `BINDINGS = [Binding("up", "permission_up")]`
   - Textual intercepts UP key
   - Calls `action_permission_up()`
   - **NEVER calls on_key()**

2. **on_key Second**: Only called if NO binding matches

**The Problem**:

```python
# Line 33-34: BINDINGS define UP/DOWN
Binding("up", "permission_up", ...),
Binding("down", "permission_down", ...),

# Line 336-415: on_key() handles UP/DOWN
def on_key(self, event):
    if key == "up":  # This code NEVER RUNS!
        # Because Binding intercepts first
```

**Status**: ❌ **CONFLICT - Bindings prevent on_key from handling UP/DOWN**

---

## Secondary Issue: Message Bubbling Fixed

### The bubble=True Fix

Earlier in this session, we fixed message classes to have `bubble = True`:

**File**: `cli/modules/multiline_input.py:709-716` (added at end)

```python
# Export nested message classes at module level
Submitted = MultiLineInput.Submitted
PermissionResponse = MultiLineInput.PermissionResponse
# ... etc
```

**And inside MultiLineInput class** (Lines 47-89):

```python
class Submitted(Message):
    bubble = True  # ✅ ADDED

class PermissionResponse(Message):
    bubble = True  # ✅ ADDED
```

**This was necessary** because:
- Messages are posted by widget: `self.post_message(PermissionResponse(selected))`
- Without `bubble = True`, messages don't reach parent TUI handlers
- Handlers in `permission_handlers.py` would never receive events

**Status**: ✅ **FIXED - Messages now bubble to parent**

---

## Summary of Findings

### What IS Working

1. ✅ Permission prompt displays correctly (render() works)
2. ✅ ActionMixin allows UP/DOWN to propagate
3. ✅ on_key() has correct permission handling code (lines 347-384)
4. ✅ watch_permission_prompt_data() tries to focus widget
5. ✅ Message bubbling fixed with bubble=True
6. ✅ Module exports added for PermissionResponse import

### What is NOT Working

1. ❌ **BINDINGS intercept UP/DOWN keys before on_key() is called**
2. ❌ **action_permission_up() and action_permission_down() methods don't exist**
3. ❌ **Focus may not be set correctly (no on_focus() log)**
4. ⚠️ **Focus exceptions swallowed by print() instead of sys.stderr**
5. ⚠️ **Potential race condition between permission_prompt_data set and focus()**

---

## The Fix Needed

### Option 1: Remove BINDINGS (Recommended)

**Remove these lines** from `cli/modules/multiline_input.py:33-34`:

```python
# DELETE THESE:
Binding("up", "permission_up", "Navigate up in permission options", show=False),
Binding("down", "permission_down", "Navigate down in permission options", show=False),
```

**Reason**: These bindings block on_key() from being called. The on_key() method already handles UP/DOWN correctly.

### Option 2: Implement action_permission_up/down Methods

**Add these methods** to `MultiLineInput` class:

```python
def action_permission_up(self) -> None:
    """Handle UP arrow in permission mode"""
    if self.permission_prompt_data:
        options = self.permission_prompt_data.get('options', [])
        if self.permission_selected_option > 0:
            self.permission_selected_option -= 1
            self.refresh()

def action_permission_down(self) -> None:
    """Handle DOWN arrow in permission mode"""
    if self.permission_prompt_data:
        options = self.permission_prompt_data.get('options', [])
        if self.permission_selected_option < len(options) - 1:
            self.permission_selected_option += 1
            self.refresh()
```

**Reason**: Bindings will call these actions, which then handle navigation.

---

## Why Context Navigation Doesn't Work

### "Contextual Navigation" Means:

- UP/DOWN in **normal mode** = History navigation (handled by parent)
- UP/DOWN in **permission mode** = Option selection (handled by widget)
- UP/DOWN in **suggestion mode** = Suggestion navigation (handled by widget)

### Current State:

**BINDINGS are STATIC** - They are defined at class level and **always active**:

```python
BINDINGS = [
    Binding("up", "permission_up", ...),  # ALWAYS tries to call action_permission_up()
]
```

This means:
- Even in normal mode, Textual tries to call `action_permission_up()`
- Method doesn't exist, so nothing happens
- on_key() is never called
- History navigation is broken

### The Solution:

**Don't use BINDINGS for contextual behavior!**

Use `on_key()` instead, which can check `self.permission_prompt_data` and `self.suggestions_active` to determine context.

**This is what the code already does** (lines 347-405), but BINDINGS prevent it from running!

---

## Files Involved

### Core Files
- `cli/modules/multiline_input.py` - Main widget with permission handling
- `cli/modules/input_widget/widget.py` - Modular refactored version
- `cli/modules/input_widget/event_handler.py` - Modular on_key handler
- `cli/modules/input_widget/messages.py` - Message classes with bubble=True

### TUI Integration
- `cli/modules/tui/core.py` - Main TUI class, imports MultiLineInput
- `cli/modules/tui/permission_handlers.py` - Sets permission_prompt_data
- `cli/modules/tui/command_handlers.py` - Imports message classes
- `cli/modules/tui/action_mixin.py` - Parent on_key() that allows propagation

### Import Locations
- `/Users/dezmondhollins/.opencli/cli/modules/multiline_input.py` (Active)
- `/Users/dezmondhollins/.opencli/modules/multiline_input.py` (Synced)
- `/Users/dezmondhollins/opencli/modules/multiline_input.py` (Synced)

---

## Test Evidence Needed

To confirm the root cause, check logs for:

1. **Focus events**:
   ```
   [MultiLineInput.on_focus] GAINED FOCUS - prompt=True
   ```
   If missing → Focus is not set

2. **Key events**:
   ```
   [MultiLineInput.on_key] 🔥 KEY='up' prompt=True focused=True 🔥
   ```
   If missing → on_key() not called (BINDINGS blocking)

3. **Permission handler**:
   ```
   [MultiLineInput] INSIDE PERMISSION HANDLER for key=up
   ```
   If missing → on_key() permission block not reached

4. **Selection change**:
   ```
   [MultiLineInput.watch_permission_selected_option] 0 -> 1
   [MultiLineInput] REFRESH triggered by selection change
   ```
   If missing → permission_selected_option not updated

---

## Conclusion

**PRIMARY ROOT CAUSE**: Textual BINDINGS for "up" and "down" keys intercept events before `on_key()` can handle them, and the target action methods (`action_permission_up`, `action_permission_down`) don't exist.

**SECONDARY ISSUE**: Focus may not be set correctly when permission prompt appears, but this is masked by the binding issue.

**FIX**: Remove the UP/DOWN bindings from `BINDINGS` list, allowing `on_key()` to handle contextual navigation.

**IMPACT**: Once bindings are removed, the existing on_key() code (lines 347-405) should work correctly for permission navigation.
