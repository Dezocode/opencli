# Legacy Permission Features Inventory

**Date:** 2025-10-22
**Status:** Phase 1 Complete
**Purpose:** Document all features in legacy permission code before migration/deletion

---

## 1. modules/permission_buffer/ (Old Permission System)

### Files:
- `__init__.py` (23 lines)
- `enums.py` (15 lines)
- `manager.py` (200 lines)
- `task.py` (50 lines)

### Features:

#### PermissionBufferManager (permission_buffer/manager.py)
**Lines:** 1-200
**Status:** ✅ Used by docker_commands.py and others

**Capabilities:**
- Priority-based queue (heapq implementation)
- Auto-dismiss functionality
- App context integration (`set_app_context()`)
- Performance statistics tracking
- Async permission requests (`request_permission()`)
- Queue processing
- UI integration

**Key Methods:**
- `set_app_context(app, prompt_input)` - Set TUI app reference
- `request_permission(prompt_data, priority, auto_dismiss_after, callback)` - Async request
- `_process_queue()` - Process priority queue
- `_process_task()` - Handle individual task
- `_show_in_ui()` - Display in TUI
- `handle_user_response()` - Process user input
- `cancel_current_prompt()` - Cancel active prompt
- `get_stats()` - Get performance metrics
- `clear_queue()` - Clear all pending prompts

**Used By:**
- Legacy docker commands (via compatibility wrapper)
- Command executor
- Tool registry

**Modular Equivalent:** ✅ modules/permissions/manager.py (enhanced version)

---

#### Enums (permission_buffer/enums.py)

**PromptPriority:**
- URGENT = 0
- HIGH = 1
- NORMAL = 2
- LOW = 3

**PromptState:**
- QUEUED
- DISPLAYING
- RESOLVED
- CANCELLED
- TIMEOUT

**Modular Equivalent:** ✅ modules/permissions/enums.py (same + more)

---

#### _PromptTask (permission_buffer/task.py)

**Features:**
- Task data structure
- Priority comparison (`__lt__`)
- Auto-dismiss checking
- Serialization (`to_dict()`)

**Modular Equivalent:** ✅ modules/permissions/task.py (enhanced)

---

## 2. modules/async_permissions.py (Async Permission Handling)

**Lines:** 180 total
**Status:** ✅ Used by async_interactive/permissions.py

### Features:

#### AsyncPermissionHandler
**Capabilities:**
- Async permission prompts
- Tool permission manager integration
- UI prompt coordination
- Timeout handling (5 min default)
- Response event system
- Permission templates

**Key Methods:**
- `check_and_prompt(tool_name, args, current_dir)` - Check if permission needed
- `_show_permission_prompt()` - Display async prompt
- `_generate_prompt_data()` - Create prompt from tool data
- `set_response()` - Handle user response
- `allow_tool_always()` - Remember permission

**Used By:**
- `modules/async_interactive/permissions.py`
- TUI async tool execution

**Modular Equivalent:** ⚠️ PARTIAL - modules/permissions/integration.py has async request_permission()
**Missing:** Tool-specific prompt generation, 5-min timeout defaults

---

## 3. modules/tool_permissions.py (Tool-Specific Permissions)

**Lines:** 400 total
**Status:** ✅ Used by async_permissions.py, async_interactive/permissions.py

### Features:

#### RiskLevel Enum
- SAFE - Read, Glob, Grep (auto-execute)
- RISKY - Edit, Write (prompt for confirmation)
- DANGEROUS - Bash (always prompt with preview)
- CRITICAL - Parent/outside dirs, system paths

#### ToolPermissionManager
**Capabilities:**
- Tool risk classification
- Path-based risk assessment
- Parent directory detection
- System path detection
- Permissions file storage (~/.opencli/tool_permissions.json)
- Auto-accept mode
- Session-based permissions

**Key Methods:**
- `is_tool_allowed(tool_name)` - Check if tool in allowed list
- `assess_path_risk(file_path, current_dir)` - Evaluate path risk
- `should_prompt(tool_name, args, current_dir)` - Determine if prompt needed
- `allow_tool_always(tool_name)` - Remember permission
- `enable_auto_accept()` - Enable auto-accept mode
- `disable_auto_accept()` - Disable auto-accept mode

**Used By:**
- `modules/async_permissions.py` (AsyncPermissionHandler)
- `modules/async_interactive/permissions.py`

**Modular Equivalent:** ❌ MISSING - No tool-specific permission logic in modules/permissions/

---

## 4. modules/permission_workflow.py (Multi-Step Workflows)

**Lines:** 171 total
**Status:** ❌ NOT USED (0 imports found)

### Features:

#### WorkflowStepStatus Enum
- PENDING
- WAITING_PERMISSION
- APPROVED
- IN_PROGRESS
- COMPLETED
- FAILED
- SKIPPED

#### WorkflowStep Dataclass
**Fields:**
- id, title, description
- requires_permission (bool)
- permission_prompt (dict)
- execute_func (async callable)
- status, result, error

#### PermissionWorkflow
**Capabilities:**
- Multi-step workflow management
- Permission gates between steps
- Status tracking
- Progress summary
- Step-by-step execution
- Cancellation support

