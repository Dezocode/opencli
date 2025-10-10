# OpenCLI SDK - Complete Visual Flow Documentation

## 📐 Visual Layout

```
┌─────────────────────────────────────────────────────────────┐
│ OpenCLI Header                                              │
│ Session: xxxxx | Model: xxx | Tokens: xxx                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Chat Output Area                                           │
│  - Command results displayed here                           │
│  - app.write() output goes here                            │
│  - Rich markdown rendering                                  │
│                                                             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ StatusLine (toggleable, shows during background ops)       │
│ Docker: ✓ Running | CPU: 45% | Memory: 2.1GB              │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 🔒 PERMISSION BUFFER (MultiLineInput overlay)          ││
│ │                                                         ││
│ │ Title: Docker: /docker ollama setup                    ││
│ │                                                         ││
│ │ Message: This will create a Docker container...        ││
│ │                                                         ││
│ │ Options (navigate with ↑↓, select with Enter):        ││
│ │ > Yes, allow this once                                 ││
│ │   Yes, and remember for this item                      ││
│ │   Yes, and auto-accept this session                    ││
│ │   No, cancel                                            ││
│ │                                                         ││
│ │ [Esc to cancel]                                         ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ⠇ Type your message... (normal input when buffer clear)    │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Widget System

### 1. MultiLineInput Widget
**Location:** `simple_tui.py` - `MultiLineInput` class

**States:**
- **Normal Mode:** User types commands/messages
- **Permission Buffer Mode:** Overlay shows, captures ↑↓ Enter Esc
- **Suggestion Mode:** Shows command autocomplete

**Key Property:**
```python
prompt_input.permission_prompt_data = {
    'title': str,
    'message': str,
    'workflow_status': dict,  # For multi-step workflows
    'options': [
        {
            'text': str,
            'response': PermissionResponse,
            'data': dict  # Custom data passed to handler
        }
    ]
}
```

**Priority System:**
1. Permission Prompt (highest) - `if permission_prompt_data is set`
2. Command Suggestions - `if suggestions_active`
3. Normal Input - `default`

### 2. StatusLine Widget
**Location:** `simple_tui.py` - `StatusLine` class

**Toggleable Display:**
- Hidden by default
- Shows during background operations
- Can be toggled with `/performance` command

**Shows:**
- Docker stats (if container running)
- CPU/Memory usage
- Background task status
- Token streaming speed

## 🔐 Permission Buffer Flows

### Command Flow (e.g., /docker ollama setup)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER TYPES: /docker ollama setup                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. async_interactive.py                                     │
│    - Detects "/" prefix                                     │
│    - Calls route_command_unified(app, session, cmd)        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. CommandRouter.route_command()                            │
│    - Normalizes command string                              │
│    - Calls executor.execute_command(name, app, session)    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. ExecutionSystem.execute_command()                        │
│    - Looks up registration in ExecutionRegistry            │
│    - Checks if enabled                                      │
│    - Calls permission_manager.check_permission()           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. PermissionManager.check_permission()                     │
│    - Checks if requires_approval                            │
│    - Checks permission memory (session/permanent)           │
│    - If needed, calls _show_permission_prompt()            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. PERMISSION BUFFER SHOWS                                  │
│    ┌───────────────────────────────────────────────────┐   │
│    │ 🔒 Docker: /docker ollama setup                   │   │
│    │                                                    │   │
│    │ This will create Docker container with:           │   │
│    │ • Network access                                  │   │
│    │ • 4 CPUs, 8GB RAM                                 │   │
│    │                                                    │   │
│    │ > Yes, allow this once                            │   │
│    │   Yes, and remember                               │   │
│    │   No, cancel                                      │   │
│    └───────────────────────────────────────────────────┘   │
│    MultiLineInput widget in permission mode                │
│    - User navigates with ↑↓                                 │
│    - Selects with Enter                                     │
│    - Cancels with Esc                                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. USER SELECTS "Yes, allow this once"                     │
│    - simple_tui.py catches Enter key                        │
│    - Sets session._permission_response = ALLOW_ONCE        │
│    - Sets session._awaiting_permission = False             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. PermissionManager gets response                          │
│    - Returns True (approved)                                │
│    - Control returns to ExecutionSystem                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 9. ExecutionSystem.execute()                                │
│    - Calls _execute_single() or _execute_workflow()        │
│    - Passes context to handler                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 10. HANDLER EXECUTES                                        │
│     async def docker_ollama_setup(app, session, **context):│
│         # Permission already approved!                      │
│         # Just do the work                                  │
│         app.write("[cyan]→ Creating container...[/cyan]\n")│
│         # ... Docker operations ...                         │
│         app.write("[green]✓ Done![/green]\n")             │
│         return True                                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 11. RESULTS IN CHAT                                         │
│     ╭──────────────────────────────────────────────────╮   │
│     │ [cyan]→ Creating container...[/cyan]             │   │
│     │ [green]✓ Done![/green]                           │   │
│     │                                                   │   │
│     │ Ollama is now available at:                      │   │
│     │ http://localhost:11434                           │   │
│     ╰──────────────────────────────────────────────────╯   │
│                                                             │
│     Buffer is cleared, normal input restored                │
└─────────────────────────────────────────────────────────────┘
```

