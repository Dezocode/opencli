"""
OpenCLI Command Registry
Centralized command management with permission system
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

class CommandRegistry:
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.permissions_file = self.config_dir / "command_permissions.json"
        self.usage_file = self.config_dir / "command_usage.json"

        # Define all available commands
        self.available_commands = {
            '/model': {
                'description': 'View or change model',
                'category': 'basic',
                'default_enabled': True,
                'requires_args': False,
                'subcommands': {
                    'list': 'List all available models (default)',
                    '<model-id>': 'Switch to specified model',
                    'r1': 'Switch to most recent model',
                    'r2': 'Switch to 2nd most recent model'
                }
            },
            '/agent': {
                'description': 'Switch to specific agent',
                'category': 'agents',
                'default_enabled': True,
                'requires_args': False,
                'requires_feature': 'AGENT_SYSTEM',
                'subcommands': {
                    'assistant': 'General-purpose coding assistant',
                    'debugger': 'Bug finding and fixing specialist',
                    'reviewer': 'Code review and quality analysis',
                    'refactor': 'Code refactoring expert',
                    'tester': 'Test writing specialist',
                    'documenter': 'Documentation expert',
                    'architect': 'System design specialist'
                }
            },
            '/agents': {
                'description': 'List all available agents',
                'category': 'agents',
                'default_enabled': True,
                'requires_args': False,
                'requires_feature': 'AGENT_SYSTEM'
            },
            '/status': {
                'description': 'Show session info',
                'category': 'basic',
                'default_enabled': True,
                'requires_args': False
            },
            '/clear': {
                'description': 'Clear conversation history',
                'category': 'basic',
                'default_enabled': True,
                'requires_args': False
            },
            '/bashes': {
                'description': 'List background tasks',
                'category': 'advanced',
                'default_enabled': True,
                'requires_args': False
            },
            '/upgrade': {
                'description': 'Upgrade to latest version',
                'category': 'system',
                'default_enabled': True,
                'requires_args': False,
                'requires_feature': 'UPGRADE_SYSTEM'
            },
            '/rollback': {
                'description': 'Rollback to previous version',
                'category': 'system',
                'default_enabled': True,
                'requires_args': False,
                'requires_feature': 'UPGRADE_SYSTEM'
            },
            '/help': {
                'description': 'Show help menu',
                'category': 'basic',
                'default_enabled': True,
                'requires_args': False
            },
            '/commands': {
                'description': 'Manage command permissions',
                'category': 'system',
                'default_enabled': True,
                'requires_args': False
            },
            '/exit': {
                'description': 'Exit the session',
                'category': 'basic',
                'default_enabled': True,
                'requires_args': False
            },
            '/quit': {
                'description': 'Exit the session',
                'category': 'basic',
                'default_enabled': True,
                'requires_args': False
            },
            '/permissions': {
                'description': 'Manage tool permissions',
                'category': 'system',
                'default_enabled': True,
                'requires_args': False,
                'requires_feature': 'TOOL_PERMISSIONS'
            },
            '/api': {
                'description': 'IPC server control (start/stop/status)',
                'category': 'advanced',
                'default_enabled': True,
                'requires_args': False,
                'subcommands': {
                    'start': 'Start IPC server',
                    'stop': 'Stop IPC server',
                    'status': 'Show IPC server status'
                }
            },
            '/providers': {
                'description': 'Manage API provider keys with auto-detection',
                'category': 'basic',
                'default_enabled': True,
                'requires_args': False,
                'subcommands': {
                    'list': 'List all configured providers',
                    'add': 'Add a new provider key (auto-detects provider)',
                    'add ollama': 'Add Ollama local server as provider',
                    'remove': 'Remove a provider key'
                }
            },
            '/specify': {
                'description': 'Create spec describing what to build (Spec-Kit)',
                'category': 'spec-driven',
                'default_enabled': True,
                'requires_args': True
            },
            '/constitution': {
                'description': 'Create project principles and guidelines (Spec-Kit)',
                'category': 'spec-driven',
                'default_enabled': True,
                'requires_args': True
            },
            '/plan': {
                'description': 'Create technical implementation plan (Spec-Kit)',
                'category': 'spec-driven',
                'default_enabled': True,
                'requires_args': True
            },
            '/tasks': {
                'description': 'Break down plan into actionable tasks (Spec-Kit)',
                'category': 'spec-driven',
                'default_enabled': True,
                'requires_args': False
            },
            '/implement': {
                'description': 'Implement tasks from the plan (Spec-Kit)',
                'category': 'spec-driven',
                'default_enabled': True,
                'requires_args': False
            },
            '/test': {
                'description': 'Create and run tests (Spec-Kit)',
                'category': 'spec-driven',
                'default_enabled': True,
                'requires_args': False
            },
            '/spec-check': {
                'description': 'Validate spec completeness (Spec-Kit)',
                'category': 'spec-driven',
                'default_enabled': True,
                'requires_args': False
            },
            '/local': {
                'description': 'Local model recommendations for Ollama',
                'category': 'basic',
                'default_enabled': True,
                'requires_args': False
            },
            '/debug': {
                'description': 'Toggle debug mode',
                'category': 'advanced',
                'default_enabled': True,
                'requires_args': False
            },
            '/performance': {
                'description': 'Performance monitoring controls',
                'category': 'advanced',
                'default_enabled': True,
                'requires_args': False
            },
            '/reload': {
                'description': 'Hot-reload modules (clear cache and reimport)',
                'category': 'advanced',
                'default_enabled': True,
                'requires_args': False
            }
        }

        self.permissions = self._load_permissions()

    def _load_permissions(self):
        """Load command permissions from file"""
        if not self.permissions_file.exists():
            # Create default permissions
            default_perms = {
                cmd: info['default_enabled']
                for cmd, info in self.available_commands.items()
            }
            self._save_permissions(default_perms)
            return default_perms

        try:
            with open(self.permissions_file) as f:
                saved_perms = json.load(f)

            # Merge with available commands to handle new commands
            merged_perms = {}
            for cmd, info in self.available_commands.items():
                if cmd in saved_perms:
                    # Keep user's saved preference
                    merged_perms[cmd] = saved_perms[cmd]
                else:
                    # New command - use default
                    merged_perms[cmd] = info['default_enabled']

            # Save merged permissions if new commands were added
            if len(merged_perms) != len(saved_perms):
                self._save_permissions(merged_perms)

            return merged_perms
        except:
            # Fallback to defaults
            return {
                cmd: info['default_enabled']
                for cmd, info in self.available_commands.items()
            }

    def _save_permissions(self, permissions):
        """Save command permissions to file"""
        try:
            with open(self.permissions_file, 'w') as f:
                json.dump(permissions, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save command permissions: {e}")

    def is_enabled(self, command):
        """Check if a command is enabled"""
        # Normalize command (add / if missing)
        if not command.startswith('/'):
            command = f'/{command}'

        # Unknown commands are disabled by default
        if command not in self.available_commands:
            return False

        # Check if explicitly disabled
        return self.permissions.get(command, True)

    def enable_command(self, command):
        """Enable a command"""
        if not command.startswith('/'):
            command = f'/{command}'

        if command not in self.available_commands:
            return False, f"Unknown command: {command}"

        self.permissions[command] = True
        self._save_permissions(self.permissions)
        return True, f"✓ Enabled: {command}"

    def disable_command(self, command):
        """Disable a command"""
        if not command.startswith('/'):
            command = f'/{command}'

        if command not in self.available_commands:
            return False, f"Unknown command: {command}"

        # Don't allow disabling /commands itself
        if command == '/commands':
            return False, "Cannot disable /commands (needed to re-enable commands)"

        self.permissions[command] = False
        self._save_permissions(self.permissions)
        return True, f"✓ Disabled: {command}"

    def get_enabled_commands(self, feature_flags=None):
        """Get list of currently enabled commands"""
        feature_flags = feature_flags or {}
        enabled = []

        for cmd, info in self.available_commands.items():
            # Check if command is enabled in permissions
            if not self.permissions.get(cmd, info['default_enabled']):
                continue

            # Check if required feature is available
            if 'requires_feature' in info:
                if not feature_flags.get(info['requires_feature'], False):
                    continue

            enabled.append(cmd)

        return sorted(enabled)

    def get_all_commands(self):
        """Get all available commands with metadata"""
        return self.available_commands

    def get_command_info(self, command):
        """Get information about a specific command"""
        if not command.startswith('/'):
            command = f'/{command}'

        return self.available_commands.get(command)

    def interactive_permission_setup(self, feature_flags=None):
        """
        Interactive setup to enable/disable commands one by one
        Returns: dict of updated permissions
        """
        feature_flags = feature_flags or {}
        print("\n🔧 Command Permission Setup\n")
        print("Enable or disable slash commands individually.\n")

        categories = {}
        for cmd, info in self.available_commands.items():
            cat = info['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((cmd, info))

        category_order = ['basic', 'spec-driven', 'agents', 'advanced', 'system']

        for category in category_order:
            if category not in categories:
                continue

            print(f"\n{'='*60}")
            print(f"  {category.upper()} COMMANDS")
            print(f"{'='*60}\n")

            for cmd, info in sorted(categories[category]):
                # Check if feature is available
                feature_available = True
                if 'requires_feature' in info:
                    feature_available = feature_flags.get(info['requires_feature'], False)

                if not feature_available:
                    print(f"{cmd:15} {info['description']}")
                    print(f"               {'❌ Feature not available'}\n")
                    continue

                # Get current status
                current_status = self.permissions.get(cmd, info['default_enabled'])
                status_str = "✓ enabled" if current_status else "✗ disabled"

                # Don't allow disabling /commands
                if cmd == '/commands':
                    print(f"{cmd:15} {info['description']}")
                    print(f"               🔒 Always enabled (required for permission management)\n")
                    continue

                print(f"{cmd:15} {info['description']}")
                print(f"               Currently: {status_str}")

                # Ask for permission
                try:
                    response = input(f"               Enable? (y/n/Enter to keep current): ").strip().lower()
                except (KeyboardInterrupt, EOFError):
                    print("\n\nSetup cancelled. Keeping existing permissions.\n")
                    return self.permissions

                if response == 'y':
                    self.permissions[cmd] = True
                elif response == 'n':
                    self.permissions[cmd] = False
                # else: keep current (Enter pressed)

                print()

    # ========================================================================
    # COMMAND SEARCH AND AUTOCOMPLETE
    # ========================================================================

    def search_commands(
        self,
        query: str,
        feature_flags: Optional[Dict] = None,
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
            feature_flags: Feature availability dict
            limit: Maximum number of results

        Returns:
            List of command matches sorted by score (highest first)
        """
        feature_flags = feature_flags or {}
        usage_stats = self.get_usage_stats()

        # Normalize query
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
            if base_cmd in self.available_commands:
                base_info = self.available_commands[base_cmd]

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

        # Regular base command search
        if not matches or not ' ' in query:
            for cmd, info in self.available_commands.items():
                # Skip disabled commands
                if not self.permissions.get(cmd, info['default_enabled']):
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

    def _score_command(
        self,
        cmd: str,
        info: Dict,
        query: str,
        usage_count: int
    ) -> int:
        """Calculate search score for a command.

        Args:
            cmd: Command name (e.g., "/model")
            info: Command metadata dict
            query: Search query
            usage_count: Number of times command used

        Returns:
            Score (higher = better match)
        """
        score = 0
        cmd_lower = cmd.lower()
        query_lower = query.lower()
        desc_lower = info['description'].lower()

        # 1. Exact prefix match (highest priority)
        if cmd_lower.startswith(query_lower):
            score += 1000
            # Bonus for exact match
            if cmd_lower == query_lower:
                score += 500

        # 2. Fuzzy match (contains query)
        elif query_lower in cmd_lower:
            score += 500

        # 3. Description match
        elif query_lower.replace('/', '') in desc_lower:
            score += 250

        else:
            # No match
            return 0

        # 4. Add usage frequency bonus (0-100)
        usage_bonus = min(usage_count, 100)
        score += usage_bonus

        return score

    # ========================================================================
    # USAGE TRACKING
    # ========================================================================

    def get_usage_stats(self) -> Dict[str, int]:
        """Load command usage statistics from file.

        Returns:
            Dict mapping command names to usage counts
        """
        if not self.usage_file.exists():
            return {}

        try:
            with open(self.usage_file) as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_usage_stats(self, stats: Dict[str, int]) -> None:
        """Persist usage statistics to file.

        Args:
            stats: Dict mapping command names to usage counts
        """
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)

            with open(self.usage_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            # Silent failure - usage tracking is not critical
            pass

    def record_usage(self, command: str) -> None:
        """Increment usage counter for a command.

        Args:
            command: Command name (e.g., "/model" or "model")
        """
        # Normalize command
        if not command.startswith('/'):
            command = f'/{command}'

        # Only track known commands
        if command not in self.available_commands:
            return

        # Load current stats
        stats = self.get_usage_stats()

        # Increment counter
        stats[command] = stats.get(command, 0) + 1

        # Save updated stats
        self._save_usage_stats(stats)

    def get_most_used_commands(self, limit: int = 10) -> List[Dict]:
        """Get most frequently used commands.

        Args:
            limit: Maximum number of commands to return

        Returns:
            List of dicts with command info sorted by usage
        """
        usage_stats = self.get_usage_stats()

        # Build list with metadata
        commands = []
        for cmd, count in usage_stats.items():
            if cmd in self.available_commands:
                info = self.available_commands[cmd]
                commands.append({
                    'name': cmd,
                    'description': info['description'],
                    'category': info['category'],
                    'usage_count': count
                })

        # Sort by usage (descending)
        commands.sort(key=lambda x: x['usage_count'], reverse=True)

        return commands[:limit]
