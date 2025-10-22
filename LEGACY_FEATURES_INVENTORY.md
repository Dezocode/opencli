# Legacy Features Inventory

**Date:** 2025-10-22  
**Purpose:** Document all features in legacy permission system files for migration analysis

---

## 1. modules/permission_buffer/ (Legacy Directory)

### Files:
- `__init__.py` (23 lines)
- `manager.py` (203 lines)
- `task.py` (49 lines)
- `enums.py` (20 lines)

### Features:

#### PermissionBufferManager (manager.py)
- ✅ Priority-based prompt queuing with heapq
- ✅ Async permission request handling
- ✅ Auto-dismiss after timeout
- ✅ UI integration via `set_app_context(app, prompt_input)`
- ✅ Queue processing with `_process_queue()`
- ✅ Task state management (QUEUED, DISPLAYING, AWAITING_INPUT, RESOLVED)
- ✅ Statistics tracking (total_prompts, auto_dismissed, user_resolved, cancelled)
- ✅ User response handling
- ✅ Queue clearing
- ✅ Global singleton instance via `get_permission_buffer_manager()`

**Modular equivalent:** ✅ `modules/permissions/manager.py` (530 lines) - enhanced version
**Still used?** ❌ Appears to be superseded by modular version
**Migration needed?** ❌ Already migrated to modular system

#### _PromptTask (task.py)
- ✅ Task dataclass with UUID, priority, timestamp
- ✅ Auto-dismiss logic
- ✅ Future/callback support
- ✅ Priority queue ordering via `__lt__`
- ✅ Task serialization via `to_dict()`

**Modular equivalent:** ✅ `modules/permissions/task.py` (295 lines) - enhanced version
**Still used?** ❌ Superseded by modular version
**Migration needed?** ❌ Already migrated

#### Enums (enums.py)
- ✅ PromptPriority (LOW, NORMAL, HIGH, URGENT)
- ✅ PromptState (QUEUED, DISPLAYING, AWAITING_INPUT, RESOLVED, CANCELLED, AUTO_DISMISSED)

**Modular equivalent:** ✅ `modules/permissions/enums.py` (72 lines) - enhanced with SDKState, PermissionResponse
**Still used?** ❌ Superseded
**Migration needed?** ❌ Already migrated

---

## 2. modules/async_permissions.py (219 lines)

### Features:

#### AsyncPermissionHandler
- ✅ Async permission prompts in TUI
- ✅ Coordinates ToolPermissionManager with UI prompts
- ✅ `check_and_prompt(tool_name, args, current_dir)` - main entry point
- ✅ Risk level integration from ToolPermissionManager
- ✅ Prompt generation for different tools:
  - Edit operations
  - Write operations
  - Bash commands
  - WebFetch
  - ConfigureHeaders
  - Refactoring
- ✅ Response handling with timeout (300s default)
- ✅ Permission response processing:
  - ALLOW_ONCE
  - ALLOW_ALWAYS (adds to allowed tools)
  - ALLOW_DOMAIN
  - DENY
  - CANCEL
- ✅ UI integration via `app.stream_display`
- ✅ Global handler instance management

**Modular equivalent:** ❓ Partially in `modules/permissions/integration.py`
**Still used?** ❓ Need to check imports
**Migration needed?** ✅ YES - Tool-specific prompt generation and async handling logic

---

## 3. modules/tool_permissions.py (321 lines)

### Features:

#### ToolPermissionManager
- ✅ Risk level classification (SAFE, RISKY, DANGEROUS, CRITICAL)
- ✅ Tool risk mapping:
  - SAFE: Read, Glob, Grep, GitHub
  - RISKY: Edit, Write, ConfigureHeaders
  - DANGEROUS: Bash
- ✅ Path-based risk assessment:
  - System directory detection (/etc, /bin, /usr, /System, etc.)
  - Parent directory detection
  - Outside working directory detection
  - `.ssh`, `.aws`, `.config` protection
- ✅ Permission file management (tool_permissions.json)
- ✅ Allowed tools list
- ✅ Auto-accept mode (global and session)
- ✅ `should_prompt()` decision logic
- ✅ Tool operation preview formatting
- ✅ Console-based permission prompting
- ✅ Session state management

