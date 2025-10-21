"""
Agent-related command handlers.

SDK-COMPLIANT: All commands use interactive permission buffer pages.
User interaction happens in buffer, handlers execute based on selections.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ..agent_manager import AgentManager

# SDK-compliant imports only
from ..permission_prompt import PermissionResponse


def _load_agent_manager(session) -> Optional[AgentManager]:
    """Best-effort AgentManager creation (mirrors default config path)."""
    config_dir = getattr(session, "config_dir", None)
    if config_dir is None:
        config_dir = Path.home() / ".opencli"

    try:
        return AgentManager(Path(config_dir))
    except Exception as exc:
        print(f"[AgentCommands] Failed to load AgentManager: {exc}")
        return None


# ============================================================================ 
# /agents - List available agents
# ============================================================================ 

def list_agents_prompt(app, session, registration, context):
    """Interactive prompt for /agents command"""

    agent_manager = _load_agent_manager(session)
    if not agent_manager:
        return None  # Will be handled in main handler

    current = getattr(session, "current_agent", agent_manager.default_agent)
    agent_names = sorted(agent_manager.agents.keys())
    agent_count = len(agent_names)

    prompt_data = {
        'title': 'System: /agents',
        'message': f"""# Available Agents

**Total Agents:** {agent_count}
**Current Agent:** {current}
**Available:** {', '.join(agent_names[:4])}{"..." if agent_count > 4 else ""}

**Select action:**""",
        'options': [
            {
                'text': 'View all agents',
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


async def list_agents(app, session, **context):
    """Show all available agents with their status - SDK COMPLIANT"""

    agent_manager = _load_agent_manager(session)
    if not agent_manager:
        app.write("[red]Agent system is not configured on this installation.[/red]\n\n")
        return

    prompt_data = context.get('_custom_prompt_data', {})
    if not prompt_data:
        app.write("[yellow]No selection made[/yellow]\n")
        return

    user_selection = prompt_data.get('data', {})
    action = user_selection.get('action')

    if not action:
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    current = getattr(session, "current_agent", agent_manager.default_agent)

    if action == 'view':
        app.write("[bold cyan]Available Agents[/bold cyan]\n")
        for name, agent in sorted(agent_manager.agents.items()):
            indicator = "[green]✓[/green]" if name == current else "[dim]•[/dim]"
            description = agent.system_prompt.splitlines()[0] if agent.system_prompt else ""
            app.write(f"  {indicator} [cyan]{name}[/cyan]")
            if description:
                app.write(f" - {description}")
            app.write("\n")
        app.write("\nUse `/agent <name>` to switch agents.\n\n")

    elif action == 'export':
        export_path = Path.cwd() / "opencli-agents.txt"
        with open(export_path, 'w') as f:
            f.write("OpenCLI Available Agents\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Current Agent: {current}\n\n")
            for name, agent in sorted(agent_manager.agents.items()):
                f.write(f"{name}\n")
                description = agent.system_prompt.splitlines()[0] if agent.system_prompt else ""
                if description:
                    f.write(f"  {description}\n")
                f.write("\n")
        app.write(f"[green]✓ Exported to {export_path}[/green]\n")


# ============================================================================ 
# /agent - Switch to specific agent
# ============================================================================ 

def set_agent_prompt(app, session, registration, context):
    """Interactive prompt for /agent command"""

    agent_manager = _load_agent_manager(session)
    if not agent_manager:
        return None

    agent_name = context.get('args', '').strip().lower()
    if not agent_name:
        reg_name = registration.name if hasattr(registration, 'name') else ''
        if reg_name.startswith('/agent-'):
            agent_name = reg_name.replace('/agent-', '')

    if not agent_name or agent_name not in agent_manager.agents:
        return None

    current = getattr(session, "current_agent", agent_manager.default_agent)

    if current == agent_name:
        return None

    current_agent = agent_manager.agents.get(current)
    new_agent = agent_manager.agents.get(agent_name)
    current_desc = current_agent.system_prompt.splitlines()[0] if current_agent and current_agent.system_prompt else "Default assistant"
    new_desc = new_agent.system_prompt.splitlines()[0] if new_agent and new_agent.system_prompt else "Default assistant"

    prompt_data = {
        'title': 'System: /agent',
        'message': f"""# Switch Agent

