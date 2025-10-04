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

    # Auto-initialize models if API key exists but no models registered
    try:
        from .model_manager import ModelManager
    except (ImportError, ValueError):
        from model_manager import ModelManager

    model_mgr = ModelManager()
    keys = model_mgr.get_configured_keys()
    models = model_mgr.list_available_models()

    # If we have an OpenRouter key but no models, fetch them
    if "openrouter" in keys and not models:
        async def auto_init_models():
            """Auto-fetch models on first run"""
            await asyncio.sleep(0.5)  # Let TUI mount first
            app.write("[dim]Detecting API key... fetching available models...[/dim]\n")

            result = await model_mgr.fetch_models_from_openrouter(keys["openrouter"])

            if result["success"]:
                model_mgr.add_api_key("openrouter", keys["openrouter"])
                model_mgr.register_models("openrouter", result["models"])
                app.write(f"[green]✓ Registered {result['count']} models from OpenRouter[/green]\n\n")
                app.write("Use [cyan]/model[/cyan] to see available models\n\n")
            else:
                app.write(f"[yellow]⚠ Could not fetch models: {result['error']}[/yellow]\n\n")

        # Schedule auto-init after TUI mounts
        asyncio.create_task(auto_init_models())

    # Setup message handler
    async def handle_user_input(user_input: str):
        """Handle user input and generate response"""

        # Handle exit commands
        if user_input.lower() in ['exit', 'quit', '/exit', '/quit']:
            app.should_exit = True
            app.exit()
            return

        # Check if awaiting model confirmation (y/n)
        if hasattr(session, '_awaiting_model_confirm') and session._awaiting_model_confirm:
            model_id = session._awaiting_model_confirm
            response = user_input.strip().lower()

            # Clear flag
            session._awaiting_model_confirm = None

            if response in ['y', 'yes']:
                try:
                    from .model_manager import ModelManager
                except (ImportError, ValueError):
                    from model_manager import ModelManager

                model_mgr = ModelManager()
                result = model_mgr.switch_model(session, model_id)

                if result["success"]:
                    app.write(f"[green]✓ Switched to {result['model']}[/green]\n\n")

                    # Show pricing info
                    if "pricing" in result:
                        pricing = result["pricing"]
                        prompt_cost = pricing.get("prompt", "?")
                        completion_cost = pricing.get("completion", "?")

                        # Build pricing message
                        pricing_parts = []

                        if prompt_cost == "0":
                            pricing_parts.append("FREE (prompt)")
                        elif prompt_cost != "?":
                            prompt_per_1m = float(prompt_cost) * 1_000_000
                            pricing_parts.append(f"${prompt_per_1m:.2f}/1M prompt tokens")

                        if completion_cost == "0":
                            pricing_parts.append("FREE (completion)")
                        elif completion_cost != "?":
                            completion_per_1m = float(completion_cost) * 1_000_000
                            pricing_parts.append(f"${completion_per_1m:.2f}/1M completion tokens")

                        if pricing_parts:
                            app.write(f"[dim]💰 Pricing: {', '.join(pricing_parts)}[/dim]\n\n")

                    # Update client
                    client.base_url = config["baseURL"]
                    client.api_key = config["apiKey"]
                    app.update_status()
                else:
                    app.write(f"[red]✗ {result['error']}[/red]\n\n")
            else:
                app.write("[dim]Model switch cancelled.[/dim]\n\n")

            return

        # Check if awaiting API key input
        if hasattr(session, '_awaiting_api_key') and session._awaiting_api_key:
            try:
                from .model_manager import ModelManager
            except (ImportError, ValueError):
                from model_manager import ModelManager

            model_mgr = ModelManager()
            api_key = user_input.strip()

            # Clear flag
            session._awaiting_api_key = False

            app.write("[dim]Validating key and fetching models...[/dim]\n")

            # Fetch models from OpenRouter
            result = await model_mgr.fetch_models_from_openrouter(api_key)

            if result["success"]:
                # Register models
                model_mgr.add_api_key("openrouter", api_key)
                model_mgr.register_models("openrouter", result["models"])

                app.write(f"[green]✓ API key added![/green]\n")
                app.write(f"[green]✓ Registered {result['count']} models[/green]\n\n")
                app.write("Use [cyan]/model[/cyan] to see available models\n\n")
            else:
                app.write(f"[red]✗ Failed: {result['error']}[/red]\n\n")

            return

        # Handle slash commands
        if user_input.startswith('/'):
            # Handle /model command locally
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
                    # Refresh models from OpenRouter to get latest rankings/pricing
                    keys = model_mgr.get_configured_keys()
                    if "openrouter" in keys:
                        app.write("[dim]Refreshing models from OpenRouter...[/dim]\n")
                        result = await model_mgr.fetch_models_from_openrouter(keys["openrouter"])
                        if result["success"]:
                            model_mgr.register_models("openrouter", result["models"])
                            app.write("[dim]✓ Updated {count} models[/dim]\n\n".format(count=result["count"]))

                    # Show available models (only those with keys)
                    current = model_mgr.get_current_model(session)
                    models = model_mgr.list_available_models()
                    recent = model_mgr.get_recent_models()

                    if not models:
                        app.write("[yellow]⚠ No models available[/yellow]\n\n")
                        app.write("Add an API key first:\n")
                        app.write("  [cyan]/model add[/cyan]\n\n")
                        return

                    # Get provider info
                    providers = model_mgr.get_providers()
                    provider_names = {p["id"]: p["name"] for p in providers}

                    # Show recently used models first
                    if recent:
                        app.write("[bold magenta]⭐ Recently Used:[/bold magenta]\n\n")

                        for idx, model in enumerate(recent[:5], 1):  # Top 5 recent
                            marker = "→" if model["id"] == current else " "
                            context = f"{model['context']//1000}K" if model['context'] else "?"
                            provider = model.get("provider", "unknown")
                            provider_name = provider_names.get(provider, provider)

                            # Check if free
                            pricing = model.get("pricing", {})
                            is_free = ":free" in model["id"] or pricing.get("prompt") == "0"
                            free_badge = " [green]FREE[/green]" if is_free else ""

                            app.write(f"{marker} [bold]r{idx}.[/bold] {model['name']}{free_badge}\n")
                            app.write(f"     ID: [dim]{model['id']}[/dim]\n")
                            app.write(f"     Provider: [cyan]{provider_name}[/cyan] | Context: {context}\n\n")

                        app.write("\n")

                    app.write("[bold cyan]📋 All Available Models:[/bold cyan]\n\n")

                    for idx, model in enumerate(models, 1):
                        marker = "→" if model["id"] == current else " "
                        context = f"{model['context']//1000}K" if model['context'] else "?"
                        provider = model.get("provider", "unknown")
                        provider_name = provider_names.get(provider, provider)

                        # Check if free
                        pricing = model.get("pricing", {})
                        is_free = ":free" in model["id"] or pricing.get("prompt") == "0"
                        free_badge = " [green]FREE[/green]" if is_free else ""

                        app.write(f"{marker} [bold]{idx}.[/bold] {model['name']}{free_badge}\n")
                        app.write(f"     ID: [dim]{model['id']}[/dim]\n")
                        app.write(f"     Provider: [cyan]{provider_name}[/cyan] | Context: {context}\n\n")

                    app.write("\n[dim]Usage: /model <number> or /model r<number> (recent)  or  /model add[/dim]\n\n")

                elif args == "add":
                    # Interactive API key setup
                    app.write("[bold]🔑 Add API Key[/bold]\n\n")
                    app.write("Enter your OpenRouter API key:\n")
                    app.write("[dim](Get one at https://openrouter.ai/keys)[/dim]\n\n")

                    # Prompt for key on next input - set a flag
                    app.write("[yellow]Type your key and press Enter:[/yellow]\n")
                    session._awaiting_api_key = True

                else:
                    # Switch model by number or ID
                    models = model_mgr.list_available_models()
                    recent = model_mgr.get_recent_models()

                    if not models:
                        app.write("[red]No models available. Use /model add first.[/red]\n\n")
                        return

                    # Check if recent model selection (r1, r2, etc.)
                    if args.lower().startswith('r') and args[1:].isdigit():
                        idx = int(args[1:]) - 1
                        if 0 <= idx < len(recent):
                            model_id = recent[idx]["id"]
                            selected_model = recent[idx]
                        else:
                            app.write(f"[red]✗ Invalid recent model number: {args}[/red]\n\n")
                            return
                    # Check if numeric selection from all models
                    elif args.isdigit():
                        idx = int(args) - 1
                        if 0 <= idx < len(models):
                            model_id = models[idx]["id"]
                            selected_model = models[idx]
                        else:
                            app.write(f"[red]✗ Invalid model number: {args}[/red]\n\n")
                            return
                    # Model ID directly
                    else:
                        model_id = args
                        # Find in models list for pricing check
                        selected_model = None
                        for m in models:
                            if m["id"] == model_id:
                                selected_model = m
                                break

                    # Check if paid model - show confirmation
                    if selected_model:
                        pricing = selected_model.get("pricing", {})
                        is_free = ":free" in selected_model["id"] or pricing.get("prompt") == "0"

                        if not is_free:
                            # Calculate readable pricing
                            prompt_cost = pricing.get("prompt", "?")
                            completion_cost = pricing.get("completion", "?")

                            app.write(f"[yellow]⚠️  PAID MODEL WARNING[/yellow]\n\n")
                            app.write(f"Model: [bold]{selected_model['name']}[/bold]\n")

                            if prompt_cost != "?":
                                prompt_per_1m = float(prompt_cost) * 1_000_000
                                app.write(f"Prompt: [yellow]${prompt_per_1m:.2f}/1M tokens[/yellow]\n")
                            if completion_cost != "?":
                                completion_per_1m = float(completion_cost) * 1_000_000
                                app.write(f"Completion: [yellow]${completion_per_1m:.2f}/1M tokens[/yellow]\n\n")

                            app.write("[yellow]Switch to this paid model? (y/n):[/yellow]\n")

                            # Set flag to await y/n response
                            session._awaiting_model_confirm = model_id
                            return

                    result = model_mgr.switch_model(session, model_id)

                    if result["success"]:
                        app.write(f"[green]✓ Switched to {result['model']}[/green]\n\n")

                        # Show pricing info if available
                        if "pricing" in result:
                            pricing = result["pricing"]
                            prompt_cost = pricing.get("prompt", "?")
                            completion_cost = pricing.get("completion", "?")

                            # Build pricing message
                            pricing_parts = []

                            # Prompt pricing
                            if prompt_cost == "0":
                                pricing_parts.append("FREE (prompt)")
                            elif prompt_cost != "?":
                                prompt_per_1m = float(prompt_cost) * 1_000_000
                                pricing_parts.append(f"${prompt_per_1m:.2f}/1M prompt tokens")

                            # Completion pricing
                            if completion_cost == "0":
                                pricing_parts.append("FREE (completion)")
                            elif completion_cost != "?":
                                completion_per_1m = float(completion_cost) * 1_000_000
                                pricing_parts.append(f"${completion_per_1m:.2f}/1M completion tokens")

                            if pricing_parts:
                                app.write(f"[dim]💰 Pricing: {', '.join(pricing_parts)}[/dim]\n\n")

                        # Update client
                        client.base_url = config["baseURL"]
                        client.api_key = config["apiKey"]

                        app.update_status()
                    else:
                        app.write(f"[red]✗ {result['error']}[/red]\n\n")

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
