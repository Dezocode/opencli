"""
Async Permission System for TUI
Integrates ToolPermissionManager with buffered UI prompts
"""

import asyncio
from pathlib import Path
from typing import Optional, Tuple

try:
    from .tool_permissions import ToolPermissionManager, RiskLevel
    from .permission_prompt import PermissionTemplates, PermissionResponse
except (ImportError, ValueError):
    from tool_permissions import ToolPermissionManager, RiskLevel
    from permission_prompt import PermissionTemplates, PermissionResponse


class AsyncPermissionHandler:
    """
    Handles async permission prompts in the TUI
    Coordinates between ToolPermissionManager and UI prompts
    """

    def __init__(self, permission_manager: ToolPermissionManager, app=None):
        self.permission_manager = permission_manager
        self.app = app
        self._pending_response = None
        self._response_event = None

    async def check_and_prompt(
        self,
        tool_name: str,
        args: dict,
        current_dir: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Check if tool execution requires permission and prompt if needed

        Returns:
            (allowed: bool, reason: str)
        """
        # Check if we should prompt
        should_prompt, reason, risk_level = self.permission_manager.should_prompt(
            tool_name, args, current_dir
        )

        if not should_prompt:
            return True, reason

        # Show permission prompt (silently - no debug messages)
        return await self._show_permission_prompt(tool_name, args, risk_level, current_dir)

    async def _show_permission_prompt(
        self,
        tool_name: str,
        args: dict,
        risk_level: RiskLevel,
        current_dir: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Show permission prompt in TUI and wait for response

        Returns:
            (allowed: bool, reason: str)
        """
        # Generate prompt data based on tool type
        prompt_data = self._generate_prompt_data(tool_name, args, current_dir)

        if not prompt_data:
            # Fallback - allow if we can't generate prompt
            return True, "no prompt available"

        # Create response event
        self._response_event = asyncio.Event()
        self._pending_response = None

        # Show prompt in UI
        if self.app and hasattr(self.app, 'stream_display'):
            self.app.stream_display.add_permission_prompt(prompt_data)

        # Wait for user response (with timeout)
        try:
            await asyncio.wait_for(self._response_event.wait(), timeout=300)  # 5 min timeout
        except asyncio.TimeoutError:
            # Timeout - deny by default
            if self.app and hasattr(self.app, 'stream_display'):
                self.app.stream_display.remove_permission_prompt()
            return False, "prompt timeout"

        # Process response
        response = self._pending_response

        if not response:
            return False, "no response"

        # Handle different response types
        if response['response'] == PermissionResponse.ALLOW_ONCE:
            return True, "user allowed once"

        elif response['response'] == PermissionResponse.ALLOW_ALWAYS:
            # Add tool to allowed list
            tool = response.get('data', {}).get('tool', tool_name)
            self.permission_manager.add_allowed_tool(tool)
            return True, f"user allowed always for {tool}"

        elif response['response'] == PermissionResponse.ALLOW_DOMAIN:
            # For WebFetch - save domain permission
            # TODO: Implement domain-based permissions
            return True, "user allowed for domain"

        elif response['response'] == PermissionResponse.DENY:
            return False, "user denied"

        elif response['response'] == PermissionResponse.CANCEL:
            return False, "user cancelled"

        return False, "unknown response"

    def _generate_prompt_data(
        self,
        tool_name: str,
        args: dict,
        current_dir: Optional[str] = None
    ) -> Optional[dict]:
        """Generate permission prompt data for the tool"""

        if tool_name == "Edit":
            return PermissionTemplates.file_edit(
                file_path=args.get('file_path', ''),
                old_str=args.get('old_string', ''),
                new_str=args.get('new_string', '')
            )

        elif tool_name == "Write":
            return PermissionTemplates.file_write(
                file_path=args.get('file_path', ''),
                content=args.get('content', '')
            )

        elif tool_name == "Bash":
            return PermissionTemplates.bash_command(
                command=args.get('command', ''),
                description=args.get('description')
            )

        elif tool_name == "WebFetch":
            return PermissionTemplates.webfetch(
                url=args.get('url', '')
            )

        elif tool_name == "ConfigureHeaders":
            return PermissionTemplates.configure_headers(
                provider=args.get('provider', ''),
                model=args.get('model'),
                issue=args.get('issue'),
                current_headers=args.get('current_headers', {}),
                proposed_headers=args.get('proposed_headers')
            )

        elif tool_name == "Refactoring":
            return PermissionTemplates.code_refactoring(
                plan=args.get('plan', {}),
                result=args.get('result', {})
            )

        # Fallback - generic prompt
        return {
            'title': f'{tool_name} Operation',
            'message': f'Claude wants to execute a {tool_name} operation.\n\nDo you want to allow this?',
            'details': {'tool': tool_name, **args},
            'options': [
                {
                    'text': 'Yes, allow this operation',
                    'response': PermissionResponse.ALLOW_ONCE
                },
                {
                    'text': f"Yes, and don't ask again for {tool_name}",
                    'response': PermissionResponse.ALLOW_ALWAYS,
                    'data': {'tool': tool_name}
                },
                {
                    'text': 'No, skip this operation (esc)',
                    'response': PermissionResponse.DENY
                }
            ]
        }

    def handle_response(self, response: dict):
        """
        Handle permission response from UI

        Args:
            response: Dict with 'response' (PermissionResponse) and 'data'
        """
        self._pending_response = response

        # Remove prompt from UI
        if self.app and hasattr(self.app, 'stream_display'):
            self.app.stream_display.remove_permission_prompt()

        # Signal that response was received
        if self._response_event:
            self._response_event.set()


# Global handler instance (set by TUI app)
_global_handler: Optional[AsyncPermissionHandler] = None


def set_global_handler(handler: AsyncPermissionHandler):
    """Set the global permission handler"""
    global _global_handler
    _global_handler = handler


def get_global_handler() -> Optional[AsyncPermissionHandler]:
    """Get the global permission handler"""
    return _global_handler
