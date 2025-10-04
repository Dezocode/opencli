"""
Async Interactive Mode for OpenCLI
Fully async architecture with Textual TUI integration
"""

import asyncio
from openai import AsyncOpenAI
from simple_tui import OpenCLITUI


async def interactive_async(config, session, initial_prompt=None):
    """
    Async interactive mode with Textual TUI

    Args:
        config: OpenCLI configuration dict
        session: Session object
        initial_prompt: Optional initial prompt string
    """
    # Create async OpenAI client
    client = AsyncOpenAI(
        base_url=config["baseURL"],
        api_key=config["apiKey"]
    )

    # Create TUI - color mode is configured automatically in __init__
    app = OpenCLITUI(session=session, config=config)

    # Store initial prompt for processing after TUI starts
    app.initial_prompt = initial_prompt

    # Setup message handler
    async def handle_user_input(user_input: str):
        """Handle user input and generate response"""

        # Handle exit commands
        if user_input.lower() in ['exit', 'quit', '/exit', '/quit']:
            app.should_exit = True
            app.exit()
            return

        # Handle slash commands
        if user_input.startswith('/'):
            # Import from main module
            try:
                import sys
                import os
                # Add home dir to path for opencli import
                home = os.path.expanduser('~')
                if home not in sys.path:
                    sys.path.insert(0, home)

                # Import handle_slash_command
                import importlib
                opencli = importlib.import_module('opencli')
                handle_slash_command = opencli.handle_slash_command

                # Parse command
                parts = user_input.split(maxsplit=1)
                cmd = parts[0]
                args = parts[1] if len(parts) > 1 else None

                # Run in thread to avoid blocking
                handled = await asyncio.to_thread(
                    handle_slash_command,
                    cmd,
                    args,
                    session,
                    config,
                    None,  # agent_manager
                    None   # command_registry
                )

                if handled:
                    app.update_status()
                    return

            except Exception as e:
                app.write(f"[red]Command error: {e}[/red]\n")
                import traceback
                app.write(f"[dim]{traceback.format_exc()}[/dim]\n")
                return

        # Add to session
        session.messages.append({
            "role": "user",
            "content": user_input
        })

        # Stream response
        try:
            response = await client.chat.completions.create(
                model=session.model or config["model"],
                messages=session.messages,
                stream=True
            )

            full_response = ""
            async for chunk in response:
                if app.should_exit:
                    break

                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    app.write(delta, end="")

            app.write("\n\n")

            # Save response
            session.messages.append({
                "role": "assistant",
                "content": full_response
            })
            session.save()

            # Update status
            app.update_status()

        except Exception as e:
            app.write(f"[red]Error: {e}[/red]\n")

    # Set message handler
    app.message_handler = handle_user_input

    # Run TUI (this blocks until app exits)
    await app.run_async()


def run_interactive_async(config, session, initial_prompt=None):
    """
    Sync wrapper to run async interactive mode
    """
    asyncio.run(interactive_async(config, session, initial_prompt))
