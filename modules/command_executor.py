"""
Unified Command Executor - Permission-First Flow

ALL commands flow through this system:
1. Permission check/prompt
2. Workflow creation
3. Live execution in permission buffer
4. Contextual statusline updates
5. Proper cleanup on completion

Every command becomes interactive and permission-gated by default.
"""

import asyncio
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum


class CommandCategory(Enum):
    """Command categories for permission management"""
    DOCKER = "docker"
    MODEL = "model"
    PROVIDER = "provider"
    LOCAL = "local"
    CONFIG = "config"
    SYSTEM = "system"
    TOOL = "tool"


class CommandRiskLevel(Enum):
    """Risk levels for commands"""
    SAFE = "safe"           # Read-only, no system changes
    LOW = "low"             # Minor changes, easily reversible
    MEDIUM = "medium"       # Significant changes, resource usage
    HIGH = "high"           # Major changes, network/disk operations
    CRITICAL = "critical"   # System-level changes, destructive


@dataclass
class CommandPermission:
    """Permission requirements for a command"""
    command: str
    category: CommandCategory
    risk_level: CommandRiskLevel
    requires_approval: bool
    description: str
    resources_needed: List[str]  # e.g., ["docker", "network", "disk"]
    estimated_duration: str      # e.g., "2-5 minutes"


@dataclass
class CommandStep:
    """A single step in command execution"""
    id: str
    title: str
    description: str
    category: str
    requires_permission: bool
    risk_level: CommandRiskLevel
    execute_func: Optional[Callable] = None
    status: str = "pending"  # pending, in_progress, completed, failed, skipped
    result: Any = None
    error: Optional[str] = None
    progress: int = 0  # 0-100


