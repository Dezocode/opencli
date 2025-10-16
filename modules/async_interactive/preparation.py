"""
Message Preparation System
Builds system context with constitution, agents, goals, spec, etc.
Port from dev6 for the refactored architecture
"""

import asyncio
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


async def build_system_context(
    session,
    config: Dict[str, Any],
    agent_manager=None,
    spec_memory=None,
    goal_tracker=None
) -> str:
    """Build comprehensive system context (dev6 pattern)

    Args:
        session: Session object
        config: Configuration dict
        agent_manager: Optional AgentManager instance
        spec_memory: Optional SpecMemory instance
        goal_tracker: Optional GoalTracker instance

    Returns:
        System context string with all relevant information
    """
    system_parts = []

    # 1. Constitution
    constitution = await load_constitution()
    if constitution:
        system_parts.append("# OpenCLI Constitution\n\n" + constitution)

    # 2. Agent context
    if agent_manager and hasattr(session, 'current_agent') and session.current_agent:
        agent_context = await load_agent_context(session.current_agent)
        if agent_context:
            system_parts.append(f"# Active Agent: {session.current_agent}\n\n{agent_context}")

    # 3. Spec context
    if spec_memory:
        spec_context = await load_spec_context(spec_memory)
        if spec_context:
            system_parts.append("# Specification Context\n\n" + spec_context)

    # 4. Goals
    if goal_tracker:
        goals_context = await load_goals_context(goal_tracker)
        if goals_context:
            system_parts.append("# Current Goals\n\n" + goals_context)

    # 5. Working directory
    cwd = os.getcwd()
    system_parts.append(f"# Working Directory\n\n`{cwd}`")

    # 6. Tool definitions
    tools_context = await load_tools_context()
    if tools_context:
        system_parts.append("# Available Tools\n\n" + tools_context)

    return "\n\n---\n\n".join(system_parts)


async def load_constitution() -> Optional[str]:
    """Load constitution from ~/.opencli/CONSTITUTION.md"""
    try:
        constitution_path = Path.home() / ".opencli" / "CONSTITUTION.md"
        if constitution_path.exists():
            async def read_file():
                with open(constitution_path) as f:
                    return f.read()
            return await asyncio.to_thread(read_file)
    except Exception:
        return None


async def load_agent_context(agent_name: str) -> Optional[str]:
    """Load AGENTS.md content for active agent"""
    try:
        agents_path = Path.cwd() / "AGENTS.md"
        if agents_path.exists():
            async def read_file():
                with open(agents_path) as f:
                    return f.read()
            return await asyncio.to_thread(read_file)
    except Exception:
        return None


async def load_spec_context(spec_memory) -> Optional[str]:
    """Load spec context from SpecMemory"""
    try:
        if hasattr(spec_memory, 'get_active_spec'):
            spec = spec_memory.get_active_spec()
            if spec:
                return f"**Spec**: {spec.get('description', 'N/A')}"
    except Exception:
        return None


async def load_goals_context(goal_tracker) -> Optional[str]:
    """Load goals from GoalTracker"""
    try:
        if hasattr(goal_tracker, 'get_active_goals'):
            goals = goal_tracker.get_active_goals()
            if goals:
                return "\n".join([f"- {g}" for g in goals])
    except Exception:
        return None


async def load_tools_context() -> Optional[str]:
    """Load tool definitions"""
    try:
        from .tools import TOOLS
        if TOOLS:
            tool_list = []
            for tool in TOOLS:
                name = tool.get('name', 'unknown')
                desc = tool.get('description', 'No description')
                tool_list.append(f"- **{name}**: {desc}")
            return "\n".join(tool_list)
    except Exception:
        return None
