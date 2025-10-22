# Unified Execution Path - 10 Phase Plan

**Date:** 2025-10-22
**Goal:** Single path for ALL commands: `Commands → SDK → Permission Buffer → Execution`
**Strategy:** Migrate features FIRST, delete legacy LAST

---

## The Single Path (What We Want)

```
User Input → SDK Executor → Unified Permission Manager → Permission Buffer → User Response → Command Handler

NO BYPASSING. NO MULTIPLE PATHS. ONE ROUTE.
```

---

## Phase 1: Inventory Legacy Features

**Goal:** List what features exist in legacy permission code that modular version needs

### 1.1 Check Legacy Files

```bash
# Files to inventory:
- modules/permission_buffer/         # Old permission system
- modules/permission_buffer_manager.py  # Compatibility stub
- modules/async_permissions.py       # Async permission handling
- modules/tool_permissions.py        # Tool-specific permissions
- modules/permission_workflow.py     # Workflow features
- modules/dual_buffer_system.py      # Dual buffer features
```

### 1.2 Document Features

**For each file, list:**
- What does it do?
- Does modular version have this? ✅/❌
- Is it still used? ✅/❌
- Migration needed? ✅/❌

**Output:** `LEGACY_FEATURES_INVENTORY.md`

---

## Phase 2: Inventory Modular Features

**Goal:** List what the modular version already has

### 2.1 Check Modular Files

```bash
# Modular permission system:
- modules/permissions/integration.py    # UnifiedPermissionManager
- modules/permissions/manager.py        # PermissionBufferManager
- modules/permissions/widget.py         # Permission widget
- modules/permissions/templates.py      # Prompt templates
- modules/permissions/analytics.py      # Analytics
- modules/permissions/audit.py          # Audit logging
- modules/permissions/cache.py          # Caching
- modules/permissions/i18n.py           # Internationalization
- modules/permissions/validation.py     # Validation
```

### 2.2 Document Capabilities

**For each module, list:**
- What features it provides
- What legacy features it replaces
- What's missing compared to legacy

**Output:** `MODULAR_FEATURES_INVENTORY.md`

---

## Phase 3: Gap Analysis

**Goal:** Identify what modular version is missing

### 3.1 Create Gap Report

**Compare inventories:**

```markdown
# Feature Gap Analysis

## Features in Modular ✅
1. UnifiedPermissionManager
2. PermissionBufferManager
3. Permission widget display
4. Prompt templates
5. Analytics
6. Audit logging
7. Caching
8. i18n support
9. Validation

## Features in Legacy Only ❌
1. [Feature from legacy not in modular]
2. [Feature from legacy not in modular]
3. ...

## Migration Required
- [ ] Feature X: Migrate from permission_buffer/ to permissions/
- [ ] Feature Y: Migrate from async_permissions.py to permissions/
- [ ] Feature Z: ...

## Can Delete Immediately (Unused)
- [ ] File X (no imports found)
- [ ] File Y (no imports found)
```

**Output:** `FEATURE_GAP_ANALYSIS.md`

---

## Phase 4: Migrate Missing Features (Part 1)

**Goal:** Move essential features from legacy to modular

### 4.1 Priority 1: Core Permission Features

**For each missing feature:**

1. **Understand** - Read legacy code, document what it does
2. **Design** - Plan where it goes in modular structure
3. **Implement** - Add to modular version
4. **Test** - Verify it works same as legacy
5. **Document** - Update modular docs

**Example:**
```python
# IF legacy has async permission handling in async_permissions.py
# AND modular doesn't have it
# THEN add to modules/permissions/integration.py

# modules/permissions/integration.py
class UnifiedPermissionManager:
    async def async_request_permission(self, ...):
        # Migrated from async_permissions.py
        ...
```

---

## Phase 5: Migrate Missing Features (Part 2)

**Goal:** Move remaining features from legacy to modular

### 5.1 Priority 2: Tool/Workflow Features

