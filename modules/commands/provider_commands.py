"""Provider Commands"""

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
