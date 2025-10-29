# OpenCLI Command Inventory - Complete Visual Map
Generated: 2025-10-22 23:06

## Executive Summary

**Total Commands Found: ~55 commands across 9 files**
- **102 total functions** defined in *_commands.py files
- **51 command pairs** (handler + prompt function)
- **46 registrations** attempted in command_registry.py
- **28 commands loading** (SDK report)
- **~18 commands blocked** by import errors

## Impact of Import Errors

**9 files have relative import errors blocking ALL their commands:**

| File | Functions | Commands | Status |
|------|-----------|----------|--------|
| agent_commands.py | 21 | 8 commands | ❌ BROKEN |
| basic_commands.py | 15 | 7 commands | ❌ BROKEN |
| dev_commands.py | 6 | 3 commands | ❌ BROKEN |
| diff_commands.py | 8 | 3 commands | ❌ BROKEN |
| local_commands.py | 2 | 1 command | ❌ BROKEN |
| model_commands.py | 10 | 5 commands | ❌ BROKEN |
| provider_commands.py | 11 | 6 commands | ❌ BROKEN |
| spec_commands.py | 15 | 7 commands | ❌ BROKEN |
| system_commands.py | 14 | 7 commands | ❌ BROKEN |

**Result:** ~47 commands broken, only ~8 commands working

## What Fixing 32 Relative Imports Will Achieve

### Before Fix:
- ❌ SDK Registration: 28 commands / 46 attempts (61% failure rate)
- ❌ Agent commands: ALL broken
- ❌ Model switching: Broken
- ❌ Provider management: Broken
- ❌ Spec/planning tools: Broken
- ❌ System commands: Broken
- ❌ Basic commands (/help, /status, /clear): Broken

### After Fix:
- ✅ SDK Registration: ~46 commands / 46 attempts (100% success)
- ✅ All agent commands working
- ✅ Model switching working
- ✅ Provider management working
- ✅ Spec/planning tools working
- ✅ System commands working
- ✅ Basic commands working

## Command Breakdown by Category

### Agent Commands (8) - BROKEN
- /agent (list agents)
- /agents (alias)
- /agent assistant
- /agent debugger
- /agent reviewer
- /agent refactor
- /agent tester
- /agent documenter
- /agent architect

### Basic Commands (7) - BROKEN
- /help
- /status
- /clear
- /bashes
- /commands
- /permissions
- /exit, /quit

### Dev Commands (3) - BROKEN
- /debug
- /performance
- /reload

### Diff Commands (3) - BROKEN
- /diff
- /diff git
- /diff worktree

### Model Commands (5) - BROKEN
- /model
- /model list
- /model providers
- /model r1
- /model r2

### Provider Commands (6) - BROKEN
- /provider
- /providers
- /providers list
- /providers add
- /providers add ollama
- /providers remove

### Spec Commands (7) - BROKEN
- (All spec-related commands broken)

### System Commands (7) - BROKEN
- /restart
- /upgrade
- /api
- /rollback
- /refactor
- /autorefactor
- /inject

### Docker Commands (8) - WORKING
- /docker
- /docker ps
- /docker stats
- /docker status
- /docker ollama setup
- /docker ollama start
- /docker ollama status
- /docker ollama stop

## The Fix

**32 relative imports** need conversion:
- Pattern: `from ..module_name` → `from modules.module_name`
- Pattern: `from ..subdir.module` → `from modules.subdir.module`
- Affects: 16 files total
- Time estimate: ~5 minutes with automated replacement

## Files Needing Import Fixes

1. modules/async_interactive/core.py (1 import)
2. modules/commands/agent_commands.py (2 imports)
3. modules/commands/basic_commands.py (2 imports)
4. modules/commands/command_registry.py (1 import)
5. modules/commands/command_router.py (2 imports)
6. modules/commands/dev_commands.py (2 imports)
7. modules/commands/diff_commands.py (2 imports)
8. modules/commands/local_commands.py (2 imports)
9. modules/commands/model_commands.py (2 imports)
10. modules/commands/provider_commands.py (2 imports)
11. modules/commands/registry.py (3 imports)
12. modules/commands/spec_commands.py (3 imports)
13. modules/commands/system_commands.py (2 imports)
14. modules/commands/tool_registry.py (1 import)
15. modules/tools/core_tools.py (2 imports)
16. modules/tui/command_handlers.py (3 imports)

## Conversion Examples

### Example 1: agent_commands.py
```python
# BEFORE
from ..agent_manager import AgentManager
from ..permission_prompt import PermissionResponse

# AFTER
from modules.agent_manager import AgentManager
from modules.permission_prompt import PermissionResponse
```

### Example 2: registry.py
```python
# BEFORE
from ..execution.registry import ExecutionType, ExecutionCategory, RiskLevel
from ..sdk.enforcement import enforce_handler, EnforcementAction

# AFTER
from modules.execution.registry import ExecutionType, ExecutionCategory, RiskLevel
from modules.sdk.enforcement import enforce_handler, EnforcementAction
```

## Verification

All target imports verified to exist:
- ✅ modules/agent_manager.py
- ✅ modules/permission_prompt.py
- ✅ modules/permission_buffer_manager.py
- ✅ modules/specify_wrapper.py
- ✅ modules/github_tool.py
- ✅ modules/header_autoconfig.py
- ✅ modules/command_suggestions.py
- ✅ modules/execution/registry.py
- ✅ modules/execution/executor.py
- ✅ modules/sdk/enforcement.py
- ✅ modules/sdk/validation.py
- ✅ modules/tui/core.py
- ✅ modules/input_widget/

**Safe to proceed with automated replacement.**
