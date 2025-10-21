# Arrow Key Test - TUI Framework API Implementation
## Status: ✅ READY TO RUN

---

## WHAT I CREATED

**File**: `test_arrow_keys_with_stderr.py` (239 lines)

A proper test using the TUI Test Framework API that:
1. ✅ Launches opencli tui in tmux with stderr capture (`2>&1 | tee`)
2. ✅ Sends /help command
3. ✅ Waits for permission buffer
4. ✅ Presses DOWN arrow
5. ✅ Presses UP arrow
6. ✅ Captures ALL stderr logs
7. ✅ Analyzes logs to answer 6 critical questions
8. ✅ Provides diagnosis and fix recommendation

---

## HOW TO RUN

```bash
cd /Users/dezmondhollins/opencli
python3 test_arrow_keys_with_stderr.py
```

**What Happens**:
1. Opens TWO Terminal windows:
   - **LEFT**: opencli tui (actual running instance)
   - **RIGHT**: Test controller (sends commands)
2. Test runs automatically
3. Captures stderr to `/tmp/tui_output_log_<pid>.txt`
4. Analyzes stderr and prints diagnosis
5. Shows which scenario matches and what fix is needed

---

## WHAT IT ANALYZES

The test answers ALL 6 critical questions from SYSTEMATIC_DEBUG_FINDINGS.md:

### Question 1: Was permission buffer shown?
- **Looks for**: `[TUI._show_permission_prompt]`
- **If YES**: ✅ _show_permission_prompt was called
- **If NO**: ❌ Buffer was never shown

### Question 2: Was permission_prompt_data set?
- **Looks for**: `PERMISSION ACTIVE`
- **If YES**: ✅ Data was set, shows which permission
- **If NO**: ❌ Data was NOT set

### Question 3: Did widget gain focus?
- **Looks for**: `[MultiLineInput.on_focus] GAINED FOCUS`
- **Also checks**: If focus was immediately lost (`on_blur`)
- **If YES**: ✅ Widget gained focus
- **If NO**: ❌ Widget NEVER gained focus → **ROOT CAUSE**

### Question 4: Was on_key() called for arrows?
- **Looks for**: `[MultiLineInput.on_key] 🔥 KEY='down'` and `KEY='up'`
- **Also checks**: `focused=True` vs `focused=False`
- **If YES**: ✅ on_key() received events
- **If NO**: ❌ on_key() NEVER called → **ROOT CAUSE**

### Question 5: Were BINDINGS action methods called?
- **Looks for**: `[MultiLineInput.action_permission_down] ENTERED`
- **Also checks**: `action_permission_up`
- **If YES**: ✅ BINDINGS fired (might override on_key)
- **If NO**: ❌ BINDINGS didn't fire either

### Question 6: Did selection change?
- **Looks for**: `[MultiLineInput.watch_permission_selected_option] 0 -> 1`
- **If YES**: ✅ Selection changed (arrows worked!)
- **If NO**: ❌ Selection NEVER changed → **BROKEN**

---

## DIAGNOSIS SCENARIOS

The test automatically diagnoses which scenario is happening:

### Scenario A: FOCUS NEVER GAINED ⚡ (Most Likely)
**Symptoms**:
- ❌ NO `on_focus` logs
- ❌ NO `on_key` logs
- ✅ Buffer shown

**Diagnosis**: Widget does not have focus
**Fix**: Force focus after render completes (use `call_after_refresh` or `set_timer`)

### Scenario B: FOCUS GAINED BUT IMMEDIATELY LOST
**Symptoms**:
- ✅ `on_focus` log
- ❌ Immediately followed by `on_blur`
- ❌ NO `on_key` logs

**Diagnosis**: Focus is being stolen
**Fix**: Prevent focus stealing - check what's calling `on_blur`

### Scenario C: FOCUS WORKS, on_key() NOT CALLED
**Symptoms**:
- ✅ `on_focus` log
- ❌ NO `on_blur` logs
- ❌ NO `on_key` logs

**Diagnosis**: Event routing broken
**Fix**: Check Textual event routing, app configuration

### Scenario D: on_key() CALLED BUT WIDGET NOT FOCUSED
**Symptoms**:
- ✅ `on_key` logs
- ⚠️ BUT `focused=False` in logs

**Diagnosis**: Focus state tracking broken
**Fix**: Fix focus state tracking or event routing

### Scenario E: BINDINGS OVERRIDE on_key()
**Symptoms**:
- ❌ NO `on_key` logs for arrows
- ✅ `action_permission_down` logs

**Diagnosis**: BINDINGS work, on_key() bypassed
**Fix**: Remove on_key() handling, rely only on BINDINGS

### Scenario F: on_key() CALLED, LOGIC FAILS
**Symptoms**:
- ✅ `on_key` logs
- ✅ `focused=True`
- ❌ NO selection change

