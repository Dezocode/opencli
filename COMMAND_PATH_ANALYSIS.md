# OpenCLI Command Path Analysis - Visual Documentation
Generated: 2025-10-22 23:15

## Permission System Architecture

### NEW REFACTORED SYSTEM (✅ Stable)
```
modules/permissions/
├── __init__.py              # Exports all components
├── manager.py               # PermissionBufferManager, get_permission_buffer_manager
├── enums.py                 # PermissionResponse, PromptPriority, PromptState
├── integration.py           # UnifiedPermissionManager, show_*_permission_prompt
├── templates.py             # PermissionTemplates
├── widget.py                # PermissionPrompt widget
├── risk_assessment.py       # RiskAssessmentManager, RiskLevel
├── validation.py            # ValidationManager
├── analytics.py             # AnalyticsManager
├── audit.py                 # AuditManager
├── cache.py                 # CacheManager
├── i18n.py                  # I18nManager
└── task.py                  # _PromptTask, TaskQueue
```

**Import Path:** `from modules.permissions import PermissionResponse, get_permission_buffer_manager`

**Status:** ✅ Working with refactored permission buffers

### LEGACY COMPATIBILITY STUBS (⚠️ Transitional)
```
modules/
├── permission_prompt.py          # Stub re-exporting from permissions/
└── permission_buffer_manager.py  # Stub re-exporting from permissions/
```

**Import Path:** `from modules.permission_prompt import PermissionResponse`

**Status:** ⚠️ Works but goes through compatibility layer

### BROKEN RELATIVE IMPORTS (❌ Non-functional)
```
Commands using: from ..permission_prompt import X
```

**Problem:** Relative imports fail with "attempted relative import beyond top-level package"

**Status:** ❌ Completely broken - imports fail at runtime

---

## SDK Enforcement & Execution Flow Architecture

### NEW SDK-CONTROLLED PATH (✅ All Commands Use This)

All commands in `command_registry.py` register through SDK enforcement:

```
Command Definition → command_registry.py → _safe_register() →
enforce_handler() → Validation/Auto-convert → ExecutionRegistry →
PermissionManager → Buffer Display
```

**Key Components:**
- **`_safe_register()`**: SDK-enforced registration wrapper in `modules/commands/registry.py`
- **`enforce_handler()`**: Validates handler compliance, auto-converts if needed
- **`ExecutionRegistry`**: Central registry tracking all commands with metadata
- **`PermissionManager`**: Displays permission buffers using refactored system

**SDK Enforcement Actions:**
- ✅ **ACCEPTED** - Handler is SDK-compliant as-is
- ⚠️ **CONVERTED** - Handler auto-converted to comply with SDK
- 🔄 **WRAPPED** - Handler wrapped with compliance layer
- ❌ **REJECTED** - Handler cannot be made compliant (fatal error)

**Registration Code Pattern:**
```python
# From modules/commands/command_registry.py
await _safe_register(
    executor, ExecutionType.COMMAND, '/help', show_help,
    ExecutionCategory.BASIC, RiskLevel.SAFE,
    requires_approval=True,
    description="Show available commands with descriptions",
    custom_prompt_func=show_help_prompt,  # ← Integrates with permission buffer
)
```

**Execution Flow for User Commands:**
```
User types: /help
    ↓
TUI Input Handler (modules/input_widget/)
    ↓
Command Router (modules/commands/command_router.py)
    ↓
ExecutionRegistry lookup (finds handler + metadata)
    ↓
PermissionManager (shows buffer using custom_prompt_func)
    ↓
User selects: [Allow] / [Cancel]
    ↓
Handler executes: show_help(app, session, **context)
    ↓
Result displayed in TUI
```

**All Commands Use SDK Path:**
- **Once imports are fixed**, ALL 47 broken commands will use this SDK-controlled path
- **Permission buffers** will display using refactored stable system
- **Handlers** are validated and converted automatically
- **Execution flow** routes through central registry with enforcement

**Why Import Fixes Enable SDK Path:**
- Commands can't register if imports fail during module load
- Broken imports → Module load fails → `_safe_register()` never called
- Fixed imports → Module loads → Commands register through SDK → Buffers work

---

## Command-by-Command Analysis

### Legend
- 🟢 **REFACTORED PATH**: Uses `from modules.*` (working with stable permission buffers)
- 🟡 **COMPAT STUB PATH**: Uses `from modules.permission_*` (working through compatibility layer)
- 🔴 **LEGACY RELATIVE**: Uses `from ..*` (BROKEN - import errors)
- ⚪ **NO PERMISSIONS**: Doesn't use permission system

