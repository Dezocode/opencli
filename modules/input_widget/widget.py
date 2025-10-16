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
        """Track when widget loses focus - trigger navigation event for permission auto-dismiss"""
        import sys
        sys.stderr.write(f"\n[MultiLineInput.on_blur] LOST FOCUS - prompt={bool(self.permission_prompt_data)}\n")
        sys.stderr.flush()

        # Constitution Principle V: Auto-dismiss permission prompts on navigation
        if self.permission_prompt_data:
            sys.stderr.write(f"[MultiLineInput.on_blur] NAVIGATION EVENT - auto-dismissing permission prompt\n")
            sys.stderr.flush()

            # Post navigation event first (for any listeners)
            from .messages import NavigationEvent, PermissionCancelled
            self.post_message(NavigationEvent("focus_lost"))

            # Then post cancellation event to handle current prompt
            self.post_message(PermissionCancelled())

            # Clear prompt data immediately (responsive UI)
            self.permission_prompt_data = None
            self.permission_selected_option = 0

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

    def on_paste(self, event: Paste) -> None:
        """Handle paste events"""
        handle_paste_event(self, event)

    def on_key(self, event) -> None:
        """Handle key presses with PERMISSION PRIORITY"""
        handle_key_event(self, event)

    def action_submit(self) -> None:
        """Submit the current value"""
        if self.value.strip():
            self.post_message(Submitted(self.value))

    def clear(self) -> None:
        """Clear the input"""
        self.value = ""
        self.cursor_position = 0

    def watch_value(self, old_value: str, new_value: str) -> None:
        """Update when value changes - detect slash commands"""
        # Ensure cursor is within bounds
        if self.cursor_position > len(new_value):
            self.cursor_position = len(new_value)

        # Detect slash command input
        if new_value.startswith('/'):
            self.suggestions_active = True
            self.post_message(ShowCommandSuggestions(new_value))
        else:
            if self.suggestions_active:
                self.suggestions_active = False
                self.post_message(HideCommandSuggestions())

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
        """React to permission prompt changes - PRIORITY SYSTEM"""
        if old_value != new_value:
            print(f"[MultiLineInput] Permission data changed")
            self.refresh()

            if new_value is not None:
                print(f"[MultiLineInput] PERMISSION ACTIVE: {new_value.get('title', 'N/A')}")

                # Force focus IMMEDIATELY so keys work right away
                try:
                    self.app.set_focus(self)
                    print(f"[MultiLineInput]   ✓ FORCED FOCUS IMMEDIATELY")
                except Exception as e:
                    print(f"[MultiLineInput]   Focus error: {e}, trying fallback")
                    self.focus()
            else:
                print(f"[MultiLineInput] Permission cleared")
