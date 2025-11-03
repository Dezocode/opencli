"""
Authorization System Setup Script

This script initializes the canonical authorization boundary and
sets up integration with legacy permission managers during the migration.

Usage:
    # In your main application initialization (opencli.py or similar)
    from modules.authz.setup import initialize_authorization_system
    
    initialize_authorization_system()
"""

import sys


def initialize_authorization_system(verbose: bool = False):
    """
    Initialize the canonical authorization system
    
    This function:
    1. Creates the authz manager singleton
    2. Sets up integration with legacy permission managers
    3. Enables deprecation warnings
    4. Logs initialization status
    
    Args:
        verbose: If True, print detailed initialization info
    """
    if verbose:
        sys.stderr.write("\n" + "="*70 + "\n")
        sys.stderr.write("🔒 Initializing Canonical Authorization System\n")
        sys.stderr.write("="*70 + "\n")
    
    # Step 1: Initialize authz manager
    from .facade import get_authz_manager
    manager = get_authz_manager()
    
    if verbose:
        sys.stderr.write("✓ Authorization manager initialized\n")
        sys.stderr.write(f"  Instance ID: {id(manager)}\n")
        sys.stderr.write(f"  Policy Version: {manager._policy_version}\n")
    
    # Step 2: Set up legacy integration
    from .migration import setup_legacy_integration, add_deprecation_warnings_to_legacy_modules
    
    try:
        setup_legacy_integration()
        if verbose:
            sys.stderr.write("✓ Legacy integration enabled\n")
    except Exception as e:
        sys.stderr.write(f"⚠️  Warning: Could not set up legacy integration: {e}\n")
        if verbose:
            import traceback
            traceback.print_exc()
    
    # Step 3: Enable deprecation warnings
    add_deprecation_warnings_to_legacy_modules()
    
    if verbose:
        sys.stderr.write("✓ Deprecation warnings enabled\n")
    
    # Step 4: Log initialization complete
    if verbose:
        sys.stderr.write("\n📊 System Status:\n")
        metrics = manager.get_metrics()
        sys.stderr.write(f"  Total decisions: {metrics.get('total_decisions', 0)}\n")
        sys.stderr.write(f"  Ready to accept authorization requests\n")
        sys.stderr.write("\n💡 Usage:\n")
        sys.stderr.write("  from modules.authz import check_authorization, AuthzSubject\n")
        sys.stderr.write("  decision = await check_authorization(...)\n")
        sys.stderr.write("\n📚 Documentation: modules/authz/README.md\n")
        sys.stderr.write("="*70 + "\n\n")
    
    sys.stderr.flush()
    
    return manager


def check_authorization_system_health() -> dict:
    """
    Check health of authorization system
    
    Returns:
        dict with health status
    """
    from .facade import get_authz_manager
    
    manager = get_authz_manager()
    metrics = manager.get_metrics()
    
    health = {
        'status': 'healthy',
        'manager_initialized': True,
        'total_decisions': metrics.get('total_decisions', 0),
        'allow_rate': metrics.get('allow_rate', 0),
        'has_legacy_integration': manager._legacy_permission_manager is not None
    }
    
    return health


if __name__ == "__main__":
    # Run initialization with verbose output
    initialize_authorization_system(verbose=True)
    
    # Show health check
    health = check_authorization_system_health()
    print("\n🏥 Health Check:")
    for key, value in health.items():
        print(f"  {key}: {value}")
