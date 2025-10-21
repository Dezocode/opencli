# on_blur() Auto-Dismiss: Fix Logic vs Comment Out
**Date**: 2025-10-21
**Question**: Should we fix on_blur() logic or remove it entirely?

---

## The Feature's Intent

**Constitution Principle V**: "Auto-dismiss permission prompts on navigation"

**User Story**:
> As a user, when a permission prompt appears and I navigate away (click elsewhere, tab to another widget), the prompt should automatically dismiss so it doesn't block the UI.

**Is this a good feature?** ✅ **YES** - Prevents orphaned/stuck prompts

---

## Current Implementation (BROKEN)

```python
def on_blur(self) -> None:
    """Track when widget loses focus - trigger navigation event for permission auto-dismiss"""
    if self.permission_prompt_data:
        # Post cancellation
        self.post_message(self.PermissionCancelled())

        # Clear immediately
        self.permission_prompt_data = None  # ← PROBLEM: Too aggressive
        self.permission_selected_option = 0
```

**Problem**: Clears on **ANY** focus loss, even spurious/technical ones.

**Timeline of Failure**:
```
T=0: Permission prompt shows
T=1: watch_permission_prompt_data() calls focus()
T=2: Widget gains focus
T=3: Something steals focus (Textual internal? Another widget?)
T=4: on_blur() fires → CLEARS DATA
T=5: Buffer still visible (cached render) but data=None
T=6: User presses arrow → action method checks data → finds None → zombie buffer
```

---

## Solution 1: Comment Out Entirely ❌ **NOT RECOMMENDED**

### Implementation:
```python
def on_blur(self) -> None:
    """Track when widget loses focus"""
    # Constitution Principle V was here - disabled due to zombie buffer bug
    # if self.permission_prompt_data:
    #     self.permission_prompt_data = None
    self.refresh()
```

### Pros:
- ✅ Simplest fix
- ✅ Prevents zombie buffer immediately
- ✅ Arrows work again

### Cons:
- ❌ Loses auto-dismiss feature entirely
- ❌ User MUST explicitly dismiss (ESC or selection)
- ❌ Orphaned prompts possible if user navigates without dismissing
- ❌ Violates Constitution Principle V

### User Impact:
**Before**: Prompt auto-dismisses on navigation (but broken, creates zombie)
**After**: Prompt stays until user explicitly dismisses

**Is this acceptable?** Maybe, but we're throwing away a good feature.

---

## Solution 2: Add Smart Focus Loss Detection ✅ **RECOMMENDED**

### Implementation:
```python
def __init__(self):
    # Add tracking
    self.permission_shown_at = 0  # Timestamp when prompt shown

def watch_permission_prompt_data(self, old_value, new_value):
    if new_value:
        import time
        self.permission_shown_at = time.time()  # Track when shown
        self.focus()

def on_blur(self) -> None:
    """Track when widget loses focus - smart auto-dismiss"""
    if self.permission_prompt_data:
        import time
        elapsed = time.time() - self.permission_shown_at

        # Only auto-dismiss if permission has been shown for >500ms
        # This avoids spurious focus loss during initial mount/render
        if elapsed > 0.5:
            sys.stderr.write(f"[on_blur] Real navigation detected (elapsed={elapsed:.2f}s), auto-dismissing\n")
            self.post_message(self.PermissionCancelled())
            self.permission_prompt_data = None
            self.permission_selected_option = 0
        else:
            sys.stderr.write(f"[on_blur] Spurious focus loss ignored (elapsed={elapsed:.2f}s)\n")
            # Try to regain focus
            self.focus()
```

### Pros:
- ✅ Keeps auto-dismiss feature for REAL navigation
- ✅ Prevents spurious dismissal during mount/render
- ✅ Maintains Constitution Principle V
- ✅ Best of both worlds

### Cons:
- ⚠️ Adds complexity (timestamp tracking)
- ⚠️ Magic number (500ms) - may need tuning
- ⚠️ Edge case: User navigates away in <500ms (unlikely)

### User Impact:
**Before**: Broken zombie buffer
**After**: Auto-dismiss works correctly for real navigation, ignores technical glitches

---

## Solution 3: Check Focus Destination ✅ **ALSO GOOD**

### Implementation:
```python
def on_blur(self) -> None:
    """Track when widget loses focus - check where focus went"""
    if self.permission_prompt_data:
        # Check what widget has focus now
        try:
            focused_widget = self.app.focused

            # If focus went to StreamingDisplay or another real widget, dismiss
            # If focused_widget is None, it's spurious focus loss - ignore
            if focused_widget is not None and focused_widget != self:
                sys.stderr.write(f"[on_blur] Focus moved to {focused_widget}, auto-dismissing\n")
                self.post_message(self.PermissionCancelled())
                self.permission_prompt_data = None
                self.permission_selected_option = 0
            else:
                sys.stderr.write(f"[on_blur] Spurious focus loss (no focused widget), ignoring\n")
                # Try to regain focus
                self.focus()
        except Exception as e:
            sys.stderr.write(f"[on_blur] Error checking focus: {e}, keeping prompt\n")
```

### Pros:
- ✅ Most semantically correct (checks WHERE focus went)
- ✅ No magic numbers
- ✅ Handles real vs spurious focus loss correctly
- ✅ Maintains Constitution Principle V

### Cons:
- ⚠️ Depends on `self.app.focused` being reliable
- ⚠️ Textual internal state may be inconsistent

### User Impact:
**Before**: Broken zombie buffer
**After**: Auto-dismiss only when focus ACTUALLY moves to another widget

