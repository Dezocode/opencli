# Unified Execution Path & Permission Buffer Plan

**Date:** 2025-10-22
**Goal:** Ensure ALL commands use SINGLE execution path through SDK executor with unified permission buffer
**Status:** Analysis Phase

---

## The Actual Goal (What You Want)

```
SINGLE PATH FOR EVERYTHING:

User Input → SDK Executor → Unified Permission Manager → Permission Buffer → User
     ↓
Command Handler gets result via context

NOT THIS MESS:
- Some commands → SDK Executor → Unified Manager ✅
- Some commands → Direct buffer manager call ❌
- Some commands → Old permission system ❌
```

---

## Phase 1: UNDERSTAND Current State (Don't Touch Anything)

### 1.1 Map ALL Command Execution Paths

**Goal:** Document exactly how EACH type of command currently executes

#### Commands to Trace:

**Group A: SDK-Registered Commands (dev_commands.py pattern)**
```python
# File: modules/commands/dev_commands.py
def debug_toggle_prompt(app, session, registration, context):
    """Returns prompt_data dict"""
    return prompt_data  # ← SDK executor handles rest

async def debug_toggle(app, session, **context):
    """Handler gets response from context"""
    prompt_data = context.get('_custom_prompt_data')
    # Execute action
```

**Execution Path:**
1. User types `/debug`
2. SDK Executor calls `debug_toggle_prompt()`
3. SDK Executor gets prompt_data dict
4. SDK Executor calls unified permission manager
5. Unified manager shows permission buffer
6. User responds
7. SDK Executor calls `debug_toggle()` handler with response in context
8. Handler executes

**Question:** Does this use permission buffer? ✅/❌
**Question:** Does this go through unified manager? ✅/❌

---

**Group B: Interactive Buffer Commands (docker_commands.py pattern)**
```python
# File: modules/docker_commands.py
async def docker_main_prompt(app, session, registration, context):
    """Calls buffer manager directly"""
    prompt_data = {...}
    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)

async def docker_main(app, session, **context):
    """Handler gets response from context"""
    prompt_data = context.get('_custom_prompt_data')
    # Execute action
```

**Execution Path:**
1. User types `/docker`
2. SDK Executor calls `docker_main_prompt()`
3. `docker_main_prompt()` calls `get_permission_buffer_manager()`
4. ??? What manager does this return now ???
5. Calls `buffer_manager.request_permission()`
6. ??? Does this show permission buffer ???
7. User responds
8. ??? Who handles response - SDK or buffer manager ???
9. SDK Executor calls `docker_main()` handler
10. Handler executes

**Questions:**
- Does `get_permission_buffer_manager()` return unified manager's buffer? ✅/❌
- Does calling `buffer_manager.request_permission()` bypass SDK executor? ✅/❌
- Do we get TWO permission prompts (SDK + buffer manager)? ✅/❌
- Is this the SAME buffer as Group A commands? ✅/❌

---

**Group C: Legacy/Old Commands**
```python
# Example: modules/command_executor.py, modules/tool_registry.py
# Do these even go through SDK executor?
```

**Questions:**
- Are these registered with SDK executor? ✅/❌
- What path do they take? Document it.

---

### 1.2 Trace Permission Manager Routing

**Current State After Phase 1 Fix:**

```python
# File: modules/permissions/manager.py:522-531
def get_permission_buffer_manager():
    """Legacy compatibility wrapper"""
    from . import get_unified_permission_manager
    unified_manager = get_unified_permission_manager()
    return unified_manager.get_buffer_manager()
```

**Questions:**
1. When `docker_commands.py` calls `get_permission_buffer_manager()`, does it get the SAME instance as SDK executor uses? ✅/❌
2. When that buffer shows a prompt, does it go through SDK executor's flow or bypass it? ✅/❌
3. Are there TWO different buffers being created? ✅/❌

---

### 1.3 Document What Permission Buffer Actually Is

**Questions:**
1. What file contains the permission buffer widget code?
2. Is it `modules/permissions/widget.py`?
3. Or is it inside `MultiLineInput` widget (`modules/input_widget/widget.py`)?
4. How many permission buffer implementations exist?
5. Do they all show the same UI to the user?

