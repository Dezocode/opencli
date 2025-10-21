# TODO: Fix Zombie Buffer - on_blur() Clearing Issue

**Issue**: on_blur() clears permission_prompt_data causing arrows to not work
**Root Cause**: SEMANTIC_ROOT_CAUSE_FOUND.md
**Files Affected**: modules/input_widget/widget.py, modules/multiline_input.py

---

## PHASE 1: UNDERSTANDING CURRENT STATE

### ☐ Task 1: Read root cause document
**Read**: `SEMANTIC_ROOT_CAUSE_FOUND.md` (all lines)
**Edit**: None (reading only)
**Test**: Explain the bug timeline T=0 through T=7 from memory

---

### ☐ Task 2: Read modular on_blur() method
**Read**: `modules/input_widget/widget.py` lines 59-81
**Edit**: None (reading only)
**Lines of Interest**:
- Line 66: `if self.permission_prompt_data:`
- Line 78: `self.permission_prompt_data = None` ← THE BUG
- Line 79: `self.permission_selected_option = 0`
**Test**: Point to exact line causing zombie buffer

---

### ☐ Task 3: Read monolithic on_blur() method
**Read**: `modules/multiline_input.py` lines 114-134
**Edit**: None (reading only)
**Lines of Interest**:
- Line 121: `if self.permission_prompt_data:`
- Line 132: `self.permission_prompt_data = None` ← THE BUG
- Line 133: `self.permission_selected_option = 0`
**Test**: Confirm both files have identical bug

---

### ☐ Task 4: Read permission data watcher (modular)
**Read**: `modules/input_widget/widget.py` - find `def watch_permission_prompt_data`
**Edit**: None (reading only)
**Test**: Explain when reactive watcher fires and what it does

---

### ☐ Task 5: Read permission data watcher (monolithic)
**Read**: `modules/multiline_input.py` lines 646-692
**Edit**: None (reading only)
**Lines of Interest**:
- Line 658: Initial selection setting
- Lines 662-669: Focus setting attempts
- Lines 682-689: Force focus with app.set_focus()
**Test**: Trace how permission_prompt_data gets set initially

---

### ☐ Task 6: Read on_focus() handler
**Read**: `modules/input_widget/widget.py` lines 52-57
**Edit**: None (reading only)
**Test**: Identify log line that confirms focus gained

---

### ☐ Task 7: Read render() method for zombie buffer
**Read**: `modules/input_widget/widget.py` lines 83-100
**Edit**: None (reading only)
**Lines of Interest**:
- Line 89: `if self.permission_prompt_data:`
- Lines 90-93: Render permission prompt
**Test**: Explain why buffer shows even after data is None

---

### ☐ Task 8: Read action_permission_down()
**Read**: `modules/multiline_input.py` lines 546-566
**Edit**: None (reading only)
**Lines of Interest**:
- Line 552: `if self.permission_prompt_data:` ← Check that fails
- Line 554: Log "options_count"
- Line 560-563: Selection change logic
**Test**: Trace why method returns early without changing selection

---

### ☐ Task 9: Read action_permission_up()
**Read**: `modules/multiline_input.py` lines 524-544
**Edit**: None (reading only)
**Lines of Interest**:
- Line 530: `if self.permission_prompt_data:` ← Check that fails
- Line 532: Log "options_count"
- Line 538-541: Selection change logic
**Test**: Trace why method returns early without changing selection

---

### ☐ Task 10: Map all permission_prompt_data clearing locations
**Read**: Search both files for `permission_prompt_data = None`
**Edit**: None (reading only)
**Locations to Find**:
- widget.py:78 (on_blur) ← TO REMOVE
- multiline_input.py:132 (on_blur) ← TO REMOVE
- multiline_input.py:486 (action_submit) ← KEEP
- multiline_input.py:514 (action_cancel) ← KEEP
**Test**: List all 4 locations and mark which to remove vs keep

---

## PHASE 2: PLANNING THE FIX

### ☐ Task 11: Read action_submit() clearing logic
**Read**: `modules/multiline_input.py` lines 469-504
**Edit**: None (reading only)
**Line of Interest**: Line 486: `self.permission_prompt_data = None`
**Test**: Explain why this clear is CORRECT (user selected option)

---

### ☐ Task 12: Read action_cancel() clearing logic
**Read**: `modules/multiline_input.py` lines 505-522
**Edit**: None (reading only)
**Line of Interest**: Line 514: `self.permission_prompt_data = None`
**Test**: Explain why this clear is CORRECT (user pressed ESC)

