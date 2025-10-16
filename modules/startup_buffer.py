"""
Startup Buffer Display

Shows module load status and SDK enforcement results in SDK dropdown widget.
Non-blocking, auto-dismisses after displaying final registration status.
"""

import asyncio
from typing import Optional
from .enforcement import get_enforcement


class StartupBuffer:
    """
    Displays module load status in SDK dropdown widget

    Shows:
    - Command/tool counts
    - Enforcement summary (✓ accepted, ⚠ converted, ✗ rejected)
    - Latest module status message
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
        Show startup buffer with module load status in SDK dropdown widget

        Args:
            app: TUI app instance
            executor: ExecutionSystem instance
            duration_ms: How long to show buffer (ms)
            auto_dismiss: If True, auto-dismiss after duration
        """
        print("[StartupBuffer] Getting SDK dropdown widget...")
        sdk_buffer = app.query_one("#sdk-loading")

        # Build display content - just show summary, no interactive navigation needed
        print("[StartupBuffer] Building content...")

        # Get counts
        cmd_count = len(executor.registry.commands)
        tool_count = len(executor.registry.tools)

        # Update SDK buffer with final status (stops loading, shows checkmark)
        sdk_buffer.stop_loading()  # Changes spinner to ✓
        sdk_buffer.update_progress(
            command_count=cmd_count,
            tool_count=tool_count,
            accepted_count=self.enforcement.accepted_count,
            converted_count=self.enforcement.converted_count,
            rejected_count=self.enforcement.rejected_count,
            latest_module="✓ Registration Complete"
        )
        sdk_buffer.remove_class("hidden")  # Make sure it's visible
        print("[StartupBuffer] SDK dropdown updated with final status!")

        # Auto-dismiss if enabled
        if auto_dismiss:
            print(f"[StartupBuffer] Will auto-dismiss in {duration_ms}ms...")
            await asyncio.sleep(duration_ms / 1000)
            print("[StartupBuffer] Dismissing buffer...")
            sdk_buffer.add_class("hidden")
            sdk_buffer.clear_data()
            print("[StartupBuffer] Buffer dismissed")

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

    async def show_blocking(self, app, executor):
        """
        Show startup buffer and wait for user to dismiss using SDK dropdown

        Use this when violations need user attention
        """
        sdk_buffer = app.query_one("#sdk-loading")

        # Get counts
        cmd_count = len(executor.registry.commands)
        tool_count = len(executor.registry.tools)

        # Update SDK buffer with warning status
        sdk_buffer.stop_loading()  # Stop spinner
        sdk_buffer.update_progress(
            command_count=cmd_count,
            tool_count=tool_count,
            accepted_count=self.enforcement.accepted_count,
            converted_count=self.enforcement.converted_count,
            rejected_count=self.enforcement.rejected_count,
            latest_module="⚠ VIOLATIONS DETECTED - Check enforcement report"
        )
        sdk_buffer.remove_class("hidden")

        # Wait longer for violations (30 seconds instead of 4)
        await asyncio.sleep(30)

        sdk_buffer.add_class("hidden")
        sdk_buffer.clear_data()


async def show_startup_status(
    app,
    executor,
    block_on_violations: bool = False,
    duration_ms: int = 4000
):
    """
    Show startup status in SDK dropdown (non-blocking)

    Args:
        app: TUI app instance
        executor: ExecutionSystem instance
        block_on_violations: If True and violations exist, show longer
        duration_ms: Auto-dismiss duration (if no violations)
    """
    buffer = StartupBuffer()
    enforcement = get_enforcement()

    if block_on_violations and enforcement.has_violations():
        # Show longer for violations
        await buffer.show_blocking(app, executor)
    else:
        # Auto-dismiss
        await buffer.show(app, executor, duration_ms)
