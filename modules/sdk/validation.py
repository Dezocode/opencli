"""
SDK Validation Utilities

Validates ExecutionRegistry contains required commands and tools.
Legacy validation against CommandRegistry removed - ExecutionRegistry is now the single source of truth.
"""

from __future__ import annotations
from typing import Dict, List


def validate_full_coverage(executor) -> Dict[str, List[str]]:
    """
    Validate that ExecutionRegistry has required commands and tools registered.

    Args:
        executor: ExecutionSystem instance (with populated registry)

    Returns:
        Dict with validation results

    Note:
        Since ExecutionRegistry is now the single source of truth,
        we just validate it has content. No comparison to legacy systems.
    """
    import sys

    registered_commands = list(executor.registry.commands.keys())
    registered_tools = list(executor.registry.tools.keys())

    sys.stderr.write(f"[SDK.validation] Commands registered: {len(registered_commands)}\n")
    sys.stderr.write(f"[SDK.validation] Tools registered: {len(registered_tools)}\n")
    sys.stderr.flush()

    # Validation: Ensure we have at least some core commands
    required_commands = ['/help', '/status', '/model', '/local']
    missing_required = [cmd for cmd in required_commands if cmd not in registered_commands]

    if missing_required:
        sys.stderr.write(f"[SDK.validation] WARNING: Missing required commands: {missing_required}\n")
        sys.stderr.flush()

    return {
        'commands': registered_commands,
        'tools': registered_tools,
        'missing_required': missing_required
    }
