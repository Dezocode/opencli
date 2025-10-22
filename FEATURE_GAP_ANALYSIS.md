# Feature Gap Analysis

**Date:** 2025-10-22  
**Purpose:** Compare legacy and modular systems to identify migration needs

---

## Executive Summary

The modular permissions system is **significantly more advanced** than the legacy system, with comprehensive subsystems for i18n, analytics, audit, cache, and validation. However, it is **missing some critical features** from the legacy system that are needed for full functionality.

---

## Features in Modular ✅

### Core Permission System
1. ✅ UnifiedPermissionManager - Single entry point
2. ✅ PermissionBufferManager - Enhanced with subsystems
3. ✅ Permission widget - Rich UI with multi-page support
4. ✅ Prompt templates - Basic file/bash/api/tool templates
5. ✅ Analytics - Comprehensive tracking and reporting
6. ✅ Audit logging - Compliance-ready event logging
7. ✅ Caching - Performance optimization with TTL
8. ✅ i18n support - Multi-language (5 languages)
9. ✅ Validation - Security-focused data validation
10. ✅ Task management - Priority queue with history
11. ✅ SDK integration - SDKState enum for coordination
12. ✅ Concurrent prompts - Up to 5 simultaneous
13. ✅ Periodic cleanup - Orphaned prompt handling

---

## Features in Legacy Only ❌

### 1. Risk Assessment System (tool_permissions.py - 321 lines)
**Status:** ❌ Missing from modular system  
**Priority:** 🔴 HIGH - Security critical

#### Missing Features:
- ❌ RiskLevel enum (SAFE, RISKY, DANGEROUS, CRITICAL)
- ❌ Tool risk classification mapping:
  - SAFE: Read, Glob, Grep, GitHub
  - RISKY: Edit, Write, ConfigureHeaders
  - DANGEROUS: Bash
- ❌ Path-based risk assessment:
  - System directory detection (/etc, /bin, /usr, /System, /Library, /var)
  - User config protection (.ssh, .aws, .config)
  - Parent directory detection
  - Outside working directory detection
- ❌ Allowed tools list management
- ❌ Auto-accept mode (global and session)
- ❌ Tool operation preview formatting

**Migration Target:** `modules/permissions/validation.py` or new `modules/permissions/risk_assessment.py`

---

### 2. Tool-Specific Async Handling (async_permissions.py - 219 lines)
**Status:** ⚠️ Partially in modular system  
**Priority:** 🟡 MEDIUM - Functional but incomplete

#### Missing Features:
- ❌ AsyncPermissionHandler class
- ❌ Tool-specific prompt generation:
  - ❌ Edit operation prompts (file_path, old_str, new_str)
  - ❌ Write operation prompts (file_path, content preview)
  - ❌ WebFetch prompts (URL)
  - ❌ ConfigureHeaders prompts (provider, model, headers)
  - ❌ Refactoring prompts (plan, result)
- ❌ Risk level integration with prompts
- ❌ Response processing with ALLOW_ALWAYS saving
- ❌ Stream display integration
- ❌ Global handler instance management

**Existing in Modular:**
- ✅ Basic templates (file, bash, api, tool)
- ✅ UnifiedPermissionManager with async support

**Migration Target:** Enhance `modules/permissions/templates.py` with tool-specific templates

---

### 3. Multi-Step Workflow System (permission_workflow.py - 171 lines)
**Status:** ❌ Missing from modular system  
**Priority:** 🟢 LOW - Nice to have, not currently used

#### Missing Features:
- ❌ PermissionWorkflow class
- ❌ WorkflowStep dataclass
- ❌ WorkflowStepStatus enum
- ❌ WorkflowManager
- ❌ Step-by-step permission gating
- ❌ Workflow status tracking
- ❌ Step approval mechanism

**Use Case:** Multi-step operations requiring permission at each step  
**Current Usage:** ❓ Unknown - need to check imports  
**Migration Target:** New `modules/permissions/workflow.py` if needed

---

### 4. Dual Buffer Streaming (dual_buffer_system.py - 247 lines)
**Status:** ❌ Missing from modular system  
**Priority:** 🟢 LOW - Display feature, not permission-related

#### Missing Features:
- ❌ ToolBuffer class (streaming character-by-character)
- ❌ CommandBuffer class (immediate writes)
- ❌ DualBufferCoordinator
- ❌ Collapsible sections
- ❌ Visual indicators (⏺ running, ✓ complete)

**Note:** This is actually a **display system**, not a permission system feature. It may belong in a different module (streaming_display/).

**Migration Target:** Consider moving to `modules/streaming_display/` instead of permissions

---

## Migration Plan

### Phase 4: Migrate Core Features (Priority 1)