**Key Methods:**
- `get_current_step()` - Get active step
- `get_status_summary()` - Progress report
- `get_permission_prompt_for_current_step()` - Get prompt data
- `approve_current_step()` - Mark step approved
- `execute_current_step()` - Run step function
- `next_step()` - Advance workflow
- `cancel()` - Cancel workflow

#### WorkflowManager
**Capabilities:**
- Workflow registry
- Multiple concurrent workflows
- Workflow lifecycle management

**Used By:** ❌ NONE (0 imports)

**Modular Equivalent:** ❌ MISSING - No workflow support in modules/permissions/

**Decision:** ⏸️ Can delete (unused) OR migrate if needed for future features

---

## 5. modules/dual_buffer_system.py (Dual Buffer Display)

**Lines:** 246 total
**Status:** ❌ NOT USED (0 imports found)

### Features:

#### ToolBuffer
**Capabilities:**
- Streaming tool output display
- Character-by-character streaming
- Collapsible sections
- Visual indicators (⏺ running, ✓ complete)
- Rich text formatting
- Status line updates

**Key Methods:**
- `start()` - Begin tool execution display
- `write_chunk(text)` - Stream output chunk
- `finish(success)` - Mark complete
- `toggle_collapse()` - Collapse/expand output

#### CommandBuffer
**Capabilities:**
- Immediate writes for system messages
- Chat message display
- Debug output
- Prevents interleaving with ToolBuffer

**Used By:** ❌ NONE (0 imports)

**Modular Equivalent:** ⚠️ UNCLEAR - Streaming display exists in modules/streaming_display/

**Decision:** ⏸️ Can delete (unused) OR check if streaming_display/ replaced this

---

## 6. modules/permission_buffer_manager.py (Compatibility Stub)

**Lines:** 70 total (2KB)
**Status:** ✅ USED by many files (imports routed to unified)

### Features:

**Compatibility Wrapper:**
```python
def get_permission_buffer_manager():
    """Get permission buffer manager (legacy compatibility)"""
    unified_manager = get_unified_permission_manager()
    return unified_manager.get_buffer_manager()
```

**Purpose:**
- Routes legacy imports to unified system
- Maintains backward compatibility
- Shows deprecation warning

**Re-exports:**
- PermissionBufferManager
- get_permission_buffer_manager
- PromptPriority
- PromptState
- _PromptTask

**Used By:** Files that haven't been updated to use modules/permissions/ directly

**Decision:** ✅ KEEP - Needed for compatibility until all imports updated

---

## 7. modules/permission_prompt.py (Re-export Stub)

**Lines:** 54 total (1.5KB)
**Status:** ✅ USED for PermissionResponse enum

### Features:

**Re-exports:**
- PermissionResponse (enum)
- PermissionTemplates (if available)

**Purpose:**
- Backward compatibility for PermissionResponse imports
- Central export point for permission enums

**Used By:** Command files (dev_commands.py, model_commands.py, etc.)

**Decision:** ✅ KEEP - Still used for PermissionResponse enum

---

## Summary: Legacy Features Status

### ✅ MUST KEEP (Used, no replacement):
1. **tool_permissions.py** - Tool-specific permission logic, risk assessment, path detection
2. **permission_buffer_manager.py** - Compatibility wrapper (until imports updated)
3. **permission_prompt.py** - PermissionResponse enum re-export

### ⚠️ USED BUT HAS MODULAR EQUIVALENT:
1. **permission_buffer/manager.py** - Replaced by permissions/manager.py (enhanced)
2. **permission_buffer/enums.py** - Replaced by permissions/enums.py
3. **permission_buffer/task.py** - Replaced by permissions/task.py
4. **async_permissions.py** - Partially replaced by permissions/integration.py

### ❌ UNUSED (Safe to delete):
1. **permission_workflow.py** - 0 imports found
2. **dual_buffer_system.py** - 0 imports found
3. **permission_buffer_manager.py.backup** - Backup file
4. **permission_prompt.py.backup** - Backup file

---

## Migration Priorities

### Priority 1: MUST MIGRATE (Used, no modular equivalent)
1. **tool_permissions.py** → modules/permissions/tool_permissions.py
   - Tool risk classification
   - Path risk assessment
   - Parent directory detection
   - System path detection

2. **async_permissions.py** (tool-specific features) → modules/permissions/
   - Tool prompt generation
   - 5-minute timeout defaults

### Priority 2: CAN MIGRATE (Used, modular has partial support)
1. **permission_workflow.py** → modules/permissions/workflow.py
   - IF needed for future multi-step commands
   - Currently unused (0 imports)

### Priority 3: KEEP AS COMPATIBILITY (Needed until imports updated)
1. **permission_buffer_manager.py** - Keep until all imports updated
2. **permission_prompt.py** - Keep for PermissionResponse enum

### Priority 4: DELETE IMMEDIATELY (Unused)
1. **.backup files** - Old backups
2. **dual_buffer_system.py** - Replaced by streaming_display/

---

**Next:** Phase 2 - Inventory modular features in modules/permissions/
