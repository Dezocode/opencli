"""
OpenCLI Command Registry
Centralized command management with permission system
"""

import json
from pathlib import Path

class CommandRegistry:
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.permissions_file = self.config_dir / "command_permissions.json"

        # Define all available commands
        self.available_commands = {
            '/model': {
                'description': 'View or change model',
                'category': 'basic',
                'default_enabled': True,
                'requires_args': False
            },
            '/provider': {
                'description': 'Manage API providers and keys',
                'category': 'basic',
                'default_enabled': True,
                'requires_args': False
            },
            '/agent': {
                'description': 'Switch to specific agent',
                'category': 'agents',
                'default_enabled': True,
                'requires_args': False,
                'requires_feature': 'AGENT_SYSTEM'
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
                'requires_args': False
            },
            '/providers': {
                'description': 'Manage API provider keys with auto-detection',
                'category': 'basic',
                'default_enabled': True,
                'requires_args': False
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

        # Save permissions
        self._save_permissions(self.permissions)

        print("\n" + "="*60)
        print("✅ Command permissions updated!")
        print("="*60 + "\n")

        # Show summary
        enabled = [cmd for cmd in self.permissions if self.permissions[cmd]]
        disabled = [cmd for cmd in self.permissions if not self.permissions[cmd]]

        print(f"Enabled commands ({len(enabled)}): {', '.join(sorted(enabled))}")
        if disabled:
            print(f"Disabled commands ({len(disabled)}): {', '.join(sorted(disabled))}")
        print()

        return self.permissions

    def show_status(self, feature_flags=None):
        """Show current command status"""
        feature_flags = feature_flags or {}

        print("\n📋 Command Status\n")

        categories = {}
        for cmd, info in self.available_commands.items():
            cat = info['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((cmd, info))

        for category in ['basic', 'spec-driven', 'agents', 'advanced', 'system']:
            if category not in categories:
                continue

            print(f"{category.upper()}:")

            for cmd, info in sorted(categories[category]):
                # Check feature availability
                feature_available = True
                feature_note = ""
                if 'requires_feature' in info:
                    feature_available = feature_flags.get(info['requires_feature'], False)
                    if not feature_available:
                        feature_note = " (feature unavailable)"

                # Get status
                enabled = self.permissions.get(cmd, info['default_enabled'])

                if not feature_available:
                    status = "❌"
                elif enabled:
                    status = "✓"
                else:
                    status = "✗"

                print(f"  {status} {cmd:15} {info['description']}{feature_note}")

            print()
