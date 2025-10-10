"""
Unified Execution Registry - Single registry for commands, tools, and APIs

Consolidates features from:
- CommandRegistry: search, usage tracking, enable/disable, categories
- ToolRegistry: tool registration and permissions
- CommandRouter: handler mapping
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class ExecutionType(Enum):
    """Type of executable item"""
    COMMAND = "command"
    TOOL = "tool"
    API = "api"


class ExecutionCategory(Enum):
    """Categories for organization"""
    # Command categories
    DOCKER = "docker"
    MODEL = "model"
    PROVIDER = "provider"
    DEV = "dev"
    REFACTOR = "refactor"
    SYSTEM = "system"
    SPEC = "spec"
    BASIC = "basic"

    # Tool categories
    FILE = "file"
    SEARCH = "search"
    BASH = "bash"
    NETWORK = "network"
    DATABASE = "database"

    # API categories
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class RiskLevel(Enum):
    """Risk levels for permission assessment"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ExecutionRegistration:
    """
    Registration info for command/tool/API

    Combines metadata from:
    - CommandRegistry (description, category, subcommands)
    - ToolPermission (risk, approval, background)
    - CommandPermission (resources, duration)
    """
    type: ExecutionType
    name: str
    handler: Callable
    category: ExecutionCategory
    risk_level: RiskLevel
    requires_approval: bool
    description: str

    # Execution behavior
    can_run_background: bool = False
    retry_on_failure: bool = False
    timeout: int = 120
    estimated_duration: str = "< 1 minute"

    # Command-specific
    subcommands: Dict[str, str] = field(default_factory=dict)
    requires_args: bool = False

    # Tool-specific
    resources_needed: List[str] = field(default_factory=list)

    # State
    enabled: bool = True
    usage_count: int = 0

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionRegistry:
    """
    Central registry for ALL commands, tools, and APIs

    Features:
    - Single registration point
    - Search and autocomplete
    - Usage tracking
    - Enable/disable control
    - Permission management
    """

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.registry_file = self.config_dir / "execution_registry.json"
        self.usage_file = self.config_dir / "execution_usage.json"

        # Registries
        self.commands: Dict[str, ExecutionRegistration] = {}
        self.tools: Dict[str, ExecutionRegistration] = {}
        self.apis: Dict[str, ExecutionRegistration] = {}

        # Load saved state
        self.usage_stats = self._load_usage_stats()
        self._load_registry_state()

    # ========================================================================
    # REGISTRATION
    # ========================================================================

    def register(
        self,
        type: ExecutionType,
        name: str,
        handler: Callable,
        category: ExecutionCategory,
        risk_level: RiskLevel,
        requires_approval: bool,
        description: str,
        **kwargs
    ) -> ExecutionRegistration:
        """
        Register command/tool/API

        Args:
            type: COMMAND, TOOL, or API
            name: Unique identifier
            handler: Execution function
            category: Organization category
            risk_level: Risk assessment
            requires_approval: Whether to show permission prompt
            description: Human-readable description
            **kwargs: Additional registration options

        Returns:
            ExecutionRegistration object
        """
        registration = ExecutionRegistration(
            type=type,
            name=name,
            handler=handler,
            category=category,
            risk_level=risk_level,
            requires_approval=requires_approval,
            description=description,
            **kwargs
        )

        # Store in appropriate registry
        if type == ExecutionType.COMMAND:
            self.commands[name] = registration
        elif type == ExecutionType.TOOL:
            self.tools[name] = registration
        elif type == ExecutionType.API:
            self.apis[name] = registration

        return registration

    def get(
        self,
        type: ExecutionType,
        name: str
    ) -> Optional[ExecutionRegistration]:
        """Get registration by type and name"""
        if type == ExecutionType.COMMAND:
            return self.commands.get(name)
        elif type == ExecutionType.TOOL:
            return self.tools.get(name)
        elif type == ExecutionType.API:
            return self.apis.get(name)
        return None

    def get_all(
        self,
        type: Optional[ExecutionType] = None,
        category: Optional[ExecutionCategory] = None,
        enabled_only: bool = False
    ) -> List[ExecutionRegistration]:
        """
        Get all registrations with optional filtering

        Args:
            type: Filter by COMMAND, TOOL, or API
            category: Filter by category
            enabled_only: Only return enabled items

        Returns:
            List of registrations
        """
        all_items = []

        if type is None or type == ExecutionType.COMMAND:
            all_items.extend(self.commands.values())
        if type is None or type == ExecutionType.TOOL:
            all_items.extend(self.tools.values())
        if type is None or type == ExecutionType.API:
            all_items.extend(self.apis.values())

        # Filter by category
        if category:
            all_items = [r for r in all_items if r.category == category]

        # Filter by enabled
        if enabled_only:
            all_items = [r for r in all_items if r.enabled]

        return all_items

    # ========================================================================
    # COMMAND SEARCH (from CommandRegistry)
    # ========================================================================

    def search_commands(
        self,
        query: str,
        limit: Optional[int] = None
    ) -> List[ExecutionRegistration]:
        """
        Search commands with priority-based ranking

        Search algorithm priority:
        1. Exact prefix match (score: 1000)
        2. Fuzzy match (score: 500)
        3. Description match (score: 250)
        4. Usage frequency (score: 0-100)

        Args:
            query: Search query (e.g., "/mo" or "/docker ollama")
            limit: Maximum number of results

        Returns:
            List of command registrations sorted by score
        """
        query = query.strip().lower()
        if not query.startswith('/'):
            query = f'/{query}'

        matches = []

        # Check if query contains a space (subcommand search)
        if ' ' in query:
            parts = query.split(maxsplit=1)
            base_cmd = parts[0]
            subquery = parts[1] if len(parts) > 1 else ''

            # Find the base command
            if base_cmd in self.commands:
                base_reg = self.commands[base_cmd]

                # Check if it has subcommands
                if base_reg.subcommands:
                    # Search subcommands
                    for subcmd, subdesc in base_reg.subcommands.items():
                        full_cmd = f"{base_cmd} {subcmd}"
                        subcmd_lower = subcmd.lower()

                        # Score the subcommand match
                        score = 0
                        if not subquery:
                            score = 1000  # No subquery - show all
                        elif subcmd_lower.startswith(subquery):
                            score = 1000  # Exact prefix
                        elif subquery in subcmd_lower:
                            score = 500  # Contains
                        elif subquery in subdesc.lower():
                            score = 250  # Description match

                        if score > 0:
                            # Create temporary registration for subcommand
                            matches.append({
                                'registration': base_reg,
                                'name': full_cmd,
                                'score': score
                            })

        # Regular base command search
        if not matches or ' ' not in query:
            for cmd, reg in self.commands.items():
                # Skip disabled commands
                if not reg.enabled:
                    continue

                # Calculate score
                score = self._score_match(cmd, reg.description, query, reg.usage_count)

                if score > 0:
                    matches.append({
                        'registration': reg,
                        'name': cmd,
                        'score': score
                    })

        # Sort by score (descending)
        matches.sort(key=lambda x: x['score'], reverse=True)

        if limit:
            matches = matches[:limit]

        # Return just the registrations
        return [m['registration'] for m in matches]

    def _score_match(
        self,
        name: str,
        description: str,
        query: str,
        usage_count: int
    ) -> int:
        """Calculate search score"""
        score = 0
        name_lower = name.lower()
        query_lower = query.lower()
        desc_lower = description.lower()

        # 1. Exact prefix match
        if name_lower.startswith(query_lower):
            score += 1000
            # Bonus for exact match
            if name_lower == query_lower:
                score += 500

        # 2. Fuzzy match
        elif query_lower in name_lower:
            score += 500

        # 3. Description match
        elif query_lower.replace('/', '') in desc_lower:
            score += 250

        else:
            return 0

        # 4. Usage frequency bonus
        usage_bonus = min(usage_count, 100)
        score += usage_bonus

        return score

    # ========================================================================
    # USAGE TRACKING (from CommandRegistry)
    # ========================================================================

    def record_usage(self, type: ExecutionType, name: str):
        """Track usage of command/tool/API"""
        key = f"{type.value}:{name}"
        self.usage_stats[key] = self.usage_stats.get(key, 0) + 1

        # Update registration
        reg = self.get(type, name)
        if reg:
            reg.usage_count = self.usage_stats[key]

        # Save periodically (every 10 uses)
        if self.usage_stats[key] % 10 == 0:
            self._save_usage_stats()

    def get_most_used(
        self,
        type: Optional[ExecutionType] = None,
        limit: int = 10
    ) -> List[ExecutionRegistration]:
        """Get most frequently used items"""
        items = self.get_all(type=type)
        items.sort(key=lambda r: r.usage_count, reverse=True)
        return items[:limit]

    def _load_usage_stats(self) -> Dict[str, int]:
        """Load usage statistics from file"""
        if not self.usage_file.exists():
            return {}

        try:
            with open(self.usage_file) as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_usage_stats(self):
        """Save usage statistics to file"""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage_stats, f, indent=2)
        except Exception:
            pass

    # ========================================================================
    # ENABLE/DISABLE (from CommandRegistry)
    # ========================================================================

    def enable(self, type: ExecutionType, name: str) -> bool:
        """Enable command/tool/API"""
        reg = self.get(type, name)
        if reg:
            reg.enabled = True
            self._save_registry_state()
            return True
        return False

    def disable(self, type: ExecutionType, name: str) -> bool:
        """Disable command/tool/API"""
        reg = self.get(type, name)
        if reg:
            reg.enabled = False
            self._save_registry_state()
            return True
        return False

    def is_enabled(self, type: ExecutionType, name: str) -> bool:
        """Check if command/tool/API is enabled"""
        reg = self.get(type, name)
        return reg.enabled if reg else False

    def _load_registry_state(self):
        """Load enabled/disabled state"""
        if not self.registry_file.exists():
            return

        try:
            with open(self.registry_file) as f:
                state = json.load(f)

            # Apply state to registrations
            for key, enabled in state.get('enabled', {}).items():
                type_str, name = key.split(':', 1)
                type_enum = ExecutionType(type_str)
                reg = self.get(type_enum, name)
                if reg:
                    reg.enabled = enabled
        except Exception:
            pass

    def _save_registry_state(self):
        """Save enabled/disabled state"""
        state = {
            'enabled': {}
        }

        # Save enabled state for all registrations
        for reg in self.get_all():
            key = f"{reg.type.value}:{reg.name}"
            state['enabled'][key] = reg.enabled

        try:
            with open(self.registry_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception:
            pass
