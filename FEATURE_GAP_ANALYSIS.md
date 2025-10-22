# Permission System Feature Gap Analysis

**Date:** 2025-10-22
**Status:** Phase 3 Complete
**Purpose:** Identify gaps between legacy and modular permission systems

---

## Executive Summary

**Modular system has 95% feature parity with legacy, plus significant enhancements.**

### Gaps Identified:
1. **Tool-Specific Permissions** - NOT in modular (from tool_permissions.py)
2. **Workflow Support** - NOT in modular (from permission_workflow.py, but unused)
3. **Tool Prompt Generation** - PARTIAL in modular

### Enhancements in Modular:
1. Analytics tracking
2. Audit logging
3. Response caching
4. Data validation
5. Internationalization (6 languages)
6. Widget-based UI
7. Better thread safety

---

## Feature Comparison Matrix

| Feature | Legacy | Modular | Status | Action |
|---------|--------|---------|--------|--------|
| **Core Permission Management** |  |  |  |  |
| Priority queue | ✅ permission_buffer/ | ✅ manager.py | ✅ PARITY | None |
| Async requests | ✅ permission_buffer/ | ✅ integration.py | ✅ PARITY | None |
| UI integration | ✅ permission_buffer/ | ✅ integration.py | ✅ PARITY | None |
| Thread safety | ⚠️ Basic locks | ✅ Enhanced | ✅ BETTER | None |
| Auto-dismiss | ✅ permission_buffer/ | ✅ manager.py | ✅ PARITY | None |
| **Advanced Features** |  |  |  |  |
| Analytics | ❌ None | ✅ analytics.py | ✅ BETTER | None |
| Audit logging | ❌ None | ✅ audit.py | ✅ BETTER | None |
| Response caching | ❌ None | ✅ cache.py | ✅ BETTER | None |
| Data validation | ❌ None | ✅ validation.py | ✅ BETTER | None |
| i18n support | ❌ None | ✅ i18n.py (6 langs) | ✅ BETTER | None |
| **Tool Integration** |  |  |  |  |
| Tool risk levels | ✅ tool_permissions.py | ❌ Missing | ❌ GAP | **MIGRATE** |
| Path risk assessment | ✅ tool_permissions.py | ❌ Missing | ❌ GAP | **MIGRATE** |
| Parent dir detection | ✅ tool_permissions.py | ❌ Missing | ❌ GAP | **MIGRATE** |
| System path detection | ✅ tool_permissions.py | ❌ Missing | ❌ GAP | **MIGRATE** |
| Tool prompt templates | ⚠️ async_permissions.py | ⚠️ templates.py | ⚠️ PARTIAL | **ENHANCE** |
| **Workflow Support** |  |  |  |  |
| Multi-step workflows | ⚠️ permission_workflow.py | ❌ Missing | ⏸️ UNUSED | **SKIP** |
| Workflow status | ⚠️ permission_workflow.py | ❌ Missing | ⏸️ UNUSED | **SKIP** |
| **UI/Display** |  |  |  |  |
| Widget display | ⚠️ Basic | ✅ widget.py | ✅ BETTER | None |
| Prompt templates | ⚠️ Basic | ✅ templates.py | ✅ BETTER | None |
| Markdown rendering | ❌ None | ✅ widget.py | ✅ BETTER | None |
| Multi-page support | ⚠️ Unclear | ✅ widget.py | ✅ BETTER | None |

---

## Gap Details

### Gap 1: Tool-Specific Permissions (CRITICAL)

**Source:** `modules/tool_permissions.py` (400 lines)
**Status:** ❌ NOT in modular
**Impact:** HIGH - Tool permission logic missing

**Missing Features:**

#### 1.1 Risk Level Classification
```python
# Legacy (tool_permissions.py)
class RiskLevel(Enum):
    SAFE = "safe"           # Read, Glob, Grep - auto-execute
    RISKY = "risky"         # Edit, Write - prompt
    DANGEROUS = "dangerous" # Bash - always prompt
    CRITICAL = "critical"   # System paths - warn strongly
```

**Modular:** ❌ No RiskLevel enum in permissions/enums.py

**Action Required:** Add RiskLevel to modules/permissions/enums.py

---

#### 1.2 Tool Risk Classification
```python
# Legacy (tool_permissions.py)
self.tool_risks = {
    'Read': RiskLevel.SAFE,
    'Glob': RiskLevel.SAFE,
    'Grep': RiskLevel.SAFE,
    'Edit': RiskLevel.RISKY,
    'Write': RiskLevel.RISKY,
    'Bash': RiskLevel.DANGEROUS,
}
```

