# Systematic Debug Findings - Arrow Keys Not Working
## Started: 2025-10-20

---

## Task 1: Read Runtime multiline_input.py ✅ COMPLETE

**File**: `/Users/dezmondhollins/.opencli/cli/modules/multiline_input.py`
**Total Lines**: 697
**Status**: Fix applied at lines 353-365 (fourth fix attempt)

### SECTION 1: Imports and Class Declaration (Lines 1-28)

```python
from textual.widget import Widget
from textual.message import Message
from textual.binding import Binding
from textual.reactive import reactive
```

**Findings:**
- ✅ All imports correct
- ✅ `Binding` imported from `textual.binding` (required for BINDINGS)
- ✅ `reactive` imported from `textual.reactive` (required for reactive properties)
- ✅ `Widget` imported correctly

---

### SECTION 2: BINDINGS Declaration (Lines 29-35)

```python
BINDINGS = [
    Binding("enter", "submit", "Submit message"),
    Binding("ctrl+c", "cancel", "Cancel input"),
    # Permission buffer navigation
    Binding("up", "permission_up", "Navigate up in permission options", show=False),
    Binding("down", "permission_down", "Navigate down in permission options", show=False),
]
```

**Findings:**
- ✅ BINDINGS is class-level attribute (correct placement)
- ✅ `up` → `permission_up` action mapping exists
- ✅ `down` → `permission_down` action mapping exists
- ⚠️ `show=False` on permission bindings (won't show in footer, but should still fire)
- ❌ NO `priority=True` flag - might be needed to override default behavior
- ❓ **QUESTION**: Should these bindings be conditional? Only active when `permission_prompt_data` is set?

**Textual Binding System**:
- When key is pressed, Textual looks for `Binding("key", "action", ...)`
- If found, calls `action_<action>()` method on the widget
- Example: `Binding("up", "permission_up", ...)` → calls `action_permission_up()`

---

### SECTION 3: Reactive Properties (Lines 37-42)

```python
value = reactive("", layout=True)
cursor_position = reactive(0)
is_spinning = reactive(False)
spinner_frame = reactive(0)
permission_prompt_data = reactive(None)
permission_selected_option = reactive(0)
```

**Findings:**
- ✅ `permission_prompt_data` is reactive (triggers `watch_permission_prompt_data` on change)
- ✅ `permission_selected_option` is reactive (triggers `watch_permission_selected_option` on change)
- ✅ Both have watchers defined later (lines 638-696)

---

### SECTION 4: __init__ Method (Lines 89-97)

```python
def __init__(self, placeholder: str = "", **kwargs):
    super().__init__(**kwargs)
    self.placeholder = placeholder
    self._lines = [""]
    self._cursor_row = 0
    self._cursor_col = 0
    self.can_focus = True
    self._spin_task = None
    self.suggestions_active = False
```

**Findings:**
- ✅ `super().__init__(**kwargs)` called (Widget initialization)
- ✅ `can_focus = True` set (widget CAN receive focus)
- ✅ `suggestions_active = False` by default (not interfering with permission buffer)

---

### SECTION 5: on_focus Method (Lines 99-104)

```python
def on_focus(self) -> None:
    """Track when widget receives focus"""
    import sys
    sys.stderr.write(f"\n[MultiLineInput.on_focus] GAINED FOCUS - prompt={bool(self.permission_prompt_data)}\n")
    sys.stderr.flush()
    self.refresh()
```

**Findings:**
- ✅ Logs when focus is gained
- ✅ Shows `permission_prompt_data` state (True/False)
- ✅ Calls `refresh()` to update display
- 🔍 **CRITICAL**: We should see this log in stderr when buffer shows

---

### SECTION 6: on_blur Method (Lines 106-127)

```python
def on_blur(self) -> None:
    """Track when widget loses focus - trigger navigation event for permission auto-dismiss"""
    import sys
    sys.stderr.write(f"\n[MultiLineInput.on_blur] LOST FOCUS - prompt={bool(self.permission_prompt_data)}\n")
    sys.stderr.flush()

    # Constitution Principle V: Auto-dismiss permission prompts on navigation
    if self.permission_prompt_data:
        sys.stderr.write(f"[MultiLineInput.on_blur] NAVIGATION EVENT - auto-dismissing permission prompt\n")
        sys.stderr.flush()

        # Post navigation event first (for any listeners)
        self.post_message(self.NavigationEvent("focus_lost"))

        # Then post cancellation event to handle current prompt
        self.post_message(self.PermissionCancelled())

        # Clear prompt data immediately (responsive UI)
        self.permission_prompt_data = None
        self.permission_selected_option = 0

    self.refresh()
```

**Findings:**
- ✅ Auto-dismisses permission buffer on focus loss
- 🔍 **CRITICAL**: If we see this log, it means widget is losing focus (problem!)

---

### SECTION 7: on_key Method (Lines 328-460) ⚠️ CRITICAL SECTION

```python
def on_key(self, event) -> None:
    """Handle key presses"""
    import sys
    key = event.key

    # AGGRESSIVE DEBUG - Log ALL key events
    sys.stderr.write(f"\n[MultiLineInput.on_key] 🔥 KEY='{key}' prompt={bool(self.permission_prompt_data)} focused={self.has_focus} 🔥\n")
    if hasattr(self, 'app') and self.app and hasattr(self.app, 'focused'):
        sys.stderr.write(f"[MultiLineInput.on_key] app_focused={self.app.focused}\n")
    sys.stderr.flush()

    # PRIORITY 1: Handle permission prompt navigation if active
    if self.permission_prompt_data:  # Line 340
        sys.stderr.write(f"[MultiLineInput] INSIDE PERMISSION HANDLER for key={key}\n")
        sys.stderr.write(f"[MultiLineInput] Current selected_option: {self.permission_selected_option}\n")
        sys.stderr.flush()
        options = self.permission_prompt_data.get('options', [])

        # If no options (informational prompt), only allow Escape
        if not options:  # Line 347
            if key == "escape":
                self.post_message(self.PermissionCancelled())
                event.prevent_default()
            return  # Line 351 - ignore all other keys

        # Handle navigation - up/down arrows
        if key == "up":  # Line 354 - MY FIX
            if self.permission_selected_option > 0:
                self.permission_selected_option -= 1
                self.refresh()
            event.prevent_default()
            return
        elif key == "down":  # Line 360 - MY FIX
            if self.permission_selected_option < len(options) - 1:
                self.permission_selected_option += 1
                self.refresh()
            event.prevent_default()
            return
        elif key == "enter":  # Line 366
            # Confirm selection (options list is not empty here)
            selected = options[self.permission_selected_option]
            self.post_message(self.PermissionResponse(selected))
            event.prevent_default()
            return
        elif key == "escape":  # Line 372
            # Cancel
            self.post_message(self.PermissionCancelled())
            event.prevent_default()
            return
```

**Findings:**
- ✅ Debug logging present (lines 334-337)
- ✅ Checks `permission_prompt_data` first (line 340)
- ✅ MY FIX is present (lines 354-365)
- ✅ Handles `up`: decrements `permission_selected_option`, refreshes, prevents default, returns
- ✅ Handles `down`: increments `permission_selected_option`, refreshes, prevents default, returns
- ✅ Logic flow is CORRECT
- 🔍 **CRITICAL QUESTION**: Is `on_key()` even being called when keys are pressed?
- 🔍 **CRITICAL QUESTION**: Does the widget have focus (`self.has_focus=True`)?
- 🔍 **CRITICAL QUESTION**: Is `permission_prompt_data` actually set?

**Expected Logs When DOWN is Pressed:**
```
[MultiLineInput.on_key] 🔥 KEY='down' prompt=True focused=True 🔥
[MultiLineInput] INSIDE PERMISSION HANDLER for key=down
[MultiLineInput] Current selected_option: 0
[MultiLineInput.watch_permission_selected_option] 0 -> 1
[MultiLineInput] REFRESH triggered by selection change
```

---

### SECTION 8: action_permission_up and action_permission_down (Lines 516-558)

```python
def action_permission_up(self) -> None:
    """Navigate up in permission options"""
    import sys
    sys.stderr.write(f"[MultiLineInput.action_permission_up] ENTERED\n")
    sys.stderr.flush()

    if self.permission_prompt_data:
        options = self.permission_prompt_data.get('options', [])
        sys.stderr.write(f"[MultiLineInput.action_permission_up] options_count={len(options)}, current={self.permission_selected_option}\n")
        sys.stderr.flush()

        if options:
            current = self.permission_selected_option
            new_selection = max(0, current - 1)
            self.permission_selected_option = new_selection
            sys.stderr.write(f"[MultiLineInput.action_permission_up] changed {current} -> {new_selection}\n")
            sys.stderr.flush()
            self.refresh()  # Force refresh
    else:
        sys.stderr.write(f"[MultiLineInput.action_permission_up] NO permission_prompt_data!\n")
        sys.stderr.flush()
```

**Findings:**
- ✅ Method exists with correct name (matches BINDINGS)
- ✅ Has extensive debug logging
- ✅ Calls `refresh()` after changing selection
- 🔍 **CRITICAL QUESTION**: Are these EVER called? We should see logs if they are!

---

### SECTION 9: watch_permission_prompt_data Watcher (Lines 638-684)

```python
def watch_permission_prompt_data(self, old_value, new_value) -> None:
    """React to permission prompt data changes - trigger layout update"""
    import sys
    sys.stderr.write(f"[MultiLineInput.watch_permission_prompt_data] old={old_value is not None}, new={new_value is not None}\n")
    sys.stderr.flush()

    # Only refresh if actually changed (not just set to same value)
    if old_value != new_value:
        sys.stderr.write(f"[MultiLineInput] PERMISSION DATA CHANGED\n")
        sys.stderr.flush()

        if new_value:
            self.permission_selected_option = new_value.get('selected', 0)
            sys.stderr.write(f"[MultiLineInput] PERMISSION ACTIVE - selected_option={self.permission_selected_option}\n")
            sys.stderr.flush()
            # Ensure we have focus when permission prompt is active (only if app is available)
            if not self.has_focus:
                try:
                    sys.stderr.write(f"[MultiLineInput] Calling self.focus()\n")
                    sys.stderr.flush()
                    self.focus()
                except Exception as e:
                    sys.stderr.write(f"[MultiLineInput] Focus failed (no app context): {e}\n")
                    sys.stderr.flush()
        else:
            sys.stderr.write(f"[MultiLineInput] PERMISSION CLEARED\n")
            sys.stderr.flush()

        # CRITICAL: Refresh MUST happen synchronously for widget to render!
        # But keep it light - no layout=True to avoid blocking
        self.refresh()

        if new_value is not None:
            print(f"[MultiLineInput] PERMISSION ACTIVE: {new_value.get('title', 'N/A')}")

            # Focus IMMEDIATELY (synchronously) so keys work right away
            try:
                self.app.set_focus(self)
                print(f"[MultiLineInput]   ✓ FORCED FOCUS IMMEDIATELY")
            except Exception as e:
                print(f"[MultiLineInput]   Focus error: {e}, trying fallback")
                try:
                    self.focus()
                except Exception as e2:
                    print(f"[MultiLineInput]   Fallback focus also failed: {e2}")
        else:
            print(f"[MultiLineInput] Permission cleared")
```

**Findings:**
- ✅ Watcher triggers when `permission_prompt_data` changes (reactive system)
- ✅ Tries to set focus TWO ways:
  1. `self.focus()` (lines 654-661)
  2. `self.app.set_focus(self)` (lines 674-676)
- ✅ Has extensive logging (both stderr and stdout)
- 🔍 **CRITICAL**: Does this actually give the widget focus? We should see the logs!

---

### SECTION 10: watch_permission_selected_option Watcher (Lines 686-696)

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

**Findings:**
- ✅ Watcher triggers when `permission_selected_option` changes
- ✅ Forces refresh to update display
- ✅ Has debug logging
- 🔍 **CRITICAL**: We should see "0 -> 1" log when DOWN is pressed (if code is working)

---

## Task 2: Read Source multiline_input.py ✅ COMPLETE

**File**: `/Users/dezmondhollins/opencli/modules/multiline_input.py`
**Total Lines**: 697

### Comparison Result: **FILES ARE IDENTICAL**

- ✅ Runtime and source have EXACT same code
- ✅ Both have fix at lines 353-365
- ✅ Both have BINDINGS at lines 29-35
- ✅ Both have action methods at lines 516-558
- ✅ Both have watchers at lines 638-696

**Conclusion**: The fix IS deployed to runtime, but still doesn't work!

---

## CRITICAL QUESTIONS TO ANSWER

### Question 1: Is on_key() being called when you press arrow keys?

**Expected Log (if yes)**:
```
[MultiLineInput.on_key] 🔥 KEY='up' prompt=True focused=True 🔥
```
OR
```
[MultiLineInput.on_key] 🔥 KEY='down' prompt=True focused=True 🔥
```

**If NO log**: on_key() is NOT receiving the event at all!

---

### Question 2: Does the widget have focus?

**Expected Log (if yes)**:
```
[MultiLineInput.on_focus] GAINED FOCUS - prompt=True
```
AND
```
[MultiLineInput.on_key] 🔥 KEY='...' prompt=True focused=True 🔥
```

**If focused=False**: Widget does not have focus, keys won't be received!

---

### Question 3: Is permission_prompt_data actually set?

**Expected Log (if yes)**:
```
[MultiLineInput.watch_permission_prompt_data] old=False, new=True
[MultiLineInput] PERMISSION DATA CHANGED
[MultiLineInput] PERMISSION ACTIVE - selected_option=0
[MultiLineInput] PERMISSION ACTIVE: System: /help
[MultiLineInput]   ✓ FORCED FOCUS IMMEDIATELY
```

**If NO log**: permission_prompt_data was never set!

---

### Question 4: Are action methods (from BINDINGS) being called?

**Expected Log (if yes)**:
```
[MultiLineInput.action_permission_up] ENTERED
```
OR
```
[MultiLineInput.action_permission_down] ENTERED
```

**If NO log**: BINDINGS are NOT firing!

---

## HYPOTHESES RANKED BY LIKELIHOOD

### Hypothesis 1: Widget Does NOT Have Focus ⚡ MOST LIKELY
**Evidence:**
- Lines 654-676 try to force focus, but might fail
- If widget loses focus, `on_key()` won't receive events
- If widget never gains focus, nothing works

**How to Test:**
- Check stderr for `[MultiLineInput.on_focus] GAINED FOCUS`
- Check if `on_key()` logs show `focused=False`

**If True:**
- Fix: Ensure focus is set AFTER buffer renders
- Fix: Use `call_after_refresh()` to set focus
- Fix: Check if parent container is stealing focus

---

### Hypothesis 2: on_key() Is NOT Being Called
**Evidence:**
- Parent TUI class might have `on_key()` that doesn't propagate
- Event might be consumed before reaching widget

**How to Test:**
- Check stderr for ANY `[MultiLineInput.on_key]` logs when pressing keys

**If True:**
- Fix: Check parent class `on_key()` implementation
- Fix: Ensure event propagation is not blocked

---

### Hypothesis 3: BINDINGS Are Interfering with on_key()
**Evidence:**
- Textual might prioritize BINDINGS over `on_key()`
- BINDINGS might consume event before `on_key()` sees it

**How to Test:**
- Check if `action_permission_up/down` logs appear
- If yes: BINDINGS work, `on_key()` is ignored
- If no: BINDINGS don't work either

**If True:**
- Fix: Remove BINDINGS, rely only on `on_key()`
- OR: Remove `on_key()` handling, rely only on BINDINGS with conditional activation

---

### Hypothesis 4: permission_prompt_data Is NOT Set
**Evidence:**
- If never set, entire permission block is skipped

**How to Test:**
- Check stderr for `[MultiLineInput] PERMISSION ACTIVE`

**If True:**
- Fix: Check `permission_handlers.py` - ensure it sets the data
- Fix: Trace how permission buffer is shown

---

## NEXT STEP: CAPTURE STDERR OUTPUT

**What to do:**
1. Run `opencli tui 2>/tmp/arrow_debug.log`
2. Type `/help`
3. Press ENTER twice
4. Press DOWN arrow
5. Press UP arrow
6. Press Ctrl+C
7. Read `/tmp/arrow_debug.log`

**Without this output, I cannot proceed further!**

The code LOOKS correct, but doesn't work. This means one of the critical questions has a "NO" answer, and only the actual runtime logs can tell us which one.

---

---

## Task 3: Read permission_handlers.py ✅ COMPLETE

**File**: `/Users/dezmondhollins/opencli/modules/tui/permission_handlers.py`
**Key Method**: `_show_permission_prompt` (Lines 370-404)

### CRITICAL SECTION: _show_permission_prompt (Lines 370-404)

```python
def _show_permission_prompt(self, prompt_data: dict) -> None:
    """Show permission prompt inside MultiLineInput"""
    try:
        import sys
        sys.stderr.write(f"[TUI._show_permission_prompt] 🔥 SETTING PERMISSION PROMPT DATA 🔥\n")
        sys.stderr.flush()

        prompt_input = self.query_one("#prompt-input", MultiLineInput)
        prompt_data['selected'] = 0
        prompt_input.permission_prompt_data = prompt_data  # Line 379 - triggers watcher

        # CRITICAL: Force focus to the input widget for permission navigation
        sys.stderr.write(f"[TUI._show_permission_prompt] Forcing focus to prompt_input\n")
        sys.stderr.flush()
        prompt_input.focus()  # Line 384 - calls focus()

        # Force refresh to show the permission buffer immediately
        prompt_input.refresh()  # Line 387
        self.refresh()  # Line 388

        sys.stderr.write(f"[TUI._show_permission_prompt] ✅ Permission prompt displayed and focused\n")
        sys.stderr.flush()

        # Debug: Show what the permission buffer looks like
        rendered = prompt_input.render()
        preview = str(rendered).replace('\n', '\\n')[:200]
        sys.stderr.write(f"[TUI._show_permission_prompt] Rendered buffer preview: {preview}...\n")
        sys.stderr.flush()

    except Exception as e:
        import sys
        import traceback
        sys.stderr.write(f"[TUI._show_permission_prompt] ❌ Exception: {e}\n")
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
```

**Findings:**
- ✅ Sets `permission_prompt_data` at line 379 (triggers watch_permission_prompt_data watcher)
- ✅ Calls `prompt_input.focus()` at line 384
- ✅ Has extensive debug logging
- 🔍 **CRITICAL**: Does `prompt_input.focus()` actually give the widget focus in Textual?

**Expected Logs When Buffer Shows:**
```
[TUI._show_permission_prompt] 🔥 SETTING PERMISSION PROMPT DATA 🔥
[MultiLineInput.watch_permission_prompt_data] old=False, new=True
[MultiLineInput] PERMISSION DATA CHANGED
[MultiLineInput] PERMISSION ACTIVE - selected_option=0
[MultiLineInput] PERMISSION ACTIVE: System: /help
[MultiLineInput]   ✓ FORCED FOCUS IMMEDIATELY
[TUI._show_permission_prompt] Forcing focus to prompt_input
[MultiLineInput.on_focus] GAINED FOCUS - prompt=True
[TUI._show_permission_prompt] ✅ Permission prompt displayed and focused
```

---

## Task 4: Read tui/core.py - Class Hierarchy ✅ COMPLETE

**File**: `/Users/dezmondhollins/opencli/modules/tui/core.py`
**Class Declaration**: Line 81

```python
class OpenCLITUI(App, PermissionHandlers, CommandHandlers, ModelHandlers, MessageHandlerMixin, ResponseGeneratorMixin, ActionMixin):
```

**Findings:**
- ✅ OpenCLITUI inherits from 7 classes
- ✅ ActionMixin is LAST in the inheritance chain (lowest priority in MRO)
- ⚠️ ActionMixin has `on_key()` method - might affect event handling

**Method Resolution Order (MRO)**:
1. OpenCLITUI
2. App (Textual base)
3. PermissionHandlers
4. CommandHandlers
5. ModelHandlers
6. MessageHandlerMixin
7. ResponseGeneratorMixin
8. ActionMixin ← Has on_key() method!

---

## Task 5: Read tui/action_mixin.py - Parent on_key() ✅ COMPLETE ⚠️ CRITICAL FINDING

**File**: `/Users/dezmondhollins/opencli/modules/tui/action_mixin.py`
**Critical Method**: `on_key()` (Lines 43-56)

```python
def on_key(self, event) -> None:
    """Handle global key events"""
    # Handle Ctrl+C to quit
    if event.key == "ctrl+c":
        self.action_quit_app()
    # Handle Ctrl+L to clear screen
    elif event.key == "ctrl+l":
        self.action_clear_screen()
    # Handle F11 for performance toggle
    elif event.key == "f11":
        self.action_toggle_performance()
    # Handle F12 for refactoring toggle
    elif event.key == "f12":
        self.action_toggle_refactoring()
```

**CRITICAL FINDINGS:**
- ❌ Only handles ctrl+c, ctrl+l, f11, f12
- ❌ Does NOT handle up/down arrows
- ❌ Does NOT call `event.prevent_default()` for unhandled keys
- ❌ Does NOT call `event.stop()` to stop propagation
- ❌ Falls through without returning for unhandled keys

**Why This Matters:**
- In Textual, events bubble from child → parent
- If MultiLineInput has focus: MultiLineInput.on_key() is called first
- If MultiLineInput does NOT have focus: OpenCLITUI.on_key() is called (via ActionMixin)
- ActionMixin.on_key() doesn't handle up/down, so they're ignored!

---

## UPDATED HYPOTHESIS: FOCUS IS THE PROBLEM! ⚡⚡⚡

### The Root Cause Theory

**What's supposed to happen:**
1. `/help` permission buffer is shown
2. `_show_permission_prompt()` calls `prompt_input.focus()` (line 384)
3. MultiLineInput gains focus
4. User presses DOWN arrow
5. MultiLineInput.on_key() receives the event (because it has focus)
6. on_key() handles it, changes selection, refreshes

**What's ACTUALLY happening (hypothesis):**
1. `/help` permission buffer is shown
2. `_show_permission_prompt()` calls `prompt_input.focus()` (line 384)
3. **MultiLineInput does NOT actually gain focus!** ⚠️
4. User presses DOWN arrow
5. **OpenCLITUI.on_key() receives event instead** (parent has focus)
6. ActionMixin.on_key() doesn't handle up/down
7. Event is ignored
8. Nothing happens

### How to Verify This Hypothesis

Check stderr logs for:

**If widget HAS focus:**
```
[MultiLineInput.on_focus] GAINED FOCUS - prompt=True
[MultiLineInput.on_key] 🔥 KEY='down' prompt=True focused=True 🔥
```

**If widget DOES NOT have focus:**
```
❌ NO "[MultiLineInput.on_focus] GAINED FOCUS" log
❌ NO "[MultiLineInput.on_key]" logs when pressing keys
```

---

## STDERR CAPTURE SCRIPT CREATED

**Script**: `/Users/dezmondhollins/opencli/CAPTURE_STDERR_SIMPLE.sh`

**Usage**:
```bash
bash /Users/dezmondhollins/opencli/CAPTURE_STDERR_SIMPLE.sh
```

**What it does:**
1. Runs `opencli tui 2>/tmp/arrow_stderr.log`
2. User manually interacts (type /help, press arrows)
3. Analyzes log and reports:
   - Was permission buffer shown?
   - Was permission_prompt_data set?
   - Did widget gain focus?
   - Was on_key() called for arrows?
   - Were BINDINGS action methods called?
   - Did selection change?

**This script will definitively answer ALL critical questions!**

---

## STATUS

- [x] Task 1: Read runtime multiline_input.py - ALL findings logged
- [x] Task 2: Read source multiline_input.py - FILES IDENTICAL
- [x] Task 3: Read permission_handlers.py - Found _show_permission_prompt
- [x] Task 4: Read tui/core.py - Class hierarchy documented
- [x] Task 5: Read tui/action_mixin.py - ⚠️ CRITICAL: Parent on_key() found!
- [x] Created CAPTURE_STDERR_SIMPLE.sh script
- [ ] **NEXT**: Run capture script to get ACTUAL runtime logs
- [ ] Analyze logs to confirm/reject focus hypothesis
