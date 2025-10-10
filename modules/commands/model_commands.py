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
    models = model_manager.get_available_models()
    
    app.write("[cyan]Available Models:[/cyan]\n\n")
    for model in models:
        app.write(f"  {model}\n")
    app.write("\n")

async def model_switch(app, session, **context):
    """Switch to a specific model"""
    model_name = context.get('model_name', context.get('args', ''))
    # Import model manager
    try:
        from modules.model_manager import ModelManager
    except:
        import importlib
        model_mgr = importlib.import_module('model_manager')
        ModelManager = model_mgr.ModelManager
    
    model_manager = ModelManager()
    success = model_manager.switch_model(model_name)
    
    if success:
        app.write(f"[green]✓ Switched to {model_name}[/green]\n\n")
    else:
        app.write(f"[red]✗ Failed to switch to {model_name}[/red]\n\n")
