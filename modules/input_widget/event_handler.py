"""
Event handling for MultiLineInput widget
Processes keyboard and paste events with permission priority
"""

from textual.events import Paste


# ═══════════════════════════════════════════════════════════
# CONTEXT-SPECIFIC KEY HANDLERS
# ═══════════════════════════════════════════════════════════

def handle_permission_keys(widget, event) -> bool:
    """
    Handle keys during PERMISSION PROMPT context

    BLOCKS all keys except:
    - UP/DOWN: Navigate options
    - ENTER: Confirm selection
    - ESCAPE: Cancel prompt

    Returns True to block all other keys
    """
    import sys
    key = event.key

    sys.stderr.write(f"[handle_permission_keys] KEY={key}\n")
    sys.stderr.flush()

    # LOG TO KEYS FILE
    with open('/tmp/opencli_keys.log', 'a') as f:
        f.write(f"[handle_permission_keys] KEY={key}\n")

    options = widget.permission_prompt_data.get('options', [])

    # If no options (informational prompt), only allow Escape
    if not options:
        if key == "escape":
            widget.post_message(widget.PermissionCancelled())
            event.prevent_default()
            return True
        # Block ALL other keys for informational prompts
        event.prevent_default()
        return True

    # Handle navigation for prompts with options
    if key == "up":
        if widget.permission_selected_option > 0:
            widget.permission_selected_option -= 1
            sys.stderr.write(f"[handle_permission_keys] UP: selected={widget.permission_selected_option}\n")
            sys.stderr.flush()
            widget.refresh()
        event.prevent_default()
        return True

    elif key == "down":
        if widget.permission_selected_option < len(options) - 1:
            widget.permission_selected_option += 1
            sys.stderr.write(f"[handle_permission_keys] DOWN: selected={widget.permission_selected_option}\n")
            sys.stderr.flush()
            widget.refresh()
        event.prevent_default()
        return True

    elif key == "enter":
        # Confirm selection
        selected = options[widget.permission_selected_option]
        sys.stderr.write(f"[handle_permission_keys] ENTER: confirming option={selected.get('text')}\n")
        sys.stderr.flush()
        widget.post_message(widget.PermissionResponse(selected))
        event.prevent_default()
        return True

    elif key == "escape":
        # Cancel
        sys.stderr.write(f"[handle_permission_keys] ESCAPE: cancelling\n")
        sys.stderr.flush()
        widget.post_message(widget.PermissionCancelled())
        event.prevent_default()
        return True

    # Block ALL other keys during permission prompt
    event.prevent_default()
    return True


def handle_suggestion_keys(widget, event) -> bool:
    """
    Handle keys during COMMAND SUGGESTION context

    Handles:
    - UP/DOWN: Navigate suggestions
    - ENTER: Select suggestion
    - ESCAPE: Hide suggestions
    - Other keys: Continue to normal handling (update query)

    Returns True if key was handled, False to continue to normal handling
    """
    import sys
    key = event.key

    sys.stderr.write(f"[handle_suggestion_keys] KEY={key}\n")
    sys.stderr.flush()

    if key == "up":
        widget.post_message(widget.CommandSuggestionNavigate("up"))
        event.prevent_default()
        return True

    elif key == "down":
        widget.post_message(widget.CommandSuggestionNavigate("down"))
        event.prevent_default()
        return True

    elif key == "enter":
        widget.post_message(widget.CommandSuggestionSelect())
        event.prevent_default()
        return True

    elif key == "escape":
        widget.post_message(widget.HideCommandSuggestions())
        widget.suggestions_active = False
        event.prevent_default()
        return True

    # For other keys (letters, backspace, etc), continue to normal handling
    return False


