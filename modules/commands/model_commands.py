"""Model Commands"""

async def model_list(app, session, **context):
    """List available models"""
    # Import model manager
    try:
        from modules.model_manager import ModelManager
    except:
        import importlib
        model_mgr = importlib.import_module('model_manager')
        ModelManager = model_mgr.ModelManager
    
    model_manager = ModelManager()
    models = model_manager.list_available_models()

    app.write("[cyan]Available Models:[/cyan]\n\n")

    if not models:
        app.write("[yellow]No models configured. Add an API key first:[/yellow]\n")
        app.write("[dim]  /model add-key <provider> <api-key>[/dim]\n\n")
        return

    for model in models:
        model_id = model.get('id', 'unknown')
        model_name = model.get('name', model_id)
        provider = model.get('provider', 'unknown')

        app.write(f"  [cyan]{model_id}[/cyan]\n")
        if model_name != model_id:
            app.write(f"     [dim]{model_name} ({provider})[/dim]\n")
        else:
            app.write(f"     [dim]({provider})[/dim]\n")
    app.write("\n")

async def model_switch(app, session, **context):
    """Switch to a specific model"""
    model_id = context.get('model_name', context.get('args', ''))

    if not model_id or not isinstance(model_id, str):
        app.write("[red]✗ Please specify a model ID[/red]\n")
        app.write("[dim]Usage: /model switch <model-id>[/dim]\n\n")
        return

    # Import model manager
    try:
        from modules.model_manager import ModelManager
    except:
        import importlib
        model_mgr = importlib.import_module('model_manager')
        ModelManager = model_mgr.ModelManager

    model_manager = ModelManager()
    result = model_manager.switch_model(session, model_id)

    if result.get('success'):
        model_name = result.get('model', model_id)
        app.write(f"[green]✓ Switched to {model_name}[/green]\n\n")

        # Show pricing if available
        if 'pricing' in result:
            pricing = result['pricing']
            prompt_cost = pricing.get('prompt', '?')
            completion_cost = pricing.get('completion', '?')
            app.write(f"[dim]Pricing: ${prompt_cost}/1M input, ${completion_cost}/1M output[/dim]\n\n")
    else:
        error = result.get('error', 'Unknown error')
        app.write(f"[red]✗ Failed to switch model: {error}[/red]\n\n")