class UnifiedCommandExecutor:
    """
    Unified execution system for ALL commands

    Features:
    - Permission-first flow
    - Live progress in permission buffer
    - Contextual statusline updates
    - Thread-safe execution
    - Workflow-based for everything
    """

    def __init__(self, app, session):
        self.app = app
        self.session = session
        self.active_commands: Dict[str, 'CommandExecution'] = {}
        self.permission_registry: Dict[str, CommandPermission] = {}

        # Initialize command registry
        self._register_default_commands()

    def _register_default_commands(self):
        """Register default command permissions"""

        # Docker commands
        self.permission_registry["/docker status"] = CommandPermission(
            command="/docker status",
            category=CommandCategory.DOCKER,
            risk_level=CommandRiskLevel.SAFE,
            requires_approval=False,
            description="Check Docker daemon status",
            resources_needed=["docker"],
            estimated_duration="< 5 seconds"
        )

        self.permission_registry["/docker ollama setup"] = CommandPermission(
            command="/docker ollama setup",
            category=CommandCategory.DOCKER,
            risk_level=CommandRiskLevel.HIGH,
            requires_approval=True,
            description="Set up Ollama Docker container (pulls ~2.7GB image)",
            resources_needed=["docker", "network", "disk"],
            estimated_duration="2-5 minutes"
        )

        self.permission_registry["/docker ollama start"] = CommandPermission(
            command="/docker ollama start",
            category=CommandCategory.DOCKER,
            risk_level=CommandRiskLevel.MEDIUM,
            requires_approval=True,
            description="Start Ollama Docker container",
            resources_needed=["docker"],
            estimated_duration="< 10 seconds"
        )

        self.permission_registry["/docker ollama stop"] = CommandPermission(
            command="/docker ollama stop",
            category=CommandCategory.DOCKER,
            risk_level=CommandRiskLevel.MEDIUM,
            requires_approval=True,
            description="Stop Ollama Docker container",
            resources_needed=["docker"],
            estimated_duration="< 10 seconds"
        )

        # Model commands
        self.permission_registry["/model"] = CommandPermission(
            command="/model",
            category=CommandCategory.MODEL,
            risk_level=CommandRiskLevel.SAFE,
            requires_approval=False,
            description="Show current model and available models",
            resources_needed=[],
            estimated_duration="< 1 second"
        )

        self.permission_registry["/model providers"] = CommandPermission(
            command="/model providers",
            category=CommandCategory.PROVIDER,
            risk_level=CommandRiskLevel.SAFE,
            requires_approval=True,
            description="Browse and configure model providers",
            resources_needed=["config"],
            estimated_duration="< 5 seconds"
        )

        self.permission_registry["/local"] = CommandPermission(
            command="/local",
            category=CommandCategory.LOCAL,
            risk_level=CommandRiskLevel.HIGH,
            requires_approval=True,
            description="Set up local models via Ollama",
            resources_needed=["ollama", "network", "disk"],
            estimated_duration="5-30 minutes"
        )

        # Config commands
        self.permission_registry["/config"] = CommandPermission(
            command="/config",
            category=CommandCategory.CONFIG,
            risk_level=CommandRiskLevel.SAFE,
            requires_approval=False,
            description="View configuration",
            resources_needed=["config"],
            estimated_duration="< 1 second"
        )

    def register_command(self, permission: CommandPermission):
        """Register a new command with permissions"""
        self.permission_registry[permission.command] = permission

    def get_permission(self, command: str) -> Optional[CommandPermission]:
        """Get permission info for a command"""
        # Exact match first
        if command in self.permission_registry:
            return self.permission_registry[command]

        # Prefix match (e.g., "/docker" matches "/docker status")
        for registered_cmd, perm in self.permission_registry.items():
            if command.startswith(registered_cmd):
                return perm

        return None

    async def execute_command(
        self,
        command: str,
        steps: List[CommandStep],
        on_complete: Optional[Callable] = None
    ):
        """
        Execute a command with permission-first flow

        Args:
            command: The command being executed
            steps: List of execution steps
            on_complete: Optional callback when command completes
        """

        # Get permission info
        permission = self.get_permission(command)
        if not permission:
            # Unregistered command - default to requiring approval
            permission = CommandPermission(
                command=command,
                category=CommandCategory.SYSTEM,
                risk_level=CommandRiskLevel.MEDIUM,
                requires_approval=True,
                description=f"Execute {command}",
                resources_needed=[],
                estimated_duration="unknown"
            )

        # Create command execution
        execution = CommandExecution(
            command=command,
            permission=permission,
            steps=steps,
            app=self.app,
            session=self.session
        )

        # Track active command
        self.active_commands[command] = execution

        # Update statusline context
        self._update_statusline_context(permission.category, "starting")

        # Show initial permission prompt if needed
        if permission.requires_approval:
            await execution.show_initial_permission_prompt()

            # Status is already set by show_initial_permission_prompt() (no polling needed)
            if execution.status == "cancelled":
                self._update_statusline_context(permission.category, "cancelled")
                del self.active_commands[command]
                return

        # Execute with live progress in permission buffer
        await execution.execute_with_live_progress()

        # Call completion callback
        if on_complete:
            await on_complete(execution)

        # Update statusline
        if execution.status == "completed":
            self._update_statusline_context(permission.category, "completed")
        elif execution.status == "failed":
            self._update_statusline_context(permission.category, "failed")

        # Clean up after showing final status for a moment
        await asyncio.sleep(2)
        del self.active_commands[command]
        self._clear_statusline_context(permission.category)

    def _update_statusline_context(self, category: CommandCategory, status: str):
        """Update statusline with current command context"""
        try:
            from simple_tui import StatusLine
            status_line = self.app.query_one("StatusLine", StatusLine)

            # Map category to statusline indicator
            if category == CommandCategory.DOCKER:
                if status == "starting":
                    status_line.show_indicator("docker", "⋯", "cyan")
                elif status == "completed":
                    status_line.show_indicator("docker", "✓", "green")
                elif status == "failed":
                    status_line.show_indicator("docker", "✗", "red")
                elif status == "cancelled":
                    status_line.hide_indicator("docker")

            # Add more category mappings as needed

        except Exception:
            pass

    def _clear_statusline_context(self, category: CommandCategory):
        """Clear statusline indicator for category"""
        try:
            from simple_tui import StatusLine
            status_line = self.app.query_one("StatusLine", StatusLine)

            if category == CommandCategory.DOCKER:
                status_line.hide_indicator("docker")

        except Exception:
            pass