---

### ☐ Task 13: Document legitimate vs problematic clears
**Read**: All clearing locations from Task 10
**Edit**: None (analysis only)
**Analysis**:
- ✅ action_submit() clear = User intent (KEEP)
- ✅ action_cancel() clear = User intent (KEEP)
- ❌ on_blur() clear = Automatic, not user intent (REMOVE)
**Test**: Justify which clears to remove and why

---

### ☐ Task 14: Read Constitution Principle V comment
**Read**: `modules/input_widget/widget.py` line 65
**Edit**: None (reading only)
**Comment**: `# Constitution Principle V: Auto-dismiss permission prompts on navigation`
**Test**: Explain original design intent behind auto-dismiss

---

### ☐ Task 15: Analyze auto-dismiss assumption
**Read**: on_blur() implementations in both files
**Edit**: None (analysis only)
**Analysis**:
- Design Assumption: Focus loss = User navigated away
- Reality: Focus loss = Technical glitch (widget focus instability)
- Result: False positive triggers zombie buffer
**Test**: Explain why auto-dismiss assumption is incorrect

---

### ☐ Task 16: Read PermissionCancelled message posting
**Read**:
- `modules/input_widget/widget.py` line 75
- `modules/multiline_input.py` line 129
**Edit**: None (reading only)
**Code**: `self.post_message(PermissionCancelled())`
**Test**: Decide if this message should still be posted after fix

---

### ☐ Task 17: Read NavigationEvent message posting
**Read**:
- `modules/input_widget/widget.py` line 72
- `modules/multiline_input.py` line 126
**Edit**: None (reading only)
**Code**: `self.post_message(NavigationEvent("focus_lost"))`
**Test**: Decide if this message should still be posted after fix

---

### ☐ Task 18: Search for PermissionCancelled handlers
**Read**: Run `grep -rn "PermissionCancelled" modules/tui/`
**Edit**: None (searching only)
**Test**: List all handlers and assess if removing message posting breaks anything

---

### ☐ Task 19: Search for NavigationEvent handlers
**Read**: Run `grep -rn "NavigationEvent" modules/tui/`
**Edit**: None (searching only)
**Test**: List all handlers and assess if removing message posting breaks anything

---

### ☐ Task 20: Draft explanatory comment for fix
**Read**: None
**Edit**: None (drafting only)
**Draft Comment**:
```python
# NOTE: Do NOT auto-clear permission_prompt_data on focus loss
# Focus loss is a technical event, not user intent to dismiss prompt
# User must explicitly dismiss with ESC or make selection with ENTER
# Root cause: on_blur() was creating "zombie buffers" - visible but non-functional
# See: SEMANTIC_ROOT_CAUSE_FOUND.md for complete analysis
```
**Test**: Comment clearly explains why clearing was removed

---

## PHASE 3: IMPLEMENTING THE FIX

### ☐ Task 21: Backup current widget.py
**Read**: None
**Edit**: `cp modules/input_widget/widget.py modules/input_widget/widget.py.backup`
**Test**: Verify backup file exists

---

### ☐ Task 22: Comment out clearing in widget.py
**Read**: `modules/input_widget/widget.py` lines 77-79
**Edit**: `modules/input_widget/widget.py` lines 77-79
**Change**:
```python
# OLD:
        self.permission_prompt_data = None
        self.permission_selected_option = 0

# NEW:
        # NOTE: Do NOT auto-clear permission_prompt_data on focus loss
        # Focus loss is a technical event, not user intent to dismiss prompt
        # User must explicitly dismiss with ESC or make selection with ENTER
        # See: SEMANTIC_ROOT_CAUSE_FOUND.md for complete analysis
        # self.permission_prompt_data = None
        # self.permission_selected_option = 0
```
**Test**: File saved, lines 77-79 commented out, comment added

---

### ☐ Task 23: Decide on message posting in widget.py on_blur()
**Read**: `modules/input_widget/widget.py` lines 72-75
**Edit**: `modules/input_widget/widget.py` lines 72-75 (conditional)
**Decision Options**:
- Option A: Keep message posting (informational only)
- Option B: Comment out message posting too
**Recommended**: Option B - comment out messages too
**Change** (if Option B):
```python
# OLD:
        self.post_message(NavigationEvent("focus_lost"))
        self.post_message(PermissionCancelled())

# NEW:
        # NOTE: Don't post auto-cancel messages on focus loss
        # self.post_message(NavigationEvent("focus_lost"))
        # self.post_message(PermissionCancelled())
```
**Test**: Decision documented, changes made if applicable

