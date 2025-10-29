# Permission System Diagnostic Guide

## Current State

All structural fixes have been applied to the permission system:

1. ✅ **Fix 1 (Commit 5 - abeedb1):** `custom_prompt_func` now stored in `registration.metadata`
2. ✅ **Fix 2 (Commit 6 - a89043c):** `handler_name` now stored directly in manager
3. ✅ **Fix 3 (Commit 7 - 0e1c1f4):** Diagnostic logging added to trace flow

## Diagnostic Logging

Three trace log files help identify where the permission flow breaks:

### Log Files

1. **`/tmp/opencli_route_trace.log`**
   - Written by: `route_command_unified()`
   - Location: `modules/command_router.py`
   - Confirms: Command routing is being called

2. **`/tmp/opencli_permission_trace.log`**
   - Written by: `check_permission()`
   - Location: `modules/permissions/integration.py`
   - Confirms: Permission check is being called
   - Shows: Whether metadata has `custom_prompt_func`

3. **`/tmp/opencli_show_prompt_trace.log`**
   - Written by: `show_permission_prompt()`
   - Location: `modules/permissions/integration.py`
   - Confirms: Prompt display function is being called
   - Shows: Whether UI callback is set

### How to Diagnose

```bash
# 1. Clear old logs
rm /tmp/opencli_*_trace.log 2>/dev/null

# 2. Run TUI
opencli tui 2>&1 | tee /tmp/opencli_full.log

# 3. Type /help and press Enter (twice if needed)

# 4. Check which files exist
ls -la /tmp/opencli_*_trace.log

# 5. Read the logs
echo "=== ROUTE TRACE ==="
cat /tmp/opencli_route_trace.log 2>/dev/null || echo "File not found - route_command_unified NOT called"

echo ""
echo "=== PERMISSION TRACE ==="
cat /tmp/opencli_permission_trace.log 2>/dev/null || echo "File not found - check_permission NOT called"

echo ""
echo "=== SHOW PROMPT TRACE ==="
cat /tmp/opencli_show_prompt_trace.log 2>/dev/null || echo "File not found - show_permission_prompt NOT called"
```

## Interpreting Results

### Scenario 1: No trace files created
**Problem:** Command routing not being called at all  
**Possible causes:**
- Command suggestion system bypassing normal flow
- Different code path for autocomplete selections
- Exception before route_command_unified is called

### Scenario 2: Only route_trace.log exists
**Problem:** Permission check not being reached  
**Possible causes:**
- Exception in route_command or execute_command
- Command not registered correctly
- Registration lookup failing

### Scenario 3: route_trace.log + permission_trace.log exist
**Problem:** show_permission_prompt not being called  
**Check permission_trace.log for:**
- `Requires approval: False` → Command doesn't require approval
- `Has custom_prompt_func: False` → Metadata fix not applied correctly
- Exception before calling request_permission

### Scenario 4: All three logs exist
**Problem:** Prompt shown but not visible  
**Check show_prompt_trace.log for:**
- `Has UI callback: False` → TUI didn't set callback (check on_mount)
- `Has UI callback: True` → UI callback called, check MultiLineInput rendering

## Expected Flow

```
User types /help + Enter
  ↓
CommandSuggestionSelect message
  ↓
on_multi_line_input_command_suggestion_select
  ↓
_handle_user_message
  ↓ (writes: "Executing command: /help")
route_command_unified ← TRACE 1
  ↓
CommandRouter.route_command  
  ↓
ExecutionSystem.execute_command
  ↓
UnifiedPermissionManager.check_permission ← TRACE 2
  ↓
request_permission
  ↓
show_permission_prompt ← TRACE 3
  ↓
_ui_callback (TUI._show_permission_prompt)
  ↓
MultiLineInput.permission_prompt_data = {...}
  ↓
User sees prompt and can select with arrows
```

## Known Issues to Check

### Issue: stderr vs stdout
The original log file (`/tmp/permission_state_v2.log`) might not capture stderr.
**Solution:** Use `2>&1` to redirect stderr to stdout

### Issue: Log buffering
Logs might not appear immediately due to buffering.
**Solution:** Force flush after writes (already done in code)

### Issue: Multiple TUI instances
Previous TUI might hold locks or file handles.
**Solution:** Kill all opencli processes before testing

## Quick Test Commands

```bash
# Test 1: Verify fixes are present
python3 diagnose_permission_flow.py

# Test 2: Check if route_command_unified is defined
grep -n "async def route_command_unified" modules/command_router.py

# Test 3: Check if /help is registered correctly
grep -A5 "'/help'" modules/commands/command_registry.py

# Test 4: Check if metadata fix is present
grep -n "custom_prompt_func = kwargs.pop" modules/registry.py
```

## Manual Verification

If all traces show the functions are being called but prompts still don't appear:

1. **Check MultiLineInput rendering:**
   ```python
   # In modules/input_widget/widget.py, line 322:
   if self.permission_prompt_data:
       return render_permission_prompt(...)
   ```

2. **Check TUI callback is set:**
   ```python
   # In modules/tui/core.py, around line 230:
   self.permission_manager.set_ui_callback(self._show_permission_prompt)
   ```

3. **Check _show_permission_prompt:**
   ```python
   # In modules/tui/permission_handlers.py, line 407:
   prompt_input.permission_prompt_data = prompt_data
   ```

## Contact Points

If you still see "Executing command: /help" but no trace logs:

1. Check if stderr is being redirected properly
2. Check if logs are going to a different location
3. Share the output of:
   ```bash
   opencli tui 2>&1 | tee /tmp/full_output.log
   # Then type /help
   # Then share /tmp/full_output.log
   ```

---

**Status:** Waiting for diagnostic log output to identify where flow breaks.
