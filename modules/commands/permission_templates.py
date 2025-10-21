"""
DEPRECATED - Use SDK-Compliant Command Pattern Instead

This file has been replaced by the SDK-compliant command pattern where each
command file implements its own `*_prompt()` and `*()` handler functions.

NEW PATTERN:
Each command now has two functions:
1. {command}_prompt(app, session, registration, context) -> prompt_data
   - Creates interactive permission buffer prompt
   - Returns prompt_data dict with options
   - Called by PermissionManager before execution

2. {command}(app, session, **context) -> None
   - Executes command after user approval
   - Reads user selection from context['_custom_prompt_data']
   - No redundant permission checks

EXAMPLE:
See modules/commands/basic_commands.py for reference implementation:
- show_help_prompt() - creates interactive buffer prompt
- show_help() - executes based on user selection

MIGRATION:
Instead of using CommandPermissionTemplate.create_*_prompt(), commands now:
1. Define their own {command}_prompt() function
2. Register with custom_prompt_func parameter in command_registry.py
3. PermissionManager calls the prompt function automatically
4. Handler reads from context['_custom_prompt_data']

Date Deprecated: 2025-10-18
Replaced By: SDK-compliant {command}_prompt() pattern in command files

====================================================================
LEGACY CODE BELOW - DO NOT USE
====================================================================

Permission Buffer Templates for Commands

All commands must create permission requests using these templates.
Templates populate the permission buffer with interactive UI before execution.
"""

from typing import List, Dict, Optional, Any


class CommandPermissionTemplate:
    """Base template for command permission requests"""

    @staticmethod
    def create_basic_command_prompt(
        command_name: str,
        description: str,
        risk_level: str,
        category: str,
        preview_data: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        Create permission prompt for basic commands

        Args:
            command_name: Name of the command (e.g., "/help")
            description: What the command does
            risk_level: SAFE, LOW, MEDIUM, HIGH, CRITICAL
            category: Command category
            preview_data: Optional data to preview in prompt

        Returns:
            Permission prompt dict for buffer
        """
        message_parts = [
            f"[bold]{command_name}[/bold]",
            f"\n{description}\n",
            f"\n[dim]Category:[/dim] {category}",
            f"\n[dim]Risk:[/dim] {risk_level}",
        ]

        if preview_data:
            message_parts.append("\n\n[bold]Preview:[/bold]")
            for key, value in preview_data.items():
                message_parts.append(f"\n  [cyan]{key}:[/cyan] {value}")

        return {
            'title': f"Execute {command_name}?",
            'message': "".join(message_parts),
            'options': [
                {
                    'text': '✓ Execute',
                    'response': 'approved',
                    'data': {'action': 'execute', 'command': command_name}
                },
                {
                    'text': '○ Execute Once (Don\'t Remember)',
                    'response': 'approved_once',
                    'data': {'action': 'execute_once', 'command': command_name}
                },
                {
                    'text': '✗ Cancel',
                    'response': 'denied',
                    'data': {'action': 'cancel'}
                }
            ]
        }

    @staticmethod
    def create_destructive_command_prompt(
        command_name: str,
        description: str,
        affected_items: List[str],
        warning_message: str
    ) -> Dict:
        """Create permission prompt for destructive commands"""
        items_preview = "\n".join(f"  • {item}" for item in affected_items[:5])
        if len(affected_items) > 5:
            items_preview += f"\n  ... and {len(affected_items) - 5} more"

        return {
            'title': f"⚠️  {command_name} - Destructive Operation",
            'message': f"""[bold red]{warning_message}[/bold red]

{description}

[bold]Will affect:[/bold]
{items_preview}

[dim]This action may not be reversible.[/dim]""",
            'options': [
                {
                    'text': '⚠️  Yes, I understand the risk',
                    'response': 'approved',
                    'data': {'action': 'execute', 'confirmed': True}
                },
                {
                    'text': '✗ Cancel',
                    'response': 'denied',
                    'data': {'action': 'cancel'}
                }
            ]
        }

    @staticmethod
    def create_info_command_prompt(
        command_name: str,
        info_summary: Dict[str, str],
        allow_export: bool = False
    ) -> Dict:
        """Create permission prompt for informational commands"""
        info_text = []
        for key, value in info_summary.items():
            info_text.append(f"[cyan]{key}:[/cyan] {value}")

        message = f"""[bold]Information Request: {command_name}[/bold]

{chr(10).join(info_text)}

[dim]This command is read-only and safe to execute.[/dim]"""

        options = [
            {
                'text': '✓ Show Information',
                'response': 'approved',
                'data': {'action': 'execute'}
            }
        ]

        if allow_export:
            options.insert(1, {
                'text': '↓ Show and Export to File',
                'response': 'approved',
                'data': {'action': 'execute_and_export'}
            })

        options.append({
            'text': '✗ Cancel',
            'response': 'denied',
            'data': {'action': 'cancel'}
        })

        return {
            'title': f"Execute {command_name}?",
            'message': message,
            'options': options
        }

    @staticmethod
    def create_configuration_prompt(
        command_name: str,
        current_settings: Dict[str, Any],
        proposed_changes: Dict[str, Any]
    ) -> Dict:
        """Create permission prompt for configuration commands"""
        changes_text = []
        for key, new_value in proposed_changes.items():
            old_value = current_settings.get(key, "[not set]")
            changes_text.append(
                f"  [yellow]{key}:[/yellow]\n"
                f"    From: {old_value}\n"
                f"    To: {new_value}"
            )

        return {
            'title': f"Configure {command_name}",
            'message': f"""[bold]Configuration Changes:[/bold]

{chr(10).join(changes_text)}

[dim]These changes will affect the current session.[/dim]""",
            'options': [
                {
                    'text': '✓ Apply Changes',
                    'response': 'approved',
                    'data': {'action': 'apply', 'changes': proposed_changes}
                },
                {
                    'text': '○ Preview Only',
                    'response': 'preview',
                    'data': {'action': 'preview'}
                },
                {
                    'text': '✗ Cancel',
                    'response': 'denied',
                    'data': {'action': 'cancel'}
                }
            ]
        }

    @staticmethod
    def create_workflow_prompt(
        workflow_name: str,
        steps: List[Dict[str, str]],
        estimated_duration: Optional[str] = None
    ) -> Dict:
        """Create permission prompt for multi-step workflows"""
        return {
            'title': f"Start Workflow: {workflow_name}",
            'message': f"""[bold]Multi-Step Workflow[/bold]

This workflow will execute {len(steps)} steps:
{chr(10).join(f"{i+1}. {step['title']}" for i, step in enumerate(steps))}

{f"[dim]Estimated time: {estimated_duration}[/dim]" if estimated_duration else ""}

[dim]You can cancel at any step.[/dim]""",
            'options': [
                {
                    'text': '▶ Start Workflow',
                    'response': 'approved',
                    'data': {'action': 'start_workflow', 'steps': steps}
                },
                {
                    'text': '○ Review Steps First',
                    'response': 'review',
                    'data': {'action': 'review'}
                },
                {
                    'text': '✗ Cancel',
                    'response': 'denied',
                    'data': {'action': 'cancel'}
                }
            ],
            'workflow_status': {
                'steps': steps,
                'current_step': 0
            }
        }


def get_permission_manager_for_command(app) -> 'PermissionManager':
    """
    Get permission manager instance for creating prompts

    Args:
        app: TUI app instance

    Returns:
        PermissionManager instance
    """
    from ..execution.permission_manager import get_permission_manager
    # Assuming session is available through app
    session = getattr(app, 'session', None)
    return get_permission_manager(app, session)
