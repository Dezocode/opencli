# OpenCLI Command Registry & Permission System

## Overview

OpenCLI includes a comprehensive command registry system that provides granular control over slash commands with persistent permissions.

## Features

- ✅ **12 registered commands** with full metadata
- ✅ **Interactive permission setup** via `/commands setup`
- ✅ **Individual command control** via enable/disable
- ✅ **Feature-aware disabling** (auto-disables if features unavailable)
- ✅ **Persistent storage** across sessions
- ✅ **Protected commands** (`/commands` cannot be disabled)
- ✅ **Category organization** (basic, agents, advanced, system)
- ✅ **Exit/quit support** (both `/exit` and `exit` work)

## Registered Commands

### Basic Commands
| Command | Description | Default |
|---------|-------------|---------|
| `/model` | View or change model | ✓ Enabled |
| `/status` | Show session info | ✓ Enabled |
| `/clear` | Clear conversation history | ✓ Enabled |
| `/help` | Show help menu | ✓ Enabled |
| `/exit` | Exit the session | ✓ Enabled |
| `/quit` | Exit the session | ✓ Enabled |

### Agent Commands (requires AGENT_SYSTEM)
| Command | Description | Default |
|---------|-------------|---------|
| `/agent` | Switch to specific agent | ✓ Enabled |
| `/agents` | List all available agents | ✓ Enabled |

### Advanced Commands
| Command | Description | Default |
|---------|-------------|---------|
| `/bashes` | List background tasks | ✓ Enabled |

### System Commands
| Command | Description | Default |
|---------|-------------|---------|
| `/upgrade` | Upgrade to latest version | ✓ Enabled |
| `/rollback` | Rollback to previous version | ✓ Enabled |
| `/commands` | Manage command permissions | 🔒 Always enabled |

## Usage

### View Command Status

```bash
opencli
> /commands
```

Shows current status of all commands:

```
📋 Command Status

BASIC:
  ✓ /model         View or change model
  ✓ /status        Show session info
  ✓ /clear         Clear conversation history
  ✓ /help          Show help menu
  ✓ /exit          Exit the session
  ✓ /quit          Exit the session

AGENTS:
  ✓ /agent         Switch to specific agent
  ✓ /agents        List all available agents

ADVANCED:
  ✓ /bashes        List background tasks

SYSTEM:
  🔒 /commands     Manage command permissions (always enabled)
  ✓ /upgrade       Upgrade to latest version
  ✓ /rollback      Rollback to previous version

Use '/commands setup' for interactive configuration
```

### Interactive Setup

Go through each command and enable/disable individually:

```bash
opencli
> /commands setup
```

Interactive flow:

```
🔧 Command Permission Setup

Enable or disable slash commands individually.

============================================================
  BASIC COMMANDS
============================================================

/model          View or change model
               Currently: ✓ enabled
               Enable? (y/n/Enter to keep current): y

/status         Show session info
               Currently: ✓ enabled
               Enable? (y/n/Enter to keep current):

/clear          Clear conversation history
               Currently: ✓ enabled
               Enable? (y/n/Enter to keep current): n

[continues for all commands...]

============================================================
✅ Command permissions updated!
============================================================

Enabled commands (11): /agent, /agents, /bashes, /commands, /exit, /help, /model, /quit, /rollback, /status, /upgrade
Disabled commands (1): /clear
```

### Enable Specific Command

```bash
opencli
> /commands enable /clear

✓ Enabled: /clear
```

### Disable Specific Command

```bash
opencli
> /commands disable /clear

✓ Disabled: /clear
```

### Test Disabled Command

```bash
opencli
> /commands disable /clear

✓ Disabled: /clear

> /clear

❌ Command '/clear' is disabled
Use /commands to enable it
```

### Exit/Quit Behavior

Both forms work and respect permissions:

```bash
# With slash
> /exit
Goodbye!

# Without slash
> exit
Goodbye!

# If disabled
> /commands disable /exit
✓ Disabled: /exit

> exit
❌ Command '/exit' is disabled
Use /commands to enable it
```

## Architecture

### Storage

Permissions are stored in `~/.opencli/command_permissions.json`:

```json
{
  "/model": true,
  "/agent": true,
  "/agents": true,
  "/status": true,
  "/clear": false,
  "/bashes": true,
  "/upgrade": true,
  "/rollback": true,
  "/commands": true,
  "/help": true,
  "/exit": true,
  "/quit": true
}
```

### Command Flow

```
User types: /clear
       ↓
handle_slash_command() called
       ↓
Check command_registry.is_enabled("/clear")
       ↓
   ┌───┴───┐
   │       │
Enabled  Disabled
   │       │
   │       └→ Show error: "Command disabled, use /commands to enable"
   │
   └→ Execute /clear normally
```

### Exit/Quit Flow