---

### 1.4 Test Current Behavior (Manual Testing Required)

**Test Case 1: SDK Pattern Command**
```bash
opencli tui
/debug    # Press ENTER
# Expected: Permission buffer appears with Yes/No
# Record: What actually happens?
# Record: Can you navigate with arrow keys?
# Record: Does ENTER select the option?
```

**Test Case 2: Interactive Buffer Command**
```bash
opencli tui
/docker   # Press ENTER
# Expected: Permission buffer appears with multi-page content
# Record: What actually happens?
# Record: Can you navigate pages?
# Record: Does it look the same as /debug buffer?
```

**Test Case 3: Compare Buffer Instances**
```bash
# Add debug logging to modules/permissions/manager.py
def get_permission_buffer_manager():
    unified_manager = get_unified_permission_manager()
    buffer = unified_manager.get_buffer_manager()
    import sys
    sys.stderr.write(f"[TRACE] Buffer instance ID: {id(buffer)}\n")
    sys.stderr.flush()
    return buffer

# Run both commands and compare IDs
# Are they the same instance? ✅/❌
```

---

## Phase 2: DEFINE Desired Architecture

### 2.1 Single Execution Path Definition

**ALL commands must follow this EXACT flow:**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Input                                               │
│    /command [args]                                          │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 2. SDK Executor (modules/execution/executor.py)            │
│    - Looks up command in registry                          │
│    - Checks if requires_approval                           │
│    - Gets custom_prompt_func                               │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 3. Call Prompt Function                                     │
│    prompt_data = custom_prompt_func(app, session, ...)     │
│    Returns: dict with title, message, options              │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 4. SDK Executor → Unified Permission Manager               │
│    unified_manager.check_permission(registration, context) │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 5. Unified Manager → Buffer Manager                        │
│    buffer_manager = unified_manager.get_buffer_manager()   │
│    buffer_manager.prompt(app, session, prompt_data)        │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 6. Buffer Manager → Permission Buffer Widget               │
│    Shows in TUI via MultiLineInput.permission_prompt_data  │
│    User sees: Title, Message, Options                      │
│    User navigates: UP/DOWN arrows                          │
│    User selects: ENTER key                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 7. User Response → Buffer Manager → Unified Manager        │
│    Response bubbles back up                                │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 8. SDK Executor calls Handler Function                     │
│    await handler_func(app, session, **context)            │
│    context['_custom_prompt_data'] = response              │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 9. Handler Executes                                         │
│    Reads response from context                             │
│    Performs command action                                 │
└─────────────────────────────────────────────────────────────┘
```

**CRITICAL RULES:**

1. **NO command calls permission manager directly** (bypasses SDK)
2. **NO command calls buffer manager directly** (bypasses SDK)
3. **Prompt functions ONLY return prompt_data dict** (SDK handles rest)
4. **Handlers ONLY read from context** (SDK provides response)
5. **ONE buffer instance** (unified manager's buffer)
6. **ONE UI callback** (TUI._show_permission_prompt)

---

### 2.2 Exception: Multi-Page Interactive Buffers

**Question:** Do some commands need multi-page buffers with navigation?

**If YES:**
```python
# Prompt function builds multi-page prompt_data
def docker_main_prompt(app, session, registration, context):
    prompt_data = {
        'title': 'Docker Operations',
        'pages': [  # ← Multi-page structure
            {'title': 'Setup', 'content': '...'},
            {'title': 'Start', 'content': '...'},
            # ...
        ],
        'options': [...]  # Options apply to current page
    }
    return prompt_data  # ← Still just return dict!

# SDK executor handles pagination
# Buffer manager renders pages
# User navigates with arrow keys
# SDK tracks current page
```

**If commands need `buffer_manager.request_permission()` for pagination:**
```python
# This is ONLY acceptable if:
# 1. SDK executor doesn't support pagination yet
# 2. We document this as temporary
# 3. We plan to move pagination into SDK executor

