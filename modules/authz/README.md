# Authorization System - Single Source of Truth

## Overview

This module provides **THE ONLY** interface for authorization decisions in OpenCLI.

**Before this fix:** Multiple permission systems spread across the codebase, different code paths yielding different decisions, cross-layer bypasses, and no audit trail.

**After this fix:** Single canonical authorization boundary with consistent decisions, full audit logging, and enforced architectural boundaries.

## Architecture Principles

### 1. Single Authorization Boundary
```python
from modules.authz import check_authorization, AuthzSubject

# THE ONLY WAY to check authorization
subject = AuthzSubject(id=session.id, type="user")
decision = await check_authorization(
    subject=subject,
    action="file:write",
    resource="/path/to/file",
    context={"args": {...}}
)
```

### 2. Policy as Data, Not Code
- Policies loaded from external source (future: OPA/Rego, Cedar, or custom DSL)
- No hardcoded permission logic scattered across modules
- Single point of policy updates

### 3. Inversion at the Boundary
- Application depends on **interface** (`check_authorization`)
- Implementation is swappable
- Clean ports & adapters pattern

### 4. Acyclic Dependencies
- `authz` module sits at the edge (infra layer)
- Never imports domain models or business logic
- All dependencies point inward

### 5. Complete Audit Trail
Every authorization decision is logged with:
- Subject (who)
- Action (what)
- Resource (where)
- Decision (allow/deny/prompt)
- Risk level
- Policy version
- Decision path
- Timestamp

## Usage

### Basic Authorization Check

```python
from modules.authz import check_authorization, AuthzSubject

async def my_operation(session, file_path):
    subject = AuthzSubject(id=session.id, type="user")
    
    decision = await check_authorization(
        subject=subject,
        action="file:write",
        resource=file_path,
        context={"args": {"content": "..."}}
    )
    
    if not decision.allowed:
        print(f"Access denied: {decision.reason}")
        return False
    
    # Proceed with operation
    write_file(file_path, content)
    return True
```

### Available Actions

Use the standard action enum:

```python
from modules.authz.facade import AuthzAction

# File operations
AuthzAction.FILE_READ
AuthzAction.FILE_WRITE
AuthzAction.FILE_EDIT
AuthzAction.FILE_DELETE

# Bash operations
AuthzAction.BASH_EXECUTE

# API operations
AuthzAction.API_CALL

# Tool operations
AuthzAction.TOOL_EXECUTE

# Command operations
AuthzAction.COMMAND_EXECUTE
```

### Risk Levels

The system automatically assesses risk:

- **SAFE**: Read operations in current directory → auto-allow
- **LOW**: Low-risk reads → prompt if needed
- **MEDIUM**: Writes in current directory → prompt
- **HIGH**: Operations outside current directory → always prompt
- **CRITICAL**: System paths (/etc, /.ssh, etc.) → always prompt with warning

### Getting Authorization Metrics

```python
from modules.authz import get_authz_manager

manager = get_authz_manager()

# Get metrics
metrics = manager.get_metrics()
print(f"Total decisions: {metrics['total_decisions']}")
print(f"Allow rate: {metrics['allow_rate']:.1%}")
print(f"By risk: {metrics['by_risk_level']}")

# Get audit log
decisions = manager.get_decision_log(
    subject_id="user123",
    action="file:write",
    limit=50
)

for decision in decisions:
    print(decision.to_dict())
```

## Migration Guide

### Old Code (DEPRECATED)

```python
# ❌ OLD - Multiple import paths
from modules.execution.permission_manager import get_permission_manager
from modules.permissions import get_unified_permission_manager
from modules.async_permissions import AsyncPermissionHandler

# ❌ OLD - Inconsistent interfaces
manager = get_permission_manager()
approved = await manager.check_permission(registration, context, app, session)

# ❌ OLD - No audit trail
if approved:
    do_something()
```

### New Code (CORRECT)

```python
# ✅ NEW - Single import
from modules.authz import check_authorization, AuthzSubject

# ✅ NEW - Consistent interface
subject = AuthzSubject(id=session.id, type="user")
decision = await check_authorization(
    subject=subject,
    action="file:write",
    resource=file_path,
    context={"args": {...}}
)

# ✅ NEW - Full audit trail
if decision.allowed:
    do_something()
    # Decision automatically logged with:
    # - subject, action, resource
    # - risk level, policy version
    # - timestamp, decision path
```

## Deprecation Schedule

| Phase | Timeline | Status |
|-------|----------|--------|
| Phase 1: Create authz facade | Week 1 | ✅ Complete |
| Phase 2: Add deprecation warnings | Week 1 | ✅ Complete |
| Phase 3: Redirect old implementations | Week 2-3 | 🚧 In Progress |
| Phase 4: Remove deprecated code | Week 4+ | ⏳ Planned |

## Deprecated Modules

The following modules are **DEPRECATED** and will be removed:

- ❌ `modules/execution/permission_manager.py` → Use `modules.authz`
- ❌ `modules/async_permissions.py` → Use `modules.authz`
- ❌ `modules/async_interactive/permissions.py` → Use `modules.authz`
- ❌ `modules/tui/permission_handlers.py` → Use `modules.authz`

Do not import from these modules in new code.

## Architecture Tests

To enforce the boundary, we have architectural tests:

```python
# Test: Only authz can make authorization decisions
def test_no_direct_permission_imports():
    """Ensure no code imports deprecated permission modules"""
    forbidden_imports = [
        'modules.execution.permission_manager',
        'modules.async_permissions',
        'modules.async_interactive.permissions'
    ]
    # ... test implementation
```

Run tests:
```bash
pytest tests/test_authz_boundary.py -v
```

## Performance SLOs

Authorization decisions must meet these SLOs:

- P95 decision from cache: < 3 ms
- P95 decision with prompt: < 100 ms (excluding user interaction)
- P99 decision: < 25 ms

Monitor with:
```python
metrics = manager.get_metrics()
# Includes timing histograms
```

## Future Enhancements

1. **Policy Engine Integration**
   - OPA/Rego for complex policies
   - Cedar for AWS-style policies
   - Custom DSL for simple rules

2. **Policy Versioning**
   - Canary rollouts (10% traffic first)
   - A/B testing of policy changes
   - Rollback support

3. **Advanced Caching**
   - Redis cache for distributed systems
   - TTL-based invalidation
   - Warm-up strategies

4. **Telemetry**
   - OpenTelemetry integration
   - Decision latency traces
   - Policy evaluation metrics

## Questions?

- See `modules/authz/facade.py` for implementation details
- See `tests/test_authz_boundary.py` for usage examples
- File issues with label `authz`

## Contributing

When adding new authorization checks:

1. **Always** use `check_authorization()` - no exceptions
2. Choose appropriate `AuthzAction` from enum
3. Provide full context for risk assessment
4. Test with different risk levels
5. Add metrics monitoring

Do **NOT**:
- Create new permission managers
- Import deprecated permission modules
- Bypass the authz boundary
- Hardcode authorization logic