def handle_normal_keys(widget, event) -> bool:
    """
    Handle keys during NORMAL INPUT context

    Handles all text editing keys:
    - Character input
    - Backspace, Delete
    - Arrow keys (left/right for cursor movement)
    - Home, End
    - Enter (submit)

    Returns True if key was handled
    """
    import sys
    key = event.key

    # Don't handle up/down for history (let parent handle if needed)
    if key in ("up", "down"):
        return False  # Let parent handle history

    # Submit on enter
    if key == "enter":
        sys.stderr.write(f"[handle_normal_keys] ENTER: calling action_submit()\n")
        sys.stderr.flush()
        widget.action_submit()
        event.prevent_default()
        return True

    # Backspace
    if key == "backspace":
        if widget.cursor_position > 0:
            new_pos = widget.cursor_position - 1
            new_value = (
                widget.value[:new_pos] +
                widget.value[widget.cursor_position:]
            )
            widget.cursor_position = new_pos
            widget.value = new_value
        event.prevent_default()
        return True

    # Delete
    if key == "delete":
        if widget.cursor_position < len(widget.value):
            widget.value = (
                widget.value[:widget.cursor_position] +
                widget.value[widget.cursor_position+1:]
            )
        event.prevent_default()
        return True

    # Left arrow
    if key == "left":
        if widget.cursor_position > 0:
            widget.cursor_position -= 1
        event.prevent_default()
        return True

    # Right arrow
    if key == "right":
        if widget.cursor_position < len(widget.value):
            widget.cursor_position += 1
        event.prevent_default()
        return True

    # Home
    if key == "home":
        widget.cursor_position = 0
        event.prevent_default()
        return True

    # End
    if key == "end":
        widget.cursor_position = len(widget.value)
        event.prevent_default()
        return True

    # Ctrl+C - Cancel
    if key == "ctrl+c":
        sys.stderr.write(f"[handle_normal_keys] CTRL+C: calling action_cancel()\n")
        sys.stderr.flush()
        widget.action_cancel()
        event.prevent_default()
        return True

    # Character input
    if event.character and event.character.isprintable():
        old_value = widget.value
        widget.value = (
            widget.value[:widget.cursor_position] +
            event.character +
            widget.value[widget.cursor_position:]
        )
        widget.cursor_position += 1

        # Debug log
        with open('/tmp/opencli_keys.log', 'a') as f:
            f.write(f"[handle_normal_keys] char='{event.character}' old='{old_value}' new='{widget.value}'\n")

        event.prevent_default()
        return True

    return False


# ═══════════════════════════════════════════════════════════
# MAIN KEY EVENT DISPATCHER
# ═══════════════════════════════════════════════════════════

def handle_key_event(widget, event) -> bool:
    """
    Main key event dispatcher with CONTEXTUAL PRIORITY

    Priority order:
    1. PERMISSION PROMPT - Blocks ALL other input
    2. COMMAND SUGGESTIONS - Handles navigation, falls through for text
    3. NORMAL INPUT - Standard text editing

    Returns:
        True if event was handled (prevents default)
        False if event should propagate
    """
    import sys
    key = event.key

    # DEBUG logging
    sys.stderr.write(f"\n🔥🔥🔥 [handle_key_event] KEY={key} 🔥🔥🔥\n")
    sys.stderr.write(f"[handle_key_event] permission_state={widget.permission_state}\n")
    sys.stderr.write(f"[handle_key_event] prompt={bool(widget.permission_prompt_data)}, focused={widget.has_focus}\n")
    sys.stderr.write(f"[handle_key_event] suggestions={widget.suggestions_active}, value='{widget.value}'\n")
    sys.stderr.flush()

    # ═══════════════════════════════════════════════════════════
    # PRIORITY 1: PERMISSION PROMPT (blocks ALL other input)
    # ═══════════════════════════════════════════════════════════
    # CRITICAL: Check permission_state instead of just permission_prompt_data
    # This prevents race condition where data is cleared before keys are pressed
    if widget.permission_state == "LISTENING":
        sys.stderr.write(f"[handle_key_event] → Permission LISTENING - Routing to handle_permission_keys()\n")
        sys.stderr.flush()
        return handle_permission_keys(widget, event)

    # ═══════════════════════════════════════════════════════════
    # PRIORITY 2: COMMAND SUGGESTIONS (if active)
    # ═══════════════════════════════════════════════════════════
    if widget.suggestions_active:
        sys.stderr.write(f"[handle_key_event] → Routing to handle_suggestion_keys()\n")
        sys.stderr.flush()
        handled = handle_suggestion_keys(widget, event)
        if handled:
            return True
        # Fall through to normal handling for text editing
        sys.stderr.write(f"[handle_key_event] → Falling through to handle_normal_keys()\n")
        sys.stderr.flush()

    # ═══════════════════════════════════════════════════════════
    # PRIORITY 3: NORMAL INPUT
    # ═══════════════════════════════════════════════════════════
    sys.stderr.write(f"[handle_key_event] → Routing to handle_normal_keys()\n")
    sys.stderr.flush()
    return handle_normal_keys(widget, event)


# ═══════════════════════════════════════════════════════════
# PASTE EVENT HANDLER
# ═══════════════════════════════════════════════════════════

def handle_paste_event(widget, event: Paste) -> None:
    """
    Handle paste events
    Blocked during permission prompts
    """
    # Don't allow paste during permission prompts
    # CRITICAL: Check permission_state to prevent race condition
    if widget.permission_state == "LISTENING":
        event.prevent_default()
        return

    # Insert pasted text at cursor position
    pasted_text = event.text
    # Remove any newlines from pasted text to keep single-line input
    pasted_text = pasted_text.replace('\n', ' ').replace('\r', '')

    widget.value = (
        widget.value[:widget.cursor_position] +
        pasted_text +
        widget.value[widget.cursor_position:]
    )
    widget.cursor_position += len(pasted_text)
    event.prevent_default()