**Diagnosis**: on_key() logic is broken
**Fix**: Debug on_key() logic - check `permission_prompt_data` checks

---

## EXPECTED OUTPUT

```
╔════════════════════════════════════════════════════════════╗
║  ARROW KEY DEBUG TEST - TUI Test Framework API            ║
║  Capturing stderr to diagnose focus/event routing issues  ║
╚════════════════════════════════════════════════════════════╝

▶ Configuring test...
✅ Test configured with 6 steps

▶ Running visual test (dual terminal windows)...
   LEFT window: opencli tui
   RIGHT window: Test controller

⏳ Test will run automatically...
   Waiting for results...

================================================================================
TUI TEST FRAMEWORK RESULT
================================================================================

Test Status: ❌ FAILED
Message: Test failed - arrow keys not working

▶ Analyzing stderr logs from: /tmp/tui_output_log_12345.txt

================================================================================
STDERR LOG ANALYSIS RESULTS
================================================================================

📁 Log File: /tmp/tui_output_log_12345.txt
📊 Log Size: 45,231 bytes

────────────────────────────────────────────────────────────────────────────────
CRITICAL QUESTIONS
────────────────────────────────────────────────────────────────────────────────

1. Was permission buffer shown?
   ✅ _show_permission_prompt was called

2. Was permission_prompt_data set?
   ✅ permission_prompt_data was set
   Type: System: /help

3. Did widget gain focus?
   ❌ Widget NEVER gained focus

4. Was on_key() called for arrows?
   DOWN: ❌ on_key() NEVER received DOWN key
   UP: ❌ on_key() NEVER received UP key

5. Were BINDINGS action methods called?
   DOWN: ❌ action_permission_down was NEVER called
   UP: ❌ action_permission_up was NEVER called

6. Did selection change?
   ❌ Selection NEVER changed

================================================================================
DIAGNOSIS
================================================================================

🔍 Scenario A: FOCUS NEVER GAINED

💡 FIX NEEDED:
   Force focus after render completes (use call_after_refresh or set_timer)

================================================================================

📄 Full logs available at: /tmp/tui_output_log_12345.txt
   View with: cat /tmp/tui_output_log_12345.txt
   Search: cat /tmp/tui_output_log_12345.txt | grep -i 'on_key\|focus\|permission'

▶ Cleaning up...

✅ Test complete!
```

---

## FILES CREATED

1. **test_arrow_keys_with_stderr.py** (239 lines)
   - Main test script using TUI Test Framework API
   - Configures 6 test steps
   - Analyzes stderr logs
   - Provides diagnosis

2. **ARROW_KEY_TEST_READY.md** (this file)
   - Documentation on how to run
   - Expected output
   - Diagnosis scenarios

---

## ADVANTAGES OVER MANUAL TESTING

1. ✅ **Automated**: No manual interaction needed
2. ✅ **Comprehensive**: Checks all 6 critical questions
3. ✅ **Visual**: See opencli running in real-time (LEFT window)
4. ✅ **Diagnostic**: Automatically identifies scenario and fix
5. ✅ **Repeatable**: Same test every time
6. ✅ **Stderr Captured**: All debug logs preserved
7. ✅ **Framework-Based**: Uses existing TUI test infrastructure

---

## NEXT STEPS

1. **Run the test**:
   ```bash
   python3 test_arrow_keys_with_stderr.py
   ```

2. **Read the diagnosis**:
   - Test will show which scenario (A-F) is happening
   - Will show exactly what fix is needed

3. **Apply the fix**:
   - Based on diagnosis, apply targeted fix
   - Re-run test to verify fix works

4. **If still failing**:
   - Check full logs: `cat /tmp/tui_output_log_*.txt`
   - Search for specific events: `grep -i 'focus\|on_key' /tmp/tui_output_log_*.txt`

---

## WHY THIS IS BETTER THAN CAPTURE_STDERR_SIMPLE.sh

| Feature | CAPTURE_STDERR_SIMPLE.sh | test_arrow_keys_with_stderr.py |
|---------|-------------------------|-------------------------------|
| Uses TUI Framework | ❌ No | ✅ Yes |
| Visual Windows | ❌ No | ✅ Yes (dual terminal) |
| Automated | ❌ Manual interaction | ✅ Fully automated |
| Stderr Capture | ✅ Yes | ✅ Yes |
| Analysis | ❌ Basic grep | ✅ Comprehensive Python analysis |
| Diagnosis | ❌ No | ✅ Automatic scenario detection |
| Fix Recommendation | ❌ No | ✅ Exact fix needed |
| Repeatable | ⚠️ Manual | ✅ Automated |

---

## READY TO RUN!

```bash
cd /Users/dezmondhollins/opencli
python3 test_arrow_keys_with_stderr.py
```

The test will:
1. Open two Terminal windows
2. Run automatically
3. Show diagnosis
4. Tell you EXACTLY what to fix

**No more guessing - we'll have the answer!**
