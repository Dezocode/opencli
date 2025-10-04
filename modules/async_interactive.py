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
            # Handle /model command locally (no API calls)
            if user_input.startswith('/model'):
                try:
                    from .model_manager import ModelManager
                except (ImportError, ValueError):
                    from model_manager import ModelManager

                model_mgr = ModelManager()

                # Parse args
                parts = user_input.split(maxsplit=1)
                args = parts[1] if len(parts) > 1 else None

                if not args:
                    # Show model selection UI
                    current = model_mgr.get_current_model(session)
                    models = model_mgr.list_models()

                    app.write("[bold cyan]📋 Available Models:[/bold cyan]\n\n")

                    for idx, model in enumerate(models, 1):
                        marker = "→" if model["id"] == current else " "
                        key_status = "✓" if model["has_key"] else "✗"
                        context = f"{model['context']//1000}K" if model['context'] else "?"

                        app.write(f"{marker} [bold]{idx}.[/bold] {model['name']}\n")
                        app.write(f"     ID: [dim]{model['id']}[/dim]\n")
                        app.write(f"     Provider: {model['provider']} {key_status}  Context: {context}\n\n")

                    app.write("\n[dim]Usage: /model <number> or /model <model-id>[/dim]\n")
                    app.write("[dim]       /model key <provider> <api-key>[/dim]\n\n")

                elif args.startswith("key "):
                    # Set API key
                    key_parts = args.split(maxsplit=2)[1:]
                    if len(key_parts) < 2:
                        app.write("[red]Usage: /model key <provider> <api-key>[/red]\n\n")
                    else:
                        provider_id, api_key = key_parts[0], key_parts[1]
                        model_mgr.set_api_key(provider_id, api_key)
                        app.write(f"[green]✓ API key set for {provider_id}[/green]\n\n")

                else:
                    # Switch model
                    models = model_mgr.list_models()

                    # Check if numeric selection
                    try:
                        idx = int(args) - 1
                        if 0 <= idx < len(models):
                            model_id = models[idx]["id"]
                        else:
                            raise ValueError()
                    except ValueError:
                        model_id = args

                    result = model_mgr.switch_model(session, model_id)

                    if result["success"]:
                        app.write(f"[green]✓ Switched to {result['model']}[/green]\n")
                        app.write(f"[dim]Provider: {result['provider']}[/dim]\n\n")

                        # Update client for new model
                        client.base_url = config["baseURL"]
                        client.api_key = model_mgr.get_api_key(models[idx]["provider_id"] if 'idx' in locals() else model_mgr.models["models"][model_id]["provider"])

                        app.update_status()
                    else:
                        app.write(f"[red]✗ {result['error']}[/red]\n")
                        if result.get("needs_key"):
                            providers = model_mgr.get_providers()
                            for prov in providers:
                                if prov["id"] == result["provider_id"]:
                                    app.write(f"\n[yellow]Set API key with:[/yellow]\n")
                                    app.write(f"  /model key {prov['id']} YOUR_API_KEY\n\n")

                return

            # Handle other commands via main opencli module
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
