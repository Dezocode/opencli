# Fix Implementation Plan - 50 Task Breakdown
**Date**: 2025-10-21
**Issue**: on_blur() clears permission_prompt_data causing zombie buffer
**Solution**: Remove auto-clear logic from on_blur()

---

## Phase 1: Understanding Current State (Tasks 1-10)

### Task 1: Read Root Cause Document
**File to Read**: `SEMANTIC_ROOT_CAUSE_FOUND.md` (all lines)
**Purpose**: Understand complete context of the bug
**Expected Outcome**: Full understanding of zombie buffer issue
**Test**: Can explain the bug timeline T=0 through T=7

### Task 2: Read Modular on_blur()
**File to Read**: `modules/input_widget/widget.py` lines 59-81
**Lines of Interest**:
- Line 66: `if self.permission_prompt_data:`
- Line 78: `self.permission_prompt_data = None` ← BUG
- Line 79: `self.permission_selected_option = 0`
**Expected Outcome**: Identify exact clearing logic
**Test**: Can point to exact line causing zombie buffer

### Task 3: Read Monolithic on_blur()
**File to Read**: `modules/multiline_input.py` lines 114-134
**Lines of Interest**:
- Line 121: `if self.permission_prompt_data:`
- Line 132: `self.permission_prompt_data = None` ← BUG
- Line 133: `self.permission_selected_option = 0`
**Expected Outcome**: Confirm both versions have same bug
**Test**: Verify both files have identical clearing logic

### Task 4: Document on_blur() Behavior
**Files to Analyze**: Both on_blur() implementations
**Document**:
- What triggers on_blur() (focus loss)
- What it does (clears permission data)
- Why it was added (Constitution Principle V)
- Side effects (zombie buffer)
**Expected Outcome**: Written summary of current behavior
**Test**: Summary explains why arrows don't work

### Task 5: Read Permission Prompt Data Watcher (Modular)
**File to Read**: `modules/input_widget/widget.py`
**Find**: `def watch_permission_prompt_data` method
**Lines of Interest**: Where it sets focus, when it's triggered
**Expected Outcome**: Understand reactive property lifecycle
**Test**: Can explain when watcher fires

### Task 6: Read Permission Prompt Data Watcher (Monolithic)
**File to Read**: `modules/multiline_input.py` lines 646-692
**Lines of Interest**:
- Line 658: `self.permission_selected_option = new_value.get('selected', 0)`
- Lines 662-669: Focus setting attempts
- Lines 682-689: Force focus with app.set_focus()
**Expected Outcome**: Understand how data is initially set
**Test**: Can trace data setting from TUI to widget

### Task 7: Document permission_prompt_data Lifecycle
**Analysis Task**: Map complete lifecycle
**Document**:
- Where it's SET: `_show_permission_prompt()` in TUI
- When it's WATCHED: Reactive property system
- Where it's CLEARED: on_blur(), action_submit(), action_cancel()
**Expected Outcome**: Complete state diagram
**Test**: Diagram shows all state transitions

### Task 8: Document permission_prompt_data Clearing Points
**Files to Analyze**: All files that set permission_prompt_data = None
**Find**:
- `modules/input_widget/widget.py:78` (on_blur)
- `modules/multiline_input.py:132` (on_blur)
- `modules/multiline_input.py:486` (action_submit)
- `modules/multiline_input.py:514` (action_cancel)
**Expected Outcome**: List of all clearing locations
**Test**: No other locations clear the data

### Task 9: Read on_focus() Handler
**File to Read**: `modules/input_widget/widget.py` lines 52-57
**Code**:
```python
def on_focus(self) -> None:
    sys.stderr.write(f"\n[MultiLineInput.on_focus] GAINED FOCUS - prompt={bool(self.permission_prompt_data)}\n")
    self.refresh()
```
**Expected Outcome**: Understand focus gain logging
**Test**: Know what log line indicates focus gained

### Task 10: Document Focus Gain Timing
**Analysis Task**: When does widget gain focus?
**Document**:
- watch_permission_prompt_data calls self.focus()
- _show_permission_prompt calls prompt_input.focus()
- Widget should have focus when permission mode active
**Expected Outcome**: Timeline of focus events
**Test**: Can explain T=2 in semantic timeline

---

## Phase 2: Understanding the Bug (Tasks 11-20)

### Task 11: Read action_submit() Clearing
**File to Read**: `modules/multiline_input.py` lines 469-504
**Line of Interest**: Line 486: `self.permission_prompt_data = None`
**Context**: This is CORRECT - clear after successful selection
**Expected Outcome**: Understand legitimate clear
**Test**: Can explain why this clear is OK

### Task 12: Read action_cancel() Clearing
**File to Read**: `modules/multiline_input.py` lines 505-522
**Line of Interest**: Line 514: `self.permission_prompt_data = None`
**Context**: This is CORRECT - clear after user cancels
**Expected Outcome**: Understand legitimate clear
**Test**: Can explain why this clear is OK

### Task 13: Document Legitimate Clear Paths
**Analysis Task**: Which clears should stay?
**Document**:
- ✅ KEEP: action_submit() clear (user selected option)
- ✅ KEEP: action_cancel() clear (user pressed ESC)
- ❌ REMOVE: on_blur() clear (automatic, not user intent)
**Expected Outcome**: Clear decision on what to change
**Test**: Can justify which clears to remove

### Task 14: Read render() Method
**File to Read**: `modules/input_widget/widget.py` lines 83-100
**Lines of Interest**:
- Line 89: `if self.permission_prompt_data:`
- Line 90-93: `return render_permission_prompt(...)`
**Expected Outcome**: Understand how buffer displays
**Test**: Can explain render caching

### Task 15: Document Zombie Buffer Mechanics
**Analysis Task**: Why does buffer show after data cleared?
**Document**:
- render() called at T=1 when data is set
- Output is rendered and displayed
- At T=4 data is cleared (None)
- But display is not re-rendered immediately
- User sees old render with new state (zombie)
**Expected Outcome**: Complete explanation of visual bug
**Test**: Can explain why user sees non-functional buffer

### Task 16: Read action_permission_down() Implementation
**File to Read**: `modules/multiline_input.py` lines 546-566
**Lines of Interest**:
- Line 552: `if self.permission_prompt_data:` ← This check fails!
- Line 558-563: Selection change logic (never reached)
**Expected Outcome**: Understand why arrows don't work
**Test**: Can trace why method returns early

### Task 17: Read action_permission_up() Implementation
**File to Read**: `modules/multiline_input.py` lines 524-544
**Lines of Interest**:
- Line 530: `if self.permission_prompt_data:` ← This check fails!
- Line 536-541: Selection change logic (never reached)
**Expected Outcome**: Understand why arrows don't work
**Test**: Can trace why method returns early

### Task 18: Document Permission Data Check Logic
**Analysis Task**: Why does check fail?
**Document**:
- action method is called (BINDINGS work)
- Method checks if self.permission_prompt_data
- Data is None (cleared by on_blur at T=4)
- Check fails, method returns early
- No selection change occurs
**Expected Outcome**: Complete flow diagram
**Test**: Can explain the if statement failure

### Task 19: Identify Lines to Comment in widget.py
**File to Modify**: `modules/input_widget/widget.py` lines 59-81
**Exact Lines to Comment Out**:
- Line 77: `self.permission_prompt_data = None`
- Line 78: `self.permission_selected_option = 0`
**Keep These Lines**:
- Line 62-68: Logging (for debugging)
- Line 72: NavigationEvent posting (may need evaluation)
- Line 75: PermissionCancelled posting (may need evaluation)
- Line 81: `self.refresh()`
**Expected Outcome**: Exact line numbers documented
**Test**: Know precisely what to comment

### Task 20: Identify Lines to Comment in multiline_input.py
**File to Modify**: `modules/multiline_input.py` lines 114-134
**Exact Lines to Comment Out**:
- Line 132: `self.permission_prompt_data = None`
- Line 133: `self.permission_selected_option = 0`
**Keep These Lines**:
- Line 117-123: Logging
- Line 126: NavigationEvent posting
- Line 129: PermissionCancelled posting
**Expected Outcome**: Exact line numbers documented
**Test**: Know precisely what to comment

---

## Phase 3: Planning the Fix (Tasks 21-30)

