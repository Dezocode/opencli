# Modular vs Monolithic MultiLineInput - Missing Functionality Analysis

**Date**: 2025-10-21
**Issue**: Determining if monolithic version is blocking refactor completion

---

## Critical Missing Methods in Modular Version

### ❌ MISSING: Action Methods for BINDINGS

**Monolithic has** (`multiline_input.py`):
```python
BINDINGS = [
    Binding("enter", "submit", "Submit message"),
    Binding("ctrl+c", "cancel", "Cancel input"),
    Binding("up", "permission_up", "Navigate up in permission options", show=False),
    Binding("down", "permission_down", "Navigate down in permission options", show=False),
]

def action_cancel(self) -> None:
    """Cancel input - clear value"""
    self.value = ""
    self.cursor_position = 0
    self.refresh()

def action_permission_up(self) -> None:
    """Navigate up in permission options"""
    if self.permission_prompt_data:
        options = self.permission_prompt_data.get('options', [])
        if self.permission_selected_option > 0:
            self.permission_selected_option -= 1
            self.refresh()

def action_permission_down(self) -> None:
    """Navigate down in permission options"""
    if self.permission_prompt_data:
        options = self.permission_prompt_data.get('options', [])
        if self.permission_selected_option < len(options) - 1:
            self.permission_selected_option += 1
            self.refresh()
```

**Modular has** (`input_widget/widget.py`):
```python
# NO BINDINGS DEFINED AT ALL!
# Only has action_submit()

def action_submit(self) -> None:
    """Submit the current input"""
    user_input = self.value.strip()
    # ... rest of method
```

**Status**: ❌ **CRITICAL MISSING** - This is why permission navigation doesn't work!

---

### ❌ MISSING: watch_permission_selected_option()

**Monolithic has**:
```python
def watch_permission_selected_option(self, old_value: int, new_value: int) -> None:
    """Watch for selection changes to trigger UI refresh"""
    import sys
    sys.stderr.write(f"[MultiLineInput.watch_permission_selected_option] {old_value} -> {new_value}\n")
    sys.stderr.flush()

    if old_value != new_value and self.permission_prompt_data:
        # Force refresh when selection changes
        self.refresh()
        sys.stderr.write(f"[MultiLineInput] REFRESH triggered by selection change\n")
        sys.stderr.flush()
```

**Modular has**:
```python
# NOTHING - No watcher for permission_selected_option changes!
```

**Status**: ❌ **MISSING** - UI won't refresh when arrow keys change selection

---

### ❌ MISSING: _render_permission_prompt() and _wrap_text()

**Monolithic has**:
```python
def _render_permission_prompt(self) -> Text:
    """Render permission prompt with options"""
    # 100+ lines of rendering logic
    # Handles title, workflow, message, options
    # Applies Frontier colors and styling

def _wrap_text(self, text: str, width: int = None) -> list[str]:
    """Wrap text to fit width"""
    # Text wrapping logic
```

**Modular has**:
```python
# Moved to permission_renderer.py as standalone function:
def render_permission_prompt(prompt_data: dict, selected_option: int) -> Text:
    """Render permission prompt - standalone function"""
    # Same logic but NOT a class method
```

**Status**: ⚠️ **REFACTORED** - Functionality exists but in different module

---

## Reactive Properties Comparison

| Property | Monolithic | Modular | Status |
|----------|-----------|---------|--------|
| `value` | ✅ `reactive("", layout=True)` | ✅ `reactive("", layout=True)` | ✅ Same |
| `cursor_position` | ✅ `reactive(0)` | ✅ `reactive(0)` | ✅ Same |
| `is_spinning` | ✅ `reactive(False)` | ✅ `reactive(False)` | ✅ Same |
| `spinner_frame` | ✅ `reactive(0)` | ✅ `reactive(0)` | ✅ Same |
| `permission_prompt_data` | ✅ `reactive(None)` | ✅ `reactive(None)` | ✅ Same |
| `permission_selected_option` | ✅ `reactive(0)` | ✅ `reactive(0)` | ✅ Same |