async def docker_main_prompt(app, session, registration, context):
    prompt_data = {...}  # Multi-page data

    # TEMPORARY: Direct buffer call until SDK supports pagination
    buffer_manager = get_permission_buffer_manager()  # Routes to unified
    return await buffer_manager.request_permission(...)  # Handles pages

    # TODO: Move pagination into SDK executor
    # Then this becomes: return prompt_data
```

**Determine:** Do we keep direct buffer calls or migrate to SDK pagination?

---

## Phase 3: VERIFY Single Instance (Testing Phase)

### 3.1 Add Tracing to All Entry Points

**File: modules/permissions/integration.py**
```python
class UnifiedPermissionManager:
    def __init__(self):
        import sys
        instance_id = id(self)
        sys.stderr.write(f"[TRACE] UnifiedPermissionManager created: {instance_id}\n")
        sys.stderr.flush()
        # ... rest of init

    def get_buffer_manager(self):
        buffer = self._buffer_manager
        import sys
        sys.stderr.write(f"[TRACE] get_buffer_manager() returning: {id(buffer)}\n")
        sys.stderr.flush()
        return buffer
```

**File: modules/execution/executor.py**
```python
async def execute(...):
    if registration.requires_approval:
        unified_manager = get_unified_permission_manager()
        import sys
        sys.stderr.write(f"[TRACE] Executor using unified manager: {id(unified_manager)}\n")
        sys.stderr.flush()
        # ... rest
```

**File: modules/permissions/manager.py**
```python
def get_permission_buffer_manager():
    unified_manager = get_unified_permission_manager()
    buffer = unified_manager.get_buffer_manager()
    import sys
    sys.stderr.write(f"[TRACE] Legacy wrapper returning buffer: {id(buffer)}\n")
    sys.stderr.flush()
    return buffer
```

### 3.2 Run Test Commands and Collect Traces

```bash
# Clear log
> /tmp/opencli_trace.log

# Run test
opencli tui 2>/tmp/opencli_trace.log

# In TUI:
/debug
# Press ENTER
# Select option

# Check trace
grep "TRACE" /tmp/opencli_trace.log

# Expected output:
# [TRACE] UnifiedPermissionManager created: 12345678
# [TRACE] Executor using unified manager: 12345678
# [TRACE] get_buffer_manager() returning: 87654321
# ↑↑↑ Same IDs = single instance ✅

# Test second command
/docker
# Press ENTER

# Check trace again
grep "TRACE" /tmp/opencli_trace.log

# Expected: SAME instance IDs
# If different IDs = multiple instances ❌
```

### 3.3 Verify Buffer UI Callback

**File: modules/tui/core.py**
```python
def _setup_permission_system(self):
    from ..permissions import get_unified_permission_manager

    self.permission_manager = get_unified_permission_manager()

    # Add trace
    import sys
    sys.stderr.write(f"[TRACE] TUI setting UI callback: {self._show_permission_prompt}\n")
    sys.stderr.flush()

    self.permission_manager.set_ui_callback(self._show_permission_prompt)
```

**File: modules/tui/permission_handlers.py**
```python
def _show_permission_prompt(self, prompt_data: dict):
    import sys
    sys.stderr.write(f"[TRACE] _show_permission_prompt CALLED with: {prompt_data.get('title')}\n")
    sys.stderr.flush()
    # ... show buffer
```

**Test:**
```bash
# Run with trace
opencli tui 2>/tmp/opencli_trace.log

/debug
# Expected in trace:
# [TRACE] TUI setting UI callback: <function _show_permission_prompt...>
# [TRACE] _show_permission_prompt CALLED with: System: /debug
```

---

## Phase 4: DOCUMENT Current Routing (Analysis Report)

### 4.1 Create Routing Report

**File: ROUTING_ANALYSIS_REPORT.md**

```markdown
# Command Execution Routing Analysis

## Group A: SDK Pattern (Correct ✅)
Commands: /debug, /model, /agent, /provider, etc.

Route:
User → SDK Executor → Unified Manager → Buffer → User → Handler

Files:
- modules/commands/dev_commands.py
- modules/commands/model_commands.py
- modules/commands/agent_commands.py