### Tool Flow (e.g., Read, Bash, Write)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. AI CALLS TOOL: Read file_path=/etc/hosts                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Tool Router (in model interaction)                       │
│    - Detects tool call                                      │
│    - Calls executor.execute_tool(name="Read", path=...)    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. ExecutionSystem.execute_tool()                           │
│    - Looks up registration in ExecutionRegistry            │
│    - Checks if enabled                                      │
│    - Calls permission_manager.check_permission()           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. PermissionManager assesses risk                          │
│    - Checks path: /etc/hosts (system file = HIGH)          │
│    - Checks tool: Read (LOW by default)                    │
│    - Total risk: HIGH (path overrides tool)                 │
│    - Shows permission prompt                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. PERMISSION BUFFER SHOWS                                  │
│    ┌───────────────────────────────────────────────────┐   │
│    │ 🔒 File: Read                                     │   │
│    │                                                    │   │
│    │ Read file: /etc/hosts                             │   │
│    │ Risk: HIGH (system file)                          │   │
│    │                                                    │   │
│    │ > Yes, allow this once                            │   │
│    │   Yes, and remember for Read                      │   │
│    │   No, cancel                                      │   │
│    └───────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. USER APPROVES → Tool handler executes                   │
│    async def file_read(app, session, **context):           │
│        path = context.get('path')                           │
│        content = open(path).read()                          │
│        return content                                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. RESULT RETURNED TO AI                                    │
│    - Tool result passed back to model                       │
│    - AI continues with file content                         │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Multi-Step Workflow Flow

For commands with multiple steps (like Docker setup):

```
┌─────────────────────────────────────────────────────────────┐
│ PERMISSION BUFFER SHOWS WORKFLOW                            │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ 🔒 Docker: /docker ollama setup                       │   │
│ │                                                        │   │
│ │ Workflow Progress:                                    │   │
│ │ [✓] Check Docker daemon             (completed)       │   │
│ │ [→] Pull Ollama image              (in progress)      │   │
│ │ [ ] Create container                (pending)         │   │
│ │ [ ] Start container                 (pending)         │   │
│ │ [ ] Verify running                  (pending)         │   │
│ │                                                        │   │
│ │ Current: Downloading layers... 45%                    │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                             │
│ Buffer updates LIVE as steps execute                        │
│ User sees progress without blocking                         │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Background Processing with StatusLine

```
When can_run_background=True in registration:

┌─────────────────────────────────────────────────────────────┐
│ Chat Output Area                                            │
│ (continues to be usable)                                    │
│                                                             │
│ User can type other commands while background task runs     │
├─────────────────────────────────────────────────────────────┤
│ ╔═══════════════════════════════════════════════════════╗   │
│ ║ StatusLine (AUTO-SHOWN during background)            ║   │
│ ║ Background: Pull Ollama image ⋯ 45% | Docker: ✓      ║   │
│ ╚═══════════════════════════════════════════════════════╝   │
├─────────────────────────────────────────────────────────────┤
│ ⠇ Type your message... (AVAILABLE during background)       │
└─────────────────────────────────────────────────────────────┘

When task completes:
- StatusLine shows: ✓ (success) or ✗ (failure)
- After 2s, StatusLine auto-hides
- Result written to chat
```

## 💾 Permission Memory

PermissionManager maintains memory across executions:

```python
# Session Memory (cleared when app closes)
permission_manager.auto_accept_session = True
# All requests auto-approved for this session (except CRITICAL)

# Persistent Memory (saved to ~/.opencli/permissions.json)
permission_manager.allowed_items = {
    'command:/docker ollama setup': True,
    'tool:Read': True,
    'tool:Bash': False  # Always prompt
}