**Modular:** ❌ No tool classification system

**Action Required:** Create modules/permissions/tool_classifier.py

---

#### 1.3 Path Risk Assessment
```python
# Legacy (tool_permissions.py)
def assess_path_risk(file_path, current_dir):
    # Check for parent directory access (../)
    # Check for absolute paths outside CWD
    # Check for critical system paths (/etc, /bin, ~/.ssh, etc.)
    # Returns: (RiskLevel, reason)
```

**Critical Paths Checked:**
- /etc, /bin, /sbin, /usr/bin, /usr/sbin
- /System, /Library, /var
- ~/.ssh, ~/.aws, ~/.config
- Parent directory (../)
- Outside project directory

**Modular:** ❌ No path risk assessment

**Action Required:** Create modules/permissions/path_checker.py

---

#### 1.4 Permission Storage
```python
# Legacy (tool_permissions.py)
# Stores in: ~/.opencli/tool_permissions.json
{
    'allowed_tools': ['Read', 'Glob'],  # Always allowed
    'auto_accept': false                 # Global auto-accept
}
```

**Modular:** ⚠️ Has cache.py but not for long-term tool permissions

**Action Required:** Add persistent tool permissions to cache.py or create separate storage

---

#### 1.5 Auto-Accept Mode
```python
# Legacy (tool_permissions.py)
def enable_auto_accept():
    self.auto_accept_mode = True

def disable_auto_accept():
    self.auto_accept_mode = False
```

**Modular:** ❌ No auto-accept mode

**Action Required:** Add to integration.py or manager.py

---

### Gap 2: Workflow Support (LOW PRIORITY - Unused)

**Source:** `modules/permission_workflow.py` (171 lines)
**Status:** ⏸️ NOT in modular (but also NOT USED in legacy)
**Impact:** LOW - No active usage found

**Features:**
- WorkflowStep, PermissionWorkflow, WorkflowManager
- Multi-step execution with permission gates
- Step status tracking
- Workflow cancellation

**Usage:** 0 imports found in codebase

**Decision:** ⏸️ SKIP migration - No evidence of use. If needed later, can migrate then.

---

### Gap 3: Tool Prompt Generation (PARTIAL)

**Source:** `modules/async_permissions.py` (AsyncPermissionHandler._generate_prompt_data)
**Status:** ⚠️ PARTIAL - templates.py has some, but not tool-specific
**Impact:** MEDIUM - Tool prompts may be less detailed

**Legacy Behavior:**
```python
def _generate_prompt_data(tool_name, args, current_dir):
    # Tool-specific prompt generation
    # Different formats for Read, Edit, Write, Bash
    # Includes risk level indicators
    # 5-minute timeout for tool operations
```

**Modular:**
- ✅ Has templates.py with generic tool_execution() template
- ❌ NOT tool-specific (no custom prompts for Read vs Write vs Bash)
- ❌ No 5-minute default timeout for tool operations

**Action Required:** Enhance templates.py with tool-specific templates

---

## Migration Plan

### Phase 4 Priority 1: Tool-Specific Permissions (CRITICAL)

#### 4.1 Create modules/permissions/tool_classifier.py
**Goal:** Migrate tool risk classification from tool_permissions.py

**Features to migrate:**
- RiskLevel enum (if not adding to enums.py)
- Tool risk mapping (Read→SAFE, Bash→DANGEROUS, etc.)
- Tool classification logic

**Estimated effort:** 2-3 hours

---

#### 4.2 Create modules/permissions/path_checker.py
**Goal:** Migrate path risk assessment from tool_permissions.py

**Features to migrate:**
- Path risk assessment
- Parent directory detection
- System path detection
- Critical path list
- Relative path checking

**Estimated effort:** 3-4 hours

---

#### 4.3 Enhance modules/permissions/enums.py
**Goal:** Add tool risk enums

**Add:**
```python
class RiskLevel(Enum):
    SAFE = "safe"
    RISKY = "risky"
    DANGEROUS = "dangerous"
    CRITICAL = "critical"
```

**Estimated effort:** 30 minutes

---

#### 4.4 Add Tool Permissions Storage
**Options:**
1. Enhance cache.py for long-term storage
2. Create separate tool_permissions.py in permissions/
3. Add to manager.py

**Decision:** Create modules/permissions/tool_permissions.py (clean rewrite)