### Task 21: Read Constitution Principle V Context
**File to Read**: `modules/input_widget/widget.py` line 65
**Comment**: `# Constitution Principle V: Auto-dismiss permission prompts on navigation`
**Analysis**: Understand original design intent
**Expected Outcome**: Know why auto-dismiss exists
**Test**: Can explain the principle

### Task 22: Document Auto-Dismiss Rationale
**Analysis Task**: Why was this feature added?
**Document**:
- Intent: Dismiss prompt when user navigates away
- Assumption: Focus loss = user navigation
- Reality: Focus loss = technical glitch
- Bug: False positive triggers zombie buffer
**Expected Outcome**: Written analysis
**Test**: Can argue for removal

### Task 23: Plan Explanatory Comment
**Task**: Write comment to replace deleted code
**Comment Should Explain**:
- Why clearing was removed
- Reference to SEMANTIC_ROOT_CAUSE_FOUND.md
- Note that user must explicitly dismiss (ESC/selection)
**Draft Comment**:
```python
# NOTE: Do NOT auto-clear permission_prompt_data on focus loss
# Focus loss is a technical event, not user intent to dismiss
# User must explicitly dismiss with ESC or make selection
# See: SEMANTIC_ROOT_CAUSE_FOUND.md for details
```
**Expected Outcome**: Clear explanatory comment
**Test**: Future developers understand why

### Task 24: Read PermissionCancelled Posting in on_blur()
**File to Read**: `modules/input_widget/widget.py` line 75
**Code**: `self.post_message(PermissionCancelled())`
**Analysis**: Should this message still be posted?
**Expected Outcome**: Decision on whether to keep/remove
**Test**: Can justify the decision

### Task 25: Read NavigationEvent Posting in on_blur()
**File to Read**: `modules/input_widget/widget.py` line 72
**Code**: `self.post_message(NavigationEvent("focus_lost"))`
**Analysis**: Should this message still be posted?
**Expected Outcome**: Decision on whether to keep/remove
**Test**: Can justify the decision

### Task 26: Document Message Posting After Fix
**Analysis Task**: What messages should on_blur() post?
**Decision**:
- Option A: Remove all message posting (clean break)
- Option B: Keep messages but not clear data
- Option C: Make messages informational only
**Expected Outcome**: Clear decision
**Test**: Can explain message handling

### Task 27: Check If Messages Should Be Removed
**Files to Analyze**: All handlers for these messages
**Search For**:
- Handlers of `PermissionCancelled`
- Handlers of `NavigationEvent`
**Expected Outcome**: Impact analysis
**Test**: Know if removing messages breaks anything

### Task 28: Read PermissionCancelled Handlers
**Files to Search**: `modules/tui/*.py`
**Method**: `grep -r "PermissionCancelled" modules/tui/`
**Expected Outcome**: List of handlers
**Test**: No handlers depend on auto-cancel

### Task 29: Read NavigationEvent Handlers
**Files to Search**: `modules/tui/*.py`
**Method**: `grep -r "NavigationEvent" modules/tui/`
**Expected Outcome**: List of handlers
**Test**: No handlers depend on auto-navigation

### Task 30: Document Message Impact
**Analysis Task**: What breaks if messages not posted?
**Document**:
- Who listens for PermissionCancelled
- Who listens for NavigationEvent
- Impact of not posting on blur
**Expected Outcome**: Risk assessment
**Test**: Know exact impact of change

---

## Phase 4: Test Planning (Tasks 31-40)

### Task 31: Create Manual Test Plan - /help
**Test Procedure**:
1. Run `opencli tui`
2. Type `/help` + ENTER
3. Verify permission buffer appears
4. Check stderr for: `[MultiLineInput.on_focus] GAINED FOCUS`
**Expected Result**: Buffer displays with options
**Pass Criteria**: Buffer visible, focus confirmed
**File Reference**: Output should match render() expectations

### Task 32: Create UP Arrow Test
**Test Procedure**:
1. With permission buffer showing
2. Press UP arrow key
3. Check stderr for: `[MultiLineInput.action_permission_up] ENTERED`
4. Check stderr for: `changed 0 -> -1` or boundary handling
5. Verify visual selection indicator moves
**Expected Result**: Selection moves up (or stays at boundary)
**Pass Criteria**: Logs show method entered and executed
**File Reference**: action_permission_up() lines 524-544

