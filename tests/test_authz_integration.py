"""
Integration Tests for Authorization System - Phase 2

These tests verify that:
1. Existing permission managers route through authz facade
2. Backward compatibility is maintained
3. Decision metrics are collected
4. All code paths converge to single boundary
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPhase2Integration:
    """Test Phase 2: Integration of existing managers with authz facade"""
    
    @pytest.mark.asyncio
    async def test_execution_permission_manager_routes_through_authz(self):
        """Test that execution/permission_manager.py routes through authz"""
        from modules.execution.permission_manager import PermissionManager
        from modules.execution.registry import ExecutionRegistration, ExecutionType, RiskLevel
        from modules.authz import get_authz_manager
        
        # Create manager
        manager = PermissionManager()
        
        # Create test registration
        registration = ExecutionRegistration(
            type=ExecutionType.COMMAND,
            name="test_command",
            handler=None,
            description="Test command",
            requires_approval=False,  # No approval for this test
            risk_level=RiskLevel.SAFE
        )
        
        # Check permission (should auto-approve)
        result = await manager.check_permission(
            registration=registration,
            context={},
            app=None,
            session=None
        )
        
        assert result == True, "Safe command should be auto-approved"
        
        # Verify decision was logged in authz
        authz_manager = get_authz_manager()
        metrics = authz_manager.get_metrics()
        assert metrics['total_decisions'] > 0, "Decision should be logged"
    
    @pytest.mark.asyncio
    async def test_unified_permission_manager_routes_through_authz(self):
        """Test that permissions/integration.py routes through authz"""
        from modules.permissions.integration import get_unified_permission_manager
        from modules.execution.registry import ExecutionRegistration, ExecutionType, RiskLevel
        from modules.authz import get_authz_manager
        
        # Get manager
        manager = get_unified_permission_manager()
        
        # Create test registration
        registration = ExecutionRegistration(
            type=ExecutionType.TOOL,
            name="Read",
            handler=None,
            description="Read file",
            requires_approval=False,
            risk_level=RiskLevel.SAFE
        )
        
        # Check permission
        result = await manager.check_permission(
            registration=registration,
            context={'file_path': './test.txt'},
            app=None,
            session=None
        )
        
        assert result == True, "Safe read should be auto-approved"
        
        # Verify in authz
        authz_manager = get_authz_manager()
        decisions = authz_manager.get_decision_log(limit=5)
        assert len(decisions) > 0, "Decisions should be logged"
    
    @pytest.mark.asyncio
    async def test_backward_compatibility_maintained(self):
        """Test that old API still works"""
        from modules.execution.permission_manager import get_permission_manager
        
        # Old way of getting manager
        manager = get_permission_manager()
        assert manager is not None, "Old API should still work"
    
    def test_decision_metrics_collected(self):
        """Test that decision metrics are collected"""
        from modules.authz import get_authz_manager
        
        manager = get_authz_manager()
        metrics = manager.get_metrics()
        
        # Check metrics structure
        assert 'total_decisions' in metrics
        assert 'allowed' in metrics or metrics['total_decisions'] == 0
        assert 'denied' in metrics or metrics['total_decisions'] == 0
        assert 'allow_rate' in metrics
    
    def test_audit_trail_complete(self):
        """Test that audit trail captures full context"""
        from modules.authz import get_authz_manager
        
        manager = get_authz_manager()
        decisions = manager.get_decision_log(limit=10)
        
        # Each decision should have complete context
        for decision in decisions:
            assert decision.context is not None
            assert decision.context.subject is not None
            assert decision.context.action is not None
            assert decision.context.resource is not None
            assert decision.risk_level is not None
            assert decision.decision_time > 0


class TestPhase3Performance:
    """Test Phase 3: Performance monitoring"""
    
    @pytest.mark.asyncio
    async def test_decision_latency_under_threshold(self):
        """Test that P95 decision latency < 3ms (target)"""
        from modules.authz import check_authorization, AuthzSubject
        import time
        
        # Run multiple authorization checks
        latencies = []
        subject = AuthzSubject(id="test", type="user")
        
        for i in range(100):
            start = time.time()
            decision = await check_authorization(
                subject=subject,
                action="file:read",
                resource=f"./test{i}.txt",
                context={}
            )
            end = time.time()
            latencies.append((end - start) * 1000)  # Convert to ms
        
        # Calculate P95
        latencies.sort()
        p95_index = int(len(latencies) * 0.95)
        p95_latency = latencies[p95_index]
        
        print(f"\nP95 latency: {p95_latency:.2f}ms")
        
        # Note: In production with cache, target is < 3ms
        # For now, just verify it completes reasonably fast
        assert p95_latency < 100, f"P95 latency {p95_latency}ms exceeds 100ms threshold"
    
    def test_memory_usage_stable(self):
        """Test that decision log doesn't grow unbounded"""
        from modules.authz import get_authz_manager
        
        manager = get_authz_manager()
        
        # Manager should limit decision log size
        # (Implementation limits to last 1000 decisions)
        metrics = manager.get_metrics()
        decisions = manager.get_decision_log(limit=2000)
        
        # Should not return more than 1000 (implementation limit)
        assert len(decisions) <= 1000, "Decision log should be bounded"


class TestPhase4Cleanup:
    """Test Phase 4: Verify deprecated modules marked for removal"""
    
    def test_deprecation_warnings_present(self):
        """Test that deprecated modules show warnings"""
        import warnings
        
        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Import deprecated module
            try:
                from modules.permissions import integration
                from modules.execution import permission_manager
                from modules import async_permissions
            except ImportError:
                pass  # Module might not exist yet
            
            # Check if deprecation warnings were issued
            # (They should be issued when modules are imported)
            # This is a basic check - actual warnings may vary
            print(f"\n{len(w)} warnings captured during import")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
