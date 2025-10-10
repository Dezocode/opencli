# Permission-First Architecture - Unified Command Execution

## Overview

**ALL commands** now flow through a standardized permission-first execution system with:

- ✅ **Live progress in permission buffer** - Commands execute IN the buffer, not outside it
- ✅ **Thread-safe async execution** - No UI blocking or hangs
- ✅ **Step-by-step permission gates** - Each risky step requires approval
- ✅ **Contextual statusline updates** - Shows what's running in real-time
- ✅ **Frontier styling throughout** - Consistent UI/UX
- ✅ **No early buffer exit** - Buffer stays visible until command completes
- ✅ **Proper error handling** - Failed steps shown in buffer with status

## Architecture Components

### 1. UnifiedCommandExecutor (`modules/unified_command_executor.py`)

**The core execution engine for ALL commands.**

```python
from modules.unified_command_executor import UnifiedCommandExecutor

# Initialized in OpenCLITUI.on_mount()
app.command_executor = UnifiedCommandExecutor(app, session)

# Execute any command with live progress
await app.command_executor.execute_command(
    command="/docker ollama setup",
    steps=[...],
    on_complete=callback
)
```

**Features:**
- Command registry with permissions/risk levels
- Automatic permission prompting
- Live progress display in permission buffer
- Contextual statusline indicators
- Step-by-step execution with approval gates

### 2. Permission Registry

All commands registered with:
- **Category** (Docker, Model, Provider, Local, Config, System, Tool)
- **Risk Level** (Safe, Low, Medium, High, Critical)
- **Resources Needed** (docker, network, disk, ollama, config)
- **Estimated Duration**
- **Requires Approval** flag

Example:
```python
CommandPermission(
    command="/docker ollama setup",
    category=CommandCategory.DOCKER,
    risk_level=CommandRiskLevel.HIGH,
    requires_approval=True,
    description="Set up Ollama Docker container (pulls ~2.7GB image)",
    resources_needed=["docker", "network", "disk"],
    estimated_duration="2-5 minutes"
)
```

### 3. Command Steps (`CommandStep`)

Each command broken into steps:

```python
CommandStep(
    id="pull_image",
    title="Pull Ollama Docker image (~2.7GB download)",
    description="Download ollama/ollama:latest from Docker Hub",
    category="docker",
    requires_permission=True,  # ← Permission gate
    risk_level=CommandRiskLevel.MEDIUM,
    execute_func=async_function,
    status="pending"  # → in_progress → completed/failed
)
```

### 4. Permission Buffer Display

**Stays visible during ENTIRE command execution** showing:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Docker: /docker ollama setup

Executing command steps...

Current: Pull Ollama Docker image (~2.7GB download)

Progress: 2/5 steps

✓ Check Docker daemon status
✓ Check for existing Ollama containers
⋯ Pull Ollama Docker image (~2.7GB download)  ← IN PROGRESS
· Create Ollama container (4 CPUs, 8g RAM)
· Verify container is running

▸ Continue
  Cancel execution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Status Indicators:**
- ✓ Completed
- ✗ Failed (with error message)
- ⋯ In progress
- ▸ Current step
- · Pending

### 5. Response Handlers (`simple_tui.py`)

Three permission handler levels:

1. **Command-level permission** (`_awaiting_command_permission`)
   - Initial approval to execute command
   - Cancel entire command

2. **Step-level permission** (`_awaiting_step_permission`)
   - Approval for individual risky steps
   - Cancel at any step

3. **Legacy workflow permission** (`_awaiting_workflow_permission`)
   - Backwards compatibility

## Flow Diagram

```
User types /docker ollama setup
         ↓
Check permission registry
         ↓
Show initial permission prompt ──→ User cancels? → Exit
         ↓                               ↓
   User approves                         No
         ↓
Show resource selection prompt ──→ User cancels? → Exit
         ↓                               ↓
  User selects resources                 No
         ↓
Initialize unified command executor
         ↓
FOR EACH STEP:
  ├─→ Update permission buffer with progress
  ├─→ Step requires permission?
  │    ├─→ Yes: Show permission gate → Wait for approval
  │    │          ↓                         ↓
  │    │      Approved?                 Cancelled?
  │    │          ↓                         ↓
  │    │        Yes                     Exit flow
  │    └─→ No: Skip gate
  ├─→ Set status = "in_progress"
  ├─→ Update buffer with ⋯ indicator
  ├─→ Execute step function
  ├─→ Success?
  │    ├─→ Yes: Set status = "completed", show ✓
  │    └─→ No: Set status = "failed", show ✗ + error
  └─→ Move to next step
         ↓
All steps complete!
         ↓
Show final status in buffer
         ↓
Update statusline (✓ Docker)
         ↓
Call on_complete callback
         ↓
Sleep 2s to show final status
         ↓
Clear permission buffer
```

