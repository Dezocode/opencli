"""
Event handling for MultiLineInput widget
Processes keyboard and paste events with permission priority
"""

from textual.events import Paste
from .messages import (
    PermissionResponse, PermissionCancelled,
    CommandSuggestionNavigate, HideCommandSuggestions,
    CommandSuggestionSelect
)


def handle_key_event(widget, event) -> bool:
    """
    Handle key press with PERMISSION PRIORITY

    Returns:
        True if event was handled (prevents default)
        False if event should propagate
    """
    import sys
    key = event.key

    # DEBUG logging
    sys.stderr.write(f"\n[handle_key_event] KEY={key} prompt={bool(widget.permission_prompt_data)} focused={widget.has_focus}\n")
    sys.stderr.flush()

    # ═══════════════════════════════════════════════════════════
    # PRIORITY 1: PERMISSION PROMPT (blocks ALL other input)
    # ═══════════════════════════════════════════════════════════
    if widget.permission_prompt_data:
        sys.stderr.write(f"[handle_key_event] PERMISSION MODE ACTIVE\n")
        sys.stderr.flush()

        options = widget.permission_prompt_data.get('options', [])

        # If no options (informational prompt), only allow Escape
        if not options:
            if key == "escape":
                widget.post_message(PermissionCancelled())
                event.prevent_default()
                return True
            return True  # Block ALL other keys for informational prompts

        # Handle navigation for prompts with options
        if key == "up":
            if widget.permission_selected_option > 0:
                widget.permission_selected_option -= 1
                widget.refresh()
            event.prevent_default()
            return True
        elif key == "down":
            if widget.permission_selected_option < len(options) - 1:
                widget.permission_selected_option += 1
                widget.refresh()
            event.prevent_default()
            return True
        elif key == "enter":
            # Confirm selection
            selected = options[widget.permission_selected_option]
            widget.post_message(PermissionResponse(selected))
            event.prevent_default()
            return True
        elif key == "escape":
            # Cancel
            widget.post_message(PermissionCancelled())
            event.prevent_default()
            return True

        # Block ALL other keys during permission prompt
        event.prevent_default()
        return True

    # ═══════════════════════════════════════════════════════════
    # PRIORITY 2: COMMAND SUGGESTIONS (if active)
    # ═══════════════════════════════════════════════════════════
    if widget.suggestions_active:
        if key == "up":
            widget.post_message(CommandSuggestionNavigate("up"))
            event.prevent_default()
            return True
        elif key == "down":
            widget.post_message(CommandSuggestionNavigate("down"))
            event.prevent_default()
            return True
        elif key == "enter":
            widget.post_message(CommandSuggestionSelect())
            event.prevent_default()
            return True
        elif key == "escape":
            widget.post_message(HideCommandSuggestions())
            widget.suggestions_active = False
            event.prevent_default()
            return True
        # For other keys, continue to normal handling (update query)

    # ═══════════════════════════════════════════════════════════
    # PRIORITY 3: NORMAL INPUT (only if no permission/suggestions)
    # ═══════════════════════════════════════════════════════════

    # Don't handle up/down for history (only if no suggestions)
    if key in ("up", "down") and not widget.suggestions_active:
        return False  # Let parent handle history

    # Submit on enter
    if key == "enter":
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

    # Character input
    if event.character and event.character.isprintable():
        widget.value = (
            widget.value[:widget.cursor_position] +
            event.character +
            widget.value[widget.cursor_position:]
        )
        widget.cursor_position += 1
        event.prevent_default()
        return True

    return False


def handle_paste_event(widget, event: Paste) -> None:
    """
    Handle paste events
    Blocked during permission prompts
    """
    # Don't allow paste during permission prompts
    if widget.permission_prompt_data:
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
