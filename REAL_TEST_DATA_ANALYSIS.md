# Real Test Data Analysis - Arrow Key Failure

## What the User's ACTUAL Test Showed

### Test Evidence (from user's terminal output):

```
Before DOWN arrow:
  │ ▸ Yes, allow this once                                                                                       │
After DOWN arrow:
  │ ▸ Yes, allow this once                                                                                       │
```

**FACT**: Selection indicator (▸) does NOT move from "Yes" to "No"

### Test Framework Detection:

```
❌ 'No' is NOT selected - DOWN ARROW FAILED!
```

### Permission Buffer IS Showing:

```
🎯 PERMISSION BUFFER DETECTED in TUI!
```

### Options ARE Visible:

```
│ ▸ Yes, allow this once                                                                                       │
│   No, cancel                                                                                                 │
```

## What This Tells Us

### ✅ Working:
1. Permission buffer displays correctly
2. Options render ("Yes" and "No" both visible)
3. Initial selection shows on "Yes" (▸ indicator)
4. DOWN keystroke is SENT to opencli
5. Test framework can detect the failure

### ❌ NOT Working:
1. DOWN arrow does NOT move selection indicator
2. Selection stays on "Yes" after DOWN press
3. UI does NOT update after DOWN arrow

## Systematic Analysis Based on Debug Logging

From my added debug logging in `multiline_input.py`, we need to check:

### Check 1: Is on_key() being called?
**Expected debug output**:
```
[MultiLineInput.on_key] ====== KEY EVENT ======
[MultiLineInput.on_key] KEY='down' (type=<class 'str'>)
```

**If NOT seen**: Widget doesn't have focus OR event not reaching widget

### Check 2: Is action_permission_down() being called?
**Expected debug output**:
```
[ACTION_PERMISSION_DOWN] CALLED - prompt=True
[ACTION_PERMISSION_DOWN] Changing 0 -> 1 (max=1)
```

**If seen**: BINDINGS are executing (may be blocking on_key)

### Check 3: Does selection value change?
**Expected debug output**:
```
[MultiLineInput.on_key] DOWN - changed 0 -> 1
```

**If NOT seen**: Conditional check failing OR key name mismatch

### Check 4: Is refresh() called?
**Expected debug output**:
```
[MultiLineInput.on_key] DOWN - refresh() called
```

**If NOT seen**: refresh() not being called

### Check 5: Does render() use correct property?
**Code check**: Line 271 of multiline_input.py
```python
if i == self.permission_selected_option:
```

**Status**: ✅ VERIFIED - Uses correct property

## Most Likely Root Causes (in order of probability)

### Theory 1: BINDINGS Blocking on_key() ⭐⭐⭐⭐⭐
**Evidence**:
- BINDINGS defined at line 33-34:
  ```python
  Binding("up", "permission_up", ...),
  Binding("down", "permission_down", ...),
  ```
- These call `action_permission_up/down()`
- May execute BEFORE `on_key()` gets event
- `event.prevent_default()` in on_key() may not prevent BINDINGS

**Test**: Check if ACTION_PERMISSION_DOWN debug appears but NOT on_key() debug

**Fix**: Remove BINDINGS or ensure on_key() executes first

### Theory 2: Key Name Case Mismatch ⭐⭐⭐⭐
**Evidence**:
- on_key() checks: `if key == "down"` (lowercase)
- Textual may send: "Down" (capitalized)
- Test sends via tmux: `send-keys "Down"`

**Test**: Check debug output for exact key name

**Fix**: Change check to case-insensitive or match exact case

### Theory 3: Widget Focus Issue ⭐⭐⭐
**Evidence**:
- TUI calls `prompt_input.focus()` but may not be effective
- on_key() has debug showing has_focus state

**Test**: Check `has_focus=True` in debug output

**Fix**: Ensure focus is set correctly when buffer shows

### Theory 4: permission_prompt_data Not Set ⭐⭐
**Evidence**:
- on_key() checks: `if self.permission_prompt_data:`
- Watcher should set it from TUI

**Test**: Check if code enters permission handler block

**Fix**: Verify watch_permission_prompt_data() fires

## Required Debug Output

To definitively identify the issue, we need to see from a REAL opencli run:

```bash
opencli tui 2>/tmp/opencli_real_debug.log

# Type: /help
# Press: ENTER
# Press: ENTER
# Press: DOWN arrow
# Press: Ctrl+C

cat /tmp/opencli_real_debug.log | grep -E "(KEY EVENT|ACTION_PERMISSION|DOWN|changed|refresh)"
```

This will show:
- Which functions actually execute
- What key name is received
- If selection value changes
- If refresh() is called

## Summary

The automated test framework gives **false positives** - it reports PASS but the user's manual test clearly shows **FAIL**.

**The bug is real**: DOWN arrow does NOT change selection in permission buffer.

**Most likely cause**: BINDINGS conflict or key name mismatch.

**Next step**: Capture real stderr debug output from actual opencli run to see which code path executes.
