# OpenCLI SDK - Quick Reference Card

## 📍 Files Location
**Everything is in:** `/Users/dezmondhollins/.opencli/modules/`

## 🎯 Key Components

### SDK Files
- `sdk/handler_interface.py` - Handler validation and compliance checking
- `sdk/startup_diagnostics.py` - Registration diagnostics
- `sdk/VISUAL_FLOW.md` - Complete visual documentation (THIS FILE!)

### Core System
- `execution/executor.py` - ExecutionSystem (main entry point)
- `execution/registry.py` - ExecutionRegistry (stores all registrations)
- `execution/permission_manager.py` - PermissionManager (handles permission buffer)
- `command_router.py` - CommandRouter (routes commands to ExecutionSystem)
- `commands/registry.py` - Central registration (ONE place for all commands/tools)

### Handlers
- `docker_commands.py` - Docker commands (STREAMLINED, SDK compliant)
- `commands/*.py` - All command handlers (SDK compliant)
- `tools/*.py` - All tool handlers (SDK compliant)

## 🔧 Handler Template (Copy & Paste)

```python
async def my_command(app, session, **context):
    """
    SDK-Compliant Handler

    Args:
        app: TUI app (use app.write() for output)
        session: Session state
        **context: Execution context (args, paths, etc.)

    Returns:
        Any: Result value
    """
    # Get parameters from context
    param = context.get('param_name', 'default')

    # Do your work
    app.write("[cyan]→ Working...[/cyan]\n")

    try:
        result = do_something(param)
        app.write(f"[green]✓ Success: {result}[/green]\n\n")
        return result

    except Exception as e:
        app.write(f"[red]✗ Error: {e}[/red]\n\n")
        return None
```

## 📋 Registration Template (Copy & Paste)

```python
# In commands/registry.py, inside register_all(executor):

executor.registry.register(
    ExecutionType.COMMAND,           # COMMAND, TOOL, or API
    '/mycommand',                    # Name (with / for commands)
    my_command,                      # Handler function
    ExecutionCategory.SYSTEM,        # Category
    RiskLevel.MEDIUM,                # SAFE, LOW, MEDIUM, HIGH, CRITICAL
    requires_approval=True,          # Show permission prompt?
    description="What this does",    # Description
    can_run_background=False,        # Show in statusline?
    timeout=120                      # Timeout in seconds
)
```

## 🎨 Widget States

### MultiLineInput (Permission Buffer)
```python
# Get widget
prompt_input = app.query_one("#prompt-input")

# Show permission prompt (ExecutionSystem does this automatically!)
prompt_input.permission_prompt_data = {
    'title': 'Command Name',
    'message': 'What will happen',
    'options': [
        {'text': 'Yes', 'response': PermissionResponse.ALLOW_ONCE},
        {'text': 'No', 'response': PermissionResponse.CANCEL}
    ]
}

# Clear buffer
prompt_input.permission_prompt_data = None
prompt_input.refresh(layout=True)
```

### StatusLine (Background Tasks)
```python
# In registration, set:
can_run_background=True

# ExecutionSystem will:
# 1. Show statusline automatically
# 2. Update with progress (⋯, ✓, ✗)
# 3. Auto-hide after 2s
```

## 🔍 Debug Output

When you run `/docker` or any command, terminal shows:
```
[CommandRouter] Registered 17 commands, 8 tools
[Router] Looking up: '/docker'
[Router] Registered commands: ['/docker ollama setup', ...]
[Router] Calling executor.execute_command('/docker')
[Router] Success!
```

If it fails, you'll see:
```
[Router] ValueError: Unknown command: /docker
```

## ✅ SDK Compliance Check

Run validation on any handler:
```python
from sdk import validate_handler

result = validate_handler(my_handler, '/mycommand')
print(f"Compliance: {result.compliance.value}")
print(f"Error: {result.error}")
```

Results:
- `compliant` - ✅ Good to go!
- `missing_context` - ❌ Add **context parameter
- `wrong_signature` - ❌ Use (app, session, **context)
- `not_async` - ❌ Make it async def

## 🚀 Testing Flow

1. **Start OpenCLI** - Terminal shows registration count
2. **Type `/docker`** - Terminal shows routing debug
3. **Check for:**
   - ✅ "Registered X commands" appears
   - ✅ "Looking up: '/docker'" appears
   - ✅ Permission buffer shows (if requires_approval=True)
   - ✅ Handler executes after approval

## 📊 Startup Diagnostics

To enable startup diagnostics in buffer:
```python
# In simple_tui.py or main app initialization:
from sdk import run_startup_diagnostics

# After router is created:
run_startup_diagnostics(app, router.executor, show_buffer=True)
```

Shows:
```
┌─────────────────────────────────────┐
│ OpenCLI Registration Diagnostics    │
│                                     │
│ Commands: 17 | Tools: 8             │
│ ✓ Compliant: 25 | ✗ Non-compliant: 0│
│                                     │
│ Sample Registered:                  │
│   ✓ /docker ollama setup           │
│   ✓ /debug                         │
│   ... and 23 more                  │
│                                     │
│ [Auto-closes in 3s]                 │
└─────────────────────────────────────┘
```

## 🎯 Common Issues & Fixes

### "Unknown command"
- ✅ Check registration in `commands/registry.py`
- ✅ Verify handler signature: `async def handler(app, session, **context)`
- ✅ Check terminal for debug output

### Permission buffer doesn't show
- ✅ Check `requires_approval=True` in registration
- ✅ Verify risk level is not SAFE (SAFE skips prompt)
- ✅ Handler should NOT manually touch `permission_prompt_data`

### Handler not executing
- ✅ Check permission was approved (not cancelled)
- ✅ Look for exceptions in terminal
- ✅ Verify handler is async

## 📚 Full Documentation

See `sdk/VISUAL_FLOW.md` for complete visual flow documentation including:
- Widget layout diagrams
- Permission buffer flow charts
- Multi-step workflow examples
- Background processing with statusline
- Permission memory system

---

**Quick Start:** Copy handler template → Paste in commands file → Register in registry.py → Test!
