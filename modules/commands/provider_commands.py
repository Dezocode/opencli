"""Provider Commands - SDK COMPLIANT

SDK-COMPLIANT: All commands use interactive permission buffer pages.
User interaction happens in buffer, handlers execute based on selections.
"""

from typing import Optional

# SDK-compliant imports only
from ..permission_prompt import PermissionResponse
from ..permission_buffer_manager import get_permission_buffer_manager


def _get_model_manager():
    """Helper to get ModelManager instance"""
    try:
        from model_manager import ModelManager
        return ModelManager()
    except (ImportError, ValueError):
        from modules.model_manager import ModelManager
        return ModelManager()


# ============================================================================
# /providers - Manage API providers
# ============================================================================

async def provider_manage_prompt(app, session, registration, context):
    """Interactive prompt for /providers command"""

    manager = _get_model_manager()
    providers = manager.get_providers()
    provider_count = len(providers)

    prompt_data = {
        'title': 'System: /providers',
        'message': f"""# Provider Management

**Total Providers:** {provider_count}
**Configured:** {', '.join([p.get('name', 'unknown') for p in providers[:3]])}{"..." if provider_count > 3 else ""} if providers else "None"

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

    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def provider_manage(app, session, **context):
    """Manage API providers - SDK COMPLIANT"""

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

    manager = _get_model_manager()
    providers = manager.get_providers()

    # Execute based on selection
    if action == 'view':
        app.write("[cyan]Provider Management[/cyan]\n\n")

        if not providers:
            app.write("[yellow]No providers configured yet[/yellow]\n\n")
            app.write("[dim]Use /providers add <provider> <key> to add a provider[/dim]\n\n")
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
        app.write("[dim]  /providers add <provider> <key>  - Add provider API key[/dim]\n")
        app.write("[dim]  /model providers                 - List available providers[/dim]\n")
        app.write("[dim]  /model list                      - List all models[/dim]\n\n")

    elif action == 'export':
        from pathlib import Path
        export_path = Path.cwd() / "opencli-providers.txt"
        with open(export_path, 'w') as f:
            f.write("OpenCLI Provider Management\n")
            f.write("=" * 40 + "\n\n")
            for p in providers:
                provider_id = p.get('id', 'unknown')
                provider_name = p.get('name', provider_id)
                has_key = p.get('has_key', False)
                model_count = p.get('model_count', 0)
                f.write(f"{provider_name} ({provider_id})\n")
                f.write(f"  Has Key: {'YES' if has_key else 'NO'}\n")
                f.write(f"  Models: {model_count}\n\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# ============================================================================
# /providers list - Alias for /providers
# ============================================================================

async def provider_list_prompt(app, session, registration, context):
    """Interactive prompt for /providers list command"""
    # Use same prompt as provider_manage
    return await provider_manage_prompt(app, session, registration, context)


async def provider_list(app, session, **context):
    """Alias for /providers list - SDK COMPLIANT"""
    await provider_manage(app, session, **context)


# ============================================================================
# /providers add - Add or update provider API key
# ============================================================================

async def provider_add_prompt(app, session, registration, context):
    """Interactive prompt for /providers add command"""

    args = (context.get("args") or "").strip()
    if not args:
        return None  # Will show error in handler

    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        return None  # Will show error in handler

    provider_id, api_key = parts

    # Mask API key for display (show first 8 chars)
    masked_key = api_key[:8] + "..." if len(api_key) > 8 else "***"

    manager = _get_model_manager()
    existing_keys = manager.models_db.get("api_keys", {})
    is_update = provider_id in existing_keys

    prompt_data = {
        'title': 'System: /providers add',
        'message': f"""# Add Provider API Key

**Provider:** {provider_id}
**Current Status:** {'Key exists (will update)' if is_update else 'No key (will add)'}
**New Key:** {masked_key}

**Confirm action:**""",
        'options': [
            {
                'text': f'{"Update" if is_update else "Add"} API key for {provider_id}',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'add', 'provider_id': provider_id, 'api_key': api_key, 'is_update': is_update}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }

    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def provider_add(app, session, **context):
    """Add or update an API key for a provider - SDK COMPLIANT"""

    args = (context.get("args") or "").strip()
    if not args:
        app.write("[red]Usage:[/red] /providers add <provider> <api-key>\n\n")
        return

    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        app.write("[red]Usage:[/red] /providers add <provider> <api-key>\n\n")
        return

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

    # Execute - add provider
    provider_id = user_selection.get('provider_id')
    api_key = user_selection.get('api_key')
    is_update = user_selection.get('is_update', False)

    manager = _get_model_manager()
    manager.add_api_key(provider_id, api_key)
    action_text = "Updated" if is_update else "Saved"
    app.write(f"[green]{action_text} API key for provider[/green] [cyan]{provider_id}[/cyan].\n\n")


# ============================================================================
# /providers add ollama - Configure Ollama provider
# ============================================================================

async def provider_add_ollama_prompt(app, session, registration, context):
    """Interactive prompt for /providers add ollama command"""

    prompt_data = {
        'title': 'System: /providers add ollama',
        'message': """# Configure Ollama Provider

**Provider:** Ollama (local)
**API Key:** Not required (local server)
**Requirements:** Ollama server must be running

**Confirm action:**""",
        'options': [
            {
                'text': 'Configure Ollama as active provider',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'configure'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }

    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def provider_add_ollama(app, session, **context):
    """Configure Ollama as a provider - SDK COMPLIANT"""

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

    # Execute - configure Ollama
    manager = _get_model_manager()
    manager._set_active_provider("ollama")
    app.write("[green]✓ Ollama configured as the active provider.[/green]\n")
    app.write("Make sure the Ollama server is running on this machine.\n\n")


# ============================================================================
# /providers remove - Remove provider API key
# ============================================================================

async def provider_remove_prompt(app, session, registration, context):
    """Interactive prompt for /providers remove command"""

    provider_id = (context.get("args") or "").strip()
    if not provider_id:
        return None  # Will show error in handler

    manager = _get_model_manager()
    keys = manager.models_db.get("api_keys", {})

    if provider_id not in keys:
        return None  # Will show error in handler

    prompt_data = {
        'title': 'System: /providers remove',
        'message': f"""# Remove Provider API Key

**Provider:** {provider_id}
**Action:** Permanently remove stored API key

**Warning:** You will need to re-add the key to use this provider again!

**Affected:**
- API key for {provider_id}
- Access to models from this provider
- Provider configuration

**Confirm removal:**""",
        'options': [
            {
                'text': f'Yes, remove API key for {provider_id}',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'remove', 'provider_id': provider_id, 'confirmed': True}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }

    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)


async def provider_remove(app, session, **context):
    """Remove a stored provider API key - SDK COMPLIANT"""

    provider_id = (context.get("args") or "").strip()
    if not provider_id:
        app.write("[red]Usage:[/red] /providers remove <provider>\n\n")
        return

    manager = _get_model_manager()
    keys = manager.models_db.get("api_keys", {})

    if provider_id not in keys:
        app.write(f"[dim]No API key stored for {provider_id}.[/dim]\n\n")
        return

    # Get user selection
    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')
    confirmed = user_selection.get('confirmed', False)

    if not action or not confirmed:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    # Execute - remove provider
    del keys[provider_id]
    manager._save_models()
    app.write(f"[green]✓ Removed stored API key for {provider_id}.[/green]\n\n")
