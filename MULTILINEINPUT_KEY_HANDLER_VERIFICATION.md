# MultiLineInput Key Handler Verification

## Executive Summary

**YES**, MultiLineInput has a key handler. This document verifies and documents the key handling architecture for permission prompts in the OpenCLI TUI.

## Findings

### 1. MultiLineInput Key Handler ✓

**Location:** `/modules/input_widget/widget.py` lines 405-424

**Method:** `handle_key_message(event: Key)`

**Decorator:** `@on(Key)` - Modern Textual key event handling

**Behavior:**
- Intercepts ALL key events before they bubble up
- Calls `event.stop()` immediately on line 414 to prevent propagation
- Routes keys to context-specific handlers in `event_handler.py`

```python
@on(Key)
def handle_key_message(self, event: Key) -> None:
    """
    DIRECT Key message handler - catches ALL keys INCLUDING ARROWS
    Uses @on(Key) decorator to intercept Key messages before parent widgets can consume them
    """
    # STOP event bubbling IMMEDIATELY
    event.stop()
    
    # Handle the key event
    handle_key_event(self, event)
```

### 2. Permission Prompt Display Architecture ✓

**How it works:**
1. Permission prompts are displayed **inside** the MultiLineInput widget
2. Set via: `prompt_input.permission_prompt_data = prompt_data`
3. Rendered in: `MultiLineInput.render()` method (lines 322-326)

```python
def render(self) -> Text:
    """Render with PERMISSION PRIORITY"""
    
    # PRIORITY: Show permission prompt if active (overrides everything)
    if self.permission_prompt_data:
        return render_permission_prompt(
            self.permission_prompt_data,
            self.permission_selected_option
        )
    
    # ... normal input rendering ...
```

### 3. Key Event Routing ✓

**Priority order** (in `event_handler.py`):

1. **PERMISSION PROMPT** - Blocks ALL other input
   - UP/DOWN: Navigate options
   - ENTER: Confirm selection
   - ESCAPE: Cancel prompt
   - All other keys: Blocked

2. **COMMAND SUGGESTIONS** - If active
   - UP/DOWN: Navigate suggestions
   - ENTER: Select suggestion
   - ESCAPE: Hide suggestions
   - Other keys: Fall through to normal input

3. **NORMAL INPUT** - Standard text editing
   - Character input, backspace, delete
   - Arrow keys for cursor movement
   - Home, End
   - ENTER: Submit

### 4. Separate PermissionPrompt Widget ⚠️

**Location:** `/modules/permissions/widget.py`

**Status:** EXISTS but NOT USED

**Details:**
- Has its own `on_key()` method (lines 186-232)
- Instantiated in `integration.py` but never added to UI tree
- Its `on_key()` handler never receives events
- Permission prompts are displayed via MultiLineInput instead

```python
class PermissionPrompt(Widget):
    """
    Permission prompt widget with formatted box and selectable options
    Displays in the chat area, between messages like the buffer status
    """
    
    def on_key(self, event) -> None:
        """Handle key presses for option selection"""
        # This method exists but is never called!
        # Permission prompts are displayed in MultiLineInput instead
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         TUI Layout                          │
├─────────────────────────────────────────────────────────────┤
│  Content Area                                               │
│  (Messages, Responses)                                      │
├─────────────────────────────────────────────────────────────┤
│  Command Suggestions                                        │
│  (Hidden by default)                                        │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐ │
│  │ MultiLineInput (id="prompt-input")                    │ │
│  │                                                         │ │
│  │ When permission_prompt_data is set:                    │ │
│  │ ┌─────────────────────────────────────────────────┐   │ │
│  │ │ ╭──────────────────────────────────────────╮    │   │ │
│  │ │ │ Permission Required                      │    │   │ │
│  │ │ │                                          │    │   │ │
│  │ │ │ Details: /help command                  │    │   │ │
│  │ │ │                                          │    │   │ │
│  │ │ │ Allow this operation?                   │    │   │ │
│  │ │ │                                          │    │   │ │
│  │ │ │ ❯ 1. Yes, allow this once               │    │   │ │
│  │ │ │   2. No, cancel                         │    │   │ │
│  │ │ │                                          │    │   │ │
│  │ │ ╰──────────────────────────────────────────╯    │   │ │
│  │ │   (Rendered inline in MultiLineInput)           │   │ │
│  │ └─────────────────────────────────────────────────┘   │ │
│  │                                                         │ │
│  │ @on(Key) handle_key_message()                          │ │
│  │   ↓                                                     │ │
│  │   event.stop() ← BLOCKS propagation                    │ │
│  │   ↓                                                     │ │
│  │   handle_key_event()                                   │ │
│  │     ├─ Permission keys → handle_permission_keys()      │ │
│  │     ├─ Suggestion keys → handle_suggestion_keys()      │ │
│  │     └─ Normal keys → handle_normal_keys()              │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Status Lines                                               │
└─────────────────────────────────────────────────────────────┘

Note: PermissionPrompt widget exists but is never added to this tree!
```

## Key Handler Methods Comparison

| Widget | Method | Used? | Notes |
|--------|--------|-------|-------|
| MultiLineInput | `@on(Key) handle_key_message()` | ✅ YES | Intercepts ALL keys, stops propagation |
| PermissionPrompt | `on_key()` | ❌ NO | Widget never added to UI tree |

## Verification Test Results

**Test Script:** `test_multiline_input_key_handler.py`

```
✓ MultiLineInput HAS key handler (@on(Key) decorator)
✓ Permission prompts ARE displayed in MultiLineInput
✓ MultiLineInput.handle_key_message() intercepts all keys
✓ Separate PermissionPrompt widget EXISTS but is NOT used
```

## Conclusion

**Answer to the question: "check if MultiLineInput has an on_key() handler"**

**YES**, MultiLineInput has a key handler:
- Uses modern `@on(Key)` decorator (not `on_key()` method)
- Method name: `handle_key_message()`
- Intercepts all key events with `event.stop()`
- Routes keys to context-specific handlers

**Current Architecture:**
- Permission prompts are displayed INSIDE MultiLineInput widget
- Keys are handled by MultiLineInput's key handler
- Separate PermissionPrompt widget exists but is unused
- All key handling is centralized in MultiLineInput

**Design Rationale:**
This appears to be an intentional design choice to:
1. Keep all input-related key handling in one place
2. Avoid focus management complexities with separate widgets
3. Ensure permission prompts can't lose focus during interaction

## Related Files

- `/modules/input_widget/widget.py` - MultiLineInput widget
- `/modules/input_widget/event_handler.py` - Key routing logic
- `/modules/input_widget/permission_renderer.py` - Permission prompt rendering
- `/modules/permissions/widget.py` - Unused PermissionPrompt widget
- `/modules/tui/core.py` - TUI layout (compose method)
- `/modules/tui/permission_handlers.py` - Permission prompt display logic

## Testing

Run verification test:
```bash
python3 test_multiline_input_key_handler.py
```

Expected output: All checks pass, confirming MultiLineInput has key handler.
