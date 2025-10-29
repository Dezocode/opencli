"""Local Commands - SDK COMPLIANT

SDK-COMPLIANT: All commands use interactive permission buffer pages.
User interaction happens in buffer, handlers execute based on selections.
"""

# SDK-compliant imports only
from modules.permissions import PermissionResponse
# Legacy import removed - using unified_permission_manager via SDK executor


# ============================================================================
# /local - Local model setup
# ============================================================================

def local_setup_prompt(app, session, registration, context):
    """Interactive prompt for /local command"""

    prompt_data = {
        'title': 'System: /local',
        'message': """# Local Model Setup

**Estimated Duration:** < 1 minute

**Workflow Steps:**
1. Check for Ollama installation
2. Verify Docker availability
3. Configure local model provider
4. Test local model connection

**Status:** Workflow not fully implemented yet

**Select action:**""",
        'options': [
            {
                'text': 'Run local setup workflow',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'setup'}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def local_setup(app, session, **context):
    """Local model setup - SDK COMPLIANT"""

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

    # Execute - local setup workflow
    app.write("[cyan]Local Model Setup[/cyan]\n\n")
    app.write("Checking for Ollama...\n")
    app.write("[yellow]⚠ Local setup workflow not fully implemented yet[/yellow]\n")
    app.write("[dim]Use /docker ollama setup for Docker-based local models[/dim]\n\n")
