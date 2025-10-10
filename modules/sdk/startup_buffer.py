"""
Startup Buffer Display

Shows module load status and SDK enforcement results in permission buffer.
Non-blocking dropdown that auto-dismisses.
"""

import asyncio
from typing import Optional

try:
    from permission_buffer_manager import get_permission_buffer_manager
except ImportError:
    from ..permission_buffer_manager import get_permission_buffer_manager

from .enforcement import get_enforcement


class StartupBuffer:
    """
    Displays module load status in permission buffer

    Shows:
    - Module categories
    - Load status (✓ loaded, ⚠ converted, ✗ rejected)
    - Enforcement summary
    - Command/tool counts
    """

    def __init__(self):
        self.enforcement = get_enforcement()

    async def show(
        self,
        app,
        executor,
        duration_ms: int = 4000,
        auto_dismiss: bool = True
    ):
        """
        Show startup buffer with module load status

        Args:
            app: TUI app instance
            executor: ExecutionSystem instance
            duration_ms: How long to show buffer (ms)
            auto_dismiss: If True, auto-dismiss after duration
        """
        print("[StartupBuffer] Getting prompt input widget...")
        prompt_input = app.query_one("#prompt-input")

        # Build display content
        print("[StartupBuffer] Building content...")
        content = self._build_content(executor)

        buffer_data = {
            'title': '🚀 OpenCLI Startup - Module Registration',
            'message': content,
            'options': [
                {
                    'text': 'Continue (or wait for auto-dismiss)',
                    'response': 'continue'
                }
            ]
        }

        session = getattr(executor, 'session', None)
        manager = get_permission_buffer_manager()

        if auto_dismiss:
            await manager.show_transient(
                app,
                session,
                buffer_data,
                duration=max(duration_ms / 1000, 0.1)
            )
        else:
            await manager.prompt(
                app,
                session,
                buffer_data,
                timeout=None
            )

    def _build_content(self, executor) -> str:
        """Build display content"""
        lines = []

        # Registration summary
        cmd_count = len(executor.registry.commands)
        tool_count = len(executor.registry.tools)

        lines.append(f"[bold]Registration Summary[/bold]\n")
        lines.append(f"Commands: [cyan]{cmd_count}[/cyan] | Tools: [cyan]{tool_count}[/cyan]\n\n")

        # Enforcement summary
        lines.append(f"[bold]SDK Enforcement[/bold]\n")
        lines.append(f"[green]✓ Compliant: {self.enforcement.accepted_count}[/green] | ")
        lines.append(f"[yellow]⚠ Converted: {self.enforcement.converted_count}[/yellow] | ")
        lines.append(f"[red]✗ Rejected: {self.enforcement.rejected_count}[/red]\n\n")

        # Show by category
        lines.append("[bold]Modules by Category[/bold]\n")

        # Group by category
        categories = {}
        for result in self.enforcement.results:
            cat = result.category
            if cat not in categories:
                categories[cat] = {
                    'accepted': [],
                    'converted': [],
                    'rejected': []
                }

            if result.action.value == 'accepted':
                categories[cat]['accepted'].append(result)
            elif result.action.value == 'converted':
                categories[cat]['converted'].append(result)
            elif result.action.value == 'rejected':
                categories[cat]['rejected'].append(result)

        # Display categories
        for cat in sorted(categories.keys()):
            results = categories[cat]
            total = len(results['accepted']) + len(results['converted']) + len(results['rejected'])

            lines.append(f"\n[cyan]▸ {cat.upper()}[/cyan] ({total})\n")

            # Accepted
            for result in results['accepted'][:3]:  # Show first 3
                lines.append(f"  [green]✓[/green] {result.original_name}\n")

            # Converted
            for result in results['converted']:
                lines.append(f"  [yellow]⚠[/yellow] {result.original_name} (auto-fixed)\n")

            # Rejected
            for result in results['rejected']:
                lines.append(f"  [red]✗[/red] {result.original_name} - {result.message}\n")

            # Show "and more" if truncated
            if len(results['accepted']) > 3:
                more = len(results['accepted']) - 3
                lines.append(f"  [dim]... and {more} more[/dim]\n")

        # Warnings if any violations
        if self.enforcement.has_violations():
            lines.append("\n[bold red]⚠ WARNING: Some modules failed to load![/bold red]\n")
            lines.append("Check enforcement report above for details.\n")

        return "".join(lines)

    def show_blocking(self, app, executor):
        """
        Show startup buffer and wait for user to dismiss

        Use this when violations need user attention
        """
        prompt_input = app.query_one("#prompt-input")

        content = self._build_content(executor)

        buffer_data = {
            'title': '⚠ OpenCLI Startup - Enforcement Violations',
            'message': content + "\n[bold]Press Enter to continue[/bold]",
            'options': [
                {
                    'text': 'Continue anyway',
                    'response': 'continue'
                },
                {
                    'text': 'Exit and fix violations',
                    'response': 'exit'
                }
            ]
        }

        # Show and wait
        prompt_input.permission_prompt_data = buffer_data
        prompt_input.permission_selected_option = 0
        # Don't call refresh - reactive watcher handles it

        # This would normally wait for user input
        # The event handler in simple_tui.py will catch the response


async def show_startup_status(
    app,
    executor,
    block_on_violations: bool = False,
    duration_ms: int = 4000
):
    """
    Show startup status buffer

    Args:
        app: TUI app instance
        executor: ExecutionSystem instance
        block_on_violations: If True and violations exist, wait for user
        duration_ms: Auto-dismiss duration (if no violations)
    """
    buffer = StartupBuffer()
    enforcement = get_enforcement()

    if block_on_violations and enforcement.has_violations():
        # Block and wait for user decision
        buffer.show_blocking(app, executor)
    else:
        # Auto-dismiss
        await buffer.show(app, executor, duration_ms)