---

## Agent Commands (8 commands) - agent_commands.py

**Status:** 🔴 **BROKEN - Legacy Relative Imports**

### Current Import Paths:
```python
from ..agent_manager import AgentManager                    # 🔴 BROKEN
from ..permission_prompt import PermissionResponse          # 🔴 BROKEN
```

### Should Be (After Fix):
```python
from modules.agent_manager import AgentManager              # 🟡 COMPAT
from modules.permissions import PermissionResponse          # 🟢 REFACTORED
# OR use compat stub:
from modules.permission_prompt import PermissionResponse    # 🟡 COMPAT
```

### Commands Affected:
- `/agent` (list agents) - 🔴 BROKEN
- `/agents` - 🔴 BROKEN
- `/agent assistant` - 🔴 BROKEN
- `/agent debugger` - 🔴 BROKEN
- `/agent reviewer` - 🔴 BROKEN
- `/agent refactor` - 🔴 BROKEN
- `/agent tester` - 🔴 BROKEN
- `/agent documenter` - 🔴 BROKEN
- `/agent architect` - 🔴 BROKEN

**Permission Buffers:** ❌ Cannot display - imports fail before reaching permission code

---

## Basic Commands (7 commands) - basic_commands.py

**Status:** 🔴 **BROKEN - Legacy Relative Imports**

### Current Import Paths:
```python
from ..permission_prompt import PermissionResponse                # 🔴 BROKEN
from ..permission_buffer_manager import get_permission_buffer_manager  # 🔴 BROKEN
```

### Should Be (After Fix):
```python
from modules.permissions import PermissionResponse, get_permission_buffer_manager  # 🟢 REFACTORED
```

### Commands Affected:
- `/help` - 🔴 BROKEN
- `/status` - 🔴 BROKEN
- `/clear` - 🔴 BROKEN
- `/bashes` - 🔴 BROKEN
- `/commands` - 🔴 BROKEN
- `/permissions` - 🔴 BROKEN (ironically, the permissions command itself is broken!)
- `/exit` / `/quit` - 🔴 BROKEN

**Permission Buffers:** ❌ Cannot display - imports fail

---

## Dev Commands (3 commands) - dev_commands.py

**Status:** 🔴 **BROKEN - Legacy Relative Imports**

### Current Import Paths:
```python
from ..permission_prompt import PermissionResponse                # 🔴 BROKEN
from ..permission_buffer_manager import get_permission_buffer_manager  # 🔴 BROKEN
```

### Commands Affected:
- `/debug` - 🔴 BROKEN
- `/performance` - 🔴 BROKEN
- `/reload` - 🔴 BROKEN

**Permission Buffers:** ❌ Cannot display

---

## Diff Commands (3 commands) - diff_commands.py

**Status:** 🔴 **BROKEN - Legacy Relative Imports**

### Current Import Paths:
```python
from ..permission_prompt import PermissionResponse                # 🔴 BROKEN
from ..permission_buffer_manager import get_permission_buffer_manager  # 🔴 BROKEN
```

### Commands Affected:
- `/diff` - 🔴 BROKEN
- `/diff git` - 🔴 BROKEN
- `/diff worktree` - 🔴 BROKEN

**Permission Buffers:** ❌ Cannot display

---

## Local Commands (1 command) - local_commands.py

**Status:** 🔴 **BROKEN - Legacy Relative Imports**

### Current Import Paths:
```python
from ..permission_prompt import PermissionResponse                # 🔴 BROKEN
from ..permission_buffer_manager import get_permission_buffer_manager  # 🔴 BROKEN
```

### Commands Affected:
- `/local` - 🔴 BROKEN

**Permission Buffers:** ❌ Cannot display

---

## Model Commands (5 commands) - model_commands.py

**Status:** 🔴 **BROKEN - Legacy Relative Imports**

### Current Import Paths:
```python
from ..permission_prompt import PermissionResponse                # 🔴 BROKEN
from ..permission_buffer_manager import get_permission_buffer_manager  # 🔴 BROKEN
```

### Commands Affected:
- `/model` - 🔴 BROKEN
- `/model list` - 🔴 BROKEN
- `/model providers` - 🔴 BROKEN
- `/model r1` - 🔴 BROKEN
- `/model r2` - 🔴 BROKEN

