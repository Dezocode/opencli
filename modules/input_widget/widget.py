"""
Core MultiLineInput widget
Permission-first input with command suggestions and spinner
"""

from textual.widget import Widget
from textual.reactive import reactive
from textual.events import Paste
from rich.text import Text
import asyncio

# Import modular components
from .messages import Submitted, ShowCommandSuggestions, HideCommandSuggestions
from .permission_renderer import render_permission_prompt
from .event_handler import handle_key_event, handle_paste_event


class MultiLineInput(Widget):
    """
    Multi-line input with PERMISSION-FIRST architecture

    Priority order:
    1. Permission prompts (blocks ALL other input)
    2. Command suggestions (if active)
    3. Normal text input
    """

    # Reactive properties
    value = reactive("", layout=True)
    cursor_position = reactive(0)
    is_spinning = reactive(False)
    spinner_frame = reactive(0)
    permission_prompt_data = reactive(None)  # When set, takes FULL control
    permission_selected_option = reactive(0)

    # Spinner frames
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    # Export message classes for convenience
    Submitted = Submitted

    def __init__(self, placeholder: str = "", **kwargs):
        super().__init__(**kwargs)
        self.placeholder = placeholder
        self._lines = [""]
        self._cursor_row = 0
        self._cursor_col = 0
        self.can_focus = True
        self._spin_task = None
        self.suggestions_active = False

    def on_focus(self) -> None:
        """Track when widget receives focus"""
        import sys
        sys.stderr.write(f"\n[MultiLineInput.on_focus] GAINED FOCUS - prompt={bool(self.permission_prompt_data)}\n")
        sys.stderr.flush()
        self.refresh()

    def on_blur(self) -> None:
        """Track when widget loses focus - DO NOT auto-dismiss permission prompts"""
        import sys
        sys.stderr.write(f"\n[MultiLineInput.on_blur] LOST FOCUS - prompt={bool(self.permission_prompt_data)}\n")
        sys.stderr.flush()

        # CRITICAL FIX: Do NOT auto-dismiss permission prompts on blur
        # The widget may temporarily lose focus during setup or layout changes
        # Permission prompts should only be dismissed by:
        # 1. User pressing Enter (selection)
        # 2. User pressing Escape (cancellation)
        # NOT by focus loss!

        self.refresh()

    def render(self) -> Text:
        """Render with PERMISSION PRIORITY"""

        # ═══════════════════════════════════════════════════════════
        # PRIORITY: Show permission prompt if active (overrides everything)
        # ═══════════════════════════════════════════════════════════
        if self.permission_prompt_data:
            return render_permission_prompt(
                self.permission_prompt_data,
                self.permission_selected_option
            )

        # ═══════════════════════════════════════════════════════════
        # NORMAL INPUT (only when no permission prompt)
        # ═══════════════════════════════════════════════════════════
        display = Text()

        # Add spinner if active, otherwise show >
        if self.is_spinning:
            frame = self.SPINNER_FRAMES[self.spinner_frame % len(self.SPINNER_FRAMES)]
            prefix = frame + " "
            display.append(prefix, style="dim cyan")
        else:
            prefix = "> "
            display.append(prefix, style="dim")

        # Show placeholder if empty and not focused
        if not self.value and self.placeholder and not self.has_focus:
            display.append(self.placeholder, style="dim")
            return display

        # Show empty cursor if no value but focused
        if not self.value and self.has_focus:
            display.append(" ", style="reverse")
            return display

        # Show empty text if no value and no focus
        if not self.value:
            return display

        # Show value with cursor
        if self.has_focus:
            before = self.value[:self.cursor_position]
            if self.cursor_position < len(self.value):
                cursor = self.value[self.cursor_position]
                after = self.value[self.cursor_position + 1:]
                display.append(before)
                display.append(cursor, style="reverse")
                display.append(after)
            else:
                # Cursor at end
                display.append(self.value)
                display.append(" ", style="reverse")
        else:
            # No focus, just show value
            display.append(self.value)

        return display

    def _wrap_text(self, text: str, width: int = None) -> list[str]:
        """Wrap text to fit width"""
        if width is None:
            width = self.size.width - 2  # Account for padding

        if width <= 0:
            return [text]

        lines = []
        current_line = ""

        for char in text:
            if char == '\n':
                lines.append(current_line)
                current_line = ""
            elif len(current_line) >= width:
                lines.append(current_line)
                current_line = char
            else:
                current_line += char

        if current_line or not lines:
            lines.append(current_line)

        return lines

    def on_paste(self, event: Paste) -> None:
        """Handle paste events"""
        handle_paste_event(self, event)

    def on_key(self, event) -> None:
        """Handle key presses with PERMISSION PRIORITY"""
        handle_key_event(self, event)

    def action_submit(self) -> None:
        """Submit the current value or select permission option"""
        import sys
        sys.stderr.write(f"\n[ACTION_SUBMIT] CALLED\n")
        sys.stderr.write(f"[ACTION_SUBMIT] value='{self.value}'\n")
        sys.stderr.write(f"[ACTION_SUBMIT] suggestions_active={self.suggestions_active}\n")
        sys.stderr.write(f"[ACTION_SUBMIT] permission_prompt_data={bool(self.permission_prompt_data)}\n")
        sys.stderr.flush()

        # If permission prompt is active, select the current option
        if self.permission_prompt_data:
            options = self.permission_prompt_data.get('options', [])
            if options and 0 <= self.permission_selected_option < len(options):
                selected_option = options[self.permission_selected_option]
                sys.stderr.write(f"[ACTION_SUBMIT] Selecting permission option: {selected_option.get('text')}\n")
                sys.stderr.flush()
                from .messages import PermissionResponse
                self.post_message(PermissionResponse(selected_option))
                self.permission_prompt_data = None  # Clear prompt after selection
                return

        # If suggestions are active, handle as command selection instead
        if self.suggestions_active:
            sys.stderr.write(f"[ACTION_SUBMIT] Posting CommandSuggestionSelect\n")
            sys.stderr.flush()
            from .messages import CommandSuggestionSelect
            self.post_message(CommandSuggestionSelect())
            return

        # Normal submission
        if self.value.strip():
            sys.stderr.write(f"[ACTION_SUBMIT] Posting Submitted('{self.value}')\n")
            sys.stderr.flush()
            self.post_message(Submitted(self.value))
        else:
            sys.stderr.write(f"[ACTION_SUBMIT] Value empty after strip, not posting\n")
            sys.stderr.flush()

    def action_cancel(self) -> None:
        """Cancel input (clear the field) or cancel permission prompt"""
        import sys
        sys.stderr.write(f"\n[ACTION_CANCEL] CALLED\n")
        sys.stderr.write(f"[ACTION_CANCEL] permission_prompt_data={bool(self.permission_prompt_data)}\n")
        sys.stderr.flush()

        # If permission prompt is active, cancel it
        if self.permission_prompt_data:
            sys.stderr.write(f"[ACTION_CANCEL] Cancelling permission prompt\n")
            sys.stderr.flush()
            from .messages import PermissionCancelled
            self.post_message(PermissionCancelled())
            self.permission_prompt_data = None  # Clear prompt after cancel
            return

        # Normal cancel - clear the field
        self.value = ""
        self.cursor_position = 0

    def clear(self) -> None:
        """Clear the input"""
        self.value = ""
        self.cursor_position = 0

    def watch_value(self, old_value: str, new_value: str) -> None:
        """Update when value changes - detect slash commands"""
        # DEBUG LOGGING
        import os
        if os.getenv('OPENCLI_DEBUG_AUTOCOMPLETE'):
            with open('/tmp/opencli-autocomplete-debug.log', 'a') as f:
                f.write(f"[watch_value] old='{old_value}' new='{new_value}' starts_with_slash={new_value.startswith('/')}\n")

        # Always log to opencli_keys.log
        with open('/tmp/opencli_keys.log', 'a') as f:
            f.write(f"[watch_value] CALLED! old='{old_value}' new='{new_value}'\n")

        # Ensure cursor is within bounds
        if self.cursor_position > len(new_value):
            self.cursor_position = len(new_value)

        # Detect slash command input
        if new_value.startswith('/'):
            # Show/update command suggestions
            self.suggestions_active = True
            self.post_message(ShowCommandSuggestions(new_value))

            # DEBUG
            if os.getenv('OPENCLI_DEBUG_AUTOCOMPLETE'):
                with open('/tmp/opencli-autocomplete-debug.log', 'a') as f:
                    f.write(f"[watch_value] Posted ShowCommandSuggestions('{new_value}')\n")

            with open('/tmp/opencli_keys.log', 'a') as f:
                f.write(f"[watch_value] SLASH DETECTED! Posting ShowCommandSuggestions\n")
        else:
            # Hide suggestions if not a slash command
            if self.suggestions_active:
                self.suggestions_active = False
                self.post_message(HideCommandSuggestions())

                # DEBUG
                if os.getenv('OPENCLI_DEBUG_AUTOCOMPLETE'):
                    with open('/tmp/opencli-autocomplete-debug.log', 'a') as f:
                        f.write(f"[watch_value] Posted HideCommandSuggestions\n")

                with open('/tmp/opencli_keys.log', 'a') as f:
                    f.write(f"[watch_value] Hiding suggestions\n")

        self.refresh()

    # ═══════════════════════════════════════════════════════════
    # Spinner methods
    # ═══════════════════════════════════════════════════════════

    def start_spinner(self) -> None:
        """Start the spinner animation"""
        if not self.is_spinning:
            self.is_spinning = True
            if self._spin_task is None or self._spin_task.done():
                self._spin_task = asyncio.create_task(self._spin())

    def stop_spinner(self) -> None:
        """Stop the spinner animation"""
        self.is_spinning = False
        if self._spin_task and not self._spin_task.done():
            try:
                self._spin_task.cancel()
            except Exception:
                pass
        self.spinner_frame = 0
        self._spin_task = None
        self.refresh()

    async def _spin(self) -> None:
        """Async task that updates the spinner"""
        try:
            while self.is_spinning:
                self.spinner_frame = (self.spinner_frame + 1) % len(self.SPINNER_FRAMES)
                self.refresh()
                await asyncio.sleep(0.08)  # 80ms per frame
        except asyncio.CancelledError:
            pass

    def watch_is_spinning(self, old_value: bool, new_value: bool) -> None:
        """React to spinning state changes"""
        if old_value != new_value:
            self.refresh()

    def watch_spinner_frame(self, old_value: int, new_value: int) -> None:
        """React to frame changes"""
        pass  # Refresh handled by _spin()

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
                # CRITICAL: Initialize selected option from prompt data
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

    def watch_permission_selected_option(self, old_value: int, new_value: int) -> None:
        """Watch for selection changes to trigger UI refresh"""
        import sys
        sys.stderr.write(f"[widget.watch_permission_selected_option] {old_value} -> {new_value}\n")
        sys.stderr.flush()

        if old_value != new_value and self.permission_prompt_data:
            self.refresh()
            sys.stderr.write(f"[widget] REFRESH triggered by selection change\n")
            sys.stderr.flush()