**Modular equivalent:** ❓ Risk assessment might be in validation.py?
**Still used?** ❓ Need to check imports
**Migration needed?** ✅ YES - Risk assessment and tool classification logic

---

## 4. modules/permission_workflow.py (171 lines)

### Features:

#### PermissionWorkflow System
- ✅ Multi-step workflow with permission gates
- ✅ WorkflowStep dataclass with:
  - ID, title, description
  - Permission requirement flag
  - Execute function
  - Status tracking
- ✅ WorkflowStepStatus enum (PENDING, WAITING_PERMISSION, APPROVED, IN_PROGRESS, COMPLETED, FAILED, SKIPPED)
- ✅ Status summary generation
- ✅ Permission prompt generation for steps
- ✅ Step approval mechanism
- ✅ Step execution with error handling
- ✅ Workflow cancellation
- ✅ WorkflowManager for managing multiple active workflows

**Modular equivalent:** ❌ Not found in modular system
**Still used?** ❓ Need to check imports
**Migration needed?** ✅ YES - Entire workflow system needs migration

---

## 5. modules/dual_buffer_system.py (247 lines)

### Features:

#### Dual Buffer Architecture
- ✅ ToolBuffer class:
  - Streaming character-by-character output
  - Collapsible sections
  - Visual indicators (⏺ running, ✓ complete, ✗ failed)
  - Tool name and args display
  - Output accumulation
  - Status line updates
- ✅ CommandBuffer class:
  - Immediate writes (no delay)
  - Markdown rendering support
  - Direct style application
  - System message handling
- ✅ DualBufferCoordinator:
  - Write lock for coordination
  - Active tool buffer tracking
  - Command buffer access
  - Tool buffer lifecycle management

**Modular equivalent:** ❌ Not found in modular system
**Still used?** ❓ Need to check imports
**Migration needed?** ✅ YES - Streaming display architecture

---

## 6. modules/permission_buffer_manager.py (70 lines)

### Features:
- ✅ Compatibility stub/re-export layer
- ✅ Re-exports from `modules.permissions`
- ✅ Fallback import logic
- ✅ Deprecation warning
- ✅ Legacy API compatibility

**Purpose:** Backward compatibility during migration
**Still used?** ✅ YES - compatibility layer
**Migration needed?** ❌ Keep for compatibility, remove after all imports updated

---

## 7. modules/permission_prompt.py (57 lines)

### Features:
- ✅ Compatibility stub/re-export layer
- ✅ Re-exports PermissionResponse, PermissionTemplates, PermissionPrompt
- ✅ Fallback import logic
- ✅ Deprecation warning

**Purpose:** Backward compatibility during migration
**Still used?** ✅ YES - compatibility layer
**Migration needed?** ❌ Keep for compatibility, remove after all imports updated

---

## Summary

### Files to KEEP (Compatibility):
- ✅ `modules/permission_buffer_manager.py` - Compatibility stub (until all imports updated)
- ✅ `modules/permission_prompt.py` - Compatibility stub (until all imports updated)

### Files to MIGRATE:
- ✅ `modules/async_permissions.py` - Tool-specific async permission handling
- ✅ `modules/tool_permissions.py` - Risk assessment and tool classification
- ✅ `modules/permission_workflow.py` - Multi-step workflow system
- ✅ `modules/dual_buffer_system.py` - Streaming display architecture

### Files to DELETE (After Migration):
- ❌ `modules/permission_buffer/` - Already superseded by modular system

### Features Needing Migration:
1. **Tool-specific prompt generation** (from async_permissions.py)
2. **Risk level assessment** (from tool_permissions.py)
3. **Path safety validation** (from tool_permissions.py)
4. **Allowed tools management** (from tool_permissions.py)
5. **Multi-step workflow system** (from permission_workflow.py)
6. **Dual buffer streaming** (from dual_buffer_system.py)

---

**Next Step:** Create MODULAR_FEATURES_INVENTORY.md to see what modular system already has