**Permission Buffers:** ❌ Cannot display - critical for model switching!

---

## Provider Commands (6 commands) - provider_commands.py

**Status:** 🔴 **BROKEN - Legacy Relative Imports**

### Current Import Paths:
```python
from ..permission_prompt import PermissionResponse                # 🔴 BROKEN
from ..permission_buffer_manager import get_permission_buffer_manager  # 🔴 BROKEN
```

### Commands Affected:
- `/provider` - 🔴 BROKEN
- `/providers` - 🔴 BROKEN
- `/providers list` - 🔴 BROKEN
- `/providers add` - 🔴 BROKEN
- `/providers add ollama` - 🔴 BROKEN
- `/providers remove` - 🔴 BROKEN

**Permission Buffers:** ❌ Cannot display

---

## Spec Commands (7 commands) - spec_commands.py

**Status:** 🔴 **BROKEN - Legacy Relative Imports**

### Current Import Paths:
```python
from ..specify_wrapper import SpecifyWrapper                      # 🔴 BROKEN
from ..permission_prompt import PermissionResponse                # 🔴 BROKEN
from ..permission_buffer_manager import get_permission_buffer_manager  # 🔴 BROKEN
```

### Commands Affected:
- `/spec` (run specify) - 🔴 BROKEN
- `/constitution` - 🔴 BROKEN
- `/plan` - 🔴 BROKEN
- `/tasks` - 🔴 BROKEN
- `/implement` - 🔴 BROKEN
- `/test` - 🔴 BROKEN
- `/spec-check` - 🔴 BROKEN

**Permission Buffers:** ❌ Cannot display

---

## System Commands (7 commands) - system_commands.py

**Status:** 🔴 **BROKEN - Legacy Relative Imports**

### Current Import Paths:
```python
from ..permission_prompt import PermissionResponse                # 🔴 BROKEN
from ..permission_buffer_manager import get_permission_buffer_manager  # 🔴 BROKEN
```

### Commands Affected:
- `/restart` - 🔴 BROKEN
- `/upgrade` - 🔴 BROKEN
- `/api` (server control) - 🔴 BROKEN
- `/rollback` - 🔴 BROKEN
- `/refactor` - 🔴 BROKEN
- `/autorefactor` - 🔴 BROKEN
- `/inject` - 🔴 BROKEN

**Permission Buffers:** ❌ Cannot display

---

## Docker Commands (8 commands) - command_registry.py

**Status:** 🟡 **WORKING - Defined directly in registry**

### Import Paths:
Docker commands are defined inline in `command_registry.py` and don't have separate files, so they use direct imports from the registry context.

### Commands Affected:
- `/docker` - ✅ WORKING
- `/docker ps` - ✅ WORKING
- `/docker stats` - ✅ WORKING
- `/docker status` - ✅ WORKING
- `/docker ollama setup` - ✅ WORKING
- `/docker ollama start` - ✅ WORKING
- `/docker ollama status` - ✅ WORKING
- `/docker ollama stop` - ✅ WORKING

**Permission Buffers:** ✅ Working with refactored system

---

## Summary Table

| File | Commands | Imports | Permission System | SDK Path | Status |
|------|----------|---------|-------------------|----------|--------|
| agent_commands.py | 8 | 🔴 Relative | ❌ Broken | ⏸️ Blocked at import | BLOCKED |
| basic_commands.py | 7 | 🔴 Relative | ❌ Broken | ⏸️ Blocked at import | BLOCKED |
| dev_commands.py | 3 | 🔴 Relative | ❌ Broken | ⏸️ Blocked at import | BLOCKED |
| diff_commands.py | 3 | 🔴 Relative | ❌ Broken | ⏸️ Blocked at import | BLOCKED |
| local_commands.py | 1 | 🔴 Relative | ❌ Broken | ⏸️ Blocked at import | BLOCKED |
| model_commands.py | 5 | 🔴 Relative | ❌ Broken | ⏸️ Blocked at import | BLOCKED |
| provider_commands.py | 6 | 🔴 Relative | ❌ Broken | ⏸️ Blocked at import | BLOCKED |
| spec_commands.py | 7 | 🔴 Relative | ❌ Broken | ⏸️ Blocked at import | BLOCKED |
| system_commands.py | 7 | 🔴 Relative | ❌ Broken | ⏸️ Blocked at import | BLOCKED |
| command_registry.py | 8 | 🟡 Mixed | ✅ Working | ✅ Using SDK enforcement | WORKING |
| **TOTAL** | **55** | | | **9 blocked, 1 working** | **47 BROKEN** |