# Next time same command runs:
# 1. Check allowed_items first
# 2. If found and not CRITICAL → skip prompt
# 3. If CRITICAL → always prompt
```

## 🎨 Permission Prompt Variations

### Simple Yes/No
```
┌───────────────────────────────────────────┐
│ 🔒 Dev: /debug                            │
│                                           │
│ Toggle debug mode on/off                  │
│ Risk: SAFE                                │
│                                           │
│ > Yes, allow this once                    │
│   No, cancel                              │
└───────────────────────────────────────────┘
```

### With Configuration Options
```
┌───────────────────────────────────────────┐
│ 🔒 Docker: /docker ollama setup           │
│                                           │
│ Choose resource allocation:               │
│                                           │
│ > Conservative (4 CPUs, 8GB) - Recommended│
│   Balanced (6 CPUs, 12GB)                 │
│   Performance (8 CPUs, 16GB)              │
│   With GPU Support                        │
│   Cancel                                  │
└───────────────────────────────────────────┘
```

### With Risk Warning
```
┌───────────────────────────────────────────┐
│ 🔒 Bash: Execute command                  │
│                                           │
│ $ rm -rf /tmp/old_data                    │
│                                           │
│ ⚠️  Risk: HIGH (destructive operation)   │
│                                           │
│ This will permanently delete files!       │
│                                           │
│ > Yes, I understand the risks             │
│   No, cancel                              │
└───────────────────────────────────────────┘
```

## 📋 Handler SDK Compliance Checklist

✅ **COMPLIANT Handler:**
```python
async def my_command(app, session, **context):
    """
    ✓ async function
    ✓ Parameters: app, session, **context
    ✓ NO manual buffer management
    ✓ Uses app.write() for output
    ✓ Returns result value
    """
    # Permission already checked by ExecutionSystem

    # Get params from context
    param = context.get('param', 'default')

    # Do work
    app.write("[cyan]Working...[/cyan]\n")
    result = do_something()

    # Write results to chat
    app.write(f"[green]✓ Done: {result}[/green]\n\n")

    # Return for programmatic use
    return result
```

❌ **NON-COMPLIANT Handler:**
```python
async def bad_command(app, session):  # ❌ Missing **context
    # ❌ Manual buffer management
    prompt_input = app.query_one("#prompt-input")
    prompt_input.permission_prompt_data = {...}

    # ❌ Manual executor call
    await app.executor.execute(...)

    # ❌ This creates duplicate flows!
```

## 🏗️ Registration Template

```python
# In commands/registry.py or similar

executor.registry.register(
    ExecutionType.COMMAND,           # or TOOL, API
    '/mycommand',                    # Command name
    my_command_handler,              # Handler function
    ExecutionCategory.SYSTEM,        # Category for organization
    RiskLevel.MEDIUM,                # Risk assessment
    requires_approval=True,          # Show permission prompt?
    description="What this does",    # Human-readable
    can_run_background=False,        # Show in statusline?
    timeout=120,                     # Timeout in seconds
    metadata={                       # Optional extra data
        'custom_key': 'value'
    }
)
```

## 🔍 Startup Diagnostics Output

```
┌─────────────────────────────────────────────────────────────┐
│ 🔒 OpenCLI Startup Diagnostics                              │
│                                                             │
│ Commands: 17 | Tools: 8                                     │
│ ✓ Compliant: 25 | ✗ Non-compliant: 0                       │
│                                                             │
│ Sample Registered:                                          │
│   ✓ /docker ollama setup (docker_commands)                 │
│   ✓ /docker ollama start (docker_commands)                 │
│   ✓ /debug (commands.dev_commands)                         │
│   ✓ Read (tools.file_tools)                                │
│   ✓ Bash (tools.exec_tools)                                │
│   ... and 20 more                                           │
│                                                             │
│ [Auto-closes in 3s or press Enter]                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start for New Handlers

1. **Create handler with SDK signature:**
   ```python
   async def my_handler(app, session, **context):
       app.write("Doing work...\n")
       return "result"
   ```

2. **Register in `commands/registry.py`:**
   ```python
   executor.registry.register(
       ExecutionType.COMMAND,
       '/mycommand',
       my_handler,
       ExecutionCategory.SYSTEM,
       RiskLevel.LOW,
       requires_approval=True,
       description="My command"
   )
   ```

3. **Done!** ExecutionSystem handles:
   - ✅ Permission checking
   - ✅ Buffer display
   - ✅ Context passing
   - ✅ Error handling
   - ✅ Usage tracking

---

**END OF VISUAL FLOW DOCUMENTATION**
