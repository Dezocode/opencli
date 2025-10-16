"""
Command Registration Core
Handles command search, scoring, and registration logic
"""

from typing import List, Dict, Optional
import json
from pathlib import Path


class CommandRegistrationCore:
    """Core command registration and search functionality"""
    
    def __init__(self, permissions_manager=None, usage_tracker=None):
        """Initialize command registration core.
        
        Args:
            permissions_manager: Object handling command permissions
            usage_tracker: Object tracking command usage statistics
        """
        self.permissions_manager = permissions_manager
        self.usage_tracker = usage_tracker
        
    def get_runtime_commands(self, executor=None, static_commands=None) -> Dict[str, Dict]:
        """Get commands from runtime registry or fallback to static definitions.

        Returns:
            Dict mapping command names to their info dictionaries.
            When executor is available, builds from executor.registry.commands.
            Otherwise, falls back to static_commands.
        """
        if executor and hasattr(executor, 'registry'):
            # Build command dict from runtime registry
            runtime_commands = {}

            for cmd_name, registration in executor.registry.commands.items():
                # Convert ExecutionRegistry format to CommandRegistry format
                runtime_commands[cmd_name] = {
                    'description': registration.description or 'No description',
                    'category': registration.category.value if hasattr(registration.category, 'value') else str(registration.category),
                    'default_enabled': True,  # Already registered means enabled
                    'requires_args': False,  # TODO: Could extract from handler signature
                    'risk_level': registration.risk_level.value if hasattr(registration.risk_level, 'value') else 'medium',
                    'requires_approval': registration.requires_approval
                }

            # Merge with static commands to preserve subcommand info
            # (runtime registry doesn't track subcommands separately)
            if static_commands:
                for cmd_name, cmd_info in static_commands.items():
                    if cmd_name in runtime_commands:
                        # Preserve subcommands from static definition
                        if 'subcommands' in cmd_info:
                            runtime_commands[cmd_name]['subcommands'] = cmd_info['subcommands']
                    else:
                        # Command in static dict but not runtime - keep it (for backward compat)
                        runtime_commands[cmd_name] = cmd_info

            return runtime_commands
        else:
            # No executor available - fall back to static definitions
            return static_commands or {}

    def search_commands(
        self,
        query: str,
        available_commands: Dict[str, Dict],
        permissions: Dict[str, bool],
        feature_flags: Optional[Dict] = None,
        usage_stats: Optional[Dict] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Search commands with priority-based ranking.

        Search algorithm priority:
        1. Exact prefix match (score: 1000)
        2. Fuzzy match (score: 500)
        3. Description match (score: 250)
        4. Usage frequency (score: 0-100)

        Args:
            query: Search query (e.g., "/mo" or "/")
            available_commands: Commands dictionary
            permissions: Command permissions dictionary
            feature_flags: Feature availability dict
            usage_stats: Command usage statistics
            limit: Maximum number of results

        Returns:
            List of command matches sorted by score (highest first)
        """
        feature_flags = feature_flags or {}
        usage_stats = usage_stats or {}

        # Normalize query
        query = query.strip().lower()
        if not query.startswith('/'):
            query = f'/{query}'

        matches = []

        # Check if query contains a space (subcommand search)
        if ' ' in query:
            matches.extend(self._search_subcommands(
                query, available_commands, usage_stats
            ))

        # Regular base command search
        if not matches or not ' ' in query:
            for cmd, info in available_commands.items():
                # Skip disabled commands
                if not permissions.get(cmd, info['default_enabled']):
                    continue

                # Skip if required feature unavailable
                if 'requires_feature' in info:
                    if not feature_flags.get(info['requires_feature'], False):
                        continue

                # Calculate score
                score = self._score_command(cmd, info, query, usage_stats.get(cmd, 0))

                if score > 0:
                    matches.append({
                        'name': cmd,
                        'description': info['description'],
                        'category': info['category'],
                        'score': score,
                        'usage_count': usage_stats.get(cmd, 0)
                    })

        # Sort by score (descending)
        matches.sort(key=lambda x: x['score'], reverse=True)

        if limit:
            matches = matches[:limit]

        return matches

    def _search_subcommands(self, query: str, available_commands: Dict, usage_stats: Dict) -> List[Dict]:
        """Search for subcommands based on query."""
        matches = []
        parts = query.split(maxsplit=1)
        base_cmd = parts[0]
        subquery = parts[1] if len(parts) > 1 else ''

        # Find the base command
        if base_cmd in available_commands:
            base_info = available_commands[base_cmd]

            # Check if it has subcommands
            if 'subcommands' in base_info:
                # Search subcommands
                for subcmd, subdesc in base_info['subcommands'].items():
                    full_cmd = f"{base_cmd} {subcmd}"
                    subcmd_lower = subcmd.lower()

                    # Score the subcommand match
                    score = 0
                    if not subquery:
                        # No subquery yet - show all subcommands
                        score = 1000
                    elif subcmd_lower.startswith(subquery):
                        score = 1000  # Exact prefix
                    elif subquery in subcmd_lower:
                        score = 500  # Contains
                    elif subquery in subdesc.lower():
                        score = 250  # Description match

                    if score > 0:
                        matches.append({
                            'name': full_cmd,
                            'description': subdesc,
                            'category': base_info['category'],
                            'score': score,
                            'usage_count': usage_stats.get(full_cmd, 0)
                        })

        return matches

    def _score_command(self, cmd: str, info: Dict, query: str, usage_count: int) -> int:
        """Score a command match against the query.
        
        Args:
            cmd: Command name
            info: Command info dictionary
            query: Search query
            usage_count: Number of times command has been used
            
        Returns:
            Score (higher is better, 0 means no match)
        """
        cmd_lower = cmd.lower()
        desc_lower = info['description'].lower()

        # Base scoring
        score = 0

        # Exact prefix match gets highest priority
        if cmd_lower.startswith(query):
            score = 1000
        # Fuzzy match (query appears anywhere in command)
        elif query in cmd_lower:
            score = 500
        # Description match
        elif query in desc_lower:
            score = 250
        else:
            # No match
            return 0

        # Add usage frequency bonus (max 100 points)
        usage_bonus = min(usage_count * 2, 100)
        score += usage_bonus

        return score

    def get_autocomplete_suggestions(
        self,
        partial: str,
        available_commands: Dict[str, Dict],
        permissions: Dict[str, bool],
        feature_flags: Optional[Dict] = None,
        limit: int = 10
    ) -> List[str]:
        """Get autocomplete suggestions for partial command input.
        
        Args:
            partial: Partial command string
            available_commands: Available command definitions
            permissions: Command permissions
            feature_flags: Feature availability flags
            limit: Maximum suggestions to return
            
        Returns:
            List of command suggestions
        """
        matches = self.search_commands(
            query=partial,
            available_commands=available_commands,
            permissions=permissions,
            feature_flags=feature_flags,
            limit=limit
        )
        
        return [match['name'] for match in matches]

    def validate_command_access(
        self,
        cmd_name: str,
        available_commands: Dict[str, Dict],
        permissions: Dict[str, bool],
        feature_flags: Optional[Dict] = None
    ) -> tuple[bool, str]:
        """Validate if a command can be accessed.
        
        Args:
            cmd_name: Command name to validate
            available_commands: Available command definitions  
            permissions: Command permissions
            feature_flags: Feature availability flags
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Normalize command name
        if not cmd_name.startswith('/'):
            cmd_name = f'/{cmd_name}'
            
        # Check if command exists
        if cmd_name not in available_commands:
            return False, f"Unknown command: {cmd_name}"
            
        cmd_info = available_commands[cmd_name]
        
        # Check if command is enabled
        if not permissions.get(cmd_name, cmd_info['default_enabled']):
            return False, f"Command disabled: {cmd_name}"
            
        # Check feature requirements
        if 'requires_feature' in cmd_info:
            required_feature = cmd_info['requires_feature']
            if not (feature_flags or {}).get(required_feature, False):
                return False, f"Feature not available: {required_feature}"
                
        return True, ""

    def record_command_usage(self, cmd_name: str, usage_file: Path) -> None:
        """Record usage of a command for autocomplete ranking.
        
        Args:
            cmd_name: Command that was used
            usage_file: Path to usage statistics file
        """
        try:
            # Load existing stats
            if usage_file.exists():
                with open(usage_file) as f:
                    stats = json.load(f)
            else:
                stats = {}
                
            # Increment usage count
            stats[cmd_name] = stats.get(cmd_name, 0) + 1
            
            # Save updated stats
            usage_file.parent.mkdir(parents=True, exist_ok=True)
            with open(usage_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception:
            # Silently ignore errors in usage tracking
            pass