"""
Command Router - Minimal routing layer

Simple router that:
1. Looks up commands in ExecutionRegistry
2. Calls ExecutionSystem.execute()
3. NO registration methods - everything registers with ExecutionSystem directly
"""

import asyncio
import time
from typing import Optional, List, Tuple
from enum import Enum
from .execution.registry import ExecutionType
from .execution.executor import get_executor


class SDKState(Enum):
    UNINITIALIZED = "uninitialized"
    STARTING = "starting"
    BACKGROUND_INIT = "background_init"
    REGISTERING = "registering"
    ENFORCING = "enforcing"  
    INITIALIZED = "initialized"
    FAILED = "failed"
    DEGRADED_MODE = "degraded_mode"


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

        # CRITICAL: Update executor references (singleton may have stale refs)
        # This ensures permission prompts have valid app/session even before _initialize_registrations()
        self.executor.app = self.app
        self.executor.session = self.session

        # Enhanced state tracking for non-blocking architecture
        self._initialized = False
        self.enforcement = None
        self._state = SDKState.UNINITIALIZED
        self._init_task: Optional[asyncio.Task] = None
        self._init_started_at: Optional[float] = None
        self._init_completed_at: Optional[float] = None
        self._init_error: Optional[Exception] = None
        self._pending_commands: List[Tuple[str, Optional[str]]] = []

    def get_sdk_state(self) -> SDKState:
        """Get current SDK initialization state"""
        return self._state

    def get_active_command_count(self) -> int:
        """Get count of pending commands during initialization"""
        return len(self._pending_commands)

    async def _initialize_registrations(self):
        """Load all registrations into ExecutionSystem with SDK enforcement - ASYNC

        Shows LIVE SDK loading via PermissionBufferManager (non-blocking, preserves focus)
        """
        import sys
        import time

        sys.stderr.write(f"\n[CommandRouter._initialize_registrations] ========== START ==========\n")
        sys.stderr.write(f"[CommandRouter._initialize_registrations] Time: {time.strftime('%H:%M:%S')}\n")
        sys.stderr.write(f"[CommandRouter._initialize_registrations] Checking _initialized flag: {self._initialized}\n")
        sys.stderr.flush()

        if self._initialized:
            sys.stderr.write(f"[CommandRouter._initialize_registrations] Already initialized - returning early\n\n")
            sys.stderr.flush()
            return  # Already initialized

        # Prevent concurrent initialization attempts
        if hasattr(self, '_initializing') and self._initializing:
            sys.stderr.write(f"[CommandRouter._initialize_registrations] Already initializing - returning early\n\n")
            sys.stderr.flush()
            return

        sys.stderr.write(f"[CommandRouter._initialize_registrations] Setting _initializing flag\n")
        sys.stderr.flush()
        self._initializing = True

        from .commands.registry import register_all
        from .sdk import get_enforcement

        # Store app reference for live updates
        self.executor.app = self.app
        sys.stderr.write(f"[CommandRouter._initialize_registrations] App reference stored\n")
        sys.stderr.flush()

        # Show SDK loading in command suggestions buffer
        try:
            suggestions_buffer = self.app.query_one("#command-suggestions")
            suggestions_buffer.remove_class("hidden")
            suggestions_buffer.start_sdk_loading()
            sys.stderr.write(f"[CommandRouter._initialize_registrations] SDK loading shown in suggestions buffer\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"[CommandRouter._initialize_registrations] Failed to show SDK loading: {e}\n")
            sys.stderr.flush()

        sys.stderr.write(f"[CommandRouter._initialize_registrations] Starting SDK registration...\n")
        sys.stderr.flush()

        # Single registration point (with SDK enforcement!)
        # commands/registry.py will update via manager.update() during registration
        try:
            sys.stderr.write(f"[CommandRouter._initialize_registrations] Calling register_all()...\n")
            sys.stderr.flush()
            reg_start = time.time()

            await register_all(self.executor)

            reg_duration = time.time() - reg_start
            sys.stderr.write(f"[CommandRouter._initialize_registrations] register_all() completed in {reg_duration:.2f}s\n")
            sys.stderr.flush()
        except ValueError as e:
            # SDK violation - handler rejected
            sys.stderr.write(f"[CommandRouter._initialize_registrations] SDK Violation: {e}\n")
            sys.stderr.flush()
            print(f"[CommandRouter] SDK Violation: {e}")
            self._initializing = False
            raise
        except Exception as e:
            # Catch ALL other exceptions to prevent silent hangs
            import traceback
            sys.stderr.write(f"[CommandRouter._initialize_registrations] CRITICAL ERROR: {type(e).__name__}: {e}\n")
            sys.stderr.flush()
            traceback.print_exc(file=sys.stderr)

            print(f"[CommandRouter] CRITICAL ERROR during registration:")
            print(f"  Exception type: {type(e).__name__}")
            print(f"  Message: {e}")
            print(f"  Traceback:")
            traceback.print_exc()
            # Show error to user
            self.app.write(f"\n[red]✗ SDK Registration Failed:[/red]\n")
            self.app.write(f"[red]{type(e).__name__}: {e}[/red]\n\n")
            self._initializing = False  # Clear flag on error
            raise

        # Get final counts
        cmd_count = len(self.executor.registry.commands)
        tool_count = len(self.executor.registry.tools)
        enforcement = get_enforcement()

        sys.stderr.write(f"[CommandRouter._initialize_registrations] Getting final counts...\n")
        sys.stderr.write(f"[CommandRouter._initialize_registrations] Commands: {cmd_count} | Tools: {tool_count}\n")
        sys.stderr.flush()

        print(f"[CommandRouter] SDK Enforcement Complete:")
        print(f"  Commands: {cmd_count} | Tools: {tool_count}")
        print(f"  ✓ Accepted: {enforcement.accepted_count}")
        print(f"  ⚠ Converted: {enforcement.converted_count}")
        print(f"  ✗ Rejected: {enforcement.rejected_count}")

        # Update suggestions buffer with final enforcement stats
        try:
            suggestions_buffer = self.app.query_one("#command-suggestions")
            suggestions_buffer.update_sdk_progress(
                command_count=cmd_count,
                tool_count=tool_count,
                accepted_count=enforcement.accepted_count,
                converted_count=enforcement.converted_count,
                rejected_count=enforcement.rejected_count,
                current_step="SDK initialization complete"
            )
            sys.stderr.write(f"[CommandRouter._initialize_registrations] Suggestions buffer updated with final stats\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"[CommandRouter._initialize_registrations] Failed to update suggestions buffer: {e}\n")
            sys.stderr.flush()

        # Store enforcement for startup buffer
        self.enforcement = enforcement
        self._initialized = True
        self._initializing = False  # Clear initialization flag

        # Wait a moment to let user see the completion stats
        sys.stderr.write(f"[CommandRouter._initialize_registrations] Starting 1.5s sleep before hiding buffer...\n")
        sys.stderr.flush()
        await asyncio.sleep(1.5)
        sys.stderr.write(f"[CommandRouter._initialize_registrations] Sleep complete, now hiding buffer\n")
        sys.stderr.flush()

        # Stop SDK loading in suggestions buffer
        try:
            sys.stderr.write(f"[CommandRouter._initialize_registrations] Querying #command-suggestions...\n")
            sys.stderr.flush()
            suggestions_buffer = self.app.query_one("#command-suggestions")
            sys.stderr.write(f"[CommandRouter._initialize_registrations] Got buffer: {suggestions_buffer}\n")
            sys.stderr.flush()

            sys.stderr.write(f"[CommandRouter._initialize_registrations] Calling stop_sdk_loading()...\n")
            sys.stderr.flush()
            suggestions_buffer.stop_sdk_loading()
            sys.stderr.write(f"[CommandRouter._initialize_registrations] stop_sdk_loading() returned\n")
            sys.stderr.flush()

            sys.stderr.write(f"[CommandRouter._initialize_registrations] Adding 'hidden' class...\n")
            sys.stderr.flush()
            suggestions_buffer.add_class("hidden")
            sys.stderr.write(f"[CommandRouter._initialize_registrations] 'hidden' class added\n")
            sys.stderr.flush()

            sys.stderr.write(f"[CommandRouter._initialize_registrations] ✓ SDK loading stopped and suggestions hidden\n")
            sys.stderr.flush()
        except Exception as e:
            import traceback
            sys.stderr.write(f"[CommandRouter._initialize_registrations] ✗ Failed to stop SDK loading: {e}\n")
            sys.stderr.write(traceback.format_exc())
            sys.stderr.flush()

        sys.stderr.write(f"[CommandRouter._initialize_registrations] ========== COMPLETE ==========\n\n")
        sys.stderr.flush()

    async def route_command(self, command: str, args: Optional[str] = None) -> bool:
        """
        Route command through ExecutionSystem

        SIMPLE FLOW:
        1. Use command name directly (already includes /)
        2. Call executor.execute_command()
        3. Return True if handled, False if not registered
        """

        # Use command name directly (registry keys include the /)
        command_name = command.strip()

        # DEBUG: Show what we're routing
        import sys
        sys.stderr.write(f"[Router] Looking up: '{command_name}'\n")
        sys.stderr.write(f"[Router] Registered commands: {list(self.executor.registry.commands.keys())[:5]}...\n")
        sys.stderr.flush()

        # Check if command exists
        if command_name not in self.executor.registry.commands:
            sys.stderr.write(f"[Router] ERROR: Command '{command_name}' not found in registry!\n")
            sys.stderr.flush()
            return False

        registration = self.executor.registry.commands[command_name]
        sys.stderr.write(f"[Router] Found registration: {registration.name}, requires_approval: {registration.requires_approval}\n")
        sys.stderr.write(f"[Router] Registration type: {type(registration)}\n")
        sys.stderr.flush()

        # Execute through ExecutionSystem (ONE entry point)
        try:
            sys.stderr.write(f"[Router] Calling executor.execute_command('{command_name}')\n")
            sys.stderr.write(f"[Router] Executor type: {type(self.executor)}\n")
            sys.stderr.write(f"[Router] Executor app: {self.executor.app}\n")
            sys.stderr.write(f"[Router] Executor session: {self.executor.session}\n")
            sys.stderr.flush()
            result = await self.executor.execute_command(
                name=command_name,
                app=self.app,
                session=self.session,
                args=args
            )
            sys.stderr.write(f"[Router] execute_command returned: {result}\n")
            sys.stderr.write(f"[Router] Success!\n")
            sys.stderr.flush()
            return True

        except Exception as e:
            # Command execution failed
            import sys
            sys.stderr.write(f"[Router] Exception in execute_command: {e}\n")
            import traceback
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
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
    import sys
    print(f"[DEBUG] 🔥 route_command_unified CALLED with '{command}' 🔥")
    sys.stderr.write(f"\n[route_command_unified] ========== START ==========\n")
    sys.stderr.write(f"[route_command_unified] Command: '{command}'\n")
    sys.stderr.write(f"[route_command_unified] Args: {args}\n")
    sys.stderr.flush()

    # TELEMETRY: Check if router was created by async_interactive/core.py
    if not hasattr(app, '_command_router'):
        sys.stderr.write(f"\n{'='*80}\n")
        sys.stderr.write(f"[TELEMETRY] ⚠ COMMAND ROUTING BEFORE ROUTER CREATION\n")
        sys.stderr.write(f"[TELEMETRY] Command: {command}\n")
        sys.stderr.write(f"[TELEMETRY] This indicates _init_command_router was not called in on_mount()\n")
        sys.stderr.write(f"[TELEMETRY] Check async_interactive/core.py - app._init_command_router assignment\n")
        sys.stderr.write(f"{'='*80}\n\n")
        sys.stderr.flush()

        sys.stderr.write(f"[route_command_unified] Creating new CommandRouter as fallback\n")
        sys.stderr.flush()
        app._command_router = CommandRouter(app, session)

    # TELEMETRY: Check if routing before initialization complete
    if not app._command_router._initialized:
        sys.stderr.write(f"\n{'='*80}\n")
        sys.stderr.write(f"[TELEMETRY] ⚠ COMMAND ROUTING BEFORE INITIALIZATION COMPLETE\n")
        sys.stderr.write(f"[TELEMETRY] Command: {command}\n")
        sys.stderr.write(f"[TELEMETRY] Router exists but _initialized=False\n")
        sys.stderr.write(f"[TELEMETRY] This may mean:\n")
        sys.stderr.write(f"[TELEMETRY]   1. Background initialization still running (normal)\n")
        sys.stderr.write(f"[TELEMETRY]   2. Initialization failed silently (check stderr above)\n")
        sys.stderr.write(f"[TELEMETRY] Starting initialization now (fallback)...\n")
        sys.stderr.write(f"{'='*80}\n\n")
        sys.stderr.flush()

        sys.stderr.write(f"[route_command_unified] Router not initialized, calling _initialize_registrations()\n")
        sys.stderr.flush()
        await app._command_router._initialize_registrations()
        sys.stderr.write(f"[route_command_unified] Initialization complete\n")
        sys.stderr.flush()
    else:
        sys.stderr.write(f"[route_command_unified] ✓ Router already initialized\n")
        sys.stderr.flush()

    # Show command count
    cmd_count = len(app._command_router.executor.registry.commands)
    sys.stderr.write(f"[route_command_unified] Registered commands count: {cmd_count}\n")
    sys.stderr.write(f"[route_command_unified] Sample commands: {list(app._command_router.executor.registry.commands.keys())[:5]}\n")
    sys.stderr.flush()

    # Show startup buffer once (non-blocking)
    if not hasattr(app, '_startup_buffer_shown'):
        app._startup_buffer_shown = True
        print("[CommandRouter] Starting startup buffer in background...")
        from .sdk import show_startup_status
        import asyncio
        asyncio.create_task(show_startup_status(
            app,
            app._command_router.executor,
            block_on_violations=False,
            duration_ms=4000
        ))
        print("[CommandRouter] Startup buffer running in background")

    sys.stderr.write(f"[route_command_unified] Calling route_command()\n")
    sys.stderr.flush()
    try:
        result = await app._command_router.route_command(command, args)
        sys.stderr.write(f"[route_command_unified] Result: {result}\n")
    except Exception as e:
        sys.stderr.write(f"[route_command_unified] ❌ EXCEPTION in route_command: {e}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return False
    sys.stderr.write(f"[route_command_unified] ========== END ==========\n\n")
    sys.stderr.flush()
    return result
