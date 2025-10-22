"""
Multi-line input widget with wrapping and history support
Designed to not break chat layout
"""

from textual.widget import Widget
from textual.message import Message
from textual.reactive import reactive
from textual.events import Paste
from rich.text import Text
from rich.console import Console
from rich.style import Style
import asyncio

# Import Frontier colors
try:
    from .frontier_colors import FRONTIER_COLORS
except (ImportError, ValueError):
    from frontier_colors import FRONTIER_COLORS


class MultiLineInput(Widget):
    """
    Custom multi-line input that wraps at edge and supports history
    Can also display permission prompts inline
    """

    value = reactive("", layout=True)
    cursor_position = reactive(0)
    is_spinning = reactive(False)
    spinner_frame = reactive(0)
    permission_prompt_data = reactive(None)
    permission_selected_option = reactive(0)

    # Spinner frames
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    class Submitted(Message):
        """Posted when user submits the input"""
        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    class PermissionResponse(Message):
        """Posted when user selects a permission option"""
        def __init__(self, option: dict) -> None:
            self.option = option
            super().__init__()

    class PermissionCancelled(Message):
        """Posted when user cancels permission prompt"""
        pass

    class ShowCommandSuggestions(Message):
        """Posted when slash command typed - triggers suggestion buffer"""
        def __init__(self, query: str) -> None:
            self.query = query
            super().__init__()

    class HideCommandSuggestions(Message):
        """Posted when suggestions should be hidden"""
        pass

    class CommandSuggestionNavigate(Message):
        """Posted when user navigates in suggestions with arrow keys"""
        def __init__(self, direction: str) -> None:
            self.direction = direction  # "up" or "down"
            super().__init__()

    class CommandSuggestionSelect(Message):
        """Posted when user presses Enter with suggestions active"""
        pass

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
        self.suggestions_active = False  # Track if command suggestions are shown

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
            self.post_message(self.NavigationEvent("focus_lost"))
            
            # Then post cancellation event to handle current prompt
            self.post_message(self.PermissionCancelled())
            
            # Clear prompt data immediately (responsive UI)
            self.permission_prompt_data = None
            self.permission_selected_option = 0
        
        self.refresh()

    def render(self) -> Text:
        """Render the current input with cursor or permission prompt"""

        # PRIORITY: Show permission prompt if active
        if self.permission_prompt_data:
            return self._render_permission_prompt()

        # Build display
        display = Text()

        # Add spinner if active, otherwise show >
        prefix = ""
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

        # For single line or simple rendering, just show value with cursor
        if self.has_focus:
            # Insert cursor at current position
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

    def _render_permission_prompt(self) -> Text:
        """Render permission prompt with Frontier colors (no extra borders - prompt box is the border)"""
        prompt_data = self.permission_prompt_data

        output = Text()

        # Get data
        title = prompt_data.get('title', 'Permission')
        message = prompt_data.get('message', '')
        options = prompt_data.get('options', [])
        workflow_status = prompt_data.get('workflow_status')  # Optional workflow progress

        # Frontier colors
        title_color = FRONTIER_COLORS.get("warning", "#E2A478")
        text_color = FRONTIER_COLORS.get("text_primary", "#B3B1AD")
        selected_color = FRONTIER_COLORS.get("success", "#6B9E78")
        dim_color = FRONTIER_COLORS.get("text_dim", "#5C6773")
        error_color = FRONTIER_COLORS.get("error", "#D95757")
        info_color = FRONTIER_COLORS.get("info", "#6B9E78")

        # Title
        output.append(f"{title}\n", style=Style(color=title_color, bold=True))
        output.append("\n")

        # Workflow progress (if present)
        if workflow_status:
            steps = workflow_status.get('steps', [])
            current_step = workflow_status.get('current_step', 0)

            # Show progress bar
            total = len(steps)
            completed = sum(1 for s in steps if s.get('status') == 'completed')
            output.append(f"Progress: {completed}/{total} steps\n", style=Style(color=info_color))
            output.append("\n")

            # Show step list with status indicators
            for i, step in enumerate(steps):
                step_status = step.get('status', 'pending')
                step_title = step.get('title', f'Step {i+1}')

                # Status indicator
                if step_status == 'completed':
                    indicator = "✓"
                    style_color = selected_color
                elif step_status == 'failed':
                    indicator = "✗"
                    style_color = error_color
                elif step_status == 'in_progress':
                    indicator = "⋯"
                    style_color = info_color
                elif i == current_step:
                    indicator = "▸"
                    style_color = text_color
                else:
                    indicator = "·"
                    style_color = dim_color

                output.append(f"{indicator} ", style=Style(color=style_color))
                output.append(f"{step_title}\n", style=Style(color=style_color))

                # Show error if failed
                if step_status == 'failed' and step.get('error'):
                    output.append(f"  Error: {step.get('error')}\n", style=Style(color=error_color))

            output.append("\n")

        # Message (with Rich markup support)
        # Parse Rich markup tags like [cyan], [bold], etc.
        try:
            # Text.from_markup() handles [color] tags properly
            markup_text = Text.from_markup(message)
            output.append(markup_text)
            # Add newline if message doesn't end with one
            if not message.endswith('\n'):
                output.append("\n")
        except Exception as e:
            # Fallback to plain text if markup parsing fails
            print(f"[MultiLineInput] Markup parsing failed: {e}")
            for line in message.split('\n'):
                if line.strip():
                    output.append(line + "\n", style=Style(color=text_color))

        output.append("\n")

        # Options (only show if there are options)
        if options:
            for i, option in enumerate(options):
                option_text = option.get('text', '')
                if i == self.permission_selected_option:
                    # Selected - highlighted with arrow
                    output.append("▸ ", style=Style(color=selected_color, bold=True))
                    output.append(option_text + "\n", style=Style(color=selected_color, bold=True))
                else:
                    # Not selected
                    output.append("  ", style=Style(color=dim_color))
                    output.append(option_text + "\n", style=Style(color=text_color))

        return output

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
        # Don't allow paste during permission prompts
        if self.permission_prompt_data:
            event.prevent_default()
            return

        # Insert pasted text at cursor position
        pasted_text = event.text
        # Remove any newlines from pasted text to keep single-line input
        pasted_text = pasted_text.replace('\n', ' ').replace('\r', '')

        self.value = (
            self.value[:self.cursor_position] +
            pasted_text +
            self.value[self.cursor_position:]
        )
        self.cursor_position += len(pasted_text)
        event.prevent_default()

    def on_key(self, event) -> None:
        """Handle key presses"""
        import sys
        key = event.key

        # AGGRESSIVE DEBUG - Log ALL key events
        sys.stderr.write(f"\n[MultiLineInput.on_key] KEY={key} prompt={bool(self.permission_prompt_data)} focused={self.has_focus}\n")
        sys.stderr.flush()

        # PRIORITY 1: Handle permission prompt navigation if active
        if self.permission_prompt_data:
            sys.stderr.write(f"[MultiLineInput] INSIDE PERMISSION HANDLER for key={key}\n")
            sys.stderr.flush()
            options = self.permission_prompt_data.get('options', [])

            # If no options (informational prompt), only allow Escape
            if not options:
                if key == "escape":
                    self.post_message(self.PermissionCancelled())
                    event.prevent_default()
                return  # Ignore all other keys for informational prompts

            # Handle navigation for prompts with options
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

        # PRIORITY 2: Handle command suggestion navigation if active
        if self.suggestions_active:
            if key == "up":
                self.post_message(self.CommandSuggestionNavigate("up"))
                event.prevent_default()
                return
            elif key == "down":
                self.post_message(self.CommandSuggestionNavigate("down"))
                event.prevent_default()
                return
            elif key == "enter":
                self.post_message(self.CommandSuggestionSelect())
                event.prevent_default()
                return
            elif key == "escape":
                self.post_message(self.HideCommandSuggestions())
                self.suggestions_active = False
                event.prevent_default()
                return
            # For other keys, continue to normal handling (update query)

        # Don't handle up/down for history (only if no suggestions)
        if key in ("up", "down") and not self.suggestions_active:
            return

        # Submit on enter
        if key == "enter":
            self.action_submit()
            event.prevent_default()
            return

        # Backspace
        if key == "backspace":
            if self.cursor_position > 0:
                new_pos = self.cursor_position - 1
                new_value = (
                    self.value[:new_pos] +
                    self.value[self.cursor_position:]
                )
                # Update both atomically to avoid race
                self.cursor_position = new_pos
                self.value = new_value
            event.prevent_default()
            return

        # Delete
        if key == "delete":
            if self.cursor_position < len(self.value):
                self.value = (
                    self.value[:self.cursor_position] +
                    self.value[self.cursor_position+1:]
                )
            event.prevent_default()
            return

        # Left arrow
        if key == "left":
            if self.cursor_position > 0:
                self.cursor_position -= 1
            event.prevent_default()
            return

        # Right arrow
        if key == "right":
            if self.cursor_position < len(self.value):
                self.cursor_position += 1
            event.prevent_default()
            return

        # Home
        if key == "home":
            self.cursor_position = 0
            event.prevent_default()
            return

        # End
        if key == "end":
            self.cursor_position = len(self.value)
            event.prevent_default()
            return

        # Use character property for actual character input (best practice)
        # This handles all printable characters including special chars
        if event.character and event.character.isprintable():
            self.value = (
                self.value[:self.cursor_position] +
                event.character +
                self.value[self.cursor_position:]
            )
            self.cursor_position += 1
            event.prevent_default()

    def action_submit(self) -> None:
        """Submit the current value"""
        if self.value.strip():
            self.post_message(self.Submitted(self.value))

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
        else:
            # Hide suggestions if not a slash command
            if self.suggestions_active:
                self.suggestions_active = False
                self.post_message(self.HideCommandSuggestions())

                # DEBUG
                if os.getenv('OPENCLI_DEBUG_AUTOCOMPLETE'):
                    with open('/tmp/opencli-autocomplete-debug.log', 'a') as f:
                        f.write(f"[watch_value] Posted HideCommandSuggestions\n")

        self.refresh()

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
        """React to frame changes - refresh already handled by _spin"""
        pass

    def watch_permission_prompt_data(self, old_value, new_value) -> None:
        """React to permission prompt data changes - trigger layout update"""
        # Only refresh if actually changed (not just set to same value)
        if old_value != new_value:
            print(f"[MultiLineInput] Permission data changed")

            # CRITICAL: Refresh MUST happen synchronously for widget to render!
            # But keep it light - no layout=True to avoid blocking
            self.refresh()

            if new_value is not None:
                print(f"[MultiLineInput] PERMISSION ACTIVE: {new_value.get('title', 'N/A')}")

                # CRITICAL FIX: Use call_after_refresh to ensure focus is set AFTER widget is ready
                # This ensures the widget is fully rendered and mounted before we try to set focus
                def set_focus_after_render():
                    """Set focus after the widget has been refreshed and is ready"""
                    try:
                        if hasattr(self, 'app') and self.app:
                            self.app.set_focus(self)
                            print(f"[MultiLineInput]   ✓ FORCED FOCUS via call_after_refresh")
                        else:
                            self.focus()
                    except Exception as e:
                        print(f"[MultiLineInput]   Focus error: {e}")

                # Schedule focus to happen after refresh completes
                self.call_after_refresh(set_focus_after_render)
            else:
                print(f"[MultiLineInput] Permission cleared")