```
User types: exit (or quit, /exit, /quit)
       ↓
Main loop detects exit command
       ↓
Check command_registry.is_enabled("/exit")
       ↓
   ┌───┴───┐
   │       │
Enabled  Disabled
   │       │
   │       └→ Show error and continue session
   │
   └→ Print "Goodbye!" and exit
```

### Feature-Aware Commands

Commands that require features auto-disable if unavailable:

```
User: /commands

📋 Command Status

AGENTS:
  ❌ /agent         Switch to specific agent (feature unavailable)
  ❌ /agents        List all available agents (feature unavailable)
```

In this case, `AGENT_SYSTEM` feature is not available (missing dependencies), so agent commands are automatically disabled.

## Command Metadata

Each command has the following metadata:

```python
{
    'description': 'Human-readable description',
    'category': 'basic|agents|advanced|system',
    'default_enabled': True|False,
    'requires_args': True|False,
    'requires_feature': 'AGENT_SYSTEM|UPGRADE_SYSTEM|GITHUB_TOOL' (optional)
}
```

## Protected Commands

### `/commands`

The `/commands` command cannot be disabled:

```bash
> /commands disable /commands

✓ Cannot disable /commands (needed to re-enable commands)
```

This prevents users from locking themselves out of the command management system.

## Default Permissions

All commands are **enabled by default** on first run. The system creates `~/.opencli/command_permissions.json` with all commands enabled:

```json
{
  "/model": true,
  "/agent": true,
  "/agents": true,
  "/status": true,
  "/clear": true,
  "/bashes": true,
  "/upgrade": true,
  "/rollback": true,
  "/commands": true,
  "/help": true,
  "/exit": true,
  "/quit": true
}
```

## Adding New Commands

To add a new command to the registry:

### 1. Add to `modules/command_registry.py`

```python
self.available_commands = {
    # ... existing commands ...
    '/newcmd': {
        'description': 'Description of new command',
        'category': 'basic',  # or agents, advanced, system
        'default_enabled': True,
        'requires_args': False,
        'requires_feature': 'SOME_FEATURE'  # optional
    }
}
```

### 2. Implement in `opencli.py`

```python
def handle_slash_command(cmd, args, session, config, agent_manager=None, command_registry=None):
    # Permission check (automatic)
    if command_registry and not command_registry.is_enabled(cmd):
        print(f"\n❌ Command '{cmd}' is disabled")
        print(f"Use /commands to enable it\n")
        return True

    # ... existing commands ...

    elif cmd == "/newcmd":
        # Your implementation here
        print("New command executed!")
        return True
```

### 3. Update `/help`

```python
elif cmd == "/help":
    print("\nAvailable commands:")
    # ... existing commands ...
    print("  /newcmd        - Description of new command")
    # ...
```

### 4. Test

```bash
opencli
> /commands
# Should show new command

> /newcmd
# Should execute

> /commands disable /newcmd
# Should disable

> /newcmd
# Should show error
```

## Troubleshooting

### Permissions file corrupted

Delete and restart:

```bash
rm ~/.opencli/command_permissions.json
opencli
```

System will recreate with defaults.

### Command not showing in `/commands`

1. Check it's added to `available_commands` in `command_registry.py`
2. Check category spelling (basic, agents, advanced, system)
3. Check `requires_feature` if applicable

### Command disabled but can't re-enable

```bash
opencli
> /commands enable /clear

✓ Enabled: /clear
```

If this doesn't work:
- Check permissions file: `cat ~/.opencli/command_permissions.json`
- Manually edit or delete the file
- Restart opencli

### `/commands` itself is broken

The emergency fix is to manually edit the permissions file:

```bash
# Edit directly
nano ~/.opencli/command_permissions.json

# Or delete and recreate
rm ~/.opencli/command_permissions.json
opencli
```

## Integration with Version Control

The command registry integrates with the upgrade system:

### Detecting New Commands

When new commands are added in a version update, the registry automatically:
1. Adds them to the available commands list
2. Sets them to default_enabled state
3. Shows them in `/commands`

### Preserving User Preferences

User permissions persist across upgrades:
- If user disabled `/clear`, it stays disabled after upgrade
- New commands get default_enabled state
- Removed commands are ignored (no errors)

### Verification Steps

The version system includes command registry verification:

```json
{
  "version": "1.1.0",
  "verification_steps": [
    "Test /commands to view and manage command permissions",
    "Test /commands setup for interactive permission configuration",
    "Verify command registry initialization on startup",
    "Check that disabled commands show appropriate error messages"
  ]
}
```

## Files

| File | Purpose |
|------|---------|
| `modules/command_registry.py` | Command registry implementation |
| `~/.opencli/command_permissions.json` | User permission preferences |
| `opencli.py` | Integration and command handlers |

## See Also

- [README.md](README.md) - Main documentation
- [UPGRADING.md](UPGRADING.md) - Upgrade guide
- [archive/VERSION_CONTROL.md](archive/VERSION_CONTROL.md) - Version control system
