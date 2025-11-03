"""
Phase 4 Cleanup Strategy

This document outlines the strategy for removing deprecated permission modules
after confirming all code paths route through the authz facade.

## Deprecated Modules to Remove

1. **modules/async_permissions.py**
   - Status: Deprecated, replaced by authz
   - Dependencies: Check imports before removal
   - Action: Remove after migration complete

2. **modules/async_interactive/permissions.py**
   - Status: Deprecated
   - Dependencies: Used by async_interactive
   - Action: Replace with authz calls

3. **Legacy functions in execution/permission_manager.py**
   - Status: Keep wrapper, mark methods as deprecated
   - Dependencies: Multiple
   - Action: Keep shell, delegate to authz

4. **Legacy functions in permissions/integration.py**
   - Status: Keep wrapper, delegate to authz
   - Dependencies: Multiple
   - Action: Already migrated in Phase 2

## Migration Checklist

### Pre-Cleanup Verification
- [x] All permission checks route through authz facade
- [x] Integration tests pass
- [x] CI enforcement active
- [x] Performance monitoring in place
- [x] Backward compatibility maintained

### Cleanup Steps (Phase 4)
- [ ] Mark deprecated modules with @deprecated decorator
- [ ] Add deprecation notices to module docstrings
- [ ] Create migration guide for external users
- [ ] Update all internal imports to use authz
- [ ] Remove unused deprecated code (cautiously)
- [ ] Update documentation to remove deprecated APIs
- [ ] Run full test suite
- [ ] Production canary deployment (10% traffic)
- [ ] Monitor for issues (1 week)
- [ ] Full rollout if stable

### Post-Cleanup Monitoring
- [ ] Check decision metrics daily
- [ ] Monitor error rates
- [ ] Track performance (P95 latency)
- [ ] Review audit logs for anomalies
- [ ] Gather user feedback

## Rollback Plan

If issues arise:
1. Keep deprecated modules in place (don't delete yet)
2. Fix issues in authz facade
3. Retest thoroughly
4. Retry cleanup after fixes validated

## Timeline

- **Week 1**: Mark deprecated (Phase 4a) - THIS COMMIT
- **Week 2**: Monitor metrics, fix issues
- **Week 3**: Canary deployment
- **Week 4**: Full rollout if stable
- **Week 5+**: Remove deprecated code after stability confirmed

## Phase 4a: Mark Everything Deprecated (Safe First Step)

Instead of deleting code (risky), first step is to mark everything deprecated
and ensure all new code uses authz. Delete only after 100% confidence.
"""

# This file is documentation only - implementation follows below
