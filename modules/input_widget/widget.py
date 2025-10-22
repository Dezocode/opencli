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
from .permission_renderer import render_permission_prompt
from .event_handler import handle_key_event, handle_paste_event
from textual.message import Message


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

    # ═══════════════════════════════════════════════════════════
    # NESTED MESSAGE CLASSES (CRITICAL for Textual handler routing!)
    # ═══════════════════════════════════════════════════════════

    class Submitted(Message):
        """Posted when user submits the input"""
        bubble = True  # CRITICAL: Must reach parent TUI for message sending!

        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    class PermissionResponse(Message):
        """Posted when user selects a permission option"""
        bubble = True  # CRITICAL: Must reach parent TUI for permission handling!

        def __init__(self, option: dict) -> None:
            self.option = option
            super().__init__()

    class PermissionCancelled(Message):
        """Posted when user cancels permission prompt"""
        bubble = True  # CRITICAL: Must reach parent TUI for permission handling!

    class ShowCommandSuggestions(Message):
        """Posted when slash command typed - triggers suggestion buffer"""
        bubble = True  # CRITICAL: Must reach parent TUI for autosuggest!

        def __init__(self, query: str) -> None:
            self.query = query
            super().__init__()

    class HideCommandSuggestions(Message):
        """Posted when suggestions should be hidden"""
        bubble = True  # CRITICAL: Must reach parent TUI!

    class CommandSuggestionNavigate(Message):
        """Posted when user navigates in suggestions with arrow keys"""
        bubble = True  # CRITICAL: Must reach parent TUI!

        def __init__(self, direction: str) -> None:
            self.direction = direction  # "up" or "down"
            super().__init__()

    class CommandSuggestionSelect(Message):
        """Posted when user presses Enter with suggestions active"""
        bubble = True  # CRITICAL: Must reach parent TUI!

    class NavigationEvent(Message):
        """Posted when user navigates away (focus lost) - triggers auto-dismiss"""
        def __init__(self, event_type: str) -> None:
            self.event_type = event_type  # "focus_lost", "window_change", etc.
            super().__init__()

    def __init__(self, placeholder: str = "", **kwargs):
        super().__init__(**kwargs)
        self.placeholder = placeholder
        self._lines = [""]
        self._cursor_row = 0
        self._cursor_col = 0
        self.can_focus = True
        self._spin_task = None
        self.suggestions_active = False

    def _watch_has_focus(self, has_focus: bool) -> None:
        """
        Override Textual's focus watcher to PREVENT focus loss during permission prompts
        This is called BEFORE on_blur/on_focus, so we can BLOCK the focus change here
        """
        import sys
        from ..focus_logger import log_focus_event

        sys.stderr.write(f"\n[MultiLineInput._watch_has_focus] Focus changing: {self.has_focus} -> {has_focus}, permission={bool(self.permission_prompt_data)}\n")
        sys.stderr.flush()

        # ═══════════════════════════════════════════════════════════
        # CRITICAL: PREVENT focus loss when permission is active
        # ═══════════════════════════════════════════════════════════
        if not has_focus and self.permission_prompt_data:
            sys.stderr.write(f"[MultiLineInput._watch_has_focus] 🔒 BLOCKING FOCUS LOSS - Permission active!\n")
            sys.stderr.flush()

            log_focus_event(
                source_file="input_widget/widget.py",
                source_function="_watch_has_focus",
                event_type="FOCUS_LOCK",
                widget_type="MultiLineInput",
                extra_info="BLOCKED focus loss - permission active"
            )

            # FORCE focus back to this widget
            if hasattr(self, 'app') and self.app:
                self.app.set_focus(self)
                sys.stderr.write(f"[MultiLineInput._watch_has_focus] ✓ Force re-focused via app.set_focus()\n")
                sys.stderr.flush()
            return  # DON'T call super() - we're blocking this focus change!

        # Normal focus changes - allow them
        super()._watch_has_focus(has_focus)

    def focus(self, scroll_visible: bool = True) -> None:
        """Override focus() to maintain focus lock during permission prompts"""
        import sys
        from ..focus_logger import log_focus_event

        # If THIS widget has permission active, ALLOW focus
        if self.permission_prompt_data:
            sys.stderr.write(f"[MultiLineInput.focus] PERMISSION ACTIVE - Allowing focus\n")
            sys.stderr.flush()
            log_focus_event(
                source_file="input_widget/widget.py",
                source_function="focus",
                event_type="PERMISSION_ACTIVE",
                widget_type="MultiLineInput",
                extra_info="Allowing focus - permission active"
            )
            super().focus(scroll_visible=scroll_visible)
            return

        # Normal focus behavior
        super().focus(scroll_visible=scroll_visible)

    def on_focus(self) -> None:
        """Track when widget receives focus"""
        import sys
        from ..focus_logger import log_focus_event, log_focus_state

        sys.stderr.write(f"\n[MultiLineInput.on_focus] GAINED FOCUS - prompt={bool(self.permission_prompt_data)}\n")
        sys.stderr.flush()

        # Log focus event
        log_focus_event(
            source_file="input_widget/widget.py",
            source_function="on_focus",
            event_type="GAINED_FOCUS",
            widget_type="MultiLineInput",
            extra_info=f"permission_active={bool(self.permission_prompt_data)}"
        )

        # Log current focus state
        log_focus_state(
            source_file="input_widget/widget.py",
            widget_type="MultiLineInput",
            has_focus=True,
            can_focus=self.can_focus,
            extra_info=f"permission={bool(self.permission_prompt_data)}"
        )

        self.refresh()

    def on_blur(self) -> None:
        """Track when widget loses focus - LOCK FOCUS during permission prompts"""
        import sys
        from ..focus_logger import log_focus_event, log_focus_attempt

        sys.stderr.write(f"\n[MultiLineInput.on_blur] ATTEMPT TO LOSE FOCUS - prompt={bool(self.permission_prompt_data)}\n")
        sys.stderr.flush()

        # Log blur attempt
        log_focus_event(
            source_file="input_widget/widget.py",
            source_function="on_blur",
            event_type="LOST_FOCUS",
            widget_type="MultiLineInput",
            extra_info=f"permission_active={bool(self.permission_prompt_data)}"
        )

        # ═══════════════════════════════════════════════════════════
        # CRITICAL: FOCUS LOCK during permission prompts
        # ═══════════════════════════════════════════════════════════
        if self.permission_prompt_data:
            sys.stderr.write(f"[MultiLineInput.on_blur] 🔒 FOCUS LOCK ACTIVE - REFUSING TO LOSE FOCUS!\n")
            sys.stderr.flush()

            # Log focus lock event
            log_focus_event(
                source_file="input_widget/widget.py",
                source_function="on_blur",
                event_type="FOCUS_LOCK",
                widget_type="MultiLineInput",
                extra_info="Permission active - re-grabbing focus immediately"
            )

            # IMMEDIATELY re-grab focus - DO NOT allow permission buffer to lose focus
            try:
                # Try app.set_focus first (most direct)
                if hasattr(self, 'app') and self.app:
                    log_focus_attempt(
                        source_file="input_widget/widget.py",
                        source_function="on_blur",
                        method="app.set_focus()",
                        widget_type="MultiLineInput",
                        success=None,
                        extra_info="FOCUS LOCK - re-grabbing focus"
                    )

                    self.app.set_focus(self)
                    sys.stderr.write(f"[MultiLineInput.on_blur] ✓ Re-grabbed focus via app.set_focus()\n")

                    log_focus_attempt(
                        source_file="input_widget/widget.py",
                        source_function="on_blur",
                        method="app.set_focus()",
                        widget_type="MultiLineInput",
                        success=True,
                        extra_info=f"FOCUS LOCK successful, has_focus={self.has_focus}"
                    )
                else:
                    # Fallback to widget.focus()
                    log_focus_attempt(
                        source_file="input_widget/widget.py",
                        source_function="on_blur",
                        method="widget.focus()",
                        widget_type="MultiLineInput",
                        success=None,
                        extra_info="FOCUS LOCK - fallback to self.focus()"
                    )

                    self.focus()
                    sys.stderr.write(f"[MultiLineInput.on_blur] ✓ Re-grabbed focus via self.focus()\n")

                    log_focus_attempt(
                        source_file="input_widget/widget.py",
                        source_function="on_blur",
                        method="widget.focus()",
                        widget_type="MultiLineInput",
                        success=True,
                        extra_info=f"FOCUS LOCK successful (fallback)"
                    )
                sys.stderr.flush()
            except Exception as e:
                sys.stderr.write(f"[MultiLineInput.on_blur] ⚠️  Focus re-grab failed: {e}\n")
                sys.stderr.flush()

                log_focus_attempt(
                    source_file="input_widget/widget.py",
                    source_function="on_blur",
                    method="app.set_focus() or widget.focus()",
                    widget_type="MultiLineInput",
                    success=False,
                    error=str(e),
                    extra_info="FOCUS LOCK failed!"
                )

            # DO NOT allow on_blur to complete normally - we've re-grabbed focus
            self.refresh()
            return

        # Normal blur (no permission prompt active) - allow focus loss
        sys.stderr.write(f"[MultiLineInput.on_blur] Normal blur (no permission prompt)\n")
        sys.stderr.flush()

        log_focus_event(
            source_file="input_widget/widget.py",
            source_function="on_blur",
            event_type="FOCUS_UNLOCK",
            widget_type="MultiLineInput",
            extra_info="Normal blur - no permission active"
        )

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
                self.post_message(self.PermissionResponse(selected_option))
                self.permission_prompt_data = None  # Clear prompt after selection
                return

        # If suggestions are active, handle as command selection instead
        if self.suggestions_active:
            sys.stderr.write(f"[ACTION_SUBMIT] Posting CommandSuggestionSelect\n")
            sys.stderr.flush()
            self.post_message(self.CommandSuggestionSelect())
            return

        # Normal submission
        if self.value.strip():
            sys.stderr.write(f"[ACTION_SUBMIT] Posting Submitted('{self.value}')\n")
            sys.stderr.flush()
            self.post_message(self.Submitted(self.value))
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
            self.post_message(self.PermissionCancelled())
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
            self.post_message(self.ShowCommandSuggestions(new_value))

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
                self.post_message(self.HideCommandSuggestions())

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

                # Log permission activation
                from ..focus_logger import log_focus_event, log_focus_attempt, log_focus_state
                log_focus_event(
                    source_file="input_widget/widget.py",
                    source_function="watch_permission_prompt_data",
                    event_type="PERMISSION_ACTIVE",
                    widget_type="MultiLineInput",
                    extra_info=f"title='{new_value.get('title', 'N/A')}', options={len(new_value.get('options', []))}"
                )

                # ═══════════════════════════════════════════════════════════
                # CRITICAL: AGGRESSIVELY GRAB FOCUS - DO NOT CHECK has_focus!
                # ═══════════════════════════════════════════════════════════

                # FIRST: Ensure widget CAN receive focus
                self.can_focus = True
                sys.stderr.write(f"[MultiLineInput] Set can_focus=True\n")
                sys.stderr.flush()

                # Log state before focus attempt
                log_focus_state(
                    source_file="input_widget/widget.py",
                    widget_type="MultiLineInput",
                    has_focus=self.has_focus,
                    can_focus=True,
                    extra_info="BEFORE aggressive focus grab"
                )

                # SECOND: Force focus IMMEDIATELY (no conditional checks)
                sys.stderr.write(f"[MultiLineInput] 🎯 FORCING FOCUS IMMEDIATELY (current focus={self.has_focus})\n")
                sys.stderr.flush()

                try:
                    # Try app.set_focus FIRST (most direct, synchronous)
                    if hasattr(self, 'app') and self.app:
                        log_focus_attempt(
                            source_file="input_widget/widget.py",
                            source_function="watch_permission_prompt_data",
                            method="app.set_focus()",
                            widget_type="MultiLineInput",
                            success=None,
                            extra_info="AGGRESSIVE GRAB - Initial attempt"
                        )

                        self.app.set_focus(self)
                        sys.stderr.write(f"[MultiLineInput] ✓ FORCED FOCUS via app.set_focus()\n")

                        log_focus_attempt(
                            source_file="input_widget/widget.py",
                            source_function="watch_permission_prompt_data",
                            method="app.set_focus()",
                            widget_type="MultiLineInput",
                            success=True,
                            extra_info=f"AGGRESSIVE GRAB successful, has_focus={self.has_focus}"
                        )

                        # ALSO schedule focus after next refresh to ensure it sticks
                        log_focus_attempt(
                            source_file="input_widget/widget.py",
                            source_function="watch_permission_prompt_data",
                            method="app.call_after_refresh(set_focus)",
                            widget_type="MultiLineInput",
                            success=None,
                            extra_info="STICKY FOCUS - Scheduling post-refresh grab"
                        )

                        self.app.call_after_refresh(lambda: self.app.set_focus(self))
                        sys.stderr.write(f"[MultiLineInput] ✓ Scheduled post-refresh focus\n")

                        log_focus_attempt(
                            source_file="input_widget/widget.py",
                            source_function="watch_permission_prompt_data",
                            method="app.call_after_refresh(set_focus)",
                            widget_type="MultiLineInput",
                            success=True,
                            extra_info="STICKY FOCUS scheduled successfully"
                        )
                    else:
                        log_focus_attempt(
                            source_file="input_widget/widget.py",
                            source_function="watch_permission_prompt_data",
                            method="widget.focus()",
                            widget_type="MultiLineInput",
                            success=None,
                            extra_info="AGGRESSIVE GRAB - Fallback (no app)"
                        )

                        self.focus()
                        sys.stderr.write(f"[MultiLineInput] ✓ FORCED FOCUS via self.focus()\n")

                        log_focus_attempt(
                            source_file="input_widget/widget.py",
                            source_function="watch_permission_prompt_data",
                            method="widget.focus()",
                            widget_type="MultiLineInput",
                            success=True,
                            extra_info="AGGRESSIVE GRAB successful (fallback)"
                        )
                    sys.stderr.flush()

                    # Double-check after forcing
                    sys.stderr.write(f"[MultiLineInput] Focus check AFTER force: has_focus={self.has_focus}\n")
                    sys.stderr.flush()

                    log_focus_state(
                        source_file="input_widget/widget.py",
                        widget_type="MultiLineInput",
                        has_focus=self.has_focus,
                        can_focus=self.can_focus,
                        extra_info="AFTER aggressive focus grab"
                    )
                except Exception as e:
                    sys.stderr.write(f"[MultiLineInput] ⚠️ FOCUS FORCING FAILED: {e}\n")
                    sys.stderr.flush()

                    log_focus_attempt(
                        source_file="input_widget/widget.py",
                        source_function="watch_permission_prompt_data",
                        method="app.set_focus() or widget.focus()",
                        widget_type="MultiLineInput",
                        success=False,
                        error=str(e),
                        extra_info="AGGRESSIVE GRAB FAILED!"
                    )
            else:
                sys.stderr.write(f"[MultiLineInput] PERMISSION CLEARED\n")
                sys.stderr.flush()

                # Log permission cleared event
                from ..focus_logger import log_focus_event
                log_focus_event(
                    source_file="input_widget/widget.py",
                    source_function="watch_permission_prompt_data",
                    event_type="PERMISSION_CLEARED",
                    widget_type="MultiLineInput",
                    extra_info="Permission buffer dismissed"
                )

            # CRITICAL: Refresh MUST happen synchronously for widget to render!
            # But keep it light - no layout=True to avoid blocking
            self.refresh()

    def watch_permission_selected_option(self, old_value: int, new_value: int) -> None:
        """Watch for selection changes to trigger UI refresh"""
        import sys
        sys.stderr.write(f"[widget.watch_permission_selected_option] {old_value} -> {new_value}\n")
        sys.stderr.flush()

        if old_value != new_value and self.permission_prompt_data:
            self.refresh()
            sys.stderr.write(f"[widget] REFRESH triggered by selection change\n")
            sys.stderr.flush()