Status: ✅ Single path, uses permission buffer

## Group B: Interactive Buffer Pattern
Commands: /docker, /docker-setup, etc.

Route:
User → SDK Executor → Prompt Function → get_permission_buffer_manager() → ???

Files:
- modules/docker_commands.py
- modules/docker_commands_unified.py

Status: ⚠️ INVESTIGATE - May bypass SDK or may be routed correctly

Questions:
1. Does get_permission_buffer_manager() return unified instance?
2. Does buffer_manager.request_permission() go through unified manager?
3. Is this the same buffer as Group A?

## Group C: Legacy/Unknown
Commands: ???

Files:
- modules/command_executor.py
- modules/tool_registry.py

Status: ❌ UNKNOWN - Need to trace execution path

## Summary
- ✅ Working: X commands
- ⚠️ Needs Verification: Y commands
- ❌ Wrong Path: Z commands
- Total: X+Y+Z commands
```

### 4.2 Create Instance Tracking Report

**File: INSTANCE_TRACKING_REPORT.md**

```markdown
# Permission Manager Instance Tracking

## Test: /debug Command
UnifiedPermissionManager ID: 12345678
Buffer Manager ID: 87654321
UI Callback: TUI._show_permission_prompt
Result: ✅/❌

## Test: /docker Command
UnifiedPermissionManager ID: 12345678 (same ✅ / different ❌)
Buffer Manager ID: 87654321 (same ✅ / different ❌)
UI Callback: TUI._show_permission_prompt (same ✅ / different ❌)
Result: ✅/❌

## Conclusion
Single instance: ✅/❌
Single buffer: ✅/❌
Single UI: ✅/❌
```

---

## Phase 5: FIX Routing Issues (If Any Found)

### 5.1 IF: Multiple Instances Detected

**Problem:** Different commands create different manager instances

**Fix:**
```python
# Ensure singleton pattern in modules/permissions/integration.py
_unified_instance = None

def get_unified_permission_manager():
    global _unified_instance
    if _unified_instance is None:
        _unified_instance = UnifiedPermissionManager()
    return _unified_instance
```

### 5.2 IF: Commands Bypass SDK Executor

**Problem:** Some commands call permission manager directly without going through SDK

**Fix:** Document which commands need updating, create migration plan

### 5.3 IF: Multiple Buffer Instances

**Problem:** Different buffers created for different commands

**Fix:** Ensure all paths use `unified_manager.get_buffer_manager()`

---

## Phase 6: VERIFY Multi-Page Buffers Work

### 6.1 Test Interactive Buffer Commands

**Test: /docker multi-page navigation**
```bash
opencli tui
/docker
# Press ENTER

# Expected:
# 1. Permission buffer appears ✅/❌
# 2. Shows multiple pages ✅/❌
# 3. Can navigate with arrow keys ✅/❌
# 4. Selecting option works ✅/❌
# 5. Command executes correctly ✅/❌
```

### 6.2 Compare Buffer Appearance

**Question:** Do ALL permission buffers look the same?

- /debug buffer appearance: [describe]
- /docker buffer appearance: [describe]
- Same UI? ✅/❌

---

## Phase 7: REVIEW PR #4 Changes

### 7.1 Check What PR Changed

**Files modified in PR:**
1. modules/docker_commands.py
2. modules/command_executor.py
3. modules/tool_registry.py
4. modules/__init__.py
5. modules/permissions/__init__.py

**For EACH file:**
- What was old import?
- What is new import?
- Does it still work? ✅/❌
- Does it use single path? ✅/❌

### 7.2 Check What PR Deleted

**Files deleted in PR:**
- modules/permission_buffer/ directory
- modules/permission_buffer_manager.py

**Questions:**
1. Did deleting these break anything? ✅/❌
2. Were they actually unused? ✅/❌
3. Did they contain unique functionality? ✅/❌

### 7.3 Decision: Keep or Reject PR

**IF all tests pass:**
- ✅ Single instance verified
- ✅ Single path verified
- ✅ Permission buffer works
- ✅ Multi-page buffers work
- ✅ No functionality lost

**THEN:** Approve PR, merge it

**IF any test fails:**
- ❌ Multiple instances
- ❌ Multiple paths
- ❌ Broken functionality
- ❌ Lost features

**THEN:** Reject PR, document what needs fixing

---

## Phase 8: DOCUMENT Final Architecture

### 8.1 Create Architecture Doc

**File: PERMISSION_ARCHITECTURE.md**

```markdown
# OpenCLI Permission System Architecture