**Status**: ✅ All reactive properties present in both

---

## Message Classes Comparison

| Message Class | Monolithic | Modular | Status |
|---------------|-----------|---------|--------|
| `Submitted` | ✅ Nested | ✅ Standalone | ✅ Both |
| `PermissionResponse` | ✅ Nested | ✅ Standalone | ✅ Both |
| `PermissionCancelled` | ✅ Nested | ✅ Standalone | ✅ Both |
| `ShowCommandSuggestions` | ✅ Nested | ✅ Standalone | ✅ Both |
| `HideCommandSuggestions` | ✅ Nested | ✅ Standalone | ✅ Both |
| `CommandSuggestionNavigate` | ✅ Nested | ✅ Standalone | ✅ Both |
| `CommandSuggestionSelect` | ✅ Nested | ✅ Standalone | ✅ Both |
| `NavigationEvent` | ✅ Nested | ✅ Standalone | ✅ Both |
| `DebugMessage` | ❌ Missing | ✅ Standalone | ⚠️ Modular only |

**Status**: ✅ All critical messages present (DebugMessage is extra)

---

## Event Handlers Comparison

| Event Handler | Monolithic | Modular | Location |
|---------------|-----------|---------|----------|
| `on_key()` | ✅ 100+ lines in class | ✅ Delegates to `handle_key_event()` | `event_handler.py` |
| `on_paste()` | ✅ In class | ✅ Delegates to `handle_paste_event()` | `event_handler.py` |
| `on_focus()` | ✅ In class | ✅ In class | Both |
| `on_blur()` | ✅ In class | ✅ In class | Both |

**Status**: ✅ All event handlers present (modular delegates to separate module)

---

## Core Methods Comparison

| Method | Monolithic | Modular | Status |
|--------|-----------|---------|--------|
| `render()` | ✅ In class | ✅ In class | ✅ Both |
| `clear()` | ✅ In class | ✅ In class | ✅ Both |
| `start_spinner()` | ✅ In class | ✅ In class | ✅ Both |
| `stop_spinner()` | ✅ In class | ✅ In class | ✅ Both |
| `watch_value()` | ✅ In class | ✅ In class | ✅ Both |
| `watch_is_spinning()` | ✅ In class | ✅ In class | ✅ Both |
| `watch_spinner_frame()` | ✅ In class | ✅ In class | ✅ Both |
| `watch_permission_prompt_data()` | ✅ In class | ✅ In class | ✅ Both |

**Status**: ✅ All core methods present

---

## The Blocking Issues

### 🚨 CRITICAL: Modular Version is INCOMPLETE

**Missing functionality that breaks permission navigation**:

1. ❌ **NO BINDINGS defined** - Textual won't know to call action methods
2. ❌ **action_permission_up()** - Can't navigate up in permissions
3. ❌ **action_permission_down()** - Can't navigate down in permissions
4. ❌ **action_cancel()** - Can't cancel with Ctrl+C
5. ❌ **watch_permission_selected_option()** - UI won't refresh on selection change

### Why This Blocks the Refactor

**The monolithic version has BINDINGS**:
```python
BINDINGS = [
    Binding("up", "permission_up", ...),
    Binding("down", "permission_down", ...),
]
```

But as we discovered in the analysis MD, these BINDINGS **prevent on_key() from being called** because:
1. Textual intercepts UP/DOWN before on_key()
2. Calls `action_permission_up()` / `action_permission_down()`
3. These methods DO exist in monolithic
4. They work (when focus is maintained)

**The modular version has NO BINDINGS**:
- Should rely on `on_key()` in `event_handler.py`
- But on_key() delegates are broken by on_blur auto-dismiss

### Current State Analysis

