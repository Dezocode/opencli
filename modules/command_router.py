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

        Shows LIVE SDK loading in separate dropdown widget below input during registration
        """
        if self._initialized:
            return  # Already initialized

        from commands.registry import register_all
        from sdk import get_enforcement

        # Store app reference for live updates
        self.executor.app = self.app

        # Show LIVE SDK loading dropdown
        try:
            sdk_buffer = self.app.query_one("#sdk-loading")
            sdk_buffer.start_loading()
            sdk_buffer.remove_class("hidden")
            print("[CommandRouter] SDK loading dropdown displayed")
        except Exception as e:
            print(f"[CommandRouter] Could not show SDK dropdown: {e}")

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

        # Hide SDK loading dropdown
        try:
            sdk_buffer = self.app.query_one("#sdk-loading")
            sdk_buffer.stop_loading()
            sdk_buffer.add_class("hidden")
            sdk_buffer.clear_data()
            print("[CommandRouter] SDK loading dropdown hidden")
        except Exception as e:
            print(f"[CommandRouter] Could not hide SDK dropdown: {e}")

        # Store enforcement for startup buffer
        self.enforcement = enforcement
        self._initialized = True

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
    # Run in background so it doesn't block the first command!
    if not hasattr(app, '_startup_buffer_shown'):
        app._startup_buffer_shown = True

        print("[CommandRouter] Starting startup buffer in background...")
        from sdk import show_startup_status
        import asyncio

        # Run in background - don't await, don't block!
        asyncio.create_task(show_startup_status(
            app,
            app._command_router.executor,
            block_on_violations=False,
            duration_ms=4000
        ))
        print("[CommandRouter] Startup buffer running in background")

    return await app._command_router.route_command(command, args)