---

## Solution 4: Hybrid (Timestamp + Focus Check) ✅ **MOST ROBUST**

### Implementation:
```python
def on_blur(self) -> None:
    """Track when widget loses focus - hybrid smart detection"""
    if self.permission_prompt_data:
        import time
        elapsed = time.time() - self.permission_shown_at

        # Ignore very recent focus losses (spurious)
        if elapsed < 0.5:
            sys.stderr.write(f"[on_blur] Ignoring spurious focus loss (elapsed={elapsed:.2f}s)\n")
            self.focus()  # Try to regain
            return

        # Check where focus went
        try:
            focused_widget = self.app.focused

            # Real navigation: focus moved to another widget
            if focused_widget is not None and focused_widget != self:
                sys.stderr.write(f"[on_blur] Real navigation to {focused_widget}, auto-dismissing\n")
                self.post_message(self.PermissionCancelled())
                self.permission_prompt_data = None
                self.permission_selected_option = 0
            else:
                # Unclear focus state, keep prompt and try to refocus
                sys.stderr.write(f"[on_blur] Unclear focus state, keeping prompt\n")
                self.focus()
        except Exception as e:
            sys.stderr.write(f"[on_blur] Error: {e}, keeping prompt\n")
```

### Pros:
- ✅ Defense in depth (two checks)
- ✅ Most robust against edge cases
- ✅ Clear debugging (logs which check triggered)
- ✅ Maintains Constitution Principle V

### Cons:
- ⚠️ Most complex implementation
- ⚠️ Slight performance overhead (timestamp + focus check)

---

## Recommendation Matrix

| Scenario | Solution 1 | Solution 2 | Solution 3 | Solution 4 |
|----------|-----------|-----------|-----------|-----------|
| **Prevents zombie buffer** | ✅ | ✅ | ✅ | ✅ |
| **Keeps auto-dismiss** | ❌ | ✅ | ✅ | ✅ |
| **Simple to implement** | ✅ | ⚠️ | ⚠️ | ❌ |
| **Robust** | ⚠️ | ⚠️ | ✅ | ✅ |
| **Maintainable** | ✅ | ✅ | ✅ | ⚠️ |

---

## My Recommendation

**Use Solution 2 (Timestamp-based)** for first iteration:

**Why**:
1. Simple to implement (just add timestamp tracking)
2. Fixes zombie buffer immediately
3. Keeps auto-dismiss feature
4. 500ms is reasonable for distinguishing spurious vs real navigation
5. Easy to debug with logs

**If Solution 2 has edge cases**, upgrade to **Solution 4 (Hybrid)**.

**Avoid Solution 1** unless Constitution Principle V is deemed unnecessary.

---

## Code Diff for Solution 2

### File: `modules/multiline_input.py`

**In __init__() (around line 50):**
```python
def __init__(self, ...):
    super().__init__(...)
    # ... existing init code ...
    self.permission_shown_at = 0  # Track when permission prompt shown
```

**In watch_permission_prompt_data() (around line 658):**
```python
def watch_permission_prompt_data(self, old_value, new_value):
    if new_value:
        import time
        self.permission_shown_at = time.time()  # ← ADD THIS
        self.permission_selected_option = new_value.get('selected', 0)
        # ... rest of existing code ...
```

**In on_blur() (lines 114-135):**
```python
def on_blur(self) -> None:
    """Track when widget loses focus - smart auto-dismiss"""
    import sys
    import time  # ← ADD
    sys.stderr.write(f"\n[MultiLineInput.on_blur] LOST FOCUS - prompt={bool(self.permission_prompt_data)}\n")
    sys.stderr.flush()

    if self.permission_prompt_data:
        elapsed = time.time() - self.permission_shown_at  # ← ADD

        # Only auto-dismiss if prompt shown for >500ms (avoid spurious focus loss)
        if elapsed > 0.5:  # ← ADD
            sys.stderr.write(f"[on_blur] Real navigation (elapsed={elapsed:.2f}s), auto-dismissing\n")
            sys.stderr.flush()

            self.post_message(self.NavigationEvent("focus_lost"))
            self.post_message(self.PermissionCancelled())

            self.permission_prompt_data = None
            self.permission_selected_option = 0
        else:  # ← ADD
            sys.stderr.write(f"[on_blur] Spurious focus loss (elapsed={elapsed:.2f}s), ignoring and refocusing\n")
            sys.stderr.flush()
            try:
                self.focus()  # Try to regain focus
            except Exception as e:
                sys.stderr.write(f"[on_blur] Refocus failed: {e}\n")
                sys.stderr.flush()

    self.refresh()
```

**Same changes needed in**: `modules/input_widget/widget.py` (modular version)

---

## Testing Plan

After implementing Solution 2:

1. **Test normal arrow navigation**: Should work (no zombie buffer)
2. **Test real navigation away**: Click on content area → prompt should auto-dismiss
3. **Test spurious focus loss**: If focus lost <500ms, prompt should stay
4. **Check logs**: Verify "Real navigation" vs "Spurious focus loss" messages
5. **Tune threshold**: If 500ms doesn't work, try 300ms or 1000ms

---

## Conclusion

**Answer to your question**: We should **fix the logic** (Solution 2 or 4), not just comment it out.

**Why**: Constitution Principle V is a good UX feature - we just need smarter detection of "real navigation" vs "technical focus loss".

**Simplest effective fix**: Add timestamp tracking and only dismiss if >500ms elapsed since prompt shown.

**Next step**: Implement Solution 2, test, and upgrade to Solution 4 if needed.