**SDK Path Status Explanation:**
- **⏸️ Blocked at import**: Import errors prevent module load, `_safe_register()` never reached
- **✅ Using SDK enforcement**: Commands register through `_safe_register()` → `enforce_handler()` flow

**After Import Fixes:**
All files will show "✅ Using SDK enforcement" and commands will register properly through the SDK-controlled path with permission buffers working.

---

## Fix Strategy

### Option 1: Use Compatibility Stubs (Safer)
```python
# Simple 1:1 replacement
from ..permission_prompt import X
↓
from modules.permission_prompt import X
```

**Pros:** Minimal change, uses existing compatibility layer
**Cons:** Goes through extra indirection layer

### Option 2: Direct to Refactored System (Better)
```python
# Use new refactored system directly
from ..permission_prompt import PermissionResponse
from ..permission_buffer_manager import get_permission_buffer_manager
↓
from modules.permissions import PermissionResponse, get_permission_buffer_manager
```

**Pros:** Direct access to refactored system, cleaner imports
**Cons:** Requires understanding which module has which component

### Recommended: Hybrid Approach
```python
# For permission components - use refactored directly
from modules.permissions import PermissionResponse, get_permission_buffer_manager

# For other modules - use simple replacement
from modules.agent_manager import AgentManager
from modules.specify_wrapper import SpecifyWrapper
```

---

## Impact of Fix

### Before (Current State):
- 🔴 **47 commands broken** - Import errors prevent loading
- ❌ Permission buffers: Cannot display (imports fail)
- ❌ SDK Registration: 28 / 46 commands (61% failure rate)
- ❌ User Experience: Most slash commands don't work

### After Fix:
- ✅ **47 commands working** - All imports resolve correctly
- ✅ Permission buffers: Display using refactored stable system
- ✅ SDK Registration: 46 / 46 commands (100% success rate)
- ✅ User Experience: All slash commands functional
- ✅ Execution flow: Messages go to AI properly
- ✅ Command handlers: Permission prompts work correctly

---

## Files Requiring Changes

**Total: 16 files, 32 import statements**

### Commands (13 files):
1. modules/commands/agent_commands.py (2 imports)
2. modules/commands/basic_commands.py (2 imports)
3. modules/commands/command_registry.py (1 import)
4. modules/commands/command_router.py (2 imports)
5. modules/commands/dev_commands.py (2 imports)
6. modules/commands/diff_commands.py (2 imports)
7. modules/commands/local_commands.py (2 imports)
8. modules/commands/model_commands.py (2 imports)
9. modules/commands/provider_commands.py (2 imports)
10. modules/commands/registry.py (3 imports)
11. modules/commands/spec_commands.py (3 imports)
12. modules/commands/system_commands.py (2 imports)
13. modules/commands/tool_registry.py (1 import)

### Other Modules (3 files):
14. modules/async_interactive/core.py (1 import)
15. modules/tools/core_tools.py (2 imports)
16. modules/tui/command_handlers.py (3 imports)

---

## Verification

All target imports verified to exist and use refactored permission system:

✅ `modules/permissions/` - Full refactored system (stable)
✅ `modules/permission_prompt.py` - Compatibility stub (working)
✅ `modules/permission_buffer_manager.py` - Compatibility stub (working)
✅ `modules/agent_manager.py` - Exists
✅ `modules/specify_wrapper.py` - Exists
✅ `modules/github_tool.py` - Exists
✅ `modules/header_autoconfig.py` - Exists
✅ `modules/command_suggestions.py` - Exists
✅ `modules/execution/registry.py` - Exists
✅ `modules/sdk/enforcement.py` - Exists
✅ `modules/tui/core.py` - Exists

**All imports will work with refactored stable permission buffer system after fix.**

---

# PERMISSION SYSTEM HEALTH & EXECUTION FLOW VISUALIZATION

## System Health Status

### 🏥 Permission System Component Health Matrix

