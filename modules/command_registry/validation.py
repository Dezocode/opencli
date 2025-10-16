"""
Command Validation System
Handles command permission management, validation, and interactive setup
"""

import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class CommandValidator:
    """Handles command validation, permissions, and access control"""
    
    def __init__(self, permissions_file: Path, available_commands: Dict):
        """Initialize command validator.
        
        Args:
            permissions_file: Path to permissions storage file
            available_commands: Dictionary of available command definitions
        """
        self.permissions_file = permissions_file
        self.available_commands = available_commands
        self.permissions = self._load_permissions()
        
    def is_enabled(self, command: str) -> bool:
        """Check if a command is enabled.
        
        Args:
            command: Command name (with or without leading /)
            
        Returns:
            True if command is enabled, False otherwise
        """
        # Normalize command (add / if missing)
        if not command.startswith('/'):
            command = f'/{command}'

        # Unknown commands are disabled by default
        if command not in self.available_commands:
            return False

        # Check if explicitly disabled
        return self.permissions.get(command, True)

    def enable_command(self, command: str) -> Tuple[bool, str]:
        """Enable a command.
        
        Args:
            command: Command name to enable
            
        Returns:
            Tuple of (success, message)
        """
        if not command.startswith('/'):
            command = f'/{command}'

        if command not in self.available_commands:
            return False, f"Unknown command: {command}"

        self.permissions[command] = True
        self._save_permissions(self.permissions)
        return True, f"✓ Enabled: {command}"

    def disable_command(self, command: str) -> Tuple[bool, str]:
        """Disable a command.
        
        Args:
            command: Command name to disable
            
        Returns:
            Tuple of (success, message)
        """
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

    def get_enabled_commands(self, feature_flags: Optional[Dict] = None) -> List[str]:
        """Get list of currently enabled commands.
        
        Args:
            feature_flags: Dictionary of available features
            
        Returns:
            List of enabled command names
        """
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

    def validate_command_access(
        self, 
        command: str, 
        feature_flags: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """Validate if a command can be accessed.
        
        Args:
            command: Command name to validate
            feature_flags: Dictionary of available features
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Normalize command name
        if not command.startswith('/'):
            command = f'/{command}'
            
        # Check if command exists
        if command not in self.available_commands:
            return False, f"Unknown command: {command}"
            
        cmd_info = self.available_commands[command]
        
        # Check if command is enabled
        if not self.permissions.get(command, cmd_info['default_enabled']):
            return False, f"Command disabled: {command}"
            
        # Check feature requirements
        if 'requires_feature' in cmd_info:
            required_feature = cmd_info['requires_feature']
            if not (feature_flags or {}).get(required_feature, False):
                return False, f"Feature not available: {required_feature}"
                
        return True, ""

    def validate_command_args(
        self, 
        command: str, 
        args: List[str]
    ) -> Tuple[bool, str]:
        """Validate command arguments.
        
        Args:
            command: Command name
            args: List of command arguments
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Normalize command name
        if not command.startswith('/'):
            command = f'/{command}'
            
        if command not in self.available_commands:
            return False, f"Unknown command: {command}"
            
        cmd_info = self.available_commands[command]
        
        # Check if command requires arguments
        if cmd_info.get('requires_args', False) and not args:
            return False, f"Command {command} requires arguments"
            
        # Check if command doesn't allow arguments
        if not cmd_info.get('requires_args', False) and cmd_info.get('requires_args') is False and args:
            return False, f"Command {command} does not accept arguments"
            
        return True, ""

    def get_command_categories(self) -> Dict[str, List[str]]:
        """Get commands grouped by category.
        
        Returns:
            Dictionary mapping categories to command lists
        """
        categories = {}
        for cmd, info in self.available_commands.items():
            cat = info.get('category', 'other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(cmd)
            
        return categories

    def get_disabled_commands(self) -> List[str]:
        """Get list of disabled commands.
        
        Returns:
            List of disabled command names
        """
        disabled = []
        for cmd, info in self.available_commands.items():
            if not self.permissions.get(cmd, info['default_enabled']):
                disabled.append(cmd)
        return sorted(disabled)

    def reset_permissions(self) -> None:
        """Reset all permissions to defaults."""
        self.permissions = {
            cmd: info['default_enabled']
            for cmd, info in self.available_commands.items()
        }
        self._save_permissions(self.permissions)

    def bulk_enable_commands(self, commands: List[str]) -> List[Tuple[str, bool, str]]:
        """Enable multiple commands at once.
        
        Args:
            commands: List of command names to enable
            
        Returns:
            List of tuples (command, success, message)
        """
        results = []
        for cmd in commands:
            success, message = self.enable_command(cmd)
            results.append((cmd, success, message))
        return results

    def bulk_disable_commands(self, commands: List[str]) -> List[Tuple[str, bool, str]]:
        """Disable multiple commands at once.
        
        Args:
            commands: List of command names to disable
            
        Returns:
            List of tuples (command, success, message)
        """
        results = []
        for cmd in commands:
            success, message = self.disable_command(cmd)
            results.append((cmd, success, message))
        return results

    def export_permissions(self) -> Dict[str, bool]:
        """Export current permissions configuration.
        
        Returns:
            Dictionary of command permissions
        """
        return self.permissions.copy()

    def import_permissions(self, permissions: Dict[str, bool]) -> List[str]:
        """Import permissions configuration.
        
        Args:
            permissions: Dictionary of command permissions
            
        Returns:
            List of warning messages for invalid commands
        """
        warnings = []
        
        # Validate permissions
        valid_permissions = {}
        for cmd, enabled in permissions.items():
            if cmd in self.available_commands:
                valid_permissions[cmd] = bool(enabled)
            else:
                warnings.append(f"Unknown command in import: {cmd}")
                
        # Add missing commands with defaults
        for cmd, info in self.available_commands.items():
            if cmd not in valid_permissions:
                valid_permissions[cmd] = info['default_enabled']
                
        self.permissions = valid_permissions
        self._save_permissions(self.permissions)
        
        return warnings

    def _load_permissions(self) -> Dict[str, bool]:
        """Load command permissions from file."""
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
        except Exception:
            # Fallback to defaults
            return {
                cmd: info['default_enabled']
                for cmd, info in self.available_commands.items()
            }

    def _save_permissions(self, permissions: Dict[str, bool]) -> None:
        """Save command permissions to file."""
        try:
            self.permissions_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.permissions_file, 'w') as f:
                json.dump(permissions, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save command permissions: {e}")


class InteractivePermissionManager:
    """Handles interactive permission setup and management"""
    
    def __init__(self, validator: CommandValidator):
        """Initialize interactive permission manager.
        
        Args:
            validator: CommandValidator instance
        """
        self.validator = validator
        
    def interactive_setup(self, feature_flags: Optional[Dict] = None) -> Dict[str, bool]:
        """Interactive setup to enable/disable commands one by one.
        
        Args:
            feature_flags: Dictionary of available features
            
        Returns:
            Updated permissions dictionary
        """
        feature_flags = feature_flags or {}
        print("\n🔧 Command Permission Setup\n")
        print("Enable or disable slash commands individually.\n")

        categories = self.validator.get_command_categories()
        
        from ..command_registry import get_command_categories
        category_order = get_command_categories()

        for category in category_order:
            if category not in categories:
                continue

            print(f"\n{'='*60}")
            print(f"  {category.upper()} COMMANDS")
            print(f"{'='*60}\n")

            for cmd in sorted(categories[category]):
                info = self.validator.available_commands[cmd]
                
                # Check if feature is available
                feature_available = True
                if 'requires_feature' in info:
                    feature_available = feature_flags.get(info['requires_feature'], False)

                if not feature_available:
                    print(f"{cmd:15} {info['description']}")
                    print(f"               {'❌ Feature not available'}\n")
                    continue

                # Get current status
                current_status = self.validator.permissions.get(cmd, info['default_enabled'])
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
                    return self.validator.permissions

                if response == 'y':
                    self.validator.permissions[cmd] = True
                elif response == 'n':
                    self.validator.permissions[cmd] = False
                # else: keep current (Enter pressed)

                print()

        # Save updated permissions
        self.validator._save_permissions(self.validator.permissions)
        print(f"\n✅ Permissions updated!\n")
        
        return self.validator.permissions

    def show_permission_summary(self) -> None:
        """Display a summary of current permissions."""
        enabled_commands = self.validator.get_enabled_commands()
        disabled_commands = self.validator.get_disabled_commands()
        
        print(f"\n📋 Command Permissions Summary")
        print(f"{'='*50}")
        print(f"✅ Enabled:  {len(enabled_commands)} commands")
        print(f"❌ Disabled: {len(disabled_commands)} commands")
        print(f"📊 Total:    {len(self.validator.available_commands)} commands")
        
        if disabled_commands:
            print(f"\nDisabled commands:")
            for cmd in disabled_commands:
                info = self.validator.available_commands[cmd]
                print(f"  {cmd} - {info['description']}")
        print()

    def quick_enable_category(self, category: str) -> List[Tuple[str, bool, str]]:
        """Enable all commands in a category.
        
        Args:
            category: Category name to enable
            
        Returns:
            List of results from enabling commands
        """
        categories = self.validator.get_command_categories()
        if category not in categories:
            return [("", False, f"Unknown category: {category}")]
            
        return self.validator.bulk_enable_commands(categories[category])

    def quick_disable_category(self, category: str) -> List[Tuple[str, bool, str]]:
        """Disable all commands in a category.
        
        Args:
            category: Category name to disable
            
        Returns:
            List of results from disabling commands
        """
        categories = self.validator.get_command_categories()
        if category not in categories:
            return [("", False, f"Unknown category: {category}")]
            
        return self.validator.bulk_disable_commands(categories[category])