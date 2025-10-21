# Arrow Key Navigation Debug Summary

## Problem
DOWN arrow key does NOT change selection in permission buffer. Test shows:
```
Before DOWN arrow:
  │ ▸ Yes, allow this once
After DOWN arrow:
  │ ▸ Yes, allow this once   # STILL ON YES - NOT CHANGING!
```

## Investigation Completed

### ✅ Things Confirmed Working:
1. **Render method uses correct property** (`modules/multiline_input.py:271`)
   - Uses `self.permission_selected_option` to determine which option is selected

2. **TUI sets initial selection** (`modules/tui/permission_handlers.py:378`)
   - Sets `prompt_data['selected'] = 0` before showing prompt

3. **Watcher syncs dict to reactive property** (`modules/multiline_input.py:656`)
   - `watch_permission_prompt_data()` copies `prompt_data['selected']` → `self.permission_selected_option`

4. **on_key() handler has correct logic** (`modules/multiline_input.py:366-381`)
   - Checks `key == "down"`
   - Updates `self.permission_selected_option += 1`
   - Calls `self.refresh()`

5. **action_permission_down() has correct logic** (`modules/multiline_input.py:549-564`)
   - Updates selection
   - Calls `self.refresh()`

### ❓ Things NOT Yet Confirmed:
1. **Is on_key() actually being called when DOWN is pressed?**
2. **What key name is Textual receiving?** (is it "down", "Down", or something else?)
3. **Is the widget focused when DOWN is pressed?**
4. **Is there a Textual BINDINGS conflict?**

## Debug Logging Added

I've added comprehensive debug logging to trace the exact flow:

### In `on_key()` method (line 334-340):
```python
sys.stderr.write(f"\n[MultiLineInput.on_key] ====== KEY EVENT ======\n")
sys.stderr.write(f"[MultiLineInput.on_key] KEY='{key}' (type={type(key)})\n")
sys.stderr.write(f"[MultiLineInput.on_key] event.key='{event.key}'\n")
sys.stderr.write(f"[MultiLineInput.on_key] permission_prompt_data={bool(self.permission_prompt_data)}\n")
sys.stderr.write(f"[MultiLineInput.on_key] has_focus={self.has_focus}\n")
```

### In DOWN arrow handler (line 367-379):
```python
sys.stderr.write(f"[MultiLineInput.on_key] DOWN KEY - current={self.permission_selected_option}, options={len(options)}\n")
# ... changes selection ...
sys.stderr.write(f"[MultiLineInput.on_key] DOWN - changed {old_val} -> {self.permission_selected_option}\n")
sys.stderr.write(f"[MultiLineInput.on_key] DOWN - refresh() called\n")
```

### In action_permission_down() (line 552-564):
```python
sys.stderr.write(f"[ACTION_PERMISSION_DOWN] CALLED - prompt={bool(self.permission_prompt_data)}\n")
sys.stderr.write(f"[ACTION_PERMISSION_DOWN] Changing {current} -> {new_val} (max={len(options)-1})\n")
sys.stderr.write(f"[ACTION_PERMISSION_DOWN] refresh() called\n")
```

## How to Test and Capture Debug Output

### Option 1: Manual Test (Recommended)
```bash
# Start opencli with stderr redirect
opencli tui 2>/tmp/opencli_debug.log

# In the TUI:
# 1. Type: /help
# 2. Press ENTER (autocomplete)
# 3. Press ENTER (show permission buffer)
# 4. Press DOWN arrow
# 5. Press Ctrl+C to exit

# View debug output
cat /tmp/opencli_debug.log | grep -E "(KEY EVENT|DOWN KEY|ACTION_PERMISSION|permission_selected)"
```

### Option 2: Automated Test
```bash
# Run the test template
echo "1" | ./test_tui_template.sh 2>&1 | tee /tmp/full_test_output.log

# Check for debug messages
grep -E "(KEY EVENT|DOWN KEY|ACTION_PERMISSION)" /tmp/full_test_output.log
```

## Expected Debug Output (if working correctly)

When DOWN arrow is pressed, you should see:

```
[MultiLineInput.on_key] ====== KEY EVENT ======
[MultiLineInput.on_key] KEY='down' (type=<class 'str'>)
[MultiLineInput.on_key] permission_prompt_data=True
[MultiLineInput.on_key] has_focus=True
[MultiLineInput] INSIDE PERMISSION HANDLER for key=down
[MultiLineInput.on_key] DOWN KEY - current=0, options=2
[MultiLineInput.on_key] DOWN - changed 0 -> 1
[MultiLineInput.on_key] DOWN - refresh() called
```

## Possible Root Causes

### Theory 1: on_key() Not Being Called
- Widget doesn't have focus
- Key event not reaching widget
- Event consumed by parent widget

### Theory 2: Wrong Key Name
- Textual receives "Down" (capital D) instead of "down"
- BINDINGS use "down" but event.key is "Down"
- Case mismatch in key name check

### Theory 3: BINDINGS Conflict
- BINDINGS defined for "up"/"down" (line 33-34)
- BINDINGS call action_permission_up/down
- on_key() calls prevent_default() blocking bindings
- OR bindings consume event before on_key()

### Theory 4: refresh() Not Working
- refresh() is called but doesn't update UI
- Reactive property not triggering re-render
- Layout issue preventing update

## Next Steps

1. **Capture debsug output** using one of the test methods above
2. **Analyze which code path executes:**
   - If NO debug output → on_key() not being called (focus or event issue)
   - If debug shows action_permission_down() → BINDINGS are working, on_key() blocked
   - If debug shows on_key() DOWN handler → check if refresh() actually updates UI
3. **Fix the identified issue**

## Files Modified

- `modules/multiline_input.py` - Added comprehensive debug logging
- Synced to runtime via `./sync_to_runtime.sh`

## Test Results Will Show

The debug output will definitively answer:
✓ Is on_key() being called?
✓ What is the exact key name received?
✓ Is the widget focused?
✓ Which code path executes (on_key vs action)?
✓ Does the selection value actually change?
✓ Is refresh() being called?

Once we have this debug output, we'll know exactly what's broken and can fix it precisely.
