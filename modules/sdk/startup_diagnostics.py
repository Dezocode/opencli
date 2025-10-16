"""
Startup Diagnostics - Show registration status

Displays in MultiLineInput buffer on startup (non-blocking)
"""

from typing import List, Dict, Any
from .handler_interface import validate_handler, HandlerRegistration, HandlerCompliance


class StartupDiagnostics:
    """
    Validates and displays registration status at startup
    """

    def __init__(self):
        self.validations: List[HandlerRegistration] = []
        self.commands_validated = 0
        self.tools_validated = 0
        self.compliant_count = 0
        self.non_compliant_count = 0

    def validate_registry(self, executor):
        """Validate all registered handlers"""
        self.validations = []

        # Validate commands
        for name, registration in executor.registry.commands.items():
            validation = validate_handler(registration.handler, name)
            self.validations.append(validation)

            if validation.is_compliant():
                self.compliant_count += 1
            else:
                self.non_compliant_count += 1

            self.commands_validated += 1

        # Validate tools
        for name, registration in executor.registry.tools.items():
            validation = validate_handler(registration.handler, name)
            self.validations.append(validation)

            if validation.is_compliant():
                self.compliant_count += 1
            else:
                self.non_compliant_count += 1

            self.tools_validated += 1

    def get_summary(self) -> str:
        """Get summary text for display"""
        lines = []
        lines.append("[bold cyan]OpenCLI Registration Diagnostics[/bold cyan]\n")
        lines.append(f"Commands: {self.commands_validated} | Tools: {self.tools_validated}\n")
        lines.append(f"[green]✓ Compliant: {self.compliant_count}[/green] | [red]✗ Non-compliant: {self.non_compliant_count}[/red]\n\n")

        # Show non-compliant handlers
        if self.non_compliant_count > 0:
            lines.append("[bold red]SDK Compliance Issues:[/bold red]\n")
            for val in self.validations:
                if not val.is_compliant():
                    lines.append(f"  [red]✗[/red] {val.name}: {val.error}\n")
            lines.append("\n")

        # Show sample of compliant handlers
        compliant = [v for v in self.validations if v.is_compliant()]
        if compliant:
            lines.append("[bold green]Sample Registered:[/bold green]\n")
            for val in compliant[:5]:
                lines.append(f"  [green]✓[/green] {val.name} ({val.module})\n")
            if len(compliant) > 5:
                lines.append(f"  [dim]... and {len(compliant) - 5} more[/dim]\n")

        return "".join(lines)

    def show_in_buffer(self, app, duration_ms: int = 3000):
        """
        Show diagnostics in permission buffer (non-blocking)

        Buffer shows for duration_ms then auto-clears
        """
        import asyncio

        prompt_input = app.query_one("#prompt-input")

        # Create buffer data
        buffer_data = {
            'title': 'OpenCLI Startup Diagnostics',
            'message': self.get_summary(),
            'auto_clear_ms': duration_ms,
            'options': [
                {
                    'text': 'Continue',
                    'response': 'continue'
                }
            ]
        }

        # Show in buffer
        prompt_input.permission_prompt_data = buffer_data
        prompt_input.permission_selected_option = 0
        prompt_input.refresh(layout=True)

        # Auto-clear after duration
        async def auto_clear():
            await asyncio.sleep(duration_ms / 1000)
            prompt_input.permission_prompt_data = None
            prompt_input.refresh(layout=True)

        # Schedule auto-clear
        asyncio.create_task(auto_clear())


def run_startup_diagnostics(app, executor, show_buffer: bool = True) -> StartupDiagnostics:
    """
    Run diagnostics and optionally show in buffer

    Args:
        app: TUI app instance
        executor: ExecutionSystem instance
        show_buffer: If True, show results in permission buffer

    Returns:
        StartupDiagnostics instance with results
    """
    diag = StartupDiagnostics()
    diag.validate_registry(executor)

    if show_buffer:
        diag.show_in_buffer(app)

    # Also write summary to chat
    app.write(diag.get_summary())
    app.write("\n")

    return diag