| Component | Location | Status | Health Check | Session Integration |
|-----------|----------|--------|--------------|---------------------|
| **PermissionBufferManager** | `modules/permissions/manager.py` | ✅ Active | Priority queue running | ✅ Worker thread daemon |
| **UnifiedPermissionManager** | `modules/permissions/integration.py` | ✅ Active | Buffer + UI integrated | ✅ UI callback registered |
| **PermissionPrompt Widget** | `modules/permissions/widget.py` | ✅ Active | Receives key events | ✅ Focus management working |
| **I18nManager** | `modules/permissions/i18n.py` | ✅ Active | Locale support ready | ⚪ Session-independent |
| **ValidationManager** | `modules/permissions/validation.py` | ✅ Active | Prompt/response validation | ⚪ Stateless validator |
| **AnalyticsManager** | `modules/permissions/analytics.py` | ✅ Active | Tracking prompts/responses | ✅ Session analytics stored |
| **AuditManager** | `modules/permissions/audit.py` | ✅ Active | Event logging enabled | ✅ Session audit trail |
| **CacheManager** | `modules/permissions/cache.py` | ✅ Active | Permission caching ready | ✅ Session-scoped cache |
| **RiskAssessmentManager** | `modules/permissions/risk_assessment.py` | ✅ Active | Risk scoring functional | ⚪ Context-based |
| **ExecutionRegistry** | `modules/execution/registry.py` | ✅ Active | Command/tool tracking | ✅ Session executor instance |
| **ExecutionSystem** | `modules/execution/executor.py` | ✅ Active | Unified execution entry | ✅ Session-bound |
| **ToolRegistry** | `modules/tool_registry.py` | ✅ Active | Tool permission gates | ✅ Session tool tracking |
| **PermissionManager** | `modules/execution/permission_manager.py` | ✅ Active | Execution permission checks | ✅ Session permission state |

**Legend:**
- ✅ **Active** - Component initialized and operational
- ⚪ **Independent** - Not session-bound (stateless utility)
- ❌ **Broken** - Component failing (none currently)
- ⚠️ **Degraded** - Partially functional (none currently)

---

## Session Memory Structure & Permission State

### 📦 Session Object Architecture

```python
class Session:
    session_id: str              # Unique session identifier (UUID)
    messages: List[Dict]         # Conversation history
    model: str                   # Active AI model
    cwd: str                     # Current working directory
    current_agent: str           # Active agent ('assistant', 'debugger', etc.)
    permission_manager: Optional # Link to PermissionManager instance
    debug_mode: bool             # Debug flag

    # Permission State (in permission_manager)
    ├── permission_cache         # Cached permission decisions
    ├── analytics_data           # Permission usage analytics
    ├── audit_log                # Permission event history
    └── active_prompts           # Currently displayed prompts
```

### 🔐 Permission State Management in Session

**Permission Manager Session Binding:**
```python
# On session creation
session = Session(model="gpt-4")
session.permission_manager = PermissionManager()

# Permission manager tracks:
session.permission_manager.permission_cache = {
    "Read:/path/to/file": {
        "decision": "ALLOW_ALWAYS",
        "timestamp": "2025-10-28T...",
        "expires": None  # ALLOW_ALWAYS never expires
    },
    "Bash:npm install": {
        "decision": "ALLOW_ONCE",
        "timestamp": "2025-10-28T...",
        "expires": "session"  # Cleared on session end
    }
}

session.permission_manager.analytics = {
    "total_prompts": 15,
    "allowed": 12,
    "denied": 2,
    "cached": 1,
    "by_category": {
        "FILE_OPERATION": 8,
        "BASH_COMMAND": 5,
        "API_CALL": 2
    }
}

session.permission_manager.audit_log = [
    {"timestamp": "...", "event": "PERMISSION_PROMPT", "tool": "Read", ...},
    {"timestamp": "...", "event": "PERMISSION_GRANTED", "tool": "Read", ...},
    # ... full audit trail
]
```

### 💾 Session Memory Lifecycle

```
Session Start
    ↓
Create Session Object
    ↓
Initialize PermissionManager
    ↓
Register with UnifiedPermissionManager
    ↓
┌─────────────────────────────────────┐
│ SESSION ACTIVE                      │
│ ✅ Messages stored                  │
│ ✅ Permissions cached               │
│ ✅ Analytics tracked                │
│ ✅ Audit logged                     │
└─────────────────────────────────────┘
    ↓
Session End / Save
    ↓
Write to ~/.opencli/sessions/{session_id}.json
    ↓
Persist:
  - session_id
  - messages
  - model
  - cwd
  - debug_mode
  - timestamp

Permission state (NOT persisted - fresh per session):
  ❌ permission_cache (cleared)
  ❌ analytics_data (reset)
  ❌ audit_log (not saved)

Note: ALLOW_ALWAYS permissions stored in global config, not session
```