---

### ☐ Task 24: Verify widget.py on_blur() after edits
**Read**: `modules/input_widget/widget.py` lines 59-81
**Edit**: None (verification only)
**Expected State**:
```python
def on_blur(self) -> None:
    """Track when widget loses focus"""
    sys.stderr.write(f"\n[MultiLineInput.on_blur] LOST FOCUS - prompt={bool(self.permission_prompt_data)}\n")
    sys.stderr.flush()

    # Constitution Principle V was here - removed, see SEMANTIC_ROOT_CAUSE_FOUND.md
    # Don't auto-clear or auto-cancel on focus loss

    self.refresh()
```
**Test**: File looks correct, no syntax errors

---

### ☐ Task 25: Backup current multiline_input.py
**Read**: None
**Edit**: `cp modules/multiline_input.py modules/multiline_input.py.backup`
**Test**: Verify backup file exists

---

### ☐ Task 26: Comment out clearing in multiline_input.py
**Read**: `modules/multiline_input.py` lines 131-133
**Edit**: `modules/multiline_input.py` lines 131-133
**Change**:
```python
# OLD:
        self.permission_prompt_data = None
        self.permission_selected_option = 0

# NEW:
        # NOTE: Do NOT auto-clear permission_prompt_data on focus loss
        # Focus loss is a technical event, not user intent to dismiss prompt
        # User must explicitly dismiss with ESC or make selection with ENTER
        # See: SEMANTIC_ROOT_CAUSE_FOUND.md for complete analysis
        # self.permission_prompt_data = None
        # self.permission_selected_option = 0
```
**Test**: File saved, lines 131-133 commented out, comment added

---

### ☐ Task 27: Decide on message posting in multiline_input.py on_blur()
**Read**: `modules/multiline_input.py` lines 126-129
**Edit**: `modules/multiline_input.py` lines 126-129 (conditional)
**Decision**: Same as Task 23
**Change** (if commenting out):
```python
# OLD:
        self.post_message(self.NavigationEvent("focus_lost"))
        self.post_message(self.PermissionCancelled())

# NEW:
        # NOTE: Don't post auto-cancel messages on focus loss
        # self.post_message(self.NavigationEvent("focus_lost"))
        # self.post_message(self.PermissionCancelled())
```
**Test**: Decision documented, changes made if applicable

---

### ☐ Task 28: Verify multiline_input.py on_blur() after edits
**Read**: `modules/multiline_input.py` lines 114-134
**Edit**: None (verification only)
**Expected State**: Similar to Task 24, clearing logic commented out
**Test**: File looks correct, no syntax errors

---

### ☐ Task 29: Check Python syntax of edited files
**Read**: None
**Edit**: None (validation only)
**Command**:
```bash
python3 -m py_compile modules/input_widget/widget.py
python3 -m py_compile modules/multiline_input.py
```
**Test**: No syntax errors reported

---

### ☐ Task 30: Determine which version is active
**Read**: `modules/tui/core.py` lines 37-46
**Edit**: None (reading only)
**Code**:
```python
try:
    from ..multiline_input import MultiLineInput  # PRIMARY
except Exception:
    try:
        from ..input_widget import MultiLineInput  # FALLBACK
```
**Test**: Know which version loads (monolithic = primary)

---

## PHASE 4: TESTING THE FIX

### ☐ Task 31: Test - Permission buffer displays
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. Run `opencli tui 2>&1 | tee /tmp/opencli-test.log`
2. Type `/help` + ENTER
3. Look for: `[MultiLineInput.on_focus] GAINED FOCUS`
4. Verify permission buffer shows on screen
**Expected Result**: Buffer displays with "Yes" and "No" options
**Pass Criteria**: Buffer visible, focus log seen

---

### ☐ Task 32: Test - Focus loss doesn't clear data
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. With buffer showing, check /tmp/opencli-test.log
2. Look for: `[MultiLineInput.on_blur] LOST FOCUS`
3. If on_blur logged, verify NO "auto-dismissing" message
4. Verify buffer still shows (not dismissed)
**Expected Result**: Focus loss logged but data NOT cleared
**Pass Criteria**: No auto-dismiss message in logs

---

### ☐ Task 33: Test - DOWN arrow works
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. With buffer showing, press DOWN arrow
2. Check log for: `[MultiLineInput.action_permission_down] ENTERED`
3. Check log for: `options_count=2, current=0`
4. Check log for: `changed 0 -> 1`
5. Verify selection indicator moves to "No"
**Expected Result**: Selection moves from "Yes" to "No"
**Pass Criteria**: Logs show action called AND selection changed

