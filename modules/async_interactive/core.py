"""
Core async interactive functionality
Main entry point for async interactive mode
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from modules.tui.core import OpenCLITUI
from .session import create_session
from .client import create_async_client
from .permissions import setup_permissions
from .ui_handlers import async_write
from .tools import TOOLS
from .streaming import StreamHandler
from .buffer_system import BufferManager


async def interactive_async(config, session=None, initial_prompt=None):
    """
    Async interactive mode with Textual TUI - Main entry point

    Args:
        config: OpenCLI configuration dict
        session: Session object (created if None)
        initial_prompt: Optional initial prompt string
    """
    # Create session if not provided
    if not session:
        session = create_session(config["model"])

    # Create async client
    client = create_async_client(config)

    # Setup permissions
    await setup_permissions(session)

    # Launch TUI
    app = OpenCLITUI(session, config, client)

    # Setup command router initialization
    import sys
    sys.stderr.write("[TUI] Setting up command router initialization...\n")
    sys.stderr.flush()

    try:
        from modules.command_router import CommandRouter

        # Create command router
        app._command_router = CommandRouter(app, session)

        # Set initialization method
        app._init_command_router = app._command_router._initialize_registrations

        sys.stderr.write("[TUI] ✓ Command router setup complete\n")
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"[TUI] ✗ Command router setup failed: {e}\n")
        sys.stderr.flush()

    # CRITICAL: Wire the execution manager's handler (dev6 pattern restored)
    # Import execution flow manager
    import sys
    sys.stderr.write("[TUI] Creating execution flow manager...\n")
    sys.stderr.flush()

    try:
        from cli.cli.modules.execution_flow import create_execution_flow_manager
        from modules.initialization import initialize_opencli_system

        # Initialize system components
        from pathlib import Path
        CONFIG_DIR = Path.home() / ".opencli"
        component_init, system_init, init_results = initialize_opencli_system(CONFIG_DIR)

        # Create execution flow manager
        execution_manager = create_execution_flow_manager(config, session, component_init, system_init)
        execution_manager.set_client(client)

        # Set the handler on the TUI
        app.set_message_handler(execution_manager.handle_user_prompt)

        sys.stderr.write(f"[TUI] Execution manager wired successfully\n")
        sys.stderr.flush()

    except Exception as e:
        import traceback
        sys.stderr.write(f"\n{'='*80}\n")
        sys.stderr.write(f"[TUI] ❌ CRITICAL: Execution manager failed to initialize!\n")
        sys.stderr.write(f"[TUI] Error: {e}\n")
        sys.stderr.write(f"[TUI] Traceback:\n")
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write(f"{'='*80}\n\n")
        sys.stderr.flush()
        # Fallback: Create a simple handler
        async def simple_handler(user_input, prompt_widget):
            sys.stderr.write(f"[SIMPLE HANDLER] Processing: {user_input}\n")
            sys.stderr.flush()
            session.add('user', user_input)
            app.write(f"\n[yellow]Using fallback handler - execution manager not available[/yellow]\n")

        app.set_message_handler(simple_handler)

    # Show initial prompt if provided
    if initial_prompt:
        await async_write(app, f"\n[cyan]>[/cyan] {initial_prompt}\n")

    # Start the TUI event loop with proper cleanup
    import sys
    sys.stderr.write("[TUI] Starting app.run_async()...\n")
    sys.stderr.flush()

    try:
        await app.run_async()
        sys.stderr.write("[TUI] app.run_async() completed normally\n")
        sys.stderr.flush()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        sys.stderr.write("\n[TUI] KeyboardInterrupt - shutting down\n")
        sys.stderr.flush()
    except Exception as e:
        # Handle other exceptions
        sys.stderr.write(f"\n[TUI] Exception during run: {e}\n")
        import traceback
        traceback.print_exc()
        sys.stderr.flush()
        raise

    # NOTE: Textual handles cleanup automatically via on_unmount()
    # Do NOT manually call on_unmount() here - it causes double cleanup
    sys.stderr.write("[TUI] TUI shutdown complete\n")
    sys.stderr.flush()


def run_interactive_async(config, session, initial_prompt=None):
    """Synchronous wrapper for interactive_async"""
    return asyncio.run(interactive_async(config, session, initial_prompt))