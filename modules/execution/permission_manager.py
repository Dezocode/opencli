"""
Unified Permission Manager - Single permission system for all execution types

Consolidates:
- ToolPermissionManager: path risk assessment, tool permissions
- Command permissions: approval gates
- API permissions: rate limits, costs

Features:
- Unified risk assessment (command + tool + path + API)
- Session and persistent approval modes
- Permission prompts in buffer
- Path-based risk detection
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from enum import Enum

from .registry import ExecutionRegistration, ExecutionType, RiskLevel


class PermissionMode(Enum):
    """Permission modes"""
    PROMPT_ALWAYS = "prompt_always"
    AUTO_ACCEPT_SESSION = "auto_accept_session"
    AUTO_ACCEPT_PERMANENT = "auto_accept_permanent"


class PermissionManager:
    """
    Unified permission system for commands, tools, and APIs

    Combines features from:
    - ToolPermissionManager: path risk, allowed tools
    - Command permissions: enable/disable
    - Step permissions: multi-gate approval
    """

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.permissions_file = self.config_dir / "permissions.json"

        # State
        self.auto_accept_session = False
        self.auto_accept_permanent = False
        self.allowed_items: Dict[str, bool] = {}

        # Load saved permissions
        self._load_permissions()

    # ========================================================================
    # PERMISSION CHECKING
    # ========================================================================

    async def check_permission(
        self,
        registration: ExecutionRegistration,
        context: Dict[str, Any],
        app=None,
        session=None
    ) -> bool:
        """
        Check if execution should be permitted

        Args:
            registration: What's being executed
            context: Execution context (args, paths, etc.)
            app: TUI app (for showing prompts)
            session: Session object

        Returns:
            True if approved, False if denied
        """

        # DEBUG LOGGING
        import sys
        sys.stderr.write(f"\n{'='*80}\n")
        sys.stderr.write(f"[PermissionManager.check_permission] ENTERED\n")
        sys.stderr.write(f"{'='*80}\n")
        sys.stderr.write(f"  registration.name: {registration.name}\n")
        sys.stderr.write(f"  registration.type: {registration.type}\n")
        sys.stderr.write(f"  registration.requires_approval: {registration.requires_approval}\n")
        sys.stderr.write(f"  registration.risk_level: {registration.risk_level}\n")
        sys.stderr.write(f"  app: {type(app) if app else None}\n")
        sys.stderr.write(f"  session: {type(session) if session else None}\n")
        sys.stderr.write(f"  context keys: {list(context.keys())}\n")
        sys.stderr.flush()

        # Skip if doesn't require approval
        if not registration.requires_approval:
            sys.stderr.write(f"[PermissionManager] ❌ SKIPPING - requires_approval=False\n")
            sys.stderr.write(f"[PermissionManager] → Returning True (auto-approved)\n")
            sys.stderr.flush()
            return True

        # Check if permanently allowed
        key = f"{registration.type.value}:{registration.name}"
        if self.allowed_items.get(key, False):
            # Still check for critical risks
            total_risk = self._assess_total_risk(registration, context)
            if total_risk == RiskLevel.CRITICAL:
                # Always prompt for critical
                pass
            else:
                return True

        # Auto-accept modes
        if self.auto_accept_permanent or self.auto_accept_session:
            # Still check for critical/high risks
            total_risk = self._assess_total_risk(registration, context)
            if total_risk in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                # Prompt for high-risk operations
                pass
            else:
                return True

        # Assess total risk
        total_risk = self._assess_total_risk(registration, context)

        # Show permission prompt
        if app and session:
            return await self._show_permission_prompt(
                app,
                session,
                registration,
                total_risk,
                context
            )
        else:
            # No UI available - default to deny
            return False

    def _assess_total_risk(
        self,
        registration: ExecutionRegistration,
        context: Dict[str, Any]
    ) -> RiskLevel:
        """
        Calculate total risk from multiple factors

        Combines:
        - Registration base risk
        - Path risk (for file operations)
        - API cost risk
        - System impact risk

        Returns:
            Highest risk level found
        """
        risks = [registration.risk_level]

        # Path risk for file operations
        if 'file_path' in context:
            path_risk = self._assess_path_risk(context['file_path'])
            risks.append(path_risk)

        # Bash command risk
        if registration.name == 'Bash' and 'command' in context:
            bash_risk = self._assess_bash_risk(context['command'])
            risks.append(bash_risk)

        # API cost risk
        if registration.type == ExecutionType.API:
            api_risk = self._assess_api_risk(registration, context)
            risks.append(api_risk)

        # Return highest risk
        risk_order = {
            RiskLevel.SAFE: 0,
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }
        return max(risks, key=lambda r: risk_order[r])

    # ========================================================================
    # PATH RISK ASSESSMENT (from ToolPermissionManager)
    # ========================================================================

    def _assess_path_risk(self, file_path: str) -> RiskLevel:
        """
        Assess risk level of file path

        Returns:
            RiskLevel based on path location
        """
        if not file_path:
            return RiskLevel.SAFE

        cwd = Path.cwd().resolve()
        target = Path(file_path).resolve()

        # Critical paths (system directories)
        critical_paths = [
            Path('/etc').resolve(),
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
                    return RiskLevel.CRITICAL
            except (ValueError, AttributeError):
                try:
                    target.relative_to(critical)
                    return RiskLevel.CRITICAL
                except ValueError:
                    pass

        # Check if target is outside current directory
        try:
            target.relative_to(cwd)
            # Within current directory
            return RiskLevel.SAFE
        except ValueError:
            # Outside current directory
            try:
                cwd.relative_to(target)
                return RiskLevel.HIGH  # Parent directory
            except ValueError:
                return RiskLevel.HIGH  # Outside working directory

    def _assess_bash_risk(self, command: str) -> RiskLevel:
        """Assess risk of bash command"""
        command_lower = command.lower()

        # Critical commands
        critical_keywords = ['rm -rf /', 'dd if=', 'mkfs', 'format', ':(){', 'sudo rm']
        for keyword in critical_keywords:
            if keyword in command_lower:
                return RiskLevel.CRITICAL

        # High risk commands
        high_risk_keywords = ['rm -r', 'rm -f', 'sudo', 'chmod 777', 'curl | sh', 'wget | sh']
        for keyword in high_risk_keywords:
            if keyword in command_lower:
                return RiskLevel.HIGH

        # Medium risk commands
        medium_risk_keywords = ['rm ', 'mv ', 'chmod', 'chown', 'git push --force']
        for keyword in medium_risk_keywords:
            if keyword in command_lower:
                return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def _assess_api_risk(
        self,
        registration: ExecutionRegistration,
        context: Dict[str, Any]
    ) -> RiskLevel:
        """Assess risk of API call"""
        # Check if large context (costly)
        if 'messages' in context:
            total_chars = sum(len(str(m)) for m in context['messages'])
            if total_chars > 100000:
                return RiskLevel.HIGH
            elif total_chars > 50000:
                return RiskLevel.MEDIUM

        return registration.risk_level

    # ========================================================================
    # PERMISSION PROMPTS
    # ========================================================================

    async def _show_permission_prompt(
        self,
        app,
        session,
        registration: ExecutionRegistration,
        risk: RiskLevel,
        context: Dict[str, Any]
    ) -> bool:
        """
        Show permission prompt in permission buffer

        Returns:
            True if approved, False if denied
        """
        from modules.permissions import PermissionResponse

        import sys
        sys.stderr.write(f"\n[PermissionManager._show_permission_prompt] ENTERED\n")
        sys.stderr.write(f"[PermissionManager] registration.name = {registration.name}\n")
        sys.stderr.write(f"[PermissionManager] registration.metadata = {registration.metadata}\n")
        sys.stderr.write(f"[PermissionManager] registration.metadata type = {type(registration.metadata)}\n")
        sys.stderr.flush()

        # NOTE: custom_prompt_func is now handled by _handle_command_options in executor.py
        # Permission manager only handles traditional permission approval, not command options

        # Build default prompt data with PROPER MARKDOWN FORMATTING
        prompt_data = {
            'title': f'System: {registration.name}',
            'message': self._format_permission_message(registration, risk, context),
            'options': [
                {
                    'text': 'Yes, allow this once',
                    'response': PermissionResponse.ALLOW_ONCE,
                    'data': {}
                },
                {
                    'text': 'Yes, and remember for this item',
                    'response': PermissionResponse.ALLOW_ALWAYS,
                    'data': {}
                },
                {
                    'text': 'Yes, and auto-accept this session',
                    'response': PermissionResponse.ALLOW_SESSION,
                    'data': {}
                },
                {
                    'text': 'No, cancel',
                    'response': PermissionResponse.CANCEL
                }
            ]
        }

        # Check if this is CLI mode (no TUI app available)
        is_cli_mode = not hasattr(app, "query_one") or app.query_one("#prompt-input") is None

        if is_cli_mode:
            sys.stderr.write(f"[PermissionManager._show_permission_prompt] CLI mode detected, using CLI prompt\n")
            sys.stderr.flush()
            # In CLI mode, show interactive terminal prompt
            return await self._show_cli_permission_prompt(prompt_data, context)

        # TUI mode: Use unified permission manager
        sys.stderr.write(f"[PermissionManager._show_permission_prompt] TUI mode detected, using unified manager\n")
        sys.stderr.flush()

        # Show in permission buffer - ROBUST ERROR HANDLING
        try:
            import sys
            sys.stderr.write(f"\n[PermissionManager._show_permission_prompt] Starting for {registration.name}\n")
            sys.stderr.flush()

            print(f"[PermissionManager] Showing permission prompt for {registration.name}")
            from modules.permissions import get_unified_permission_manager

            sys.stderr.write(f"[PermissionManager._show_permission_prompt] Getting buffer manager\n")
            sys.stderr.flush()

            unified_manager = get_unified_permission_manager()

            sys.stderr.write(f"[PermissionManager._show_permission_prompt] Got unified_manager: {type(unified_manager)}\n")
            sys.stderr.write(f"[PermissionManager._show_permission_prompt] Has request_permission: {hasattr(unified_manager, 'request_permission')}\n")
            sys.stderr.flush()

            sys.stderr.write(f"[PermissionManager._show_permission_prompt] Calling unified_manager.request_permission()\n")
            sys.stderr.flush()

            response_data = await unified_manager.request_permission(app, session, prompt_data, timeout=None)

            # Convert unified manager response to option format
            response = response_data.get("response")
            if response in ["allow_once", "allow_session", "allow_always"]:
                option = {"response": response, "data": response_data.get("data", {})}
            else:
                option = {"response": "cancel", "data": {}}


            sys.stderr.write(f"[PermissionManager._show_permission_prompt] request_permission() returned: {response_data}\n")
            sys.stderr.flush()

            if not option:
                return False

            response = option.get('response')
            print(f"[PermissionManager] User response: {response}")

            if response == PermissionResponse.ALLOW_ONCE:
                return True
            elif response == PermissionResponse.ALLOW_ALWAYS:
                key = f"{registration.type.value}:{registration.name}"
                self.allowed_items[key] = True
                self._save_permissions()
                return True
            elif response == PermissionResponse.ALLOW_SESSION:
                self.auto_accept_session = True
                return True
            else:
                return False

        except Exception as e:
            print(f"[PermissionManager] ERROR showing permission prompt: {e}")
            import traceback
            traceback.print_exc()
            # Default deny on error
            return False

    def _format_permission_message(
        self,
        registration: ExecutionRegistration,
        risk: RiskLevel,
        context: Dict[str, Any]
    ) -> str:
        """Format permission message with MARKDOWN like startup buffer - ROBUST"""
        lines = []

        try:
            # Description
            desc = getattr(registration, 'description', 'No description available')
            lines.append(desc)
            lines.append("")

            # Risk level with PROPER markdown
            risk_colors = {
                RiskLevel.SAFE: "green",
                RiskLevel.LOW: "cyan",
                RiskLevel.MEDIUM: "yellow",
                RiskLevel.HIGH: "bright_red",
                RiskLevel.CRITICAL: "red"
            }
            risk_name = risk.value.upper() if hasattr(risk, 'value') else str(risk).upper()
            risk_color = risk_colors.get(risk, "white")
            lines.append(f"Risk Level: [{risk_color}]{risk_name}[/{risk_color}]")

            # Duration
            duration = getattr(registration, 'estimated_duration', None)
            if duration:
                lines.append(f"Duration: {duration}")
            else:
                lines.append("Duration: < 1 minute")

            # Proceed prompt
            lines.append("Proceed?")
            lines.append("")

        except Exception as e:
            print(f"[PermissionManager] ERROR formatting message: {e}")
            lines = ["Permission required", "", "Proceed?", ""]

        # Resources
        if registration.resources_needed:
            lines.append(f"Resources: {', '.join(registration.resources_needed)}")

        # Path warning for file operations
        if 'file_path' in context:
            path_risk = self._assess_path_risk(context['file_path'])
            if path_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                lines.append("")
                lines.append(f"⚠️  PATH WARNING: {path_risk.value.upper()}")
                lines.append(f"Target: {Path(context['file_path']).resolve()}")
                lines.append(f"Current: {Path.cwd().resolve()}")

        # Command preview for bash
        if registration.name == 'Bash' and 'command' in context:
            lines.append("")
            lines.append(f"Command: {context['command']}")

        lines.append("")
        lines.append("Proceed?")

        return "\n".join(lines)

    async def _show_cli_permission_prompt(self, prompt_data: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Show interactive permission prompt in CLI terminal mode.

        Displays the prompt data and waits for user input via stdin.
        """
        import sys
        from modules.permissions import PermissionResponse

        print(f"\n{'='*60}")
        print(f"🔐 {prompt_data.get('title', 'Permission Required')}")
        print(f"{'='*60}")

        # Display message
        message = prompt_data.get('message', 'Permission required')
        print(f"\n{message}\n")

        # Display options
        options = prompt_data.get('options', [])
        if not options:
            print("❌ No options available")
            return False

        print("Options:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option.get('text', 'Unknown option')}")

        print(f"\n{'='*60}")

        # Get user input
        while True:
            try:
                choice = input("Enter your choice (number): ").strip()

                if not choice:
                    print("❌ Please enter a number")
                    continue

                try:
                    choice_num = int(choice)
                except ValueError:
                    print("❌ Please enter a valid number")
                    continue

                if choice_num < 1 or choice_num > len(options):
                    print(f"❌ Please enter a number between 1 and {len(options)}")
                    continue

                # Get selected option
                selected_option = options[choice_num - 1]

                print(f"✅ Selected: {selected_option.get('text')}")

                # Store user selection in context
                context['_custom_prompt_data'] = selected_option

                # Check response type (compare with string values)
                response = selected_option.get('response')
                if response == 'allow_once':
                    return True
                elif response == 'allow_always':
                    # For CLI mode, we can't permanently allow, so treat as once
                    print("ℹ️  Note: CLI mode allows once per session")
                    return True
                elif response == 'allow_session':
                    # Session allow is the same as once in CLI
                    return True
                else:
                    # CANCEL or other rejection
                    return False

            except KeyboardInterrupt:
                print("\n❌ Operation cancelled by user")
                return False
            except EOFError:
                print("\n❌ Input stream closed")
                return False

    # ========================================================================
    # PERSISTENCE
    # ========================================================================

    def _load_permissions(self):
        """Load saved permissions"""
        if not self.permissions_file.exists():
            return

        try:
            with open(self.permissions_file) as f:
                data = json.load(f)

            self.auto_accept_permanent = data.get('auto_accept_permanent', False)
            self.allowed_items = data.get('allowed_items', {})
        except Exception:
            pass

    def _save_permissions(self):
        """Save permissions to file"""
        data = {
            'auto_accept_permanent': self.auto_accept_permanent,
            'allowed_items': self.allowed_items
        }

        try:
            with open(self.permissions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    # ========================================================================
    # MANAGEMENT
    # ========================================================================

    def set_auto_accept_permanent(self, enabled: bool):
        """Enable/disable permanent auto-accept mode"""
        self.auto_accept_permanent = enabled
        self._save_permissions()

    def get_allowed_items(self) -> Dict[str, bool]:
        """Get all permanently allowed items"""
        return self.allowed_items.copy()

    def remove_allowed_item(self, type: ExecutionType, name: str):
        """Remove item from allowed list"""
        key = f"{type.value}:{name}"
        if key in self.allowed_items:
            del self.allowed_items[key]
            self._save_permissions()


# Import asyncio at module level
import asyncio


# Global permission manager instance
_permission_manager = None

def get_permission_manager(app=None, session=None):
    """Get or create global permission manager instance"""
    global _permission_manager
    
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    
    return _permission_manager
