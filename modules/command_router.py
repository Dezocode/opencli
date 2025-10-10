"""
Command Router - Minimal routing layer

Simple router that:
1. Looks up commands in ExecutionRegistry
2. Calls ExecutionSystem.execute()
3. NO registration methods - everything registers with ExecutionSystem directly
"""

import asyncio
from typing import Optional
from execution.registry import ExecutionType
from execution.executor import get_executor


class CommandRouter:
    """
    MINIMAL router - just lookup and execute

    NO duplicate register() methods
    NO manual execution

    Everything flows through:
    ExecutionRegistry → ExecutionSystem → PermissionManager → Buffer
    """

    def __init__(self, app, session):
        self.app = app
        self.session = session

        # Get global ExecutionSystem (singleton)
        self.executor = get_executor(app, session)

        # Track initialization state
        self._initialized = False
        self.enforcement = None

    async def _initialize_registrations(self):
        """Load all registrations into ExecutionSystem with SDK enforcement - ASYNC

        Shows LIVE SDK loading in MultiLineInput dropdown during registration
        """
        if self._initialized:
            return  # Already initialized

        from commands.registry import register_all
        from sdk import get_enforcement

        # Store app reference for live updates
        self.executor.app = self.app

        # Show LIVE SDK loading buffer
        try:
            prompt_input = self.app.query_one("#prompt-input")

            # Initial loading message
            loading_data = {
                'title': '🔄 OpenCLI SDK - Loading Modules',
                'message': 'Validating and registering modules...\n\nThis ensures all commands are secure and compliant.\n\n[dim]Starting...[/dim]',
                'options': []  # No options, just info
            }

            prompt_input.permission_prompt_data = loading_data
            # Don't call refresh - reactive watcher handles it
            print("[CommandRouter] SDK loading buffer displayed")
        except Exception as e:
            print(f"[CommandRouter] Could not show loading buffer: {e}")

        # Single registration point (with SDK enforcement!)
        # This will update the buffer LIVE as each module registers
        try:
            await register_all(self.executor)
        except ValueError as e:
            # SDK violation - handler rejected
            print(f"[CommandRouter] SDK Violation: {e}")
            raise

        # Get final counts
        cmd_count = len(self.executor.registry.commands)
        tool_count = len(self.executor.registry.tools)
        enforcement = get_enforcement()

        print(f"[CommandRouter] SDK Enforcement Complete:")
        print(f"  Commands: {cmd_count} | Tools: {tool_count}")
        print(f"  ✓ Accepted: {enforcement.accepted_count}")
        print(f"  ⚠ Converted: {enforcement.converted_count}")
        print(f"  ✗ Rejected: {enforcement.rejected_count}")

        # Store enforcement for startup buffer
        self.enforcement = enforcement
        self._initialized = True

        # CRITICAL: Clear the loading buffer now that registration is complete
        try:
            prompt_input = self.app.query_one("#prompt-input")
            prompt_input.permission_prompt_data = None
            print("[CommandRouter] SDK loading buffer cleared")
        except Exception as e:
            print(f"[CommandRouter] Could not clear loading buffer: {e}")

    async def route_command(self, command: str, args: Optional[str] = None) -> bool:
        """
        Route command through ExecutionSystem

        SIMPLE FLOW:
        1. Normalize command string
        2. Call executor.execute_command()
        3. Return True if handled, False if not registered
        """

        # Normalize command
        full_command = command.strip()
        if args:
            full_command = f"{command.strip()} {args.strip()}"

        # DEBUG: Show what we're routing
        print(f"[Router] Looking up: '{full_command}'")
        print(f"[Router] Registered commands: {list(self.executor.registry.commands.keys())[:3]}...")

        # Execute through ExecutionSystem (ONE entry point)
        try:
            print(f"[Router] Calling executor.execute_command('{full_command}')")
            await self.executor.execute_command(
                name=full_command,
                app=self.app,
                session=self.session,
                args=args
            )
            print(f"[Router] Success!")
            return True

        except ValueError as e:
            # Command not registered
            print(f"[Router] ValueError: {e}")
            return False

        except PermissionError as e:
            # User denied permission (still handled)
            print(f"[Router] PermissionError: {e}")
            return True

        except Exception as e:
            # Execution error (still handled)
            print(f"[Router] Exception: {e}")
            import traceback
            traceback.print_exc()
            self.app.write(f"[red]✗ Error: {e}[/red]\n\n")
            return True

    def is_registered(self, command: str) -> bool:
        """Check if command is registered"""
        registration = self.executor.registry.get(ExecutionType.COMMAND, command)
        return registration is not None and registration.enabled

    def get_available_commands(self) -> list:
        """Get all registered commands"""
        return sorted(self.executor.registry.commands.keys())


async def route_command_unified(app, session, command: str, args: Optional[str] = None) -> bool:
    """
    Global routing function for async_interactive.py

    Creates CommandRouter (which initializes ExecutionSystem)
    Shows startup buffer on first call
    Routes command through ExecutionSystem

    FULLY ASYNC - Non-blocking initialization and registration
    """
    # Initialize router if needed
    if not hasattr(app, '_command_router'):
        app._command_router = CommandRouter(app, session)

    # Initialize registrations ASYNC (non-blocking)
    if not app._command_router._initialized:
        await app._command_router._initialize_registrations()

    # Show startup buffer on FIRST COMMAND ONLY (after registration complete)
    if not hasattr(app, '_startup_buffer_shown'):
        app._startup_buffer_shown = True

        print("[CommandRouter] Showing startup buffer...")
        from sdk import show_startup_status
        try:
            await show_startup_status(
                app,
                app._command_router.executor,
                block_on_violations=False,  # Don't block, just show
                duration_ms=4000             # Auto-dismiss after 4s
            )
            print("[CommandRouter] Startup buffer displayed")
        except Exception as e:
            print(f"[CommandRouter] Could not show startup buffer: {e}")
            import traceback
            traceback.print_exc()

    return await app._command_router.route_command(command, args)