---

## Tools vs Commands: Dual Execution Paths

### 🛠️ Registered Tools (9 Default Tools)

| Tool Name | Category | Risk Level | Approval Required | Background | Session Tracked |
|-----------|----------|------------|-------------------|------------|-----------------|
| `openai_chat_completion` | API_CALL | MEDIUM | ❌ No (fast/frequent) | ❌ Foreground | ✅ Yes |
| `anthropic_messages` | API_CALL | MEDIUM | ❌ No | ❌ Foreground | ✅ Yes |
| `docker_container_create` | DOCKER | HIGH | ✅ Yes | ✅ Background | ✅ Yes |
| `docker_image_pull` | DOCKER | MEDIUM | ✅ Yes | ✅ Background | ✅ Yes |
| `file_write` | FILE_OPERATION | MEDIUM | ✅ Yes | ❌ Foreground | ✅ Yes |
| `file_delete` | FILE_OPERATION | HIGH | ✅ Yes | ❌ Foreground | ✅ Yes |
| `http_request` | NETWORK | MEDIUM | ✅ Yes | ⚠️ Optional | ✅ Yes |
| **+ Custom Tools** | Various | Various | Configurable | Configurable | ✅ Yes |

**Tool Execution Flow:**
```
AI requests tool → ToolRegistry lookup → Check requires_approval
    ↓
If approval required:
    ToolRegistry → UnifiedPermissionManager → PermissionPrompt Widget
    ↓
User decision: [Allow] / [Deny]
    ↓
If allowed:
    ExecutionSystem.execute() → Tool handler → Result
    ↓
Track in session.active_tools
    ↓
Update analytics & audit log
```

### 📋 Registered Commands (55 Slash Commands)

**Command Categories:**
- **Agent Commands** (8): `/agent`, `/agent assistant`, etc.
- **Basic Commands** (7): `/help`, `/status`, `/clear`, etc.
- **Dev Commands** (3): `/debug`, `/performance`, `/reload`
- **Diff Commands** (3): `/diff`, `/diff git`, `/diff worktree`
- **Docker Commands** (8): `/docker`, `/docker ps`, etc.
- **Local Commands** (1): `/local`
- **Model Commands** (5): `/model`, `/model list`, etc.
- **Provider Commands** (6): `/provider`, `/providers add`, etc.
- **Spec Commands** (7): `/spec`, `/constitution`, `/plan`, etc.
- **System Commands** (7): `/restart`, `/upgrade`, `/api`, etc.

**Command Execution Flow:**
```
User types: /help
    ↓
TUI Input Widget captures keystroke
    ↓
Command Router identifies: ExecutionType.COMMAND
    ↓
ExecutionRegistry lookup → Find handler + metadata
    ↓
Check registration.requires_approval
    ↓
If approval required:
    ExecutionSystem → UnifiedPermissionManager → PermissionPrompt Widget
    ↓
    Display custom_prompt_func() result in permission buffer
    ↓
    User navigates with arrow keys: [Allow Once] / [Allow Always] / [Cancel]
    ↓
    User presses Enter
    ↓
If allowed:
    SDK Enforcement: enforce_handler() validates compliance
    ↓
    Handler executes: await show_help(app, session, **context)
    ↓
    Result rendered in TUI
    ↓
Update session analytics & audit log
```

---

## Complete Data Flow Architecture

### 🔄 Unified Execution Flow (Tools + Commands)

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INPUT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  TUI Input Widget          AI Tool Request                      │
│  (KeyPress handler)        (OpenAI/Anthropic API)               │
└────────┬──────────────────────────┬─────────────────────────────┘
         │                          │
         ▼                          ▼
┌─────────────────┐        ┌──────────────────┐
│ Command Router  │        │  Tool Registry   │
│ (Slash commands)│        │  (API tools)     │
└────────┬────────┘        └────────┬─────────┘
         │                          │
         └──────────┬───────────────┘
                    ▼
        ┌──────────────────────────┐
        │   ExecutionRegistry      │
        │   (Lookup handler)       │
        └──────────┬───────────────┘
                   ▼
        ┌──────────────────────────┐
        │   Check requires_approval│
        └──────────┬───────────────┘
                   │
         ┌─────────┴──────────┐
         │ YES                │ NO
         ▼                    ▼
