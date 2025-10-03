"""
OpenCLI Tool Permission System
Manages user confirmation for risky tool operations (Edit, Write, Bash)
"""

import json
from pathlib import Path
from enum import Enum

class RiskLevel(Enum):
    SAFE = "safe"           # Read, Glob, Grep - auto-execute
    RISKY = "risky"         # Edit, Write - prompt for confirmation
    DANGEROUS = "dangerous"  # Bash - always prompt with command preview

class ToolPermissionManager:
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.permissions_file = self.config_dir / "tool_permissions.json"

        # Tool risk classification
        self.tool_risks = {
            'Read': RiskLevel.SAFE,
            'Glob': RiskLevel.SAFE,
            'Grep': RiskLevel.SAFE,
            'Edit': RiskLevel.RISKY,
            'Write': RiskLevel.RISKY,
            'Bash': RiskLevel.DANGEROUS,
            'GitHub': RiskLevel.SAFE,
        }

        # Load saved permissions
        self.permissions = self._load_permissions()

        # Session state
        self.auto_accept_mode = False
        self.accept_all_session = False

    def _load_permissions(self):
        """Load tool permissions from file"""
        if not self.permissions_file.exists():
            return {
                'allowed_tools': [],      # Tools always allowed
                'auto_accept': False,     # Global auto-accept mode
            }

        try:
            with open(self.permissions_file) as f:
                return json.load(f)
        except:
            return {'allowed_tools': [], 'auto_accept': False}

    def _save_permissions(self):
        """Save permissions to file"""
        try:
            with open(self.permissions_file, 'w') as f:
                json.dump(self.permissions, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save permissions: {e}")

    def is_tool_allowed(self, tool_name):
        """Check if tool is in allowed list"""
        return tool_name in self.permissions.get('allowed_tools', [])

    def add_allowed_tool(self, tool_name):
        """Add tool to allowed list (skip future prompts)"""
        if tool_name not in self.permissions.get('allowed_tools', []):
            if 'allowed_tools' not in self.permissions:
                self.permissions['allowed_tools'] = []
            self.permissions['allowed_tools'].append(tool_name)
            self._save_permissions()
            return True
        return False

    def remove_allowed_tool(self, tool_name):
        """Remove tool from allowed list"""
        if tool_name in self.permissions.get('allowed_tools', []):
            self.permissions['allowed_tools'].remove(tool_name)
            self._save_permissions()
            return True
        return False

    def set_auto_accept(self, enabled):
        """Enable/disable global auto-accept mode"""
        self.permissions['auto_accept'] = enabled
        self.auto_accept_mode = enabled
        self._save_permissions()

    def should_prompt(self, tool_name, args=None):
        """
        Determine if we should prompt for permission

        Returns: (should_prompt: bool, reason: str)
        """
        # Check if in auto-accept mode (global or session)
        if self.auto_accept_mode or self.accept_all_session:
            return False, "auto-accept enabled"

        # Check global auto-accept from config
        if self.permissions.get('auto_accept', False):
            return False, "global auto-accept"

        # Check if tool is in allowed list
        if self.is_tool_allowed(tool_name):
            return False, "tool allowed"

        # Check risk level
        risk = self.tool_risks.get(tool_name, RiskLevel.RISKY)

        if risk == RiskLevel.SAFE:
            return False, "safe tool"

        # Risky and dangerous tools require prompt
        return True, f"{risk.value} tool"

    def format_tool_preview(self, tool_name, args):
        """Format tool operation for preview"""
        if tool_name == 'Edit':
            return f"Edit file: {args.get('file_path')}\n" \
                   f"Replace: {args.get('old_string')[:50]}...\n" \
                   f"With: {args.get('new_string')[:50]}..."

        elif tool_name == 'Write':
            content_preview = args.get('content', '')[:100]
            return f"Write file: {args.get('file_path')}\n" \
                   f"Content ({len(args.get('content', ''))} chars): {content_preview}..."

        elif tool_name == 'Bash':
            return f"Execute command: {args.get('command')}\n" \
                   f"Description: {args.get('description', 'No description')}"

        return f"{tool_name}: {args}"

    def prompt_for_permission(self, tool_name, args):
        """
        Prompt user for permission to execute tool

        Returns: (allowed: bool, remember: bool, session_mode: str)
        """
        risk = self.tool_risks.get(tool_name, RiskLevel.RISKY)

        print(f"\n🔒 {risk.value.upper()} TOOL: {tool_name}")
        print("─" * 60)
        print(self.format_tool_preview(tool_name, args))
        print("─" * 60)
        print()
        print("Options:")
        print("  y - Yes, allow this once")
        print("  a - Yes, and always allow this tool")
        print("  s - Yes, and accept all for this session")
        print("  n - No, skip this operation")
        print()

        try:
            response = input("Allow? (y/a/s/n): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nSkipped.\n")
            return False, False, None

        if response == 'y':
            return True, False, None
        elif response == 'a':
            self.add_allowed_tool(tool_name)
            print(f"✓ {tool_name} added to allowed tools\n")
            return True, True, None
        elif response == 's':
            self.accept_all_session = True
            print("✓ Auto-accepting all tools for this session\n")
            return True, False, 'session'
        else:
            print("✗ Operation cancelled\n")
            return False, False, None

    def get_allowed_tools(self):
        """Get list of allowed tools"""
        return self.permissions.get('allowed_tools', [])

    def show_status(self):
        """Show current permission status"""
        print("\n🔒 Tool Permission Status\n")

        print(f"Auto-accept mode: {'✓ ENABLED' if self.auto_accept_mode or self.permissions.get('auto_accept') else '✗ disabled'}")
        print(f"Session accept-all: {'✓ ENABLED' if self.accept_all_session else '✗ disabled'}")
        print()

        allowed = self.get_allowed_tools()
        if allowed:
            print(f"Always allowed tools ({len(allowed)}):")
            for tool in allowed:
                print(f"  ✓ {tool}")
        else:
            print("No tools in allowed list (will prompt for risky operations)")

        print()
        print("Tool risk levels:")
        for tool, risk in sorted(self.tool_risks.items()):
            status = "✓" if tool in allowed else " "
            print(f"  {status} {tool:15} {risk.value}")

        print()