### Task 33: Create DOWN Arrow Test
**Test Procedure**:
1. With permission buffer showing
2. Press DOWN arrow key
3. Check stderr for: `[MultiLineInput.action_permission_down] ENTERED`
4. Check stderr for: `changed 0 -> 1`
5. Verify visual selection indicator moves
**Expected Result**: Selection moves down
**Pass Criteria**: Logs show selection change
**File Reference**: action_permission_down() lines 546-566

### Task 34: Create ENTER Test
**Test Procedure**:
1. Navigate to option with arrows
2. Press ENTER
3. Check stderr for: `[ACTION_SUBMIT] CALLED`
4. Verify PermissionResponse posted
5. Verify permission_prompt_data cleared
6. Verify buffer dismisses
**Expected Result**: Selection confirmed, buffer gone
**Pass Criteria**: action_submit() works, data cleared
**File Reference**: action_submit() lines 469-504

### Task 35: Create ESC Test
**Test Procedure**:
1. With permission buffer showing
2. Press ESC
3. Check stderr for: `[ACTION_CANCEL] CALLED`
4. Verify PermissionCancelled posted
5. Verify permission_prompt_data cleared
6. Verify buffer dismisses
**Expected Result**: Buffer cancelled and gone
**Pass Criteria**: action_cancel() works, data cleared
**File Reference**: action_cancel() lines 505-522

### Task 36: Create Selection Clear Test
**Test Procedure**:
1. Show permission buffer
2. Make selection with ENTER
3. Verify permission_prompt_data = None
4. Verify buffer no longer shows
5. Try typing - should accept normal input
**Expected Result**: Data cleared, normal mode restored
**Pass Criteria**: Selection clears data properly
**File Reference**: action_submit() line 486

### Task 37: Create Cancel Clear Test
**Test Procedure**:
1. Show permission buffer
2. Press ESC to cancel
3. Verify permission_prompt_data = None
4. Verify buffer no longer shows
5. Try typing - should accept normal input
**Expected Result**: Data cleared, normal mode restored
**Pass Criteria**: Cancel clears data properly
**File Reference**: action_cancel() line 514

### Task 38: Create Normal Mode Regression Test
**Test Procedure**:
1. Normal input mode (no buffer)
2. Type regular text
3. Press UP arrow - should show history
4. Press DOWN arrow - should show history
5. Press ENTER - should submit
**Expected Result**: Normal mode unaffected
**Pass Criteria**: No regression in normal behavior
**File Reference**: on_key() normal mode handling

### Task 39: Create Suggestion Mode Test
**Test Procedure**:
1. Type `/` to trigger suggestions
2. Press UP arrow - should navigate suggestions
3. Press DOWN arrow - should navigate suggestions
4. Press ENTER - should select suggestion
**Expected Result**: Suggestions still work
**Pass Criteria**: No regression in suggestion mode
**File Reference**: on_key() suggestion handling

### Task 40: Create Focus Loss Test
**Test Procedure**:
1. Show permission buffer
2. Click on another terminal/app (lose focus)
3. Click back to opencli (regain focus)
4. Try pressing arrows
5. Verify they still work
**Expected Result**: Buffer persists through focus changes
**Pass Criteria**: Arrows work after focus regain
**File Reference**: on_blur() and on_focus()

---

## Phase 5: Documentation & Verification (Tasks 41-50)

### Task 41: Document Expected Log Output
**Create**: Log output reference document
**Include**:
- Normal case logs (permission works)
- Fixed case logs (no data clearing)
- Error case logs (if something wrong)
**Expected Outcome**: Log interpretation guide
**Test**: Can diagnose from logs alone

### Task 42: Create Rollback Plan
**Document**: How to undo the fix
**Steps**:
1. Uncomment lines 77-78 in widget.py
2. Uncomment lines 132-133 in multiline_input.py
3. git revert if needed
4. Restart opencli
**Expected Outcome**: Safe rollback procedure
**Test**: Can quickly undo if needed

### Task 43: Read Existing Permission Tests
**Files to Read**:
- `tests/test_permission_buffer_flow.py`
- `tests/test_permission_buffer_display.py`
- `examples/test_permission_buffer.py`
**Expected Outcome**: Understand test coverage
**Test**: Know what automated tests exist

### Task 44: Check If Automated Tests Need Updates
**Analysis Task**: Will existing tests pass/fail with fix?
**Document**:
- Which tests check on_blur() behavior
- Which tests expect auto-dismiss
- Which tests need updating
**Expected Outcome**: Test update plan
**Test**: No test regressions

### Task 45: Document Active Version
**File to Read**: `modules/tui/core.py` lines 37-46
**Code**:
```python
try:
    from ..multiline_input import MultiLineInput  # Line 38 - PRIMARY
    HAS_MULTILINE = True
except Exception:
    try:
        from ..input_widget import MultiLineInput  # Line 42 - FALLBACK
        HAS_MULTILINE = True
```
**Expected Outcome**: Know which version is active
**Test**: Can identify which file needs fix

### Task 46: Check If Both Versions Need Fixing
**Analysis Task**: Fix one or both?
**Decision**:
- If monolithic is primary → fix that first
- If modular is primary → fix that first
- Should probably fix both for consistency
**Expected Outcome**: Fix scope decision
**Test**: Know exactly what to edit

### Task 47: Read TUI Import Logic
**File to Read**: `modules/tui/core.py` lines 37-46
**Analysis**: Understand primary vs fallback
**Document**:
- Line 38: Primary import (multiline_input)
- Line 42: Fallback import (input_widget)
- Exception handling between imports
**Expected Outcome**: Import precedence clear
**Test**: Can explain which loads first

### Task 48: Document Import Precedence
**Analysis Task**: Which version loads in production?
**Document**:
- Try multiline_input first
- Fall back to input_widget if that fails
- Both should have same fix for safety
**Expected Outcome**: Loading logic documented
**Test**: Know which version is live

### Task 49: Create Comprehensive Fix Documentation
**Create**: FIX_APPLIED.md document
**Include**:
- What was changed (exact lines)
- Why it was changed (root cause)
- How to test (all 10 test procedures)
- How to rollback (if needed)
- Related commits and files
**Expected Outcome**: Complete fix documentation
**Test**: Another developer can understand fix

### Task 50: Document Fix in Semantic Doc
**File to Update**: `SEMANTIC_ROOT_CAUSE_FOUND.md`
**Add Section**: "Fix Applied"
**Include**:
- Date fix applied
- Files modified with line numbers
- Test results
- Any issues encountered
**Expected Outcome**: Complete investigation closed
**Test**: Document is comprehensive record

---

## Summary of Files to Edit

**After completing all 50 tasks, these files will be edited:**

1. **modules/input_widget/widget.py**
   - Lines 77-78: Comment out clearing logic
   - Add explanatory comment

2. **modules/multiline_input.py**
   - Lines 132-133: Comment out clearing logic
   - Add explanatory comment

3. **SEMANTIC_ROOT_CAUSE_FOUND.md**
   - Add "Fix Applied" section

4. **FIX_APPLIED.md** (new file)
   - Complete fix documentation

---

## Testing Matrix

| Test | File Reference | Expected Log | Pass Criteria |
|------|---------------|--------------|---------------|
| /help command | permission_handlers.py:370-404 | Buffer displays | Visual confirmation |
| UP arrow | multiline_input.py:524-544 | action_permission_up ENTERED | Selection moves |
| DOWN arrow | multiline_input.py:546-566 | action_permission_down ENTERED | Selection moves |
| ENTER key | multiline_input.py:469-504 | ACTION_SUBMIT CALLED | Option selected |
| ESC key | multiline_input.py:505-522 | ACTION_CANCEL CALLED | Buffer dismissed |
| Selection clears | multiline_input.py:486 | Data = None | Buffer gone |
| Cancel clears | multiline_input.py:514 | Data = None | Buffer gone |
| Normal mode | multiline_input.py:336-449 | Normal input works | No regression |
| Suggestion mode | multiline_input.py:386-401 | Suggestions work | No regression |
| Focus loss | widget.py:59-81 | Buffer persists | Arrows still work |

---

**All 50 tasks are documented with:**
- ✅ File to read
- ✅ Lines to examine
- ✅ Expected outcome
- ✅ Test criteria
- ✅ NO CODE EDITED (yet)

**Ready to execute once approved.**