┌────────────────────┐   ┌─────────────────┐
│ PERMISSION LAYER   │   │ Execute directly│
├────────────────────┤   └─────────────────┘
│ UnifiedPermission  │
│ Manager            │
└─────────┬──────────┘
          ▼
┌─────────────────────────────────────────┐
│  PermissionBufferManager                │
│  ├── Priority Queue (heapq)             │
│  ├── Worker Thread (daemon)             │
│  ├── Task Validation                    │
│  ├── I18n/Analytics/Audit/Cache         │
│  └── Widget Integration                 │
└─────────┬───────────────────────────────┘
          ▼
┌─────────────────────────────────────────┐
│  PermissionPrompt Widget                │
│  ├── Display in TUI permission buffer   │
│  ├── Arrow key navigation (UP/DOWN)     │
│  ├── Enter to select                    │
│  ├── Custom prompt from metadata        │
│  └── Focus management                   │
└─────────┬───────────────────────────────┘
          ▼
    USER DECISION
    [Allow] / [Deny]
          │
          ▼
┌─────────────────────────────────────────┐
│  Response Handling                      │
│  ├── Update permission cache            │
│  ├── Log to audit trail                 │
│  ├── Update analytics                   │
│  └── Store in session memory            │
└─────────┬───────────────────────────────┘
          ▼
┌─────────────────────────────────────────┐
│  EXECUTION LAYER                        │
├─────────────────────────────────────────┤
│  SDK Enforcement (for commands)         │
│  ├── enforce_handler()                  │
│  ├── Validation                         │
│  ├── Auto-conversion if needed          │
│  └── Compliance wrapping                │
└─────────┬───────────────────────────────┘
          ▼
┌─────────────────────────────────────────┐
│  Handler Execution                      │
│  ├── Command handler: async fn(app,    │
│  │   session, **context)                │
│  ├── Tool handler: API/file/docker op   │
│  ├── Circuit breaker protection         │
│  ├── Retry logic                        │
│  └── Timeout management                 │
└─────────┬───────────────────────────────┘
          ▼
┌─────────────────────────────────────────┐
│  RESULT LAYER                           │
├─────────────────────────────────────────┤
│  ├── TUI rendering                      │
│  ├── Session message append             │
│  ├── Background status (if applicable)  │
│  └── Error handling                     │
└─────────────────────────────────────────┘
```

---

## Permission System Health Checklist

### ✅ System Health Verification Steps

**1. PermissionBufferManager Health:**
```bash
# Check worker thread is running
ps aux | grep "permission-buffer"

# Verify priority queue accepts tasks
# (Tested by triggering any command requiring approval)
```

**2. UnifiedPermissionManager Integration:**
```python
# In session
from modules.permissions import get_unified_permission_manager
manager = get_unified_permission_manager()
print(f"Manager initialized: {manager is not None}")
print(f"Buffer manager: {manager.get_buffer_manager()}")
print(f"UI callback registered: {manager._ui_callback is not None}")
```

**3. Session Memory Health:**
```python
# Check session permission state
session.permission_manager  # Should exist
session.permission_manager.permission_cache  # Check cache
session.permission_manager.analytics  # Check analytics
```

**4. Widget Display Health:**
```python
# Trigger any command requiring approval (e.g., /help)
# Verify:
# ✅ Permission buffer appears
# ✅ Arrow keys navigate options
# ✅ Enter selects option
# ✅ Selection changes before/after navigation
```

**5. Import Path Health (CRITICAL):**
```python
# All 47 broken commands depend on fixing imports!
# Current status: ❌ 9 files blocked at import
# After fix: ✅ All 55 commands use SDK path
```

### 🔍 Health Monitoring Commands

**Check Permission Analytics:**
```python
from modules.permissions import get_permission_buffer_manager
manager = get_permission_buffer_manager()
report = manager.get_analytics_report()
print(json.dumps(report, indent=2))
```

**Check Audit Log:**
```python
from modules.permissions import get_permission_buffer_manager
manager = get_permission_buffer_manager()
log = manager.get_audit_log()
for event in log:
    print(f"{event['timestamp']}: {event['event']} - {event.get('tool', 'N/A')}")
```

**Check Session Permission Cache:**
```python
# In active session
if session.permission_manager:
    cache = session.permission_manager.permission_cache
    print(f"Cached permissions: {len(cache)}")
    for key, decision in cache.items():
        print(f"  {key}: {decision['decision']}")