**Current Agent:** {current}
{current_desc}

**New Agent:** {agent_name}
{new_desc}

**Confirm switch:**""",
        'options': [
            {
                'text': f'Yes, switch to {agent_name}',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {'action': 'switch', 'agent_name': agent_name}
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }
    return prompt_data


async def set_agent(app, session, agent_name: str):
    """Shared helper to switch the active agent - SDK COMPLIANT"""

    agent_manager = _load_agent_manager(session)
    if not agent_manager:
        app.write("[red]Agent system is not configured on this installation.[/red]\n\n")
        return

    agent_name = agent_name.lower()
    if agent_name not in agent_manager.agents:
        app.write(f"[red]Unknown agent:[/red] {agent_name}\n")
        app.write("Use `/agents` to list available agents.\n\n")
        return

    current = getattr(session, "current_agent", agent_manager.default_agent)

    if current == agent_name:
        app.write(f"[yellow]Already using agent[/yellow] [cyan]{agent_name}[/cyan]\n\n")
        return

    session.current_agent = agent_name
    app.write(f"[green]✓ Active agent set to[/green] [cyan]{agent_name}[/cyan]\n\n")


# ============================================================================ 
# /agent - Main agent command (with optional args)
# ============================================================================ 

def agent_main_prompt(app, session, registration, context):
    """Interactive prompt for /agent command - delegates to list or set"""
    args = context.get('args', '').strip()
    if not args:
        return list_agents_prompt(app, session, registration, context)
    else:
        return set_agent_prompt(app, session, registration, context)


async def agent_main(app, session, **context):
    """Handle `/agent` with optional argument inside context."""
    args = (context.get("args") or "").strip()
    if not args:
        await list_agents(app, session, **context)
        return
    await set_agent(app, session, args)


# ============================================================================ 
# Specific agent commands - each with their own prompt function
# ============================================================================ 

def agent_assistant_prompt(app, session, registration, context):
    """Prompt for /agent assistant command"""
    context = {**context, 'args': 'assistant'}
    return set_agent_prompt(app, session, registration, context)


async def agent_assistant(app, session, **context):
    await set_agent(app, session, "assistant")

def agent_debugger_prompt(app, session, registration, context):
    """Prompt for /agent debugger command"""
    context = {**context, 'args': 'debugger'}
    return set_agent_prompt(app, session, registration, context)


async def agent_debugger(app, session, **context):
    await set_agent(app, session, "debugger")

def agent_reviewer_prompt(app, session, registration, context):
    """Prompt for /agent reviewer command"""
    context = {**context, 'args': 'reviewer'}
    return set_agent_prompt(app, session, registration, context)


async def agent_reviewer(app, session, **context):
    await set_agent(app, session, "reviewer")

def agent_refactor_prompt(app, session, registration, context):
    """Prompt for /agent refactor command"""
    context = {**context, 'args': 'refactor'}
    return set_agent_prompt(app, session, registration, context)


async def agent_refactor(app, session, **context):
    await set_agent(app, session, "refactor")

def agent_tester_prompt(app, session, registration, context):
    """Prompt for /agent tester command"""
    context = {**context, 'args': 'tester'}
    return set_agent_prompt(app, session, registration, context)


async def agent_tester(app, session, **context):
    await set_agent(app, session, "tester")

def agent_documenter_prompt(app, session, registration, context):
    """Prompt for /agent documenter command"""
    context = {**context, 'args': 'documenter'}
    return set_agent_prompt(app, session, registration, context)


async def agent_documenter(app, session, **context):
    await set_agent(app, session, "documenter")

def agent_architect_prompt(app, session, registration, context):
    """Prompt for /agent architect command"""
    context = {**context, 'args': 'architect'}
    return set_agent_prompt(app, session, registration, context)


async def agent_architect(app, session, **context):
    await set_agent(app, session, "architect")