**Continue migration:**
- Tool-specific permissions → modules/permissions/
- Workflow features → modules/permissions/
- Any other gaps identified in Phase 3

### 5.2 Update Imports

**For each migrated feature:**
- Update all files that imported from legacy
- Point to new modular location
- Test still works

---

## Phase 6: Verify Single Path for Commands

**Goal:** Ensure ALL commands use: `Command → SDK → Permission Buffer`

### 6.1 Trace Command Groups

**Group A: Already Correct**
```python
# Pattern: dev_commands.py, model_commands.py, etc.
def command_prompt(...):
    return prompt_data  # SDK handles permission

async def command_handler(..., **context):
    response = context.get('_custom_prompt_data')
    # Execute
```

**Route:** Command → SDK Executor → Unified Manager → Buffer ✅

---

**Group B: Need to Verify**
```python
# Pattern: docker_commands.py, etc.
async def command_prompt(...):
    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(...)

async def command_handler(..., **context):
    response = context.get('_custom_prompt_data')
    # Execute
```

**Check:**
- Does `get_permission_buffer_manager()` return unified buffer? ✅/❌
- Does this go through SDK or bypass it? Trace it.
- Is this the SAME buffer as Group A? Test it.

---

**Group C: Legacy/Unknown**
```python
# Check: command_executor.py, tool_registry.py
# Do these go through SDK? Trace them.
```

### 6.2 Fix Any Bypasses

**IF:** Command bypasses SDK executor
**THEN:** Refactor to use SDK pattern

**IF:** Command uses different permission manager
**THEN:** Update to use unified manager

**IF:** Command has no permission handling
**THEN:** Add SDK-compliant permission prompt

---

## Phase 7: Verify Multi-Page Buffers Work

**Goal:** Ensure interactive multi-page permission buffers still work

### 7.1 Test Interactive Commands

```bash
# Test /docker command (multi-page)
opencli tui
/docker
# Press ENTER

# Verify:
✅ Permission buffer appears
✅ Shows multiple pages of content
✅ Arrow keys navigate pages
✅ ENTER selects option
✅ Command executes correctly
```

### 7.2 Test All Buffer Features

**Test each permission buffer feature:**
- [ ] Simple Yes/No prompts
- [ ] Multi-page navigation
- [ ] Option selection
- [ ] Arrow key navigation (UP/DOWN)
- [ ] ENTER key selection
- [ ] ESC to cancel
- [ ] Markdown rendering
- [ ] Prompt titles
- [ ] Option descriptions

**All must work SAME as before migration**

---

## Phase 8: Verify Single Instance

**Goal:** Confirm only ONE permission manager exists

### 8.1 Add Instance Tracking

```python
# modules/permissions/integration.py
class UnifiedPermissionManager:
    def __init__(self):
        import sys
        sys.stderr.write(f"[INSTANCE] UnifiedPermissionManager created: {id(self)}\n")
        sys.stderr.flush()
```

### 8.2 Test Multiple Commands

```bash
opencli tui 2>/tmp/trace.log

# Run different commands
/debug
/docker
/model

# Check trace
grep "INSTANCE" /tmp/trace.log

# Expected: SAME ID for all commands
# [INSTANCE] UnifiedPermissionManager created: 12345678
# [INSTANCE] UnifiedPermissionManager created: 12345678  ← Same!
# [INSTANCE] UnifiedPermissionManager created: 12345678  ← Same!
```

**IF different IDs:** Multiple instances exist - FIX IT
**IF same ID:** Single instance confirmed ✅

---

## Phase 9: Remove Legacy Code

**Goal:** Delete old permission system files ONLY after verification

### 9.1 Pre-Delete Checklist

**ONLY proceed if ALL are ✅:**

- [ ] Phase 3: All features migrated to modular
- [ ] Phase 4-5: Migration complete and tested
- [ ] Phase 6: All commands use single path
- [ ] Phase 7: Multi-page buffers work
- [ ] Phase 8: Single instance verified
- [ ] All imports updated to modular
- [ ] No broken functionality
- [ ] Tests pass