---

### ☐ Task 34: Test - UP arrow works (boundary)
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. With selection on "Yes" (0), press UP arrow
2. Check log for: `[MultiLineInput.action_permission_up] ENTERED`
3. Verify selection stays at "Yes" (boundary check)
**Expected Result**: Selection stays at top (doesn't go negative)
**Pass Criteria**: Boundary handling works correctly

---

### ☐ Task 35: Test - DOWN arrow from bottom (boundary)
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. Navigate to "No" option (last)
2. Press DOWN arrow
3. Verify selection stays at "No"
**Expected Result**: Selection stays at bottom (doesn't overflow)
**Pass Criteria**: Boundary handling works correctly

---

### ☐ Task 36: Test - ENTER confirms selection
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. Navigate to option with arrows
2. Press ENTER
3. Check log for: `[ACTION_SUBMIT] CALLED`
4. Check log for: `Selecting permission option: ...`
5. Verify permission_prompt_data cleared (buffer gone)
6. Verify command executes
**Expected Result**: Selection confirmed, buffer dismissed
**Pass Criteria**: action_submit works, data cleared

---

### ☐ Task 37: Test - ESC cancels buffer
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. Show permission buffer with /help
2. Press ESC
3. Check log for: `[ACTION_CANCEL] CALLED`
4. Verify buffer dismissed
5. Verify permission_prompt_data cleared
**Expected Result**: Buffer cancelled and gone
**Pass Criteria**: action_cancel works, data cleared

---

### ☐ Task 38: Test - Selection clears data properly
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. Show buffer, make selection with ENTER
2. Verify buffer no longer visible
3. Type regular text
4. Verify normal input works
**Expected Result**: After selection, normal mode restored
**Pass Criteria**: Can type normally after selection

---

### ☐ Task 39: Test - Cancel clears data properly
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. Show buffer, press ESC
2. Verify buffer no longer visible
3. Type regular text
4. Verify normal input works
**Expected Result**: After cancel, normal mode restored
**Pass Criteria**: Can type normally after cancel

---

### ☐ Task 40: Test - Normal mode UP/DOWN (regression)
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. Normal input mode (no buffer)
2. Type some text, press ENTER
3. Press UP arrow - should show previous command
4. Press DOWN arrow - should clear/next
**Expected Result**: History navigation works
**Pass Criteria**: No regression in normal arrow behavior

---

### ☐ Task 41: Test - Suggestion mode (regression)
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. Type `/` to trigger suggestions
2. Press UP arrow - navigate suggestions
3. Press DOWN arrow - navigate suggestions
4. Press ENTER - select suggestion
**Expected Result**: Suggestions still work
**Pass Criteria**: No regression in suggestion mode

---

### ☐ Task 42: Test - Multiple focus loss/gain cycles
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. Show permission buffer
2. Click away (lose focus)
3. Click back (gain focus)
4. Press arrows
5. Verify they work
6. Repeat 3-5 times
**Expected Result**: Arrows work through focus cycles
**Pass Criteria**: Buffer persists, navigation works after regain

---

### ☐ Task 43: Test - Rapid arrow pressing
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. Show permission buffer
2. Rapidly press DOWN DOWN DOWN UP UP DOWN
3. Verify selection follows each press
4. Check logs for each action call
**Expected Result**: Every arrow press logged and handled
**Pass Criteria**: No lost keypresses, selection accurate

---

### ☐ Task 44: Test - Different permission prompts
**Read**: None
**Edit**: None (testing only)
**Test Procedure**:
1. Test /help (2 options)
2. Test other commands with permission prompts
3. Verify arrows work for all
**Expected Result**: Fix works for all permission prompts
**Pass Criteria**: Consistent behavior across commands

---

### ☐ Task 45: Analyze test logs for issues
**Read**: `/tmp/opencli-test.log`
**Edit**: None (analysis only)
**Look For**:
- Any unexpected errors
- Any "NO permission_prompt_data!" messages (should be NONE)
- All action methods entering and executing
- Clean focus gain/loss cycles
**Test**: Log analysis document created with findings

---

## PHASE 5: DOCUMENTATION

### ☐ Task 46: Create FIX_APPLIED.md
**Read**: Test results from Tasks 31-45
**Edit**: Create new file `FIX_APPLIED.md`
**Content**:
```markdown
# Fix Applied: Zombie Buffer - on_blur() Clearing

## Date Applied: [DATE]

## Files Modified:
- modules/input_widget/widget.py lines 77-79 (commented out clearing)
- modules/multiline_input.py lines 131-133 (commented out clearing)

## Changes Made:
[Exact code changes]

## Test Results:
[All 15 test results from Tasks 31-45]

## Issues Encountered:
[Any problems during fix or testing]

## Rollback Procedure:
[Steps to undo if needed]
```
**Test**: Document is complete and accurate

---

### ☐ Task 47: Update SEMANTIC_ROOT_CAUSE_FOUND.md
**Read**: `SEMANTIC_ROOT_CAUSE_FOUND.md`
**Edit**: `SEMANTIC_ROOT_CAUSE_FOUND.md` - add section at end
**Add Section**:
```markdown
---

## FIX APPLIED

**Date**: [DATE]
**Applied By**: [NAME]
**Branch**: claude/dev16-011CULSTdSenV3HeSxUrUbFT

**Files Modified**:
- modules/input_widget/widget.py:77-79
- modules/multiline_input.py:131-133

**Solution Used**: Solution 3 (recommended)
- Removed auto-clear on focus loss
- User must explicitly dismiss with ESC or selection
- Messages posting also commented out

**Test Results**: PASS
- All 15 tests passing
- No regressions found
- Arrow navigation works correctly
- Focus loss doesn't break buffer

**Status**: RESOLVED ✅
```
**Test**: Section added, document updated

---

### ☐ Task 48: Check existing automated tests
**Read**:
- `tests/test_permission_buffer_flow.py`
- `tests/test_permission_buffer_display.py`
**Edit**: None (analysis only)
**Analysis**: Do tests pass with fix? Do any need updates?
**Test**: Document test compatibility

---

### ☐ Task 49: Update automated tests if needed
**Read**: Test files from Task 48
**Edit**: Test files (if needed based on Task 48 analysis)
**Changes**: Update any tests expecting auto-dismiss behavior
**Test**: All automated tests pass

---

### ☐ Task 50: Create comprehensive commit
**Read**: None
**Edit**: None (git commit)
**Commit Message**:
```
fix: Remove on_blur() auto-clear to resolve zombie buffer

PROBLEM:
on_blur() was clearing permission_prompt_data when widget lost focus,
creating "zombie buffers" - visible on screen but non-functional.
Arrow keys didn't work because action methods checked for data and found None.

ROOT CAUSE:
Widget loses focus briefly after permission prompt displays.
on_blur() clears data thinking user navigated away.
But user is still looking at buffer (cached render).
When user presses arrows, data is already gone.

SOLUTION:
Removed auto-clear logic from on_blur() in both versions:
- modules/input_widget/widget.py:77-79 (commented out)
- modules/multiline_input.py:131-133 (commented out)

User must now explicitly dismiss with ESC or make selection with ENTER.
Focus loss is a technical event, not user intent.

TESTING:
- ✅ UP/DOWN arrows work in permission buffer
- ✅ ENTER confirms selection (data cleared correctly)
- ✅ ESC cancels buffer (data cleared correctly)
- ✅ Focus loss doesn't break navigation
- ✅ No regressions in normal/suggestion modes

REFERENCE:
- SEMANTIC_ROOT_CAUSE_FOUND.md (complete analysis)
- FIX_APPLIED.md (test results)
- TODO_FIX_ZOMBIE_BUFFER.md (implementation checklist)

Fixes: Zombie buffer issue
See: SEMANTIC_ROOT_CAUSE_FOUND.md
```
**Test**: Commit created with detailed message

---

## COMPLETION CHECKLIST

- [ ] All 50 tasks completed
- [ ] Both files modified correctly
- [ ] All 15 tests passing
- [ ] Documentation updated
- [ ] Commit created
- [ ] Changes pushed to branch

---

## ROLLBACK PROCEDURE

If fix causes issues:

1. **Restore backups**:
```bash
cp modules/input_widget/widget.py.backup modules/input_widget/widget.py
cp modules/multiline_input.py.backup modules/multiline_input.py
```

2. **Or git revert**:
```bash
git revert HEAD
```

3. **Verify rollback**:
```bash
git diff HEAD~1 modules/input_widget/widget.py
git diff HEAD~1 modules/multiline_input.py
```

---

**END OF TODO LIST**

Total Tasks: 50
Research Tasks: 20
Implementation Tasks: 8
Testing Tasks: 15
Documentation Tasks: 7
