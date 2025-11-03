"""
Canonical Authorization Boundary - Single Source of Truth

This module provides THE ONLY interface for authorization decisions in OpenCLI.
All permission checks MUST go through this boundary to ensure consistency,
auditability, and maintainability.

Architecture:
    - Single check() API for all authorization decisions
    - Policy as data, not code spread around
    - Inversion at the boundary (application depends on interface)
    - Acyclic dependencies (authz at the edge, never imports domain models)

Usage:
    from modules.authz import check_authorization

    allowed = await check_authorization(
        subject=session.user,
        action="file:write",
        resource="/path/to/file",
        context={"risk_level": "high"}
    )
"""

from .facade import (
    check_authorization,
    AuthzContext,
    AuthzDecision,
    AuthzSubject,
    get_authz_manager
)

__all__ = [
    'check_authorization',
    'AuthzContext',
    'AuthzDecision',
    'AuthzSubject',
    'get_authz_manager'
]
