# CRITICAL FINDING - on_key() Logic Flow Issue

## Location
`modules/multiline_input.py` lines 340-386

## The Problem

When permission buffer is showing and user presses UP/DOWN:

### Current Code Flow (lines 340-386):
```python
if self.permission_prompt_data:  # Line 340 - ENTERS this block
    options = self.permission_prompt_data.get('options', [])  # Line 344

    # If no options (informational prompt), only allow Escape
    if not options:  # Line 347 - FALSE (we have options)
        if key == "escape":
            self.post_message(self.PermissionCancelled())
            event.prevent_default()
        return  # Line 351 - NOT REACHED

    # Line 353-354 comment: REMOVED: Navigation handled by BINDINGS
    elif key == "enter":  # Line 355 - FALSE (key is "up" or "down")
        selected = options[self.permission_selected_option]
        self.post_message(self.PermissionResponse(selected))
        event.prevent_default()
        return
    elif key == "escape":  # Line 361 - FALSE (key is "up" or "down")
        self.post_message(self.PermissionCancelled())
        event.prevent_default()
        return

    # FALLS THROUGH HERE! No return for up/down keys!

# Line 367: Handle command suggestion navigation if active
if self.suggestions_active:  # FALSE
    # ... skipped

# Line 385: Don't handle up/down for history
if key in ("up", "down") and not self.suggestions_active and not self.permission_prompt_data:
    #   ✓ key is up/down          ✓ not suggestions          ✗ FAIL - permission_prompt_data IS set!
    return  # NOT REACHED!

# Continues to backspace, delete, left, right handlers...
# NEVER calls event.prevent_default() for up/down!
# Event continues propagating...
```

## Root Cause Analysis

**Up/Down keys when permission buffer is showing:**

1. ✅ Enter `if self.permission_prompt_data:` block (line 340)
2. ✅ options exist, skip `if not options:` block
3. ❌ key is "up"/"down", not "enter", not "escape"
4. ❌ **FALLS THROUGH** the if/elif chain without returning!
5. ❌ Line 385 check FAILS because `permission_prompt_data` IS set
6. ❌ Never calls `event.prevent_default()`
7. ❌ Event continues to... BINDINGS? Or gets consumed elsewhere?

## Expected Behavior

The comment on lines 353-354 says:
```
# REMOVED: Navigation handled by BINDINGS (action_permission_up/down)
# This was causing conflicts between on_key() and bindings
```

This implies:
- on_key() should NOT handle up/down
- BINDINGS should handle up/down
- action_permission_up/down should be called

## Why Aren't BINDINGS Firing?

BINDINGS exist (lines 29-35):
```python
Binding("up", "permission_up", ...)
Binding("down", "permission_down", ...)
```

Action methods exist (lines 505-547):
```python
def action_permission_up(self) -> None:
def action_permission_down(self) -> None:
```

**Possible causes why BINDINGS don't fire:**

### Theory 1: Event order in Textual
- on_key() is called FIRST
- If on_key() doesn't call prevent_default(), event continues
- But event might be consumed by something else before BINDINGS process it

### Theory 2: Focus issue
- BINDINGS only work when widget has focus
- Focus might not actually be on the widget despite focus() being called

### Theory 3: BINDINGS require conditional activation
- BINDINGS might need `priority=True` to override default behavior
- BINDINGS with show=False might not be active

### Theory 4: Parent widget consuming events
- ActionMixin.on_key() in parent TUI class
- But ActionMixin only handles ctrl+c, ctrl+l, f11, f12 - NOT up/down

## Next Steps

1. **Add prevent_default() to permission block**
   - When permission_prompt_data is set and key is up/down
   - Stop event propagation in on_key()
   - Let BINDINGS handle it exclusively

2. **OR: Check if BINDINGS are actually registered**
   - Verify Textual is seeing the BINDINGS
   - Check if priority is needed

3. **OR: Check if focus is actually on widget**
   - Add logging to verify has_focus when pressing keys
   - Verify app.focused points to MultiLineInput

4. **OR: Handle up/down directly in on_key()**
   - Remove reliance on BINDINGS
   - Handle navigation in on_key() like enter/escape

## Recommended Fix

**Option A: Prevent event in on_key, let BINDINGS handle**
```python
if self.permission_prompt_data:
    options = self.permission_prompt_data.get('options', [])

    if not options:
        if key == "escape":
            self.post_message(self.PermissionCancelled())
            event.prevent_default()
        return

    # For up/down, prevent default and let BINDINGS handle
    if key in ("up", "down"):
        event.prevent_default()  # STOP on_key from processing
        return  # Let BINDINGS fire action_permission_up/down

    elif key == "enter":
        ...
```

**Option B: Handle in on_key directly (don't rely on BINDINGS)**
```python
if self.permission_prompt_data:
    options = self.permission_prompt_data.get('options', [])

    if not options:
        if key == "escape":
            self.post_message(self.PermissionCancelled())
            event.prevent_default()
        return

    # Handle all navigation in on_key
    if key == "up":
        if self.permission_selected_option > 0:
            self.permission_selected_option -= 1
            self.refresh()
        event.prevent_default()
        return
    elif key == "down":
        if self.permission_selected_option < len(options) - 1:
            self.permission_selected_option += 1
            self.refresh()
        event.prevent_default()
        return
    elif key == "enter":
        ...
```

## Status

- [x] Identified logic flow issue in on_key()
- [ ] Determine why BINDINGS aren't firing
- [ ] Apply fix
- [ ] Test
