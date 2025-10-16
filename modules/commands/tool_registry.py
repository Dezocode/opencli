"""Tool Registration - All tool handlers registered here

Imports and registers all API tools with SDK enforcement.
Called by main registry.py during initialization.
"""

from ..execution.registry import ExecutionType, ExecutionCategory, RiskLevel


async def register_all_tools(executor, _safe_register, _update_sdk_buffer):
    """Register ALL tools - ASYNC

    Args:
        executor: ExecutionSystem instance
        _safe_register: SDK-enforced registration function
        _update_sdk_buffer: Live progress update function
    """

    _update_sdk_buffer(executor.app, current_step="Registering core tools", current_file="core_tools.py", cmd_count=len(executor.registry.commands))
    from ..tools.core_tools import (
        tool_read,
        tool_write,
        tool_edit,
        tool_bash,
        tool_glob,
        tool_grep,
        tool_github,
        tool_configure_headers,
    )

    await _safe_register(
        executor, ExecutionType.TOOL, 'Read', tool_read,
        ExecutionCategory.FILE, RiskLevel.SAFE, requires_approval=True,
        description="Read file contents",
    )

    await _safe_register(
        executor, ExecutionType.TOOL, 'Write', tool_write,
        ExecutionCategory.FILE, RiskLevel.MEDIUM, requires_approval=True,
        description="Write or create a file",
    )

    await _safe_register(
        executor, ExecutionType.TOOL, 'Edit', tool_edit,
        ExecutionCategory.FILE, RiskLevel.MEDIUM, requires_approval=True,
        description="Edit an existing file",
    )

    await _safe_register(
        executor, ExecutionType.TOOL, 'Glob', tool_glob,
        ExecutionCategory.SEARCH, RiskLevel.SAFE, requires_approval=True,
        description="Find files by glob pattern",
    )

    await _safe_register(
        executor, ExecutionType.TOOL, 'Grep', tool_grep,
        ExecutionCategory.SEARCH, RiskLevel.SAFE, requires_approval=True,
        description="Search file contents via grep",
    )

    await _safe_register(
        executor, ExecutionType.TOOL, 'Bash', tool_bash,
        ExecutionCategory.BASH, RiskLevel.HIGH, requires_approval=True,
        description="Execute shell commands",
        timeout=120,
    )

    await _safe_register(
        executor, ExecutionType.TOOL, 'GitHub', tool_github,
        ExecutionCategory.NETWORK, RiskLevel.MEDIUM, requires_approval=True,
        description="Perform authenticated GitHub operations",
    )

    await _safe_register(
        executor, ExecutionType.TOOL, 'ConfigureHeaders', tool_configure_headers,
        ExecutionCategory.SYSTEM, RiskLevel.MEDIUM, requires_approval=True,
        description="Auto-configure API request headers for models",
    )

    # Update final tool count
    _update_sdk_buffer(executor.app, current_step="Tool registration complete", tool_count=len(executor.registry.tools))
