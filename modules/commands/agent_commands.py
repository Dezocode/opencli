"""
Agent-related command handlers.

These commands interact with the AgentManager to list and switch between
configured agents. When agent definitions are missing, graceful fallbacks
notify the user instead of raising.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from agent_manager import AgentManager


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


async def list_agents(app, session, **context):
    """Show all available agents with their status."""
    agent_manager = _load_agent_manager(session)
    if not agent_manager:
        app.write("[red]Agent system is not configured on this installation.[/red]\n\n")
        return

    current = getattr(session, "current_agent", agent_manager.default_agent)
    app.write("[bold cyan]Available Agents[/bold cyan]\n")
    for name, agent in sorted(agent_manager.agents.items()):
        indicator = "[green]✓[/green]" if name == current else "[dim]•[/dim]"
        description = agent.system_prompt.splitlines()[0] if agent.system_prompt else ""
        app.write(f"  {indicator} [cyan]{name}[/cyan]")
        if description:
            app.write(f" - {description}")
        app.write("\n")
    app.write("\nUse `/agent <name>` to switch agents.\n\n")


async def set_agent(app, session, agent_name: str):
    """Shared helper to switch the active agent."""
    agent_manager = _load_agent_manager(session)
    if not agent_manager:
        app.write("[red]Agent system is not configured on this installation.[/red]\n\n")
        return

    agent_name = agent_name.lower()
    if agent_name not in agent_manager.agents:
        app.write(f"[red]Unknown agent:[/red] {agent_name}\n")
        app.write("Use `/agents` to list available agents.\n\n")
        return

    session.current_agent = agent_name
    app.write(f"[green]Active agent set to[/green] [cyan]{agent_name}[/cyan]\n\n")


async def agent_main(app, session, **context):
    """Handle `/agent` with optional argument inside context."""
    args = (context.get("args") or "").strip()
    if not args:
        await list_agents(app, session)
        return
    await set_agent(app, session, args)


async def agent_assistant(app, session, **context):
    await set_agent(app, session, "assistant")


async def agent_debugger(app, session, **context):
    await set_agent(app, session, "debugger")


async def agent_reviewer(app, session, **context):
    await set_agent(app, session, "reviewer")


async def agent_refactor(app, session, **context):
    await set_agent(app, session, "refactor")


async def agent_tester(app, session, **context):
    await set_agent(app, session, "tester")


async def agent_documenter(app, session, **context):
    await set_agent(app, session, "documenter")


async def agent_architect(app, session, **context):
    await set_agent(app, session, "architect")