## Overview
Single unified execution path for all commands with permission buffer UI.

## Components

### 1. UnifiedPermissionManager
Location: modules/permissions/integration.py
Singleton: Yes
Manages: Permission requests, buffer manager, UI callbacks

### 2. PermissionBufferManager
Location: modules/permissions/manager.py
Singleton: Yes (via UnifiedPermissionManager)
Manages: Prompt queue, display, responses

### 3. Permission Buffer Widget
Location: modules/input_widget/widget.py (MultiLineInput.permission_prompt_data)
Renders: Permission prompts in TUI

### 4. SDK Executor
Location: modules/execution/executor.py
Role: Routes all commands through unified manager

## Execution Flow
[Diagram from Phase 2]

## Command Patterns

### Pattern A: Simple Prompt
[Example code]

### Pattern B: Multi-Page Prompt
[Example code]

## Testing
[How to verify single path]

## Migration Guide
[How to update old commands]
```

---

## Phase 9: CREATE Migration Guide (If Needed)

### 9.1 IF: Some commands still use old pattern

**Document:**

```markdown
# Migrating Commands to Unified Path

## Old Pattern (Don't Do This)
```python
async def command_prompt(...):
    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(...)
```

## New Pattern (Do This)
```python
def command_prompt(...):
    return prompt_data  # SDK handles the rest
```

## Migration Steps
1. Remove async from prompt function
2. Remove buffer_manager calls
3. Return prompt_data dict only
4. Test command still works
```

---

## Phase 10: CLEANUP Legacy Code (If Safe)

### 10.1 Only Delete If:

**Criteria:**
1. ✅ All commands use unified path
2. ✅ All tests pass
3. ✅ No broken imports
4. ✅ No lost functionality
5. ✅ Documentation complete

### 10.2 What Can Be Deleted

**Safe to delete:**
- [ ] modules/permission_buffer/ (IF all imports updated)
- [ ] modules/permission_buffer_manager.py (IF all imports updated)
- [ ] Backup files (.backup)
- [ ] Unused workflow files

**KEEP (needed for compatibility):**
- [ ] modules/permission_prompt.py (re-export stub)
- [ ] modules/permissions/manager.py (core buffer manager)
- [ ] modules/permissions/integration.py (unified manager)

---

## EXECUTION ORDER

```
Phase 1: UNDERSTAND  → Trace all paths, test manually
Phase 2: DEFINE      → Document desired architecture
Phase 3: VERIFY      → Add tracing, check instances
Phase 4: DOCUMENT    → Create routing analysis report
Phase 5: FIX         → Fix any issues found in Phase 3/4
Phase 6: VERIFY      → Test multi-page buffers work
Phase 7: REVIEW      → Check PR #4 against findings
Phase 8: DOCUMENT    → Final architecture documentation
Phase 9: MIGRATE     → Create migration guide if needed
Phase 10: CLEANUP    → Delete legacy code if safe
```

**CRITICAL:** Do NOT skip phases. Do NOT delete code until Phase 10.

---

## SUCCESS CRITERIA

At the end of Phase 10, verify:

- [ ] Single UnifiedPermissionManager instance
- [ ] Single PermissionBufferManager instance
- [ ] All commands route through SDK executor
- [ ] All commands use same permission buffer UI
- [ ] Multi-page buffers work correctly
- [ ] No broken imports
- [ ] No lost functionality
- [ ] Documentation complete
- [ ] Tests pass
- [ ] Legacy code removed (if safe)

If ANY checkbox is unchecked, plan FAILED - do not delete code.

---

**Last Updated:** 2025-10-22
**Status:** Phase 1 - Ready to Execute
**Next Action:** Trace execution paths for all command groups
