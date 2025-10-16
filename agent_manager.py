#!/usr/bin/env python3
"""
Agent Manager for OpenCLI
Implements agents.md specification with smart context management
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class AgentConfig:
    """Represents an agent configuration from YAML or AGENTS.md"""

    def __init__(self, name: str, config: Dict[str, any]):
        self.name = name
        # Fix: Explicitly handle dictionary get operations
        self.system_prompt = config.get('system_prompt', '') if config else ''
        self.instructions = config.get('instructions', []) if config else []
        self.tools = config.get('tools', []) if config else []
        self.context_strategy = config.get('context_strategy', 'auto') if config else 'auto'
        self.max_context_tokens = config.get('max_context_tokens', 100000) if config else 100000
        self.priority = config.get('priority', 0) if config else 0
        self.triggers = config.get('triggers', []) if config else []
        self.examples = config.get('examples', []) if config else []

    def matches_trigger(self, user_input: str) -> bool:
        """Check if user input matches any triggers"""
        user_lower = user_input.lower()
        for trigger in self.triggers:
            if trigger.lower() in user_lower:
                return True
        return False

    def build_system_message(self, project_context: Dict = None) -> str:
        """Build complete system prompt with project context"""
        parts = [self.system_prompt]

        if project_context:
            if 'agents_md' in project_context:
                parts.append(f"\n## Project Context\n{project_context['agents_md']}")
            if 'working_dir' in project_context:
                parts.append(f"\nWorking directory: {project_context['working_dir']}")

        if self.instructions:
            parts.append("\n## Instructions")
            for idx, instruction in enumerate(self.instructions, 1):
                parts.append(f"{idx}. {instruction}")

        if self.examples:
            parts.append("\n## Examples")
            for example in self.examples:
                parts.append(f"\n{example}")

        return '\n'.join(parts)


class ContextManager:
    """Manages context window with smart compression"""

    @staticmethod
    def count_tokens(messages: List[Dict]) -> int:
        """Estimate token count (4 chars per token)"""
        return sum(len(json.dumps(m)) // 4 for m in messages)

    @staticmethod
    def compress_context(messages: List[Dict], max_tokens: int, strategy: str = 'auto') -> List[Dict]:
        """
        Compress context using various strategies:
        - auto: Keep system + first + last N messages
        - sliding: Keep only last N messages
        - summary: Summarize middle messages (future)
        """
        current_tokens = ContextManager.count_tokens(messages)

        if current_tokens <= max_tokens * 0.8:
            return messages

        if strategy == 'sliding':
            # Keep only recent messages
            keep_count = 15
            return messages[-keep_count:]

        elif strategy == 'auto':
            # Keep system message(s), first user message, and recent messages
            system_msgs = [m for m in messages if m.get('role') == 'system']
            non_system = [m for m in messages if m.get('role') != 'system']

            if len(non_system) <= 10:
                return messages

            # Keep first 2 and last 10 non-system messages
            compressed = system_msgs + non_system[:2] + non_system[-10:]
            return compressed

        return messages

    @staticmethod
    def optimize_tool_results(messages: List[Dict]) -> List[Dict]:
        """Truncate excessively long tool results"""
        MAX_TOOL_RESULT = 5000  # chars

        optimized = []
        for msg in messages:
            if msg.get('role') == 'tool':
                content = msg.get('content', '')
                if len(content) > MAX_TOOL_RESULT:
                    # Keep first and last portions
                    truncated = (
                        content[:MAX_TOOL_RESULT//2] +
                        f"\n\n[... truncated {len(content) - MAX_TOOL_RESULT} chars ...]\n\n" +
                        content[-MAX_TOOL_RESULT//2:]
                    )
                    msg = {**msg, 'content': truncated}
            optimized.append(msg)

        return optimized


class AgentManager:
    """Manages multiple agents and routes requests"""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.agents: Dict[str, AgentConfig] = {}
        self.default_agent = 'assistant'
        self.context_manager = ContextManager()
        self.load_agents()

    def load_agents(self):
        """Load agent configurations from YAML files"""
        agents_config_file = self.config_dir / 'agents.yaml'

        if agents_config_file.exists():
            with open(agents_config_file) as f:
                config = yaml.safe_load(f)
                for agent_name, agent_config in config.get('agents', {}).items():
                    self.agents[agent_name] = AgentConfig(agent_name, agent_config)

        # Always ensure a default assistant agent exists
        if 'assistant' not in self.agents:
            self.agents['assistant'] = AgentConfig('assistant', {
                'system_prompt': 'You are a helpful AI coding assistant.',
                'context_strategy': 'auto',
                'max_context_tokens': 100000
            })

    def find_agents_md(self, working_dir: str = None) -> Optional[str]:
        """Find and read AGENTS.md file (closest to working dir)"""
        search_paths = []

        if working_dir:
            current = Path(working_dir)
            # Walk up directory tree
            for parent in [current] + list(current.parents):
                agents_file = parent / 'AGENTS.md'
                if agents_file.exists():
                    with open(agents_file) as f:
                        return f.read()

        # Fallback to current directory
        if Path('AGENTS.md').exists():
            with open('AGENTS.md') as f:
                return f.read()

        return None

    def select_agent(self, user_input: str, current_agent: str = None) -> str:
        """Select appropriate agent based on user input"""
        # Check for explicit agent selection via slash command
        if user_input.startswith('/agent '):
            requested = user_input.split()[1]
            if requested in self.agents:
                return requested

        # Check trigger-based selection
        matched_agents = []
        for name, agent in self.agents.items():
            if agent.matches_trigger(user_input):
                matched_agents.append((agent.priority, name))

        if matched_agents:
            # Return highest priority match
            matched_agents.sort(reverse=True)
            return matched_agents[0][1]

        # Continue with current agent or default
        return current_agent or self.default_agent

    def prepare_messages(
        self,
        agent_name: str,
        messages: List[Dict],
        working_dir: str = None,
        session_id: str = None
    ) -> List[Dict]:
        """Prepare optimized messages for agent with context management"""
        agent = self.agents.get(agent_name)
        if not agent:
            return messages

        # Build project context
        project_context = {
            'working_dir': working_dir or os.getcwd()
        }
        
        # Stash session_id for downstream components to access
        if session_id:
            project_context['session_id'] = session_id

        agents_md = self.find_agents_md(working_dir)
        if agents_md:
            project_context['agents_md'] = agents_md

        # Build system message
        system_message = {
            'role': 'system',
            'content': agent.build_system_message(project_context)
        }

        # Remove old system messages and add new one
        non_system = [m for m in messages if m.get('role') != 'system']
        all_messages = [system_message] + non_system

        # Optimize tool results
        all_messages = self.context_manager.optimize_tool_results(all_messages)

        # Compress context if needed
        compressed = self.context_manager.compress_context(
            all_messages,
            agent.max_context_tokens,
            agent.context_strategy
        )

        return compressed

    def get_agent_tools(self, agent_name: str, base_tools: List[Dict]) -> List[Dict]:
        """Get tools for specific agent (merge with base tools)"""
        agent = self.agents.get(agent_name)
        if not agent or not agent.tools:
            return base_tools

        # Agent can specify tool overrides or additions
        # For now, just return base tools
        return base_tools

    def list_agents(self) -> List[Tuple[str, str]]:
        """List all available agents"""
        return [(name, agent.system_prompt[:100]) for name, agent in self.agents.items()]