**IF ANY ❌:** DO NOT DELETE - Fix issue first

### 9.2 Delete Legacy Files

**Safe to delete:**
```bash
# Delete old permission system
rm -rf modules/permission_buffer/

# Delete unused files
rm modules/permission_workflow.py
rm modules/dual_buffer_system.py
rm modules/async_permissions.py        # IF migrated
rm modules/tool_permissions.py         # IF migrated

# Delete backups
rm modules/permission_buffer_manager.py.backup
rm modules/permission_prompt.py.backup

# Delete stub IF all imports updated
rm modules/permission_buffer_manager.py  # Only if no imports remain
```

**KEEP (needed):**
```bash
# Keep modular system
modules/permissions/                    # Main system
modules/permission_prompt.py            # Re-export stub for compatibility
```

### 9.3 Verify After Deletion

```bash
# Test all commands still work
opencli tui

/debug
/docker
/model
/agent
# All should work identically
```

---

## Phase 10: Final Verification & Documentation

**Goal:** Confirm single path works, document architecture

### 10.1 Full System Test

**Test every command type:**
- [ ] Simple prompts (/debug, /model, etc.)
- [ ] Multi-page prompts (/docker, etc.)
- [ ] Tool permissions (if applicable)
- [ ] Async permissions (if applicable)

**Verify:**
- [ ] Single execution path: Command → SDK → Buffer
- [ ] Single permission manager instance
- [ ] Single buffer instance
- [ ] All buffers look the same
- [ ] All features work same as before

### 10.2 Document Final Architecture

**Create:** `PERMISSION_SYSTEM_ARCHITECTURE.md`

```markdown
# OpenCLI Permission System Architecture

## Overview
Single unified execution path for all commands.

## Execution Flow
```
User Input
    ↓
SDK Executor (modules/execution/executor.py)
    ↓
Unified Permission Manager (modules/permissions/integration.py)
    ↓
Buffer Manager (modules/permissions/manager.py)
    ↓
Permission Buffer Widget (modules/input_widget/widget.py)
    ↓
User Response
    ↓
Command Handler
```

## Components
- UnifiedPermissionManager: Single instance, manages all permissions
- PermissionBufferManager: Single instance, manages buffer display
- Permission Widget: Displays prompts in TUI
- SDK Executor: Routes all commands

## Command Patterns
[Example code for simple and multi-page prompts]

## Testing
[How to verify single path]

## Migration Guide
[How commands were migrated from legacy]
```

### 10.3 Success Criteria

**ALL must be ✅:**

- [ ] Single UnifiedPermissionManager instance
- [ ] Single PermissionBufferManager instance
- [ ] All commands route through SDK executor
- [ ] All commands use same permission buffer UI
- [ ] Multi-page buffers work correctly
- [ ] No legacy code remains (except compatibility stubs)
- [ ] No broken imports
- [ ] No lost functionality
- [ ] All tests pass
- [ ] Documentation complete

**IF ANY ❌:** Plan INCOMPLETE - do not merge

---

## Execution Order

```
Phase 1:  Inventory legacy features        → LEGACY_FEATURES_INVENTORY.md
Phase 2:  Inventory modular features       → MODULAR_FEATURES_INVENTORY.md
Phase 3:  Gap analysis                     → FEATURE_GAP_ANALYSIS.md
Phase 4:  Migrate core features            → Update modular code
Phase 5:  Migrate remaining features       → Update modular code
Phase 6:  Verify single path               → Test all command groups
Phase 7:  Verify multi-page buffers        → Test interactive commands
Phase 8:  Verify single instance           → Add tracing, test
Phase 9:  Remove legacy code               → Delete old files
Phase 10: Final verification & docs        → ARCHITECTURE.md
```

---

## Current Status

**Phase 1:** READY TO START
**Next Action:** Create `LEGACY_FEATURES_INVENTORY.md`

---

**Last Updated:** 2025-10-22
**Branch:** refactor2
**Maintainer:** Claude Code
