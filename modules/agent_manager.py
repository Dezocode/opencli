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

try:
    from context_builder import ContextBuilder
    HAS_CONTEXT_BUILDER = True
except ImportError:
    HAS_CONTEXT_BUILDER = False


class AgentConfig:
    """Represents an agent configuration from YAML or AGENTS.md"""

    def __init__(self, name: str, config: Dict):
        self.name = name
        self.system_prompt = config.get('system_prompt', '')
        self.instructions = config.get('instructions', [])
        self.tools = config.get('tools', [])
        self.context_strategy = config.get('context_strategy', 'auto')
        self.max_context_tokens = config.get('max_context_tokens', 100000)
        self.priority = config.get('priority', 0)
        self.triggers = config.get('triggers', [])
        self.examples = config.get('examples', [])

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

        # Initialize context builder if available
        self.context_builder = None
        if HAS_CONTEXT_BUILDER:
            try:
                self.context_builder = ContextBuilder(config_dir)
            except Exception as e:
                print(f"Warning: ContextBuilder initialization failed: {e}")

        self.load_agents()
        self._context_cache = {}  # Cache compiled contexts per session

    def load_agents(self):
        """Load agent configurations from YAML files"""
        # Try new location first (agents/configs/agents.yaml)
        agents_config_file = self.config_dir / 'agents' / 'configs' / 'agents.yaml'

        # Fallback to old location for backwards compatibility
        if not agents_config_file.exists():
            agents_config_file = self.config_dir / 'agents.yaml'

        if agents_config_file.exists():
            with open(agents_config_file) as f:
                config = yaml.safe_load(f)
                for agent_name, agent_config in config.get('agents', {}).items():
                    self.agents[agent_name] = AgentConfig(agent_name, agent_config)

        # Load custom agents from agents/configs/custom/
        custom_dir = self.config_dir / 'agents' / 'configs' / 'custom'
        if custom_dir.exists():
            for custom_file in custom_dir.glob('*.yaml'):
                try:
                    with open(custom_file) as f:
                        config = yaml.safe_load(f)
                        for agent_name, agent_config in config.get('agents', {}).items():
                            self.agents[agent_name] = AgentConfig(agent_name, agent_config)
                except Exception as e:
                    print(f"Warning: Failed to load custom agent config {custom_file}: {e}")

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

        # Check if we already have a system message with context for this session/agent
        cache_key = f"{session_id}_{agent_name}" if session_id else agent_name
        has_system_message = any(m.get('role') == 'system' for m in messages)

        # Only build context if:
        # 1. No system message exists yet
        # 2. Context not cached for this session
        # 3. Agent switched
        if not has_system_message or cache_key not in self._context_cache:
            if self.context_builder:
                # Use optimized context builder with caching
                compiled_context, was_cached = self.context_builder.build_context(
                    agent_name,
                    agent.system_prompt,
                    working_dir or os.getcwd()
                )

                if was_cached:
                    print(f"\033[2m[Using cached context]\033[0m")
            else:
                # Fallback to old method
                project_context = {
                    'working_dir': working_dir or os.getcwd()
                }
                agents_md = self.find_agents_md(working_dir)
                if agents_md:
                    project_context['agents_md'] = agents_md

                compiled_context = agent.build_system_message(project_context)

            # Cache the compiled context for this session
            self._context_cache[cache_key] = compiled_context

            # Build system message
            system_message = {
                'role': 'system',
                'content': self._context_cache[cache_key]
            }

            # Remove old system messages and add new one
            non_system = [m for m in messages if m.get('role') != 'system']
            all_messages = [system_message] + non_system
        else:
            # System message already exists, don't re-inject
            all_messages = messages

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