## Contextual Statusline

Bottom statusline shows command execution context:

```
[Session: abc12345 | Ready]  [⋯ Docker]  [Model: gpt-4]
                               ↑
                     Shows Docker command running
```

**Indicators:**
- ⋯ (cyan) - Command starting/running
- ✓ (green) - Command completed
- ✗ (red) - Command failed
- (hidden) - Command cancelled

## Example: Docker Setup Execution

### Before (OLD FLOW - BROKEN)
```
User: /docker ollama setup
↓
Show permission buffer
↓
User clicks "Yes"
↓
❌ Buffer clears immediately
❌ Command hangs in background
❌ No progress visibility
❌ Can't cancel mid-execution
❌ Statusline doesn't update
```

### After (NEW UNIFIED FLOW - FIXED)
```
User: /docker ollama setup
↓
Show permission buffer: "Set up Ollama Docker Container?"
↓
User clicks "Yes"
↓
Show resource selection: "Conservative (4 CPUs, 8GB) - Recommended"
↓
User selects resources
↓
✅ Buffer stays visible
✅ Shows: "Progress: 0/5 steps"
✅ Step 1: ✓ Check Docker daemon status
✅ Step 2: ✓ Check for existing Ollama containers
✅ Step 3: ⋯ Pull Ollama Docker image
    ↓ User sees live progress
    ↓ Can cancel at any time
✅ Step 3: ✓ Pull complete
✅ Step 4: Shows permission gate "Create container (4 CPUs, 8g RAM)?"
    ↓ User approves
✅ Step 4: ⋯ Creating container...
✅ Step 4: ✓ Container created
✅ Step 5: ✓ Verify container is running
✅ Shows: "Progress: 5/5 steps"
✅ Shows completion message
✅ Statusline: [✓ Docker]
✅ Buffer clears after 2s
```

## Extending to Other Commands

**Any command can use this system:**

```python
# modules/my_command_unified.py
from modules.unified_command_executor import CommandStep, CommandRiskLevel

async def my_command_unified(app, session):
    steps = [
        CommandStep(
            id="step1",
            title="Do something safe",
            description="Read-only operation",
            category="mycommand",
            requires_permission=False,
            risk_level=CommandRiskLevel.SAFE,
            execute_func=my_async_func
        ),
        CommandStep(
            id="step2",
            title="Do something risky",
            description="Modifies system",
            category="mycommand",
            requires_permission=True,  # ← Permission gate!
            risk_level=CommandRiskLevel.HIGH,
            execute_func=my_risky_func
        )
    ]

    await app.command_executor.execute_command(
        command="/mycommand",
        steps=steps
    )
```

## Migration Checklist

To migrate existing commands to unified flow:

- [ ] Create `modules/{command}_commands_unified.py`
- [ ] Define `CommandStep` list with execution functions
- [ ] Set `requires_permission=True` for risky steps
- [ ] Add command to permission registry
- [ ] Update command handler to call unified executor
- [ ] Test with live progress visibility
- [ ] Verify statusline updates
- [ ] Confirm buffer stays visible during execution

## Benefits

1. **Consistency** - All commands use same execution pattern
2. **Visibility** - Users see exactly what's happening
3. **Control** - Can cancel at any step
4. **Safety** - Permission gates for risky operations
5. **No Hangs** - Proper async threading prevents UI blocks
6. **Better UX** - Frontier styling, live progress, contextual indicators
7. **Maintainability** - Single execution engine to maintain

## Current Status

✅ **Implemented:**
- Unified command executor core
- Permission handlers for 3 levels
- Docker Ollama setup using unified flow
- Docker Ollama start using unified flow
- Docker Ollama stop using unified flow
- Contextual statusline updates
- Live progress in permission buffer
- Step-by-step permission gates

🔜 **Next:**
- Migrate `/model providers` to unified flow
- Migrate `/local` to unified flow
- Migrate all other commands
- Add contextual indicators for all command categories
- Expand permission registry for all commands
