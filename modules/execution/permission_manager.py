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

        # Skip if doesn't require approval
        if not registration.requires_approval:
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
        from modules.permission_prompt import PermissionResponse

        # Check if command provides custom prompt function
        custom_prompt_func = registration.metadata.get('custom_prompt_func')
        if custom_prompt_func:
            # Let handler provide custom prompt with configuration options
            prompt_data = await custom_prompt_func(app, session, registration, context)
            # Custom prompts handle their own approval logic
            # Store data in context for handler to use
            context['_custom_prompt_data'] = prompt_data
            return True  # Approved, handler will manage the interaction

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

        # Show in permission buffer - ROBUST ERROR HANDLING
        try:
            print(f"[PermissionManager] Showing permission prompt for {registration.name}")
            prompt_input = app.query_one("#prompt-input")

            if not prompt_input:
                print("[PermissionManager] ERROR: Could not find #prompt-input widget")
                return False

            print(f"[PermissionManager] Setting permission_prompt_data...")

            # Set up event FIRST before showing UI
            session._awaiting_permission = True
            session._permission_response = None

            # Create asyncio.Event for efficient waiting (no busy loop!)
            session._permission_event = asyncio.Event()

            # Now set the data - reactive watcher will handle refresh + focus
            prompt_input.permission_prompt_data = prompt_data
            prompt_input.permission_selected_option = 0
            # DON'T call refresh() - reactive watcher handles it!
            print(f"[PermissionManager] Permission prompt set (watcher will refresh)")

            # CRITICAL: Yield to event loop so UI can update BEFORE we start waiting
            await asyncio.sleep(0)

            # Wait for user response using Event (efficient, non-blocking)
            print(f"[PermissionManager] Waiting for permission response (event-driven)...")
            try:
                await asyncio.wait_for(session._permission_event.wait(), timeout=30.0)
                print(f"[PermissionManager] Permission event received!")
            except asyncio.TimeoutError:
                print("[PermissionManager] WARNING: Permission request timed out after 30s")
                session._awaiting_permission = False
                return False

            # Check response
            response = getattr(session, '_permission_response', None)
            print(f"[PermissionManager] User response: {response}")

            if response == PermissionResponse.ALLOW_ONCE:
                return True
            elif response == PermissionResponse.ALLOW_ALWAYS:
                # Save to allowed items
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
            # Clear permission state
            if hasattr(session, '_awaiting_permission'):
                session._awaiting_permission = False
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
                RiskLevel.HIGH: "orange",
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
