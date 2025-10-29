"""Model Commands - SDK COMPLIANT

SDK-COMPLIANT: All commands use interactive permission buffer pages.
User interaction happens in buffer, handlers execute based on selections.
"""

# SDK-compliant imports only
from modules.permissions import PermissionResponse
# Legacy import removed - using unified_permission_manager via SDK executor


# ============================================================================
# /model list - List available models
# ============================================================================

def model_list_prompt(app, session, registration, context):
    """Interactive prompt for /model list command"""

    # Import model manager
    try:
        from modules.model_manager import ModelManager
    except:
        import importlib
        model_mgr = importlib.import_module('model_manager')
        ModelManager = model_mgr.ModelManager

    model_manager = ModelManager()
    models = model_manager.list_available_models()
    model_count = len(models) if models else 0

    prompt_data = {
        'title': 'System: /model list',
        'message': f"""# Available Models

**Total Models:** {model_count}
**Status:** {'No models configured' if model_count == 0 else f'{model_count} models available'}

**Select action:**""",
        'options': [
            {
                'text': 'View all models',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'view'}
            },
            {
                'text': 'Export to file',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'export'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def model_list(app, session, **context):
    """List available models - SDK COMPLIANT"""

    # Get user selection
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    # Import model manager
    try:
        from modules.model_manager import ModelManager
    except:
        import importlib
        model_mgr = importlib.import_module('model_manager')
        ModelManager = model_mgr.ModelManager

    model_manager = ModelManager()
    models = model_manager.list_available_models()

    # Execute based on selection
    if action == 'view':
        app.write("[cyan]Available Models:[/cyan]\n\n")

        if not models:
            app.write("[yellow]No models configured. Add an API key first:[/yellow]\n")
            app.write("[dim]  /providers add <provider> <api-key>[/dim]\n\n")
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

    elif action == 'export':
        from pathlib import Path
        export_path = Path.cwd() / "opencli-models.txt"
        with open(export_path, 'w') as f:
            f.write("OpenCLI Available Models\n")
            f.write("=" * 40 + "\n\n")
            for model in models:
                model_id = model.get('id', 'unknown')
                model_name = model.get('name', model_id)
                provider = model.get('provider', 'unknown')
                f.write(f"{model_id}\n")
                f.write(f"  Name: {model_name}\n")
                f.write(f"  Provider: {provider}\n\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# ============================================================================
# /model switch - Switch to specific model
# ============================================================================

def model_switch_prompt(app, session, registration, context):
    """Interactive prompt for /model switch command"""

    # Get model ID from args
    model_id = context.get('args', '').strip()
    if not model_id:
        return None  # Will show error in handler

    # Get current model
    current_model = getattr(session, 'model', getattr(session, 'current_model', 'unknown'))

    prompt_data = {
        'title': 'System: /model switch',
        'message': f"""# Switch Model

**Current Model:** {current_model}
**New Model:** {model_id}

**Confirm switch:**""",
        'options': [
            {
                'text': f'Yes, switch to {model_id}',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'switch', 'model_id': model_id}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def model_switch(app, session, model_name=None, **context):
    """Switch to a specific model - SDK COMPLIANT"""

    # Get model ID from parameter or args
    if model_name is None:
        model_name = context.get('model_name', context.get('args', ''))

    model_id = model_name

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

    # Execute - switch model (permission already checked via custom_prompt_func)
    switch_result = model_manager.switch_model(session, model_id)

    if switch_result.get('success'):
        model_name_display = switch_result.get('model', model_id)
        app.write(f"[green]✓ Switched to {model_name_display}[/green]\n\n")

        # Show pricing if available
        if 'pricing' in switch_result:
            pricing = switch_result['pricing']
            prompt_cost = pricing.get('prompt', '?')
            completion_cost = pricing.get('completion', '?')
            app.write(f"[dim]Pricing: ${prompt_cost}/1M input, ${completion_cost}/1M output[/dim]\n\n")
    else:
        error = switch_result.get('error', 'Unknown error')
        app.write(f"[red]✗ Failed to switch model: {error}[/red]\n\n")


# ============================================================================
# /model providers - List registered providers
# ============================================================================

def model_list_providers_prompt(app, session, registration, context):
    """Interactive prompt for /model providers command"""

    try:
        from modules.model_manager import ModelManager
    except:
        import importlib
        model_mgr = importlib.import_module('model_manager')
        ModelManager = model_mgr.ModelManager

    manager = ModelManager()
    providers = manager.get_providers()
    provider_count = len(providers)

    prompt_data = {
        'title': 'System: /model providers',
        'message': f"""# Configured Providers

**Total Providers:** {provider_count}
**Configured:** {', '.join([p['name'] for p in providers[:3]])}{"..." if provider_count > 3 else ""}

**Select action:**""",
        'options': [
            {
                'text': 'View all providers',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'view'}
            },
            {
                'text': 'Export to file',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'export'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def model_list_providers(app, session, **context):
    """List registered providers - SDK COMPLIANT"""

    # Get user selection
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    try:
        from modules.model_manager import ModelManager
    except:
        import importlib
        model_mgr = importlib.import_module('model_manager')
        ModelManager = model_mgr.ModelManager

    manager = ModelManager()
    providers = manager.get_providers()

    # Execute based on selection
    if action == 'view':
        app.write("[bold cyan]Configured Providers[/bold cyan]\n")
        for provider in providers:
            status = "[green]✓ key[/green]" if provider.get("has_key") else "[yellow]○ no key[/yellow]"
            models = provider.get("model_count", 0)
            app.write(f"  {status} [cyan]{provider['name']}[/cyan] ({models} models cached)\n")
        app.write("\nUse `/providers` commands to manage API keys.\n\n")

    elif action == 'export':
        from pathlib import Path
        export_path = Path.cwd() / "opencli-providers.txt"
        with open(export_path, 'w') as f:
            f.write("OpenCLI Configured Providers\n")
            f.write("=" * 40 + "\n\n")
            for provider in providers:
                has_key = "YES" if provider.get("has_key") else "NO"
                models = provider.get("model_count", 0)
                f.write(f"{provider['name']}\n")
                f.write(f"  Has Key: {has_key}\n")
                f.write(f"  Cached Models: {models}\n\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# ============================================================================
# /model r1, /model r2 - Switch to recent models
# ============================================================================

def model_switch_recent_prompt(app, session, registration, context):
    """Interactive prompt for /model r1 or /model r2 commands"""

    # Determine index from registration name or context
    reg_name = registration.name if hasattr(registration, 'name') else ''
    if 'r1' in reg_name:
        index = 0
    elif 'r2' in reg_name:
        index = 1
    else:
        index = context.get('index', 0)

    try:
        from modules.model_manager import ModelManager
    except:
        import importlib
        model_mgr = importlib.import_module('model_manager')
        ModelManager = model_mgr.ModelManager

    manager = ModelManager()
    recent = manager.get_recent_models()

    if not recent or index >= len(recent):
        return None  # Will show error in handler

    model_id = recent[index].get("id")
    if not model_id:
        return None  # Will show error in handler

    # Get current model
    current_model = getattr(session, 'model', getattr(session, 'current_model', 'unknown'))

    prompt_data = {
        'title': f'System: /model r{index+1}',
        'message': f"""# Switch to Recent Model

**Current Model:** {current_model}
**Recent Model #{index+1}:** {model_id}

**Confirm switch:**""",
        'options': [
            {
                'text': f'Yes, switch to {model_id}',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'switch', 'model_id': model_id}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def model_switch_recent(app, session, index: int):
    """Switch to a recent model by index - SDK COMPLIANT"""

    try:
        from modules.model_manager import ModelManager
    except:
        import importlib
        model_mgr = importlib.import_module('model_manager')
        ModelManager = model_mgr.ModelManager

    manager = ModelManager()
    recent = manager.get_recent_models()

    if not recent or index >= len(recent):
        app.write("[yellow]No recent models recorded for this session yet.[/yellow]\n\n")
        return

    model_id = recent[index].get("id")
    if not model_id:
        app.write("[red]Recent model entry was missing an ID.[/red]\n\n")
        return

    # Execute - switch to recent model (permission already checked via custom_prompt_func)
    await model_switch(app, session, model_name=model_id)


async def model_switch_recent_1(app, session, **context):
    """Switch to most recent model - SDK COMPLIANT"""
    await model_switch_recent(app, session, 0)


async def model_switch_recent_2(app, session, **context):
    """Switch to 2nd most recent model - SDK COMPLIANT"""
    await model_switch_recent(app, session, 1)


# Aliases for registry compatibility (both r1 and r2 use the same prompt function)
model_switch_recent_1_prompt = model_switch_recent_prompt
model_switch_recent_2_prompt = model_switch_recent_prompt
