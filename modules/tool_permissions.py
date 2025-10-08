"""
OpenCLI Tool Permission System
Manages user confirmation for risky tool operations (Edit, Write, Bash)
Includes path-based risk detection for parent/outside directory access
"""

import json
import os
from pathlib import Path
from enum import Enum

class RiskLevel(Enum):
    SAFE = "safe"           # Read, Glob, Grep - auto-execute
    RISKY = "risky"         # Edit, Write - prompt for confirmation
    DANGEROUS = "dangerous"  # Bash - always prompt with command preview
    CRITICAL = "critical"    # Parent/outside directories, system paths

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
            'ConfigureHeaders': RiskLevel.RISKY,
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

    def assess_path_risk(self, file_path, current_dir=None):
        """
        Assess risk level of file path

        Returns: (risk_level: RiskLevel, reason: str)
        """
        if not file_path:
            return RiskLevel.SAFE, "no path specified"

        # Get current working directory
        cwd = Path(current_dir or os.getcwd()).resolve()
        target = Path(file_path).resolve()

        # Critical paths (system directories)
        critical_paths = [
            Path('/etc').resolve(),          # Resolve symlinks (macOS: /etc -> /private/etc)
            Path('/private/etc'),
            Path('/bin').resolve(),
            Path('/sbin').resolve(),
            Path('/usr/bin'),
            Path('/usr/sbin'),
            Path('/System'),
            Path('/Library'),
            Path('/var'),
            Path.home() / '.ssh',
            Path.home() / '.aws',
            Path.home() / '.config',
        ]

        # Check if target is in critical system path
        for critical in critical_paths:
            try:
                if target.is_relative_to(critical):
                    return RiskLevel.CRITICAL, f"system directory: {critical}"
            except (ValueError, AttributeError):
                # is_relative_to not available in older Python
                try:
                    target.relative_to(critical)
                    return RiskLevel.CRITICAL, f"system directory: {critical}"
                except ValueError:
                    pass

        # Check if target is outside current directory
        try:
            target.relative_to(cwd)
            # Within current directory
            return RiskLevel.SAFE, "within working directory"
        except ValueError:
            # Outside current directory
            # Check if it's a parent directory
            try:
                cwd.relative_to(target)
                return RiskLevel.DANGEROUS, f"parent directory: {target}"
            except ValueError:
                return RiskLevel.DANGEROUS, f"outside working directory: {target}"

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

    def should_prompt(self, tool_name, args=None, current_dir=None):
        """
        Determine if we should prompt for permission

        Returns: (should_prompt: bool, reason: str, path_risk: RiskLevel)
        """
        # Assess path risk for file operations
        path_risk = RiskLevel.SAFE
        path_reason = ""

        if args and tool_name in ['Edit', 'Write', 'Read']:
            file_path = args.get('file_path')
            if file_path:
                path_risk, path_reason = self.assess_path_risk(file_path, current_dir)

                # CRITICAL paths always require prompt (even for Read)
                if path_risk == RiskLevel.CRITICAL:
                    return True, f"CRITICAL: {path_reason}", path_risk

        # Check if in auto-accept mode (global or session)
        if self.auto_accept_mode or self.accept_all_session:
            # Don't auto-accept CRITICAL or DANGEROUS path operations
            if path_risk in [RiskLevel.CRITICAL, RiskLevel.DANGEROUS]:
                return True, f"risky path: {path_reason}", path_risk
            return False, "auto-accept enabled", path_risk

        # Check global auto-accept from config
        if self.permissions.get('auto_accept', False):
            # Don't auto-accept CRITICAL or DANGEROUS path operations
            if path_risk in [RiskLevel.CRITICAL, RiskLevel.DANGEROUS]:
                return True, f"risky path: {path_reason}", path_risk
            return False, "global auto-accept", path_risk

        # Check if tool is in allowed list
        if self.is_tool_allowed(tool_name):
            # Don't auto-allow CRITICAL path operations
            if path_risk == RiskLevel.CRITICAL:
                return True, f"CRITICAL path: {path_reason}", path_risk
            # Warn about DANGEROUS paths even if tool is allowed
            if path_risk == RiskLevel.DANGEROUS:
                return True, f"risky path: {path_reason}", path_risk
            return False, "tool allowed", path_risk

        # Check tool risk level
        tool_risk = self.tool_risks.get(tool_name, RiskLevel.RISKY)

        if tool_risk == RiskLevel.SAFE:
            # Even safe tools need prompt for CRITICAL/DANGEROUS paths
            if path_risk in [RiskLevel.CRITICAL, RiskLevel.DANGEROUS]:
                return True, f"risky path: {path_reason}", path_risk
            return False, "safe tool", path_risk

        # Risky and dangerous tools require prompt
        # Use higher of tool_risk and path_risk
        effective_risk = max(tool_risk, path_risk, key=lambda r: ['safe', 'risky', 'dangerous', 'critical'].index(r.value))
        return True, f"{effective_risk.value} operation", effective_risk

    def format_tool_preview(self, tool_name, args, path_risk=None, current_dir=None):
        """Format tool operation for preview"""
        preview = ""

        if tool_name == 'Edit':
            file_path = args.get('file_path')
            preview = f"Edit file: {file_path}\n" \
                     f"Replace: {args.get('old_string', '')[:50]}...\n" \
                     f"With: {args.get('new_string', '')[:50]}..."

        elif tool_name == 'Write':
            file_path = args.get('file_path')
            content_preview = args.get('content', '')[:100]
            preview = f"Write file: {file_path}\n" \
                     f"Content ({len(args.get('content', ''))} chars): {content_preview}..."

        elif tool_name == 'Read':
            file_path = args.get('file_path')
            preview = f"Read file: {file_path}"

        elif tool_name == 'Bash':
            preview = f"Execute command: {args.get('command')}\n" \
                     f"Description: {args.get('description', 'No description')}"
        else:
            preview = f"{tool_name}: {args}"

        # Add path risk warning if applicable
        if path_risk and tool_name in ['Edit', 'Write', 'Read']:
            file_path = args.get('file_path')
            if file_path:
                path_risk_level, path_reason = self.assess_path_risk(file_path, current_dir)
                if path_risk_level in [RiskLevel.DANGEROUS, RiskLevel.CRITICAL]:
                    cwd = Path(current_dir or os.getcwd()).resolve()
                    preview += f"\n\n⚠️  PATH WARNING: {path_reason}"
                    preview += f"\nCurrent directory: {cwd}"
                    preview += f"\nTarget path: {Path(file_path).resolve()}"

        return preview

    def prompt_for_permission(self, tool_name, args, current_dir=None):
        """
        Prompt user for permission to execute tool

        Returns: (allowed: bool, remember: bool, session_mode: str)
        """
        # Determine effective risk level (tool + path)
        tool_risk = self.tool_risks.get(tool_name, RiskLevel.RISKY)
        path_risk = RiskLevel.SAFE

        if tool_name in ['Edit', 'Write', 'Read']:
            file_path = args.get('file_path')
            if file_path:
                path_risk, _ = self.assess_path_risk(file_path, current_dir)

        # Use higher risk level
        effective_risk = max(tool_risk, path_risk, key=lambda r: ['safe', 'risky', 'dangerous', 'critical'].index(r.value))

        print(f"\n🔒 {effective_risk.value.upper()} OPERATION: {tool_name}")
        print("─" * 60)
        print(self.format_tool_preview(tool_name, args, path_risk, current_dir))
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
