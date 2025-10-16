"""Action Mixin - TUI action handlers

Handles all TUI actions including:
- Application control (quit)
- Screen management (clear)
- Performance monitoring toggle
- Refactoring monitoring toggle
"""


class ActionMixin:
    """Mixin for TUI action handlers"""

    def action_quit_app(self) -> None:
        """Quit the application"""
        self.exit()

    def action_toggle_performance(self) -> None:
        """Toggle performance monitoring"""
        if self.performance_status:
            enabled = self.performance_status.toggle()
            status = "enabled" if enabled else "disabled"
            self.write(f"[dim]Performance monitoring {status}[/dim]\n")

    def action_toggle_refactoring(self) -> None:
        """Toggle refactoring monitoring"""
        if self.refactoring_status:
            enabled = self.refactoring_status.toggle()
            status = "enabled" if enabled else "disabled"
            self.write(f"[dim]Refactoring monitoring {status}[/dim]\n")

    def action_clear_screen(self) -> None:
        """Clear the screen content"""
        try:
            content = self._resolve_content_widget()
            if hasattr(content, 'clear'):
                content.clear()
            else:
                content.update("")
        except:
            pass

    def on_key(self, event) -> None:
        """Handle global key events"""
        # Handle Ctrl+C to quit
        if event.key == "ctrl+c":
            self.action_quit_app()
        # Handle Ctrl+L to clear screen
        elif event.key == "ctrl+l":
            self.action_clear_screen()
        # Handle F11 for performance toggle
        elif event.key == "f11":
            self.action_toggle_performance()
        # Handle F12 for refactoring toggle
        elif event.key == "f12":
            self.action_toggle_refactoring()