class CommandExecution:
    """
    Represents a single command execution with live progress
    """

    def __init__(
        self,
        command: str,
        permission: CommandPermission,
        steps: List[CommandStep],
        app,
        session
    ):
        self.command = command
        self.permission = permission
        self.steps = steps
        self.app = app
        self.session = session
        self.status = "pending"  # pending, awaiting_permission, running, completed, failed, cancelled
        self.current_step_index = 0

    async def show_initial_permission_prompt(self):
        """Show initial permission prompt for command"""
        from modules.permission_prompt import PermissionResponse

        # Build permission prompt
        prompt_data = {
            'title': f'{self.permission.category.value.title()} Command',
            'message': f'{self.permission.description}\n\n'
                      f'Risk Level: {self.permission.risk_level.value}\n'
                      f'Resources: {", ".join(self.permission.resources_needed)}\n'
                      f'Duration: {self.permission.estimated_duration}\n\n'
                      f'Proceed with execution?',
            'options': [
                {
                    'text': 'Yes, execute',
                    'response': PermissionResponse.ALLOW_ONCE,
                    'data': {'command': self.command}
                },
                {
                    'text': 'No, cancel',
                    'response': PermissionResponse.CANCEL
                }
            ]
        }

        # Use permission buffer manager (non-blocking)
        from .permissions import get_unified_permission_manager

        manager = get_unified_permission_manager().get_buffer_manager()

        # Set status
        self.status = "awaiting_permission"
        self.session._current_command_execution = self

        try:
            # Non-blocking permission prompt via manager
            option = await manager.prompt(self.app, self.session, prompt_data, timeout=30.0)

            if not option or option.get('response') == 'cancel':
                self.status = "cancelled"
                self.session._current_command_execution = None
                return

        except asyncio.TimeoutError:
            self.status = "timeout"
            self.session._current_command_execution = None
            return

    async def execute_with_live_progress(self):
        """Execute command with live progress updates using permission buffer manager"""
        from .permissions import get_unified_permission_manager

        manager = get_unified_permission_manager().get_buffer_manager()
        self.status = "running"

        # Execute each step
        for i, step in enumerate(self.steps):
            self.current_step_index = i

            # Build progress display
            progress_data = {
                'title': f'{self.permission.category.value.title()}: {self.command}',
                'message': f'Executing command steps...\n\nCurrent: {step.title}',
                'workflow_status': {
                    'steps': [
                        {
                            'title': s.title,
                            'status': s.status,
                            'error': s.error
                        }
                        for s in self.steps
                    ],
                    'current_step': i
                },
                'options': [
                    {
                        'text': 'Cancel execution',
                        'response': 'cancel',
                        'data': {'command': self.command}
                    }
                ] if step.requires_permission else []
            }

            # Update buffer with progress (non-blocking)
            manager.update(progress_data)

            # Check if step requires permission
            if step.requires_permission:
                try:
                    option = await manager.prompt(self.app, self.session, progress_data, timeout=30.0)

                    if not option or option.get('response') == 'cancel':
                        self.status = "cancelled"
                        manager.clear()
                        return

                except asyncio.TimeoutError:
                    self.status = "timeout"
                    manager.clear()
                    return

            # Execute step
            step.status = "in_progress"
            progress_data['workflow_status']['steps'][i]['status'] = 'in_progress'
            manager.update(progress_data)

            self.app.write(f"[cyan]▸ {step.title}...[/cyan]\n")

            try:
                if step.execute_func:
                    step.result = await step.execute_func()

                step.status = "completed"
                progress_data['workflow_status']['steps'][i]['status'] = 'completed'
                self.app.write(f"[green]✓ {step.title}[/green]\n")
                if step.result:
                    self.app.write(f"[dim]{step.result}[/dim]\n")
                self.app.write("\n")

            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                progress_data['workflow_status']['steps'][i]['status'] = 'failed'
                progress_data['workflow_status']['steps'][i]['error'] = str(e)
                self.app.write(f"[red]✗ {step.title} - {e}[/red]\n\n")

                # Update and show error via MANAGER (not direct write!)
                manager.update(progress_data)
                await asyncio.sleep(3)

                self.status = "failed"
                manager.clear()
                return

            # Update progress via MANAGER (not direct write!)
            manager.update(progress_data)

        # All steps complete!
        self.status = "completed"
        self.app.write(f"[bold green]✓ {self.command} completed successfully![/bold green]\n\n")

        # Clear permission buffer after showing final status
        await asyncio.sleep(1)
        manager.clear()
