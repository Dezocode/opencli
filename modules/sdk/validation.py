"""
SDK Validation Utilities

Ensures the unified execution registry actually covers every command and tool
declared in the legacy registries. This prevents silent omissions where a
command shows up in autocomplete/help but never receives an SDK registration.
"""

from __future__ import annotations

from typing import Dict, List, Set

from command_registry import CommandRegistry
from tool_permissions import ToolPermissionManager


def _normalize_subcommand(parent: str, subcommand: str) -> str | None:
    """
    Build a fully-qualified command name while skipping dynamic placeholders.
    """
    normalized = subcommand.strip()

    # Ignore dynamic entries (placeholders like <file>, {mode}, etc.)
    if not normalized:
        return None

    if any(token in normalized for token in ("<", "{", "[", "]", ">")):
        return None

    return f"{parent} {normalized}".strip()


def collect_expected_commands() -> Set[str]:
    """
    Return the canonical set of command identifiers from CommandRegistry.

    Includes base commands and concrete subcommands (excluding placeholders).
    """
    registry = CommandRegistry()
    expected: Set[str] = set()

    for command, info in registry.available_commands.items():
        expected.add(command)

        subcommands: Dict[str, str] = info.get("subcommands", {}) or {}
        for sub_name in subcommands.keys():
            normalized = _normalize_subcommand(command, sub_name)
            if normalized:
                expected.add(normalized)

    return expected


def collect_expected_tools() -> Set[str]:
    """
    Return the canonical set of tool identifiers from ToolPermissionManager.
    """
    permission_manager = ToolPermissionManager()
    return set(permission_manager.tool_risks.keys())


def validate_full_coverage(executor) -> Dict[str, List[str]]:
    """
    Validate that every expected command/tool has an SDK registration.

    Args:
        executor: ExecutionSystem instance (with populated registry)

    Returns:
        Dict with missing command/tool lists for additional reporting.

    Raises:
        ValueError: if any expected command or tool lacks a registration.
    """
    registered_commands = set(executor.registry.commands.keys())
    registered_tools = set(executor.registry.tools.keys())

    expected_commands = collect_expected_commands()
    expected_tools = collect_expected_tools()

    missing_commands = sorted(expected_commands - registered_commands)
    missing_tools = sorted(expected_tools - registered_tools)

    if missing_commands or missing_tools:
        parts: List[str] = []
        if missing_commands:
            preview = ", ".join(missing_commands[:10])
            if len(missing_commands) > 10:
                preview += ", …"
            parts.append(
                f"missing command registrations ({len(missing_commands)}): {preview}"
            )

        if missing_tools:
            preview = ", ".join(missing_tools[:10])
            if len(missing_tools) > 10:
                preview += ", …"
            parts.append(
                f"missing tool registrations ({len(missing_tools)}): {preview}"
            )

        message = "SDK validation failed – " + " | ".join(parts)
        raise ValueError(message)

    return {
        "missing_commands": missing_commands,
        "missing_tools": missing_tools,
    }
