# Arrow Key Visual Test - Using TUI Framework API
## Simple Visual Testing with Dual Windows

---

## QUICK START

```bash
cd /Users/dezmondhollins/opencli
python3 test_arrow_keys_visual.py
```

**That's it!** The framework handles everything.

---

## WHAT HAPPENS

### 1. Two Terminal Windows Open Automatically:

**LEFT Window (opencli TUI)**:
- Shows actual `opencli tui` running
- You can SEE the permission buffer appear
- You can SEE if arrow keys change selection
- Real visual feedback

**RIGHT Window (Test Controller)**:
- Shows test commands being sent
- Shows state collection
- Shows BEFORE/AFTER comparisons
- Shows PASS/FAIL results

### 2. Test Runs Automatically:

```
STEP 1: Type /help command
  ▶ Typing /help

STEP 2: Autocomplete command
  ▶ Pressing ENTER

STEP 3: Submit command
  ▶ Pressing ENTER
  📊 Collecting TUI state...

STEP 4: Collect permission buffer state
  ✅ PERMISSION BUFFER: PRESENT
  ✅ YES/NO OPTIONS: PRESENT

STEP 5: Press DOWN arrow to select No
  📊 State BEFORE down arrow:
     ✅ 'Yes' is selected (default)
  ▶ Pressing DOWN arrow
  📊 State AFTER down arrow:
     ❌ 'No' is NOT selected - DOWN ARROW FAILED!  ← THE PROBLEM

STEP 6: Verify No is selected
  ❌ 'No' is NOT selected - VERIFICATION FAILED

FINAL ANALYSIS:
  ✅ PASS: Permission buffer appeared
  ✅ PASS: Yes/No options shown
  ❌ FAIL: DOWN arrow did NOT change selection  ← ROOT CAUSE
```

### 3. Results Show Exactly What Failed:

```
TEST RESULTS
================================================================================

Status: ❌ FAILED
Message: Test failed - arrow keys not working

📄 Full output log: /tmp/tui_output_log_12345.txt
   View: cat /tmp/tui_output_log_12345.txt
   Search stderr: cat /tmp/tui_output_log_12345.txt | grep -E '\[MultiLineInput|\[TUI'
   Search focus: cat /tmp/tui_output_log_12345.txt | grep -i focus
   Search keys: cat /tmp/tui_output_log_12345.txt | grep -i 'KEY='

📋 Failures:
   ❌ FAIL: DOWN arrow did NOT change selection

✅ Test complete!
```

---

## THE CODE (3 Lines!)

```python
from modules.testing.tui_test_framework import create_permission_buffer_test

# Use convenience API
test = create_permission_buffer_test("/help")

# Run with visual dual windows
result = test.run_test(visual=True)
```

That's literally it! The framework does:
- ✅ Creates tmux session
- ✅ Launches opencli tui in LEFT window
- ✅ Opens controller in RIGHT window
- ✅ Sends all commands automatically
- ✅ Captures stderr to log file
- ✅ Collects state BEFORE/AFTER arrow keys
- ✅ Shows visual comparison
- ✅ Returns pass/fail result

---

## ANALYZE THE LOGS

After the test runs, check the stderr logs to answer critical questions:

### Check if Widget Has Focus:
```bash
cat /tmp/tui_output_log_*.txt | grep -i "on_focus"
```

**Expected (if working)**:
```
[MultiLineInput.on_focus] GAINED FOCUS - prompt=True
```

**If you see NOTHING**: Widget never gained focus → ROOT CAUSE!

### Check if on_key() Receives Arrow Keys:
```bash
cat /tmp/tui_output_log_*.txt | grep "KEY='down'\|KEY='up'"
```

**Expected (if working)**:
```
[MultiLineInput.on_key] 🔥 KEY='down' prompt=True focused=True 🔥
```

**If you see NOTHING**: on_key() is not being called → Events go to parent!

### Check if BINDINGS Fire:
```bash
cat /tmp/tui_output_log_*.txt | grep "action_permission"
```

**Expected (if BINDINGS work)**:
```
[MultiLineInput.action_permission_down] ENTERED
```

**If you see NOTHING**: BINDINGS don't fire either!

### Check if Selection Changes:
```bash
cat /tmp/tui_output_log_*.txt | grep "watch_permission_selected_option"
```

**Expected (if working)**:
```
[MultiLineInput.watch_permission_selected_option] 0 -> 1
```

**If you see NOTHING**: Selection never changed!

---

## INTERPRETATION GUIDE

### Scenario A: No Focus Logs (Most Likely!)
```
❌ NO: [MultiLineInput.on_focus] GAINED FOCUS
❌ NO: [MultiLineInput.on_key] logs
✅ YES: [TUI._show_permission_prompt] (buffer shown)
```

**Diagnosis**: Widget does NOT have focus
**Why**: `focus()` is called but doesn't work (timing/async issue)
**Fix**: Use `call_after_refresh()` or `set_timer()` to set focus AFTER render

### Scenario B: Focus Then Immediately Lost
```
✅ YES: [MultiLineInput.on_focus] GAINED FOCUS
❌ THEN: [MultiLineInput.on_blur] LOST FOCUS
❌ NO: [MultiLineInput.on_key] logs
```

**Diagnosis**: Focus is being stolen
**Why**: Another widget or app steals focus right after setting it
**Fix**: Find what calls `on_blur` and prevent it

### Scenario C: Focus Works, on_key() Silent
```
✅ YES: [MultiLineInput.on_focus] GAINED FOCUS
❌ NO: [MultiLineInput.on_blur] logs
❌ NO: [MultiLineInput.on_key] logs
```

**Diagnosis**: Event routing is broken
**Why**: Widget has focus but on_key() not called
**Fix**: Check Textual event routing, parent on_key() blocking

### Scenario D: BINDINGS Work, on_key() Doesn't
```
❌ NO: [MultiLineInput.on_key] logs for arrows
✅ YES: [MultiLineInput.action_permission_down] ENTERED
✅ YES: Selection changed 0 -> 1
```

**Diagnosis**: BINDINGS override on_key()
**Why**: Textual prioritizes BINDINGS over on_key()
**Fix**: Remove on_key() handling, rely only on BINDINGS

---

## FILES CREATED

1. **test_arrow_keys_visual.py** - Simple visual test (uses convenience API)
2. **test_arrow_keys_with_stderr.py** - Advanced test (with auto-analysis)
3. **RUN_VISUAL_TEST.md** - This documentation

---

## WHICH TEST TO RUN?

### Use `test_arrow_keys_visual.py` if:
- ✅ You want to SEE opencli running (visual feedback)
- ✅ You want simplest code (3 lines)
- ✅ You'll manually check logs afterward

### Use `test_arrow_keys_with_stderr.py` if:
- ✅ You want automatic analysis
- ✅ You want scenario diagnosis
- ✅ You want fix recommendations

**Both tests capture stderr logs to /tmp/tui_output_log_*.txt for analysis!**

---

## RUN THE TEST NOW

```bash
python3 test_arrow_keys_visual.py
```

Watch the dual windows, see where it fails, then check the logs!
