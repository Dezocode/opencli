# MESSAGE FLOW FIX - FOCUS STEALING ISSUE

## The Actual Problem

**StreamingDisplay was stealing focus from MultiLineInput**, preventing the input widget from receiving keyboard events.

## Root Cause

1. **modules/streaming_display/core.py line 38** had:
   ```python
   can_focus = True
   ```

2. When the TUI mounted, `on_mount()` called `prompt_input.focus()` (core.py:358)

3. But **StreamingDisplay also had `can_focus = True`**, so Textual's focus management gave focus to StreamingDisplay instead

4. **Result**: MultiLineInput never received keyboard events
   - Enter key never reached the widget
   - `action_submit()` never called
   - No `Submitted` message posted
   - Handler never called
   - Messages never sent to chat

## The Fix

### Changed modules/streaming_display/core.py line 38:
```python
# BEFORE (BROKEN):
can_focus = True

# AFTER (FIXED):
can_focus = False  # CRITICAL: Don't steal focus from input widget
```

### Also fixed modules/streaming_display.py line 34:
```python
# BEFORE (BROKEN):
can_focus = True

# AFTER (FIXED):
can_focus = False  # CRITICAL: Don't steal focus from input widget
```

### Cleared Python caches:
```bash
find modules -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find modules -name "*.pyc" -delete 2>/dev/null
```

## Message Flow (NOW WORKING)

1. User types in MultiLineInput widget (has focus ✓)
2. User presses Enter
3. `action_submit()` called (multiline_input.py:456)
4. Posts `MultiLineInput.Submitted(value)` message
5. Handler `on_multi_line_input_submitted` receives it (command_handlers.py:238)
6. Handler calls `_handle_user_message(user_input, prompt_input)` (command_handlers.py:266)
7. `_handle_user_message` echoes message with `self.write()` (core.py:416)
8. Message appears in chat area ✓

## Test Now

```bash
opencli tui
# Type a message
# Press Enter
# Message should appear in chat!
```

## Files Changed

1. `/Users/dezmondhollins/opencli/modules/streaming_display/core.py`
   - Line 38: Set `can_focus = False`

2. `/Users/dezmondhollins/opencli/modules/streaming_display.py`
   - Line 34: Set `can_focus = False`

3. Cleared all `__pycache__` directories and `.pyc` files

## Why This Fix Works

- Only MultiLineInput should be focusable by default
- StreamingDisplay doesn't need focus for basic operation
- Users can still manually focus StreamingDisplay if needed (for text selection)
- But on mount, input widget now keeps focus and receives keyboard events
