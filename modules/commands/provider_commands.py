"""Provider Commands"""

from typing import Optional

async def provider_manage(app, session, **context):
    """Manage API providers"""
    try:
        from model_manager import ModelManager
    except (ImportError, ValueError):
        from .model_manager import ModelManager

    mgr = ModelManager()
    providers = mgr.get_providers()

    app.write("[cyan]Provider Management[/cyan]\n\n")

    if not providers:
        app.write("[yellow]No providers configured yet[/yellow]\n\n")
        app.write("[dim]Use /model add-key <provider> <key> to add a provider[/dim]\n\n")
        return

    app.write(f"[green]Configured Providers ({len(providers)}):[/green]\n\n")

    for p in providers:
        provider_id = p.get('id', 'unknown')
        provider_name = p.get('name', provider_id)
        has_key = p.get('has_key', False)
        model_count = p.get('model_count', 0)

        key_status = "[green]✓[/green]" if has_key else "[red]✗[/red]"

        app.write(f"  {key_status} [cyan]{provider_name}[/cyan] ({provider_id})\n")
        if model_count > 0:
            app.write(f"     [dim]{model_count} models available[/dim]\n")
        app.write("\n")

    app.write("[dim]Commands:[/dim]\n")
    app.write("[dim]  /model add-key <provider> <key>  - Add provider API key[/dim]\n")
    app.write("[dim]  /model providers                 - List available providers[/dim]\n")
    app.write("[dim]  /model list                      - List all models[/dim]\n\n")


async def provider_list(app, session, **context):
    """Alias for /providers list."""
    await provider_manage(app, session, **context)


def _get_model_manager():
    try:
        from model_manager import ModelManager
        return ModelManager()
    except (ImportError, ValueError):
        from .model_manager import ModelManager as LocalModelManager
        return LocalModelManager()


async def provider_add(app, session, **context):
    """Add or update an API key for a provider."""
    args = (context.get("args") or "").strip()
    if not args:
        app.write("[red]Usage:[/red] /providers add <provider> <api-key>\n\n")
        return

    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        app.write("[red]Usage:[/red] /providers add <provider> <api-key>\n\n")
        return

    provider_id, api_key = parts
    manager = _get_model_manager()
    manager.add_api_key(provider_id, api_key)
    app.write(f"[green]Saved API key for provider[/green] [cyan]{provider_id}[/cyan].\n\n")


async def provider_add_ollama(app, session, **context):
    """
    Configure Ollama as a provider (no API key needed).
    """
    manager = _get_model_manager()
    manager._set_active_provider("ollama")
    app.write("[green]Ollama configured as the active provider.[/green]\n")
    app.write("Make sure the Ollama server is running on this machine.\n\n")


async def provider_remove(app, session, **context):
    """Remove a stored provider API key."""
    provider_id = (context.get("args") or "").strip()
    if not provider_id:
        app.write("[red]Usage:[/red] /providers remove <provider>\n\n")
        return

    manager = _get_model_manager()
    keys = manager.models_db.get("api_keys", {})
    if provider_id in keys:
        del keys[provider_id]
        manager._save_models()
        app.write(f"[yellow]Removed stored API key for {provider_id}.[/yellow]\n\n")
    else:
        app.write(f"[dim]No API key stored for {provider_id}.[/dim]\n\n")