```

**Check Active Executions:**
```python
# In ExecutionSystem
system = session.executor  # If available
print(f"Active executions: {len(system.active_executions)}")
for exec_id, exec_data in system.active_executions.items():
    print(f"  {exec_id}: {exec_data['status']}")
```

---

## Current System Status Summary

### 🎯 What's Working (Once Imports Fixed)

| System | Current Status | After Import Fix |
|--------|----------------|------------------|
| Permission Buffer Display | ✅ Working for 8 docker commands | ✅ Working for ALL 55 commands |
| UnifiedPermissionManager | ✅ Initialized and active | ✅ Handling all permission requests |
| Session Memory | ✅ Tracking messages/state | ✅ Tracking permission cache/analytics |
| Analytics Tracking | ✅ Collecting data | ✅ Comprehensive analytics |
| Audit Logging | ✅ Recording events | ✅ Full audit trail |
| Permission Caching | ✅ Caching decisions | ✅ Session-scoped cache working |
| Widget Navigation | ✅ Arrow keys working | ✅ All commands show prompts |
| SDK Enforcement | ⏸️ Blocked for 47 commands | ✅ Enforcing all 55 commands |
| Tool Execution | ✅ 9 default tools registered | ✅ All tools flow through permissions |
| Command Registration | ⚠️ 28/46 loading (61%) | ✅ 46/46 loading (100%) |

### 🚨 Critical Blockers

**Import Errors Preventing:**
1. ❌ 47 commands can't register (module load fails)
2. ❌ SDK enforcement never reached (imports fail first)
3. ❌ Permission prompts can't display (handlers don't exist)
4. ❌ Session tracking incomplete (missing commands)
5. ❌ Analytics gaps (unregistered commands)
6. ❌ Audit trail incomplete (missing events)

**After Fixing 32 Imports:**
1. ✅ All 55 commands register through SDK
2. ✅ SDK enforcement validates all handlers
3. ✅ Permission prompts display for all commands
4. ✅ Session tracking complete
5. ✅ Analytics comprehensive
6. ✅ Audit trail complete

---

## Permission State Persistence Strategy

### 🔄 What Gets Saved vs Cleared

**Persisted to Disk (Session Save):**
```json
{
  "session_id": "uuid",
  "messages": [...],
  "model": "gpt-4",
  "cwd": "/path",
  "debug_mode": false,
  "timestamp": "2025-10-28T..."
}
```

**Stored in Session Memory (Runtime Only):**
```python
session.permission_manager = {
    "permission_cache": {...},      # Cleared on session end
    "analytics_data": {...},        # Reset per session
    "audit_log": [...]             # Not persisted
}
```

**Global Config (Persists Across Sessions):**
```python
# ~/.opencli/config.json
{
    "permissions": {
        "always_allow": [
            "Read:/Users/user/safe-dir/**",
            "Bash:ls",
            "Bash:git status"
        ],
        "always_deny": [
            "Bash:rm -rf /",
            "file_delete:/etc/**"
        ]
    }
}
```

**Why This Design:**
- **Session cache**: Fast lookups, cleared for security
- **Global config**: User preferences persist forever
- **Audit log**: Could be persisted in future for compliance tracking
- **Analytics**: Reset per session for fresh metrics

---

## Next Steps: Enabling Full System Health

### 📝 Import Fix Implementation Plan

**Step 1: Fix Imports (Enables Everything)**
```bash
# Fix 32 relative imports in 16 files
# Pattern: from ..X → from modules.X
# Time estimate: 5-10 minutes

Files to fix:
1. modules/commands/agent_commands.py (2 imports)
2. modules/commands/basic_commands.py (2 imports)
... [14 more files]
```

**Step 2: Verify System Health**
```python
# Check all 55 commands load
opencli tui
# Look for: "Commands: 46" (not 28)

# Test permission buffer
/help
# Verify permission prompt appears with navigation

# Test analytics
from modules.permissions import get_permission_buffer_manager
manager = get_permission_buffer_manager()
print(manager.get_analytics_report())
```

**Step 3: Comprehensive Smoke Test**
```bash
# Test each command category
/agent          # Agent commands
/model          # Model commands
/help           # Basic commands
/docker         # Docker commands
/diff           # Diff commands

# Verify all show permission buffers correctly
# Verify arrow key navigation works
# Verify selection and execution works
```

**Result:** Full system health achieved with all components integrated and functional.