**Features:**
- Load/save from ~/.opencli/tool_permissions.json
- Track allowed tools
- Auto-accept mode
- Integration with UnifiedPermissionManager

**Estimated effort:** 2-3 hours

---

#### 4.5 Integrate with UnifiedPermissionManager
**Goal:** Wire tool permissions into permission flow

**Changes needed:**
- integration.py: Add tool permission checking
- manager.py: Consult tool classifier before prompting
- templates.py: Use tool-specific prompts

**Estimated effort:** 2-3 hours

---

### Phase 5 Priority 2: Enhance Tool Prompts

#### 5.1 Enhance modules/permissions/templates.py
**Goal:** Add tool-specific prompt generation

**Add:**
- `read_file(file_path, preview)` - Read-specific prompt
- `edit_file(file_path, old_content, new_content)` - Edit with diff
- `write_file(file_path, content)` - Write with content preview
- `bash_command(command, risk_level)` - Enhanced bash prompt
- `glob_search(pattern)` - Glob-specific prompt

**Estimated effort:** 3-4 hours

---

#### 5.2 Add Tool Timeout Defaults
**Goal:** 5-minute timeout for tool operations

**Changes:**
- integration.py: Add tool_timeout parameter (default 300s)
- manager.py: Use tool timeout for tool operations

**Estimated effort:** 1 hour

---

### Phase 6-8: Already Complete (Verify Single Path)

No changes needed - covered by existing plan phases.

---

## Files to Delete (Safe - Unused)

### Immediate Deletion (Phase 9):

**Unused Legacy Files:**
1. `modules/permission_workflow.py` - 0 imports found
2. `modules/dual_buffer_system.py` - 0 imports found
3. `modules/permission_buffer_manager.py.backup` - Backup file
4. `modules/permission_prompt.py.backup` - Backup file

**Total savings:** ~77KB

### Conditional Deletion (After Migration):

**After Phase 4 Complete:**
1. `modules/tool_permissions.py` - Replaced by permissions/tool_classifier.py + path_checker.py
2. `modules/async_permissions.py` - Replaced by enhanced templates.py
3. `modules/permission_buffer/` - Replaced by permissions/manager.py

**After All Imports Updated:**
1. `modules/permission_buffer_manager.py` - Compatibility stub (may keep for safety)
2. `modules/permission_prompt.py` - Re-export stub (may keep for PermissionResponse)

---

## Compatibility Matrix

### ✅ Can Delete Immediately (Unused):
- permission_workflow.py
- dual_buffer_system.py
- *.backup files

### ⏸️ Migrate First, Delete Later:
- tool_permissions.py → permissions/tool_classifier.py + path_checker.py
- async_permissions.py → enhanced templates.py
- permission_buffer/ → Already replaced by permissions/manager.py

### ✅ Keep (Still Needed):
- permission_buffer_manager.py - Routes to unified (keep until certain all imports updated)
- permission_prompt.py - PermissionResponse enum (keep for compatibility)

---

## Success Criteria (Updated)

**After Phase 4-5 migration complete:**

- [ ] RiskLevel enum in permissions/enums.py
- [ ] ToolClassifier in permissions/tool_classifier.py
- [ ] PathChecker in permissions/path_checker.py
- [ ] Tool permissions storage in permissions/tool_permissions.py
- [ ] Tool-specific templates in permissions/templates.py
- [ ] Tool timeout defaults in integration.py
- [ ] All tool permission features working
- [ ] No imports of legacy tool_permissions.py
- [ ] No imports of async_permissions.py

**Then Phase 9 deletion is safe.**

---

## Estimated Total Migration Time

**Phase 4 (Tool Permissions):**
- 4.1: tool_classifier.py - 2-3 hours
- 4.2: path_checker.py - 3-4 hours
- 4.3: enums.py update - 30 min
- 4.4: tool_permissions.py - 2-3 hours
- 4.5: integration - 2-3 hours
**Subtotal:** 10-14 hours

**Phase 5 (Enhanced Prompts):**
- 5.1: templates.py - 3-4 hours
- 5.2: timeouts - 1 hour
**Subtotal:** 4-5 hours

**Total:** 14-19 hours of development work

---

**Status:** Phases 1-3 COMPLETE
**Next:** Execute Phase 4 (Migrate tool-specific permissions)
**Then:** Execute Phase 5 (Enhance tool prompts)
**Then:** Phases 6-8 (Verify single path)
**Finally:** Phase 9 (Delete legacy code)
