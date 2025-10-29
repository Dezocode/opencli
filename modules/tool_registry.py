"""
Tool Registry - Permission-First Execution for ALL Tools

Registers ALL API tools and ensures they flow through:
1. Permission manager
2. Permission buffer for progress
3. Multithreaded execution with proper async
4. Background status in togglable statusline
"""

import asyncio
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class ToolCategory(Enum):
    """Tool categories for permission management"""
    API_CALL = "api_call"
    FILE_OPERATION = "file_operation"
    NETWORK = "network"
    DOCKER = "docker"
    DATABASE = "database"
    SYSTEM = "system"


class ToolRiskLevel(Enum):
    """Risk levels for tools"""
    SAFE = "safe"           # Read-only
    LOW = "low"             # Minor changes
    MEDIUM = "medium"       # Significant changes
    HIGH = "high"           # Major changes
    CRITICAL = "critical"   # Destructive


@dataclass
class ToolPermission:
    """Permission requirements for a tool"""
    tool_name: str
    category: ToolCategory
    risk_level: ToolRiskLevel
    requires_approval: bool
    description: str
    can_run_background: bool  # If True, shows in statusline
    estimated_duration: str


@dataclass
class ToolExecution:
    """Represents a tool execution with status tracking"""
    tool_name: str
    status: str  # "pending", "running", "completed", "failed"
    progress: int  # 0-100
    result: Any = None
    error: Optional[str] = None
    background: bool = False  # Running in background