| Version | BINDINGS | on_key() | action methods | Works? |
|---------|----------|----------|----------------|--------|
| **Monolithic** | ✅ Has | ✅ Has (but skipped by BINDINGS) | ✅ Has action_permission_up/down | ⚠️ Broken by on_blur |
| **Modular** | ❌ Missing | ✅ Has (in event_handler.py) | ❌ Missing action_permission_up/down | ⚠️ Broken by on_blur |

**Both versions are broken by the on_blur issue we just fixed!**

---

## Root Cause Summary

### Why Both Versions Fail

1. **on_blur() auto-dismiss** (NOW FIXED)
   - Permission prompt dismissed on focus loss
   - Never gave user chance to use arrow keys
   - Fixed in both versions

2. **Monolithic: BINDINGS conflict**
   - BINDINGS intercept UP/DOWN keys
   - Call action_permission_up/down (which DO exist)
   - But on_blur fired first, clearing permission_prompt_data
   - Result: methods run but permission_prompt_data is None

3. **Modular: Missing action methods**
   - NO BINDINGS defined
   - Should use on_key() in event_handler.py
   - But on_blur fired first, clearing permission_prompt_data
   - Result: on_key() runs but permission_prompt_data is None

### Which Version is Actually Running?

From import order in `tui/core.py`:
```python
try:
    from ..multiline_input import MultiLineInput  # ← Monolithic FIRST
except:
    from ..input_widget import MultiLineInput     # ← Modular fallback
```

**Answer**: The **MONOLITHIC** version is running (unless import fails).

---

## Recommendations

### Option 1: Complete the Modular Refactor (Recommended)

**Add to `input_widget/widget.py`**:

```python
from textual.binding import Binding

class MultiLineInput(Widget):
    BINDINGS = [
        Binding("enter", "submit", "Submit message"),
        Binding("ctrl+c", "cancel", "Cancel input"),
        Binding("up", "permission_up", "Navigate up", show=False),
        Binding("down", "permission_down", "Navigate down", show=False),
    ]

    def action_cancel(self) -> None:
        self.value = ""
        self.cursor_position = 0
        self.refresh()

    def action_permission_up(self) -> None:
        if self.permission_prompt_data:
            options = self.permission_prompt_data.get('options', [])
            if self.permission_selected_option > 0:
                self.permission_selected_option -= 1
                self.refresh()

    def action_permission_down(self) -> None:
        if self.permission_prompt_data:
            options = self.permission_prompt_data.get('options', [])
            if self.permission_selected_option < len(options) - 1:
                self.permission_selected_option += 1
                self.refresh()

    def watch_permission_selected_option(self, old_value: int, new_value: int) -> None:
        if old_value != new_value and self.permission_prompt_data:
            self.refresh()
```

**Then**: Update imports to prefer modular version, delete monolithic file.

### Option 2: Fix the Monolithic Version Only

**Remove BINDINGS from `multiline_input.py`**:

```python
# DELETE THESE LINES:
BINDINGS = [
    Binding("up", "permission_up", ...),
    Binding("down", "permission_down", ...),
]

# DELETE THESE METHODS:
def action_permission_up(self): ...
def action_permission_down(self): ...
```

**Reason**: Let on_key() handle everything (it already has the logic).

### Option 3: Hybrid Approach

1. Keep both versions temporarily
2. Fix on_blur in both (DONE)
3. Remove BINDINGS from monolithic to unblock on_key()
4. Gradually migrate imports to modular
5. Complete modular version
6. Delete monolithic file

---

## Conclusion

**Is monolithic blocking the refactor?**

**YES**, because:
1. Imports prefer monolithic (loaded first)
2. Modular is incomplete (missing BINDINGS and action methods)
3. You can't switch to modular without adding missing functionality
4. Meanwhile, monolithic BINDINGS block on_key() from working

**Solution**:
- Either complete modular version (add missing methods)
- Or remove BINDINGS from monolithic (let on_key() work)
- With on_blur fix applied, either approach should work

**Next Step**: Choose one version and complete it!
