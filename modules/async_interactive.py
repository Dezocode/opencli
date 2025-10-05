"""
Async Interactive Mode for OpenCLI
Fully async architecture with Textual TUI integration
"""

import os
import asyncio
from datetime import datetime
from pathlib import Path
from openai import AsyncOpenAI
from simple_tui import OpenCLITUI

try:
    from .frontier_colors import FRONTIER_COLORS
except (ImportError, ValueError):
    try:
        from frontier_colors import FRONTIER_COLORS
    except ImportError:
        FRONTIER_COLORS = {}


def prepare_messages_with_context(messages, config):
    """
    Prepare messages with system context (constitution + AGENTS.md + cwd)
    Only adds system message if one doesn't already exist
    """
    # Check if system message already exists
    has_system = any(m.get('role') == 'system' for m in messages)

    if has_system:
        return messages

    # Load essential context
    config_dir = Path.home() / '.opencli'
    constitution_file = config_dir / 'agents' / 'system_prompts' / 'base' / 'constitution.md'
    agents_template = config_dir / 'agents' / 'system_prompts' / 'base' / 'AGENTS.md'

    # Build system message
    system_parts = []

    # Add constitution (tool guides)
    if constitution_file.exists():
        with open(constitution_file) as f:
            system_parts.append(f.read())

    # Add AGENTS.md (project context or template)
    # First try to find project-specific AGENTS.md
    cwd = os.getcwd()
    current = Path(cwd)
    agents_md_content = None

    for parent in [current] + list(current.parents):
        agents_file = parent / 'AGENTS.md'
        if agents_file.exists():
            with open(agents_file) as f:
                agents_md_content = f.read()
            break

    # If no project AGENTS.md, use template
    if not agents_md_content and agents_template.exists():
        with open(agents_template) as f:
            agents_md_content = f.read()

    if agents_md_content:
        system_parts.append(f"\n## Project Context\n{agents_md_content}")

    # Add working directory
    system_parts.append(f"\nWorking directory: {cwd}")

    # Create system message
    system_message = {
        'role': 'system',
        'content': '\n'.join(system_parts)
    }

    # Return messages with system message first
    return [system_message] + messages


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

        # Check if awaiting provider key input
        if hasattr(session, '_awaiting_provider_key') and session._awaiting_provider_key:
            try:
                from .model_manager import ModelManager
            except (ImportError, ValueError):
                from model_manager import ModelManager

            model_mgr = ModelManager()
            api_key = user_input.strip()

            # Clear flag
            session._awaiting_provider_key = False

            # Auto-detect provider
            provider = model_mgr.detect_provider(api_key)

            if not provider:
                app.write("[red]✗ Could not detect provider from API key format[/red]\n\n")
                app.write("Supported key formats:\n")
                app.write("  • OpenRouter: sk-or-...\n")
                app.write("  • Anthropic: sk-ant-...\n")
                app.write("  • OpenAI: sk-proj-... or sk-...\n")
                app.write("  • DeepSeek: sk-...\n")
                app.write("  • Google AI: AIza...\n\n")
                return

            provider_info = model_mgr.models_db.get("providers", {}).get(provider, {})
            provider_name = provider_info.get("name", provider)

            app.write(f"[green]✓ Detected provider: {provider_name}[/green]\n")
            app.write("[dim]Fetching models...[/dim]\n\n")

            # Fetch models from provider
            result = await model_mgr.fetch_models_from_provider(provider, api_key)

            if result["success"]:
                model_mgr.add_api_key(provider, api_key)
                model_mgr.register_models(provider, result["models"])

                app.write(f"[green]✓ Added {provider_name}![/green]\n")
                app.write(f"[green]✓ Registered {result['count']} models[/green]\n\n")
                app.write("Use [cyan]/model[/cyan] to see and switch to these models\n\n")
            else:
                app.write(f"[red]✗ Failed to fetch models: {result['error']}[/red]\n\n")

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

            # Handle /providers command locally
            if user_input.startswith('/providers'):
                try:
                    from .model_manager import ModelManager
                except (ImportError, ValueError):
                    from model_manager import ModelManager

                model_mgr = ModelManager()

                # Parse args
                parts = user_input.split(maxsplit=2)
                subcommand = parts[1] if len(parts) > 1 else None
                args = parts[2] if len(parts) > 2 else None

                if not subcommand or subcommand == "list":
                    # List all providers with status
                    providers = model_mgr.get_providers()

                    app.write("[bold cyan]🔌 API Providers[/bold cyan]\n\n")

                    for provider in providers:
                        status = "[green]✓ Configured[/green]" if provider["has_key"] else "[dim]Not configured[/dim]"
                        model_count = provider.get("model_count", 0)
                        models_text = f"({model_count} models)" if provider["has_key"] else ""

                        app.write(f"[bold]{provider['name']}[/bold] {status} {models_text}\n")
                        app.write(f"  ID: [dim]{provider['id']}[/dim]\n\n")

                    app.write("\n[dim]Usage:[/dim]\n")
                    app.write("  [cyan]/providers add[/cyan]          Add new provider key\n")
                    app.write("  [cyan]/providers add <key>[/cyan]   Add specific key (auto-detects provider)\n")
                    app.write("  [cyan]/providers remove <id>[/cyan] Remove provider key\n\n")

                elif subcommand == "add":
                    if not args:
                        # Interactive mode - prompt for key
                        app.write("[bold]🔑 Add Provider API Key[/bold]\n\n")
                        app.write("Paste your API key and I'll auto-detect the provider:\n")
                        app.write("[dim](Supports: OpenRouter, Anthropic, OpenAI, DeepSeek, Google AI)[/dim]\n\n")
                        app.write("[yellow]Type your key and press Enter:[/yellow]\n")

                        # Set flag to await provider key
                        session._awaiting_provider_key = True
                    else:
                        # Direct key provided - detect and add
                        api_key = args.strip()
                        provider = model_mgr.detect_provider(api_key)

                        if not provider:
                            app.write("[red]✗ Could not detect provider from API key format[/red]\n\n")
                            app.write("Supported key formats:\n")
                            app.write("  • OpenRouter: sk-or-...\n")
                            app.write("  • Anthropic: sk-ant-...\n")
                            app.write("  • OpenAI: sk-proj-... or sk-...\n")
                            app.write("  • DeepSeek: sk-...\n")
                            app.write("  • Google AI: AIza...\n\n")
                            return

                        provider_info = model_mgr.models_db.get("providers", {}).get(provider, {})
                        provider_name = provider_info.get("name", provider)

                        app.write(f"[green]✓ Detected provider: {provider_name}[/green]\n")
                        app.write("[dim]Fetching models...[/dim]\n\n")

                        # Fetch models from provider
                        result = await model_mgr.fetch_models_from_provider(provider, api_key)

                        if result["success"]:
                            model_mgr.add_api_key(provider, api_key)
                            model_mgr.register_models(provider, result["models"])

                            app.write(f"[green]✓ Added {provider_name}![/green]\n")
                            app.write(f"[green]✓ Registered {result['count']} models[/green]\n\n")
                            app.write("Use [cyan]/model[/cyan] to see and switch to these models\n\n")
                        else:
                            app.write(f"[red]✗ Failed to fetch models: {result['error']}[/red]\n\n")

                elif subcommand == "remove":
                    if not args:
                        app.write("[red]✗ Specify provider ID to remove[/red]\n\n")
                        app.write("Example: [cyan]/providers remove openrouter[/cyan]\n\n")
                        return

                    provider_id = args.strip()
                    providers = model_mgr.models_db.get("providers", {})

                    if provider_id not in providers:
                        app.write(f"[red]✗ Unknown provider: {provider_id}[/red]\n\n")
                        return

                    # Remove the key
                    if provider_id in model_mgr.models_db.get("api_keys", {}):
                        del model_mgr.models_db["api_keys"][provider_id]
                        model_mgr._save_models()
                        app.write(f"[green]✓ Removed {provider_id} API key[/green]\n\n")
                    else:
                        app.write(f"[yellow]⚠ {provider_id} was not configured[/yellow]\n\n")

                else:
                    app.write(f"[red]✗ Unknown subcommand: {subcommand}[/red]\n\n")
                    app.write("Usage: [cyan]/providers [list|add|remove][/cyan]\n\n")

                return

            # Handle /restart command (restart OpenCLI while keeping IPC alive)
            if user_input.startswith('/restart'):
                app.write("[cyan]🔄 Restarting OpenCLI...[/cyan]\n\n")

                try:
                    import sys
                    import os

                    # Keep IPC server alive by enabling persistence
                    if hasattr(session, 'ipc_server') and session.ipc_server and session.ipc_server.running:
                        # Enable persistence mode (20 min timeout)
                        async def persist_server():
                            await session.ipc_server.stop(persist=True)

                        try:
                            asyncio.create_task(persist_server())
                            app.write("[dim]✓ IPC server will remain active for 20 minutes[/dim]\n")
                        except Exception:
                            pass

                    # Save current session
                    session.save()
                    app.write("[dim]✓ Session saved[/dim]\n\n")

                    # Get the OpenCLI command path
                    opencli_path = os.path.expanduser("~/bin/opencli")

                    # Prepare restart command that will resume this session
                    restart_cmd = f"{opencli_path} --resume {session.session_id}"

                    app.write(f"[green]Restarting with session {session.session_id[:8]}...[/green]\n\n")

                    # Use os.execv to replace the current process
                    # This maintains the shell and restarts OpenCLI
                    os.execv(sys.executable, [sys.executable, opencli_path, '--resume', session.session_id])

                except Exception as e:
                    app.write(f"[red]✗ Restart failed: {e}[/red]\n\n")
                    import traceback
                    app.write(f"[dim]{traceback.format_exc()}[/dim]\n\n")

                return

            # Handle /upgrade command (reload modules)
            if user_input.startswith('/upgrade'):
                app.write("[cyan]🔄 Reloading modules...[/cyan]\n\n")

                try:
                    import importlib
                    import sys

                    # List of modules to reload
                    modules_to_reload = [
                        'simple_tui',
                        'streaming_display',
                        'frontier_colors',
                        'markdown_renderer',
                        'async_interactive',
                        'opencli_ipc',
                        'model_manager'
                    ]

                    reloaded_count = 0
                    for module_name in modules_to_reload:
                        if module_name in sys.modules:
                            try:
                                importlib.reload(sys.modules[module_name])
                                reloaded_count += 1
                                app.write(f"[dim]✓ Reloaded {module_name}[/dim]\n")
                            except Exception as e:
                                app.write(f"[yellow]⚠ Could not reload {module_name}: {e}[/yellow]\n")

                    app.write(f"\n[green]✓ Reloaded {reloaded_count} modules[/green]\n\n")

                    # Refresh laser colors on the running app instance
                    try:
                        # Try relative import first
                        try:
                            from .frontier_colors import FRONTIER_LASER_COLORS
                        except (ImportError, ValueError):
                            from frontier_colors import FRONTIER_LASER_COLORS

                        # Update main app colors
                        app._laser_colors = FRONTIER_LASER_COLORS

                        # Update streaming display widget colors
                        try:
                            stream_display = app.query_one("#stream-display")
                            stream_display.set_laser_colors(FRONTIER_LASER_COLORS)
                            app.write(f"[dim]✓ Refreshed laser colors: {FRONTIER_LASER_COLORS[:3]}...[/dim]\n\n")
                        except Exception:
                            # Fallback if query fails
                            if hasattr(app, '_content_widget') and app._content_widget:
                                app._content_widget.set_laser_colors(FRONTIER_LASER_COLORS)
                                app.write(f"[dim]✓ Refreshed laser colors: {FRONTIER_LASER_COLORS[:3]}...[/dim]\n\n")
                            else:
                                app.write(f"[dim]✓ Refreshed app laser colors (restart may be needed for full effect)[/dim]\n\n")
                    except Exception as e:
                        app.write(f"[yellow]⚠ Could not refresh laser colors: {e}[/yellow]\n\n")

                    app.write("[dim]Note: Some changes may require restarting OpenCLI[/dim]\n\n")

                except Exception as e:
                    app.write(f"[red]✗ Module reload failed: {e}[/red]\n\n")
                    import traceback
                    app.write(f"[dim]{traceback.format_exc()}[/dim]\n\n")

                return

            # Handle /api command (IPC server control)
            if user_input.startswith('/api'):
                parts = user_input.split(maxsplit=1)
                subcommand = parts[1] if len(parts) > 1 else "status"

                if subcommand == "start":
                    # Start IPC server
                    try:
                        if hasattr(session, 'ipc_server') and session.ipc_server:
                            if session.ipc_server.running:
                                app.write("[yellow]⚠ IPC server is already running[/yellow]\n\n")
                            else:
                                await session.ipc_server.start()

                                # Initialize shell injector
                                try:
                                    from .shell_injector import get_shell_injector
                                except (ImportError, ValueError):
                                    from shell_injector import get_shell_injector

                                session.shell_injector = get_shell_injector(session.ipc_server)
                                await session.shell_injector.start()

                                # Register response handler for command results
                                try:
                                    from .opencli_ipc import MessageType
                                except (ImportError, ValueError):
                                    from opencli_ipc import MessageType

                                async def handle_response(message):
                                    """Handle responses from subagents"""
                                    result = message.payload.get('result', {})
                                    if result.get('success'):
                                        app.write(f"\n[green]📥 Response from {message.sender_id[:8]}...[/green]\n")
                                        if 'stdout' in result:
                                            app.write(f"[dim]{result['stdout']}[/dim]\n")
                                    else:
                                        app.write(f"\n[red]📥 Error from {message.sender_id[:8]}...[/red]\n")
                                        app.write(f"[dim]{result.get('error', 'Unknown error')}[/dim]\n")
                                    app.write("\n")

                                async def handle_message(message):
                                    """Handle messages from subagents - send to AI or handle commands"""
                                    payload = message.payload
                                    content = payload.get('content', '')

                                    # Display in chat
                                    app.write(f"\n[dim]📨 {content}[/dim]\n\n")

                                    # Route to handle_user_input which will detect if it's a command
                                    await handle_user_input(content)

                                session.ipc_server.register_handler(MessageType.RESPONSE.value, handle_response)
                                session.ipc_server.register_handler(MessageType.MESSAGE.value, handle_message)

                                app.write("[green]✓ IPC server started[/green]\n\n")
                                app.write(f"Socket: /tmp/opencli/opencli_{session.session_id}.sock\n\n")
                                app.write(f"[dim]Shell injection enabled - Messages logged to ~/.opencli/ipc_logs/[/dim]\n\n")
                        else:
                            # Create and start IPC server
                            try:
                                from .opencli_ipc import IPCServer
                            except (ImportError, ValueError):
                                from opencli_ipc import IPCServer

                            session.ipc_server = IPCServer(session.session_id)
                            await session.ipc_server.start()

                            # Initialize shell injector
                            try:
                                from .shell_injector import get_shell_injector
                            except (ImportError, ValueError):
                                from shell_injector import get_shell_injector

                            session.shell_injector = get_shell_injector(session.ipc_server)
                            await session.shell_injector.start()

                            # Register response handler for command results
                            try:
                                from .opencli_ipc import MessageType
                            except (ImportError, ValueError):
                                from opencli_ipc import MessageType

                            async def handle_response(message):
                                """Handle responses from subagents"""
                                result = message.payload.get('result', {})
                                if result.get('success'):
                                    app.write(f"\n[green]📥 Response from {message.sender_id[:8]}...[/green]\n")
                                    if 'stdout' in result:
                                        app.write(f"[dim]{result['stdout']}[/dim]\n")
                                else:
                                    app.write(f"\n[red]📥 Error from {message.sender_id[:8]}...[/red]\n")
                                    app.write(f"[dim]{result.get('error', 'Unknown error')}[/dim]\n")
                                app.write("\n")

                            async def handle_message(message):
                                """Handle messages from subagents - send to AI or handle commands"""
                                payload = message.payload
                                content = payload.get('content', '')

                                # Display in chat
                                app.write(f"\n[dim]📨 {content}[/dim]\n\n")

                                # Route to handle_user_input which will detect if it's a command
                                await handle_user_input(content)

                            session.ipc_server.register_handler(MessageType.RESPONSE.value, handle_response)
                            session.ipc_server.register_handler(MessageType.MESSAGE.value, handle_message)

                            app.write("[green]✓ IPC server started[/green]\n\n")
                            app.write(f"Socket: /tmp/opencli/opencli_{session.session_id}.sock\n\n")
                            app.write(f"[dim]Shell injection enabled - Messages logged to ~/.opencli/ipc_logs/[/dim]\n\n")
                    except Exception as e:
                        app.write(f"[red]✗ Failed to start IPC server: {e}[/red]\n\n")
                        import traceback
                        app.write(f"[dim]{traceback.format_exc()}[/dim]\n\n")

                elif subcommand == "stop":
                    # Stop IPC server
                    if hasattr(session, 'ipc_server') and session.ipc_server:
                        # Stop shell injector first
                        if hasattr(session, 'shell_injector') and session.shell_injector:
                            await session.shell_injector.stop()

                        await session.ipc_server.stop()
                        app.write("[green]✓ IPC server stopped[/green]\n\n")
                    else:
                        app.write("[yellow]⚠ IPC server is not running[/yellow]\n\n")

                elif subcommand == "status":
                    # Show IPC server status
                    if hasattr(session, 'ipc_server') and session.ipc_server:
                        if session.ipc_server.running:
                            subagent_count = session.ipc_server.get_subagent_count()
                            app.write("[green]✓ IPC server is running[/green]\n")
                            app.write(f"Socket: /tmp/opencli/opencli_{session.session_id}.sock\n")
                            app.write(f"Session ID: {session.session_id}\n")
                            app.write(f"Subagents: {subagent_count}\n\n")
                        else:
                            app.write("[yellow]⚠ IPC server is not running[/yellow]\n\n")
                    else:
                        app.write("[yellow]⚠ IPC server is not initialized[/yellow]\n\n")
                        app.write("Use [cyan]/api start[/cyan] to start the server\n\n")

                elif subcommand == "logs":
                    # Show injection logs summary
                    if hasattr(session, 'shell_injector') and session.shell_injector:
                        summary = session.shell_injector.get_log_summary()
                        app.write("[cyan]📊 Shell Injection Logs[/cyan]\n\n")
                        app.write(f"Total Messages: {summary['total_messages']}\n")
                        app.write(f"Log File: {summary['log_file']}\n\n")

                        if summary['by_type']:
                            app.write("By Type:\n")
                            for msg_type, count in summary['by_type'].items():
                                app.write(f"  • {msg_type}: {count}\n")
                            app.write("\n")

                        if summary['by_agent']:
                            app.write("By Agent:\n")
                            for agent, count in summary['by_agent'].items():
                                app.write(f"  • {agent}: {count}\n")
                            app.write("\n")
                    else:
                        app.write("[yellow]⚠ Shell injector not running[/yellow]\n\n")
                        app.write("Start IPC server first: [cyan]/api start[/cyan]\n\n")

                else:
                    app.write(f"[red]✗ Unknown subcommand: {subcommand}[/red]\n\n")
                    app.write("Usage:\n")
                    app.write("  [cyan]/api status[/cyan]  - Show server status\n")
                    app.write("  [cyan]/api start[/cyan]   - Start IPC server\n")
                    app.write("  [cyan]/api stop[/cyan]    - Stop IPC server\n")
                    app.write("  [cyan]/api logs[/cyan]    - Show injection logs\n\n")

                return

            # Handle /inject command - Send commands to subagents
            if user_input.startswith('/inject'):
                parts = user_input.split(maxsplit=2)

                if len(parts) < 3:
                    app.write("[yellow]Usage: /inject <agent-id|all> <command>[/yellow]\n\n")
                    app.write("Examples:\n")
                    app.write("  [cyan]/inject all ls -la[/cyan]           - Run command on all agents\n")
                    app.write("  [cyan]/inject <agent-id> pwd[/cyan]       - Run command on specific agent\n")
                    app.write("  [cyan]/inject all read /path/to/file[/cyan] - Read file on all agents\n\n")

                    if hasattr(session, 'ipc_server') and session.ipc_server:
                        subagents = session.ipc_server.get_subagents()
                        if subagents:
                            app.write("Connected agents:\n")
                            for agent in subagents:
                                app.write(f"  • {agent.name} ({agent.agent_id[:8]}...)\n")
                            app.write("\n")
                    return

                target = parts[1]
                command = parts[2]

                if not hasattr(session, 'ipc_server') or not session.ipc_server or not session.ipc_server.running:
                    app.write("[red]✗ IPC server is not running[/red]\n\n")
                    app.write("Start it with: [cyan]/api start[/cyan]\n\n")
                    return

                # Get subagents
                subagents = session.ipc_server.get_subagents()

                if not subagents:
                    app.write("[yellow]⚠ No subagents connected[/yellow]\n\n")
                    return

                # Determine targets
                if target.lower() == 'all':
                    targets = [agent.agent_id for agent in subagents]
                    app.write(f"[cyan]📤 Sending command to {len(targets)} agent(s)...[/cyan]\n\n")
                else:
                    # Try to match by ID prefix or name
                    matched = None
                    for agent in subagents:
                        if agent.agent_id.startswith(target) or agent.name.lower() == target.lower():
                            matched = agent
                            break

                    if not matched:
                        app.write(f"[red]✗ Agent not found: {target}[/red]\n\n")
                        app.write("Connected agents:\n")
                        for agent in subagents:
                            app.write(f"  • {agent.name} ({agent.agent_id[:8]}...)\n")
                        app.write("\n")
                        return

                    targets = [matched.agent_id]
                    app.write(f"[cyan]📤 Sending command to {matched.name}...[/cyan]\n\n")

                # Send command to targets
                for agent_id in targets:
                    try:
                        try:
                            from .opencli_ipc import MessageType
                        except (ImportError, ValueError):
                            from opencli_ipc import MessageType

                        await session.ipc_server.send_to_agent(
                            agent_id,
                            MessageType.COMMAND.value,
                            {
                                'command': command,
                                'type': 'bash',
                                'timestamp': datetime.now().isoformat()
                            }
                        )
                        app.write(f"[green]✓ Command sent to {agent_id[:8]}...[/green]\n")
                    except Exception as e:
                        app.write(f"[red]✗ Failed to send to {agent_id[:8]}...: {e}[/red]\n")

                app.write("\n")
                return

            # Handle Spec-Driven Development commands (Spec-Kit integration)
            spec_commands = ['/specify', '/constitution', '/plan', '/tasks',
                           '/implement', '/test', '/spec-check']

            if any(user_input.startswith(cmd) for cmd in spec_commands):
                try:
                    from .specify_wrapper import get_specify_wrapper
                except (ImportError, ValueError):
                    from specify_wrapper import get_specify_wrapper

                wrapper = get_specify_wrapper()
                parsed = wrapper.parse_slash_command(user_input)

                if parsed:
                    command = parsed['command']
                    content = parsed['content']

                    # Show user what they're requesting
                    app.write(f"[{FRONTIER_COLORS.get('info', '#6B8E9E') if FRONTIER_COLORS else 'cyan'}]Spec-Driven Development: {command}[/]\n\n")

                    # Format the spec command as instructions for the AI
                    ai_prompt = wrapper.format_spec_for_ai(command, content)

                    # Recursively call handle_user_input with the formatted prompt
                    # This sends it to the AI as a regular message
                    await handle_user_input(ai_prompt)

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
                    None  # agent_manager
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

        # Auto-save session state
        session.save()

        # Stream response in separate thread to avoid blocking UI
        async def stream_ai_response():
            """Run AI streaming in background without blocking UI"""
            try:
                # Prepare messages with system context
                messages_with_context = prepare_messages_with_context(session.messages, config)

                response = await client.chat.completions.create(
                    model=session.model or config["model"],
                    messages=messages_with_context,
                    stream=True
                )

                full_response = ""
                async for chunk in response:
                    if app.should_exit:
                        break

                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response += delta
                        # Thread-safe write to UI
                        app.write(delta, end="")

                # Finish streaming to process markdown FIRST (before adding newlines)
                if hasattr(app, 'finish_stream'):
                    app.finish_stream()

                # Then add spacing after rendered markdown
                app.write("\n\n")

                # Stop spinner - API response complete
                if hasattr(app, 'stop_spinner'):
                    app.stop_spinner()

                # Save response
                session.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

                # Auto-save session state
                session.save()

                # Broadcast response to IPC clients
                if hasattr(session, 'ipc_server') and session.ipc_server and session.ipc_server.running:
                    try:
                        from .opencli_ipc import MessageType
                    except (ImportError, ValueError):
                        from opencli_ipc import MessageType

                    await session.ipc_server.broadcast(
                        MessageType.MESSAGE.value,
                        {
                            "role": "assistant",
                            "content": full_response,
                            "from_ai": True
                        }
                    )

                # Update status
                app.update_status()

            except Exception as e:
                app.write(f"[red]Error: {e}[/red]\n")

        # Start streaming in background task
        asyncio.create_task(stream_ai_response())

    # Set message handler
    app.message_handler = handle_user_input

    # Run TUI (this blocks until app exits)
    await app.run_async()


def run_interactive_async(config, session, initial_prompt=None):
    """
    Sync wrapper to run async interactive mode
    """
    asyncio.run(interactive_async(config, session, initial_prompt))
