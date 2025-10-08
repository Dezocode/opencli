# Debug: Slash Command Flow Analysis

## Expected Flow When User Types `/local` + Enter

### Step 1: User types `/`
**File**: `modules/multiline_input.py`
**Method**: `watch_value()`
**Line**: 372

```python
if new_value.startswith('/'):
    self.suggestions_active = True
    self.post_message(self.ShowCommandSuggestions(new_value))
```

**Expected**:
- `suggestions_active` = True
- ShowCommandSuggestions message posted

### Step 2: SimpleTUI receives message
**File**: `modules/simple_tui.py`
**Method**: `on_multi_line_input_show_command_suggestions()`
**Line**: 745

```python
# Search commands
matches = registry.search_commands(query, feature_flags=feature_flags)

# Update suggestion buffer
suggestions_buffer.update_suggestions(command_matches, query)

# Show the buffer
suggestions_buffer.remove_class("hidden")
```

**Expected**:
- Command registry searched
- Buffer updated with matches
- Buffer visible

### Step 3: User presses Enter
**File**: `modules/multiline_input.py`
**Method**: `on_key()`
**Line**: 267

```python
if self.suggestions_active:
    if key == "enter":
        self.post_message(self.CommandSuggestionSelect())
        event.prevent_default()
        return
```

**Expected**:
- CommandSuggestionSelect message posted
- Default Enter behavior prevented

### Step 4: SimpleTUI handles selection
**File**: `modules/simple_tui.py`
**Method**: `on_multi_line_input_command_suggestion_select()`
**Line**: 841

```python
# Get selected command
selected = suggestions_buffer.get_selected_command()

if selected:
    # Record usage
    registry.record_usage(selected.name)

    # Hide suggestions
    suggestions_buffer.add_class("hidden")
    suggestions_buffer.clear()
    prompt_input.suggestions_active = False

    # Execute the command
    await self._handle_user_message(selected.name, prompt_input)
```

**Expected**:
- Selected command retrieved
- Usage recorded
- Suggestions hidden
- Command passed to `_handle_user_message`

### Step 5: _handle_user_message processes
**File**: `modules/simple_tui.py`
**Method**: `_handle_user_message()`
**Line**: 1132

```python
# Show user message
self.write(f"[{user_color}]{username}:[/{user_color}] [{text_color}]{user_input}[/{text_color}]\n\n")

# Call message handler if set
if self.message_handler:
    await self.message_handler(user_input)
```

**Expected**:
- Message displayed in UI
- `message_handler` called with command

### Step 6: handle_user_input in async_interactive
**File**: `modules/async_interactive.py`
**Method**: `handle_user_input()`
**Line**: 914 + 1122

```python
# Handle slash commands
if user_input.startswith('/'):
    # Handle /debug command
    if user_input.startswith('/debug'):
        # ... handle debug
        return

    # Handle /local command
    if user_input.startswith('/local'):
        # ... handle local
        return
```

**Expected**:
- Slash command detected
- Command handled locally
- Returns WITHOUT calling API

---

## Potential Issues

### Issue 1: watch_value not called
**Symptom**: Autocomplete dropdown never shows
**Cause**: User is running old code (cache issue)
**Fix**: Sync files to ~/.opencli/modules/ and clear cache

### Issue 2: suggestions_active not set
**Symptom**: Enter key bypasses autocomplete
**Cause**: `watch_value()` not setting flag correctly
**Debug**: Check if `suggestions_active` is True when Enter pressed

### Issue 3: Message handler not set
**Symptom**: Nothing happens when Enter pressed
**Cause**: `app.message_handler` not assigned
**Debug**: Check if `message_handler` is set in async_interactive startup

### Issue 4: Slash command not in async_interactive
**Symptom**: Command sent to API instead of handled locally
**Cause**: Missing slash command handler for specific command
**Debug**: Check if command has handler in async_interactive.py

### Issue 5: Command misspelled
**Symptom**: `/loacl` (typo) sent to API
**Cause**: Typo doesn't match registered command `/local`
**Debug**: User needs to use autocomplete or fix typo

---

## Debugging Steps

### 1. Enable debug logging
```bash
export OPENCLI_DEBUG_AUTOCOMPLETE=1
cd ~/.opencli
python3 opencli.py
```

### 2. Type `/` and check log
```bash
cat /tmp/opencli-autocomplete-debug.log
```

**Expected output**:
```
[watch_value] old='' new='/' starts_with_slash=True
[watch_value] Posted ShowCommandSuggestions('/')
[SimpleTUI] Received ShowCommandSuggestions('/')
[SimpleTUI] Found suggestions buffer
[SimpleTUI] Found 27 matches
[SimpleTUI] Updated suggestions buffer
[SimpleTUI] Removed 'hidden' class from buffer
```

### 3. Type `local` after `/`
**Expected**: Log shows updated query `/local`

### 4. Press Enter
**Expected**: Command executes locally, NOT sent to API

### 5. Check if command appears in chat
**If command appears followed by "✦"**: SENT TO API (BUG)
**If command shows result directly**: Handled locally (CORRECT)

---

## Quick Test Commands

### Commands that SHOULD be handled locally:
- `/debug` - Toggle debug mode
- `/performance` - Performance monitoring
- `/reload` - Hot-reload modules
- `/local` - Local model setup
- `/model` - Model management
- `/status` - Show status

### Commands that MIGHT go to API (if not implemented):
- Any unknown slash command
- Misspelled commands
- Commands without handlers

---

## Fix Checklist

If slash commands are still sent to API:

- [ ] Files synced to ~/.opencli/modules/
- [ ] Cache cleared in ~/.opencli/
- [ ] OpenCLI restarted (old process killed)
- [ ] Debug logging enabled
- [ ] Log shows autocomplete activating
- [ ] `suggestions_active` = True when typing `/`
- [ ] Enter key posts CommandSuggestionSelect
- [ ] message_handler is set (not None)
- [ ] handle_user_input checks for slash commands
- [ ] Specific command has handler in async_interactive.py