class ToolRegistry:
    """
    Registry for ALL tools with permission-first execution

    Features:
    - Permission gates for every tool
    - Background execution with statusline display
    - Live progress in permission buffer
    - Proper async/multithreaded execution
    """

    def __init__(self, app, session):
        self.app = app
        self.session = session
        self.tool_permissions: Dict[str, ToolPermission] = {}
        self.active_tools: Dict[str, ToolExecution] = {}

        # Register default tools
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default API tools and operations"""

        # OpenAI API calls
        self.tool_permissions["openai_chat_completion"] = ToolPermission(
            tool_name="openai_chat_completion",
            category=ToolCategory.API_CALL,
            risk_level=ToolRiskLevel.MEDIUM,
            requires_approval=False,  # Fast, frequent - no approval needed
            description="Call OpenAI Chat Completion API",
            can_run_background=False,  # Foreground only
            estimated_duration="< 5 seconds"
        )

        # Anthropic API calls
        self.tool_permissions["anthropic_messages"] = ToolPermission(
            tool_name="anthropic_messages",
            category=ToolCategory.API_CALL,
            risk_level=ToolRiskLevel.MEDIUM,
            requires_approval=False,
            description="Call Anthropic Messages API",
            can_run_background=False,
            estimated_duration="< 5 seconds"
        )

        # Docker operations (already have unified commands, but tools too)
        self.tool_permissions["docker_container_create"] = ToolPermission(
            tool_name="docker_container_create",
            category=ToolCategory.DOCKER,
            risk_level=ToolRiskLevel.HIGH,
            requires_approval=True,
            description="Create Docker container",
            can_run_background=True,  # Can run in background
            estimated_duration="10-30 seconds"
        )

        self.tool_permissions["docker_image_pull"] = ToolPermission(
            tool_name="docker_image_pull",
            category=ToolCategory.DOCKER,
            risk_level=ToolRiskLevel.MEDIUM,
            requires_approval=True,
            description="Pull Docker image from registry",
            can_run_background=True,
            estimated_duration="1-5 minutes"
        )

        # File operations
        self.tool_permissions["file_write"] = ToolPermission(
            tool_name="file_write",
            category=ToolCategory.FILE_OPERATION,
            risk_level=ToolRiskLevel.MEDIUM,
            requires_approval=True,
            description="Write to file",
            can_run_background=False,
            estimated_duration="< 1 second"
        )

        self.tool_permissions["file_delete"] = ToolPermission(
            tool_name="file_delete",
            category=ToolCategory.FILE_OPERATION,
            risk_level=ToolRiskLevel.HIGH,
            requires_approval=True,
            description="Delete file",
            can_run_background=False,
            estimated_duration="< 1 second"
        )

        # Network operations
        self.tool_permissions["http_request"] = ToolPermission(
            tool_name="http_request",
            category=ToolCategory.NETWORK,
            risk_level=ToolRiskLevel.MEDIUM,
            requires_approval=True,
            description="Make HTTP request",
            can_run_background=True,
            estimated_duration="< 10 seconds"
        )

    def register_tool(self, permission: ToolPermission):
        """Register a new tool with permissions"""
        self.tool_permissions[permission.tool_name] = permission

    async def execute_tool(
        self,
        tool_name: str,
        execute_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a tool with permission-first flow

        Args:
            tool_name: Name of the tool
            execute_func: Async function to execute
            *args: Arguments for execute_func
            **kwargs: Keyword arguments for execute_func

        Returns:
            Result of execute_func
        """

        # Get permission info
        permission = self.tool_permissions.get(tool_name)
        if not permission:
            # Unregistered tool - default to requiring approval
            permission = ToolPermission(
                tool_name=tool_name,
                category=ToolCategory.SYSTEM,
                risk_level=ToolRiskLevel.MEDIUM,
                requires_approval=True,
                description=f"Execute {tool_name}",
                can_run_background=False,
                estimated_duration="unknown"
            )

        # Check if approval needed
        if permission.requires_approval:
            # Show permission prompt
            approved = await self._show_tool_permission_prompt(permission)
            if not approved:
                raise PermissionError(f"Permission denied for {tool_name}")

        # Create execution tracking
        execution = ToolExecution(
            tool_name=tool_name,
            status="running",
            progress=0,
            background=permission.can_run_background
        )

        self.active_tools[tool_name] = execution

        # Update statusline if background
        if permission.can_run_background:
            self._update_statusline_for_tool(tool_name, "running")

        try:
            # Execute in background if allowed
            if permission.can_run_background:
                # Run in thread pool
                result = await asyncio.to_thread(execute_func, *args, **kwargs)
            else:
                # Run in foreground
                result = await execute_func(*args, **kwargs)

            # Success
            execution.status = "completed"
            execution.progress = 100
            execution.result = result

            if permission.can_run_background:
                self._update_statusline_for_tool(tool_name, "completed")

            return result

        except Exception as e:
            # Failure
            execution.status = "failed"
            execution.error = str(e)

            if permission.can_run_background:
                self._update_statusline_for_tool(tool_name, "failed")

            raise

        finally:
            # Cleanup after delay
            await asyncio.sleep(2)
            if tool_name in self.active_tools:
                del self.active_tools[tool_name]

            if permission.can_run_background:
                self._clear_statusline_for_tool(tool_name)

    async def _show_tool_permission_prompt(self, permission: ToolPermission) -> bool:
        """Show permission prompt for tool execution"""

        from modules.permissions import PermissionResponse

        prompt_data = {
            'title': f'{permission.category.value.title()} Tool',
            'message': f'{permission.description}\n\n'
                      f'Risk Level: {permission.risk_level.value}\n'
                      f'Duration: {permission.estimated_duration}\n'
                      f'Background: {"Yes" if permission.can_run_background else "No"}\n\n'
                      f'Allow execution?',
            'options': [
                {
                    'text': 'Yes, allow',
                    'response': PermissionResponse.ALLOW_ONCE,
                    'data': {'tool': permission.tool_name}
                },
                {
                    'text': 'No, deny',
                    'response': PermissionResponse.CANCEL
                }
            ]
        }

        # Show in permission buffer
        prompt_input = self.app.query_one("#prompt-input")
        # Use permission buffer manager (non-blocking)
        from permissions import get_permission_buffer_manager

        manager = get_permission_buffer_manager()
        self.session._current_tool_execution = permission.tool_name

        try:
            option = await manager.prompt(self.app, self.session, prompt_data, timeout=30.0)

            if not option:
                return False

            response = option.get('response')
            return response in ['allow_once', 'allow_always']

        except asyncio.TimeoutError:
            return False

    def _update_statusline_for_tool(self, tool_name: str, status: str):
        """Update statusline with tool status"""

        try:
            from simple_tui import StatusLine
            status_line = self.app.query_one("StatusLine", StatusLine)

            # Map status to indicator
            if status == "running":
                status_line.show_indicator(tool_name, "⋯", "cyan")
            elif status == "completed":
                status_line.show_indicator(tool_name, "✓", "green")
            elif status == "failed":
                status_line.show_indicator(tool_name, "✗", "red")

        except Exception:
            pass

    def _clear_statusline_for_tool(self, tool_name: str):
        """Clear statusline indicator for tool"""

        try:
            from simple_tui import StatusLine
            status_line = self.app.query_one("StatusLine", StatusLine)
            status_line.hide_indicator(tool_name)
        except Exception:
            pass

    def get_active_tools(self) -> List[ToolExecution]:
        """Get list of currently executing tools"""
        return list(self.active_tools.values())

    def get_background_tools(self) -> List[ToolExecution]:
        """Get list of tools running in background"""
        return [t for t in self.active_tools.values() if t.background]


# Global tool registry instance (initialized in OpenCLITUI.on_mount)
_tool_registry: Optional[ToolRegistry] = None


def get_tool_registry(app, session) -> ToolRegistry:
    """Get or create global tool registry"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry(app, session)
    return _tool_registry


async def execute_tool_with_permissions(
    app,
    session,
    tool_name: str,
    execute_func: Callable,
    *args,
    **kwargs
) -> Any:
    """
    Execute any tool with permission-first flow

    Use this wrapper for ALL tool executions to ensure:
    - Permission gates are respected
    - Progress shown in buffer or statusline
    - Proper async/multithreaded execution
    - Background tools show in statusline

    Example:
        result = await execute_tool_with_permissions(
            app, session,
            "docker_image_pull",
            pull_image_async,
            "ollama/ollama:latest"
        )
    """

    registry = get_tool_registry(app, session)
    return await registry.execute_tool(tool_name, execute_func, *args, **kwargs)
