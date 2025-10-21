# Systematic Debug Log - Arrow Keys Not Working

## Task 1: Read runtime multiline_input.py COMPLETE

**File:** `/Users/dezmondhollins/.opencli/cli/modules/multiline_input.py`

### Line-by-line Analysis

**Lines 1-28: Imports and Class Declaration**
```python
from textual.widget import Widget
from textual.message import Message
from textual.binding import Binding
from textual.reactive import reactive
```
- ✅ All imports correct
- ✅ Binding imported from textual.binding
- ✅ Widget, reactive imported correctly

**Lines 29-35: BINDINGS Declaration**
```python
BINDINGS = [
    Binding("enter", "submit", "Submit message"),
    Binding("ctrl+c", "cancel", "Cancel input"),
    # Permission buffer navigation
    Binding("up", "permission_up", "Navigate up in permission options", show=False),
    Binding("down", "permission_down", "Navigate down in permission options", show=False),
]
```
**FINDINGS:**
- ✅ BINDINGS is class-level attribute (correct)
- ✅ up → permission_up mapping exists
- ✅ down → permission_down mapping exists
- ⚠️ show=False on permission bindings
- ⚠️ No priority=True flag
- ❓ Question: Are these BINDINGS conditional? Should they only be active when permission_prompt_data is set?

**Lines 37-42: Reactive Properties**
```python
value = reactive("", layout=True)
cursor_position = reactive(0)
is_spinning = reactive(False)
spinner_frame = reactive(0)
permission_prompt_data = reactive(None)
permission_selected_option = reactive(0)
```
**FINDINGS:**
- ✅ permission_prompt_data is reactive
- ✅ permission_selected_option is reactive
- ✅ Both have watchers defined later

**Lines 89-97: __init__ Method**
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
**FINDINGS:**
- ✅ super().__init__(**kwargs) called (Widget initialization)
- ✅ can_focus = True set
- ✅ suggestions_active = False by default

**Lines 99-104: on_focus Method**
```python
def on_focus(self) -> None:
    """Track when widget receives focus"""
    import sys
    sys.stderr.write(f"\n[MultiLineInput.on_focus] GAINED FOCUS - prompt={bool(self.permission_prompt_data)}\n")
    sys.stderr.flush()
    self.refresh()
```
**FINDINGS:**
- ✅ Logs when focus is gained
- ✅ Shows permission_prompt_data state
- ✅ Calls refresh()

**Lines 328-449: on_key Method (CRITICAL)**
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
    if self.permission_prompt_data:
        sys.stderr.write(f"[MultiLineInput] INSIDE PERMISSION HANDLER for key={key}\n")
        sys.stderr.write(f"[MultiLineInput] Current selected_option: {self.permission_selected_option}\n")
        sys.stderr.flush()
        options = self.permission_prompt_data.get('options', [])

        # If no options (informational prompt), only allow Escape
        if not options:
            if key == "escape":
                self.post_message(self.PermissionCancelled())
                event.prevent_default()
            return  # Ignore all other keys for informational prompts

        # Handle navigation - up/down arrows
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
            # Confirm selection (options list is not empty here)
            selected = options[self.permission_selected_option]
            self.post_message(self.PermissionResponse(selected))
            event.prevent_default()
            return
        elif key == "escape":
            # Cancel
            self.post_message(self.PermissionCancelled())
            event.prevent_default()
            return
```
**FINDINGS:**
- ✅ Debug logging present
- ✅ Checks permission_prompt_data first
- ✅ MY FIX is present (lines 353-365)
- ✅ Handles up: decrements, refreshes, prevents default, returns
- ✅ Handles down: increments, refreshes, prevents default, returns
- ❓ **CRITICAL QUESTION**: Is on_key() even being called when keys are pressed?
- ❓ **CRITICAL QUESTION**: Does the widget have focus when buffer shows?
- ❓ **CRITICAL QUESTION**: Is permission_prompt_data actually set?

**Lines 505-547: action_permission_up and action_permission_down**
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
**FINDINGS:**
- ✅ Method exists
- ✅ Has debug logging
- ✅ Calls refresh()
- ❓ **Are these EVER called?**

**Lines 627-673: watch_permission_prompt_data (CRITICAL)**
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
**FINDINGS:**
- ✅ Watcher triggers when permission_prompt_data changes
- ✅ Tries to set focus TWO ways (self.focus() and self.app.set_focus(self))
- ✅ Has extensive logging
- ❓ **CRITICAL**: Does this actually give the widget focus?

## CRITICAL QUESTIONS TO ANSWER

1. **Is on_key() being called when you press arrow keys?**
   - Need to capture stderr and check for: `[MultiLineInput.on_key] 🔥 KEY='up'` or `KEY='down'`

2. **Does the widget have focus?**
   - Check stderr for: `[MultiLineInput.on_focus] GAINED FOCUS`
   - Check stderr for: `focused=True` in on_key logs

3. **Is permission_prompt_data actually set?**
   - Check stderr for: `[MultiLineInput] PERMISSION ACTIVE`
   - Check stderr for: `prompt=True` in on_key logs

4. **Are action methods (from BINDINGS) being called?**
   - Check stderr for: `[MultiLineInput.action_permission_up] ENTERED`
   - Check stderr for: `[MultiLineInput.action_permission_down] ENTERED`

## NEXT TASK

Need to capture ACTUAL stderr output when you:
1. Start opencli tui
2. Type /help
3. Press ENTER twice
4. Press DOWN arrow
5. Press UP arrow

Without this output, I'm coding blind.

---

**Status:** Task 1 complete with detailed findings
**Next:** Need stderr capture to answer critical questions