#### Task 4.1: Add Risk Assessment to Modular System
**Target:** `modules/permissions/risk_assessment.py` (NEW)  
**Lines:** ~350 lines  
**Effort:** 🔴 High  

**Steps:**
1. Create new `risk_assessment.py` module
2. Migrate RiskLevel enum
3. Migrate tool risk classification
4. Migrate path safety assessment:
   - System directory detection
   - User config protection
   - Parent/outside directory detection
5. Add allowed tools management
6. Add auto-accept mode support
7. Add operation preview formatting
8. Integrate with ValidationManager

**Test Requirements:**
- Path safety detection tests
- Risk level classification tests
- System directory detection tests
- Tool risk mapping tests

---

#### Task 4.2: Enhance Templates with Tool-Specific Prompts
**Target:** `modules/permissions/templates.py`  
**Lines:** Add ~150 lines  
**Effort:** 🟡 Medium  

**Steps:**
1. Add `file_edit()` method (Edit tool)
2. Add `file_write()` method (Write tool)
3. Add `webfetch()` method (WebFetch tool)
4. Add `configure_headers()` method (ConfigureHeaders tool)
5. Add `code_refactoring()` method (Refactoring tool)
6. Add risk level display to all templates
7. Update existing templates to use risk assessment

**Test Requirements:**
- Template generation tests
- Risk level integration tests
- Option structure tests

---

#### Task 4.3: Integrate Risk Assessment with UnifiedPermissionManager
**Target:** `modules/permissions/integration.py`  
**Lines:** Add ~50 lines  
**Effort:** 🟡 Medium  

**Steps:**
1. Add RiskAssessmentManager instance to UnifiedPermissionManager
2. Add risk assessment delegation methods
3. Update `request_permission()` to assess risk
4. Update prompt generation to include risk level
5. Add auto-accept decision logic

**Test Requirements:**
- Risk-based permission flow tests
- Auto-accept mode tests
- Integration tests

---

### Phase 5: Migrate Remaining Features (Priority 2)

#### Task 5.1: Evaluate Workflow System Need
**Target:** TBD  
**Lines:** ~200 lines if needed  
**Effort:** 🟢 Low (if not used, skip)  

**Steps:**
1. Search codebase for workflow system imports
2. If used, create `modules/permissions/workflow.py`
3. If not used, mark for deletion

---

#### Task 5.2: Evaluate Dual Buffer System
**Target:** `modules/streaming_display/` (NOT permissions)  
**Lines:** N/A - out of scope  
**Effort:** 🟢 Low  

**Steps:**
1. Confirm this is display logic, not permission logic
2. Consider moving to streaming_display module
3. Out of scope for permission system migration

---

## Import Updates Required

After migration, update imports in:

### Files Using `modules.async_permissions`:
```python
# OLD
from modules.async_permissions import AsyncPermissionHandler

# NEW
from modules.permissions.integration import UnifiedPermissionManager
```

### Files Using `modules.tool_permissions`:
```python
# OLD
from modules.tool_permissions import ToolPermissionManager, RiskLevel

# NEW
from modules.permissions.risk_assessment import RiskAssessmentManager, RiskLevel
```

### Files Using `modules.permission_workflow`:
```python
# OLD (if used)
from modules.permission_workflow import PermissionWorkflow

# NEW
from modules.permissions.workflow import PermissionWorkflow
```

---

## Files to Delete After Migration

### Safe to Delete Immediately:
- ❌ `modules/permission_buffer/` - Already superseded by modular system

### Delete After Migration Complete:
- ❌ `modules/async_permissions.py` - After templates enhanced
- ❌ `modules/tool_permissions.py` - After risk assessment migrated
- ❌ `modules/permission_workflow.py` - After workflow migrated or confirmed unused
- ❌ `modules/dual_buffer_system.py` - After moved to streaming_display or confirmed unused

### Keep for Compatibility:
- ✅ `modules/permission_buffer_manager.py` - Compatibility stub (until all imports updated)
- ✅ `modules/permission_prompt.py` - Compatibility stub (until all imports updated)

---

## Success Criteria

### Phase 4 Complete When:
- [x] Risk assessment system migrated
- [x] Tool-specific templates added
- [x] Risk assessment integrated with UnifiedPermissionManager
- [x] All tests passing
- [x] No functionality lost

### Phase 5 Complete When:
- [x] Workflow system evaluated and migrated/deleted
- [x] Dual buffer system evaluated and moved/deleted
- [x] All imports updated
- [x] Legacy files deleted (except compatibility stubs)
- [x] All tests passing

---

**Next Step:** Begin Phase 4 - Migrate risk assessment system to modular architecture
