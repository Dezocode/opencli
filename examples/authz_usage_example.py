"""
Example Usage of Canonical Authorization System

This example shows how to use the new authz facade for authorization checks.
"""

import asyncio
from modules.authz import check_authorization, AuthzSubject, get_authz_manager
from modules.authz.facade import AuthzAction


async def example_file_write_check():
    """Example: Check authorization for file write"""
    print("\n" + "="*70)
    print("Example 1: File Write Authorization Check")
    print("="*70)
    
    # Create subject (represents the user/session)
    subject = AuthzSubject(
        id="user123",
        type="user",
        attributes={"username": "developer"}
    )
    
    # Check authorization for writing to a file
    decision = await check_authorization(
        subject=subject,
        action=AuthzAction.FILE_WRITE.value,
        resource="/home/user/project/src/main.py",
        context={
            "args": {"content": "new code..."},
            "current_dir": "/home/user/project"
        }
    )
    
    print(f"Decision: {decision.result.value}")
    print(f"Allowed: {decision.allowed}")
    print(f"Reason: {decision.reason}")
    print(f"Risk Level: {decision.risk_level.value}")
    print(f"Decision Path: {decision.decision_path}")
    
    if decision.allowed:
        print("✓ Operation authorized - proceeding with file write")
    else:
        print("✗ Operation denied - file write blocked")
    
    return decision


async def example_bash_command_check():
    """Example: Check authorization for bash command"""
    print("\n" + "="*70)
    print("Example 2: Bash Command Authorization Check")
    print("="*70)
    
    subject = AuthzSubject(id="user123", type="user")
    
    # Check authorization for running a bash command
    decision = await check_authorization(
        subject=subject,
        action=AuthzAction.BASH_EXECUTE.value,
        resource="npm install",
        context={
            "args": {"command": "npm install", "description": "Install dependencies"},
            "current_dir": "/home/user/project"
        }
    )
    
    print(f"Decision: {decision.result.value}")
    print(f"Allowed: {decision.allowed}")
    print(f"Reason: {decision.reason}")
    print(f"Risk Level: {decision.risk_level.value}")
    
    return decision


async def example_system_path_check():
    """Example: Check authorization for critical system path"""
    print("\n" + "="*70)
    print("Example 3: Critical System Path Authorization Check")
    print("="*70)
    
    subject = AuthzSubject(id="user123", type="user")
    
    # Check authorization for writing to a system path (should be critical risk)
    decision = await check_authorization(
        subject=subject,
        action=AuthzAction.FILE_WRITE.value,
        resource="/etc/hosts",
        context={
            "args": {"content": "127.0.0.1 localhost"},
            "current_dir": "/home/user/project"
        }
    )
    
    print(f"Decision: {decision.result.value}")
    print(f"Allowed: {decision.allowed}")
    print(f"Reason: {decision.reason}")
    print(f"Risk Level: {decision.risk_level.value} ⚠️")
    
    return decision


async def example_metrics_and_audit():
    """Example: Get authorization metrics and audit log"""
    print("\n" + "="*70)
    print("Example 4: Authorization Metrics and Audit Trail")
    print("="*70)
    
    manager = get_authz_manager()
    
    # Get overall metrics
    metrics = manager.get_metrics()
    print(f"\n📊 Metrics:")
    print(f"  Total decisions: {metrics['total_decisions']}")
    print(f"  Allowed: {metrics.get('allowed', 0)}")
    print(f"  Denied: {metrics.get('denied', 0)}")
    print(f"  Allow rate: {metrics.get('allow_rate', 0):.1%}")
    
    if metrics.get('by_risk_level'):
        print(f"\n  By Risk Level:")
        for risk, count in metrics['by_risk_level'].items():
            print(f"    {risk}: {count}")
    
    # Get audit log
    print(f"\n📋 Recent Decisions (last 5):")
    decisions = manager.get_decision_log(limit=5)
    for i, decision in enumerate(decisions, 1):
        print(f"\n  {i}. {decision.context.action} on {decision.context.resource}")
        print(f"     Result: {decision.result.value}")
        print(f"     Risk: {decision.risk_level.value}")
        print(f"     Time: {decision.decision_time:.3f}")


async def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("🔒 Canonical Authorization System - Usage Examples")
    print("="*70)
    print("\nThese examples show how to use the new authz facade.")
    print("All authorization checks go through a single entry point:")
    print("  from modules.authz import check_authorization\n")
    
    # Run examples
    await example_file_write_check()
    await example_bash_command_check()
    await example_system_path_check()
    await example_metrics_and_audit()
    
    print("\n" + "="*70)
    print("✓ Examples Complete")
    print("="*70)
    print("\nFor more information:")
    print("  • See modules/authz/README.md")
    print("  • Run tests: pytest tests/test_authz_boundary.py")
    print("  • Check health: python -m modules.authz.setup")
    print()


if __name__ == "__main__":
    asyncio.run(main())
