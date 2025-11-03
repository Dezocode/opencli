"""
Migration Utilities - Bridge Between Legacy and New Authorization System

This module provides compatibility shims to gradually migrate from the old
permission systems to the new canonical authz boundary.

Usage during migration:
    from modules.authz.migration import setup_legacy_integration
    
    # In your initialization code
    setup_legacy_integration(permission_manager, risk_manager)
"""

import sys
from typing import Optional


def setup_legacy_integration(permission_manager=None, risk_manager=None):
    """
    Set up integration between new authz facade and legacy permission managers
    
    This allows the authz facade to delegate to existing implementations
    during the migration period, ensuring backward compatibility.
    
    Args:
        permission_manager: Legacy PermissionManager instance (optional)
        risk_manager: Legacy RiskAssessmentManager instance (optional)
    """
    from .facade import get_authz_manager
    
    manager = get_authz_manager()
    
    # If managers not provided, try to import from legacy locations
    if permission_manager is None:
        try:
            from ..execution.permission_manager import get_permission_manager
            permission_manager = get_permission_manager()
        except ImportError:
            sys.stderr.write(
                "[authz.migration] Warning: Could not import legacy permission_manager\n"
            )
    
    if risk_manager is None:
        try:
            from ..permissions.risk_assessment import get_risk_assessment_manager
            risk_manager = get_risk_assessment_manager()
        except ImportError:
            sys.stderr.write(
                "[authz.migration] Warning: Could not import legacy risk_manager\n"
            )
    
    # Register legacy managers
    manager.set_legacy_managers(permission_manager, risk_manager)
    
    sys.stderr.write(
        "[authz.migration] ✓ Legacy integration enabled\n"
        "  Permission checks will route through authz facade\n"
        "  while delegating to existing implementations.\n"
    )
    sys.stderr.flush()


def add_deprecation_warnings_to_legacy_modules():
    """
    Add deprecation warnings to legacy permission modules
    
    This should be called during application initialization to warn
    developers when they import deprecated modules.
    """
    import warnings
    
    # Enable all deprecation warnings for this project
    warnings.filterwarnings('default', category=DeprecationWarning)
    warnings.filterwarnings('default', category=PendingDeprecationWarning)
    
    sys.stderr.write(
        "[authz.migration] ✓ Deprecation warnings enabled\n"
        "  Deprecated permission imports will show warnings.\n"
    )
    sys.stderr.flush()


def migrate_permission_check_to_authz(
    registration,
    context: dict,
    app=None,
    session=None
) -> dict:
    """
    Helper to migrate a legacy permission check to the new authz system
    
    This function bridges the old ExecutionRegistration-based checks
    to the new AuthzContext-based checks.
    
    Args:
        registration: ExecutionRegistration object from legacy system
        context: Legacy context dict
        app: TUI app instance
        session: Session object
    
    Returns:
        dict with 'allowed' bool and 'decision' AuthzDecision
    """
    from .facade import check_authorization, AuthzSubject
    import asyncio
    
    # Create authz subject from session
    subject = AuthzSubject(
        id=getattr(session, 'id', 'unknown') if session else 'unknown',
        type='user',
        attributes={'session': session} if session else {}
    )
    
    # Map registration to action
    action = f"{registration.type.value}:{registration.name}"
    
    # Extract resource from context
    resource = context.get('file_path') or context.get('resource') or context.get('command') or 'unknown'
    
    # Create authz context
    authz_context = {
        'args': context.get('args', {}),
        'current_dir': context.get('current_dir'),
        'metadata': context.get('metadata', {})
    }
    
    # Run authorization check
    loop = asyncio.get_event_loop()
    decision = loop.run_until_complete(
        check_authorization(
            subject=subject,
            action=action,
            resource=resource,
            context=authz_context,
            app=app,
            session=session
        )
    )
    
    return {
        'allowed': decision.allowed,
        'decision': decision
    }


class LegacyPermissionManagerShim:
    """
    Shim for legacy PermissionManager that routes to authz facade
    
    This can replace the old PermissionManager in code during migration:
    
        # Old code
        from modules.execution.permission_manager import PermissionManager
        manager = PermissionManager()
        
        # New code (temporary during migration)
        from modules.authz.migration import LegacyPermissionManagerShim
        manager = LegacyPermissionManagerShim()
    """
    
    def __init__(self):
        from .facade import get_authz_manager
        self._authz_manager = get_authz_manager()
        
        sys.stderr.write(
            "[LegacyPermissionManagerShim] ⚠️  Using compatibility shim\n"
            "  This is a temporary bridge to the new authz system.\n"
            "  Please migrate to: from modules.authz import check_authorization\n"
        )
        sys.stderr.flush()
    
    async def check_permission(self, registration, context, app=None, session=None):
        """Legacy check_permission interface"""
        result = migrate_permission_check_to_authz(
            registration, context, app, session
        )
        return result['allowed']


class LegacyRiskManagerShim:
    """
    Shim for legacy RiskAssessmentManager that routes to authz facade
    
    Similar to LegacyPermissionManagerShim but for risk assessment.
    """
    
    def __init__(self):
        from .facade import get_authz_manager
        self._authz_manager = get_authz_manager()
        
        sys.stderr.write(
            "[LegacyRiskManagerShim] ⚠️  Using compatibility shim\n"
            "  This is a temporary bridge to the new authz system.\n"
            "  Please migrate to: from modules.authz import check_authorization\n"
        )
        sys.stderr.flush()
    
    def assess_operation_risk(self, tool_name, args, current_dir=None):
        """Legacy assess_operation_risk interface"""
        from .facade import RiskLevel
        
        # Simple risk assessment based on tool name
        # This is simplified - real implementation in facade.py
        high_risk_tools = ['Bash', 'Delete', 'Write', 'Edit']
        safe_tools = ['Read', 'Glob', 'Grep']
        
        if tool_name in safe_tools:
            return RiskLevel.SAFE, "Safe operation"
        elif tool_name in high_risk_tools:
            return RiskLevel.HIGH, f"{tool_name} is high risk"
        else:
            return RiskLevel.MEDIUM, "Medium risk operation"
    
    def should_prompt(self, tool_name, args, current_dir=None):
        """Legacy should_prompt interface"""
        risk_level, reason = self.assess_operation_risk(tool_name, args, current_dir)
        
        # Prompt for medium risk and above
        should_prompt = risk_level.value not in ['safe', 'low']
        
        return should_prompt, reason, risk_level


def print_migration_status():
    """
    Print the current migration status to help track progress
    """
    from .facade import get_authz_manager
    
    manager = get_authz_manager()
    metrics = manager.get_metrics()
    
    print("\n" + "="*70)
    print("📊 AUTHORIZATION MIGRATION STATUS")
    print("="*70)
    print(f"New authz system initialized: ✅")
    print(f"Total authorization decisions: {metrics.get('total_decisions', 0)}")
    print(f"Allow rate: {metrics.get('allow_rate', 0):.1%}")
    print()
    print("Next steps:")
    print("  1. Review modules/authz/README.md for migration guide")
    print("  2. Run: pytest tests/test_authz_boundary.py")
    print("  3. Update imports to use: from modules.authz import check_authorization")
    print("="*70 + "\n")
