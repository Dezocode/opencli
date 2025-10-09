# OpenCLI IPC System Guide

## Overview

OpenCLI now has a complete IPC (Inter-Process Communication) system with:
- ✅ IPC server for subagent connections
- ✅ Bidirectional shell injection
- ✅ Communication logging
- ✅ Status line indicator (S: off/0)
- ✅ Claude Code bridge integration

## Status Line

The status line now shows IPC server status:
- `S: off` - Server is off (gray color)
- `S: 0` - Server running with 0 subagents (cyan color)
- `S: 3` - Server running with 3 subagents (cyan color)

## Commands

### /api - IPC Server Control

```bash
/api status   # Show server status and subagent count
/api start    # Start IPC server with shell injection
/api stop     # Stop IPC server and injector
/api logs     # Show injection logs summary
```

### Server Status Output
```
✓ IPC server is running
Socket: /tmp/opencli/opencli_{session_id}.sock
Session ID: {session_id}
Subagents: 2
```

## Architecture

### 1. IPC Server (`opencli_ipc.py`)

**Message Types:**
- `REGISTER` - Subagent registration
- `UNREGISTER` - Subagent deregistration
- `MESSAGE` - Chat messages
- `COMMAND` - Command execution
- `RESPONSE` - Command response
- `STATUS` - Status updates
- `HEARTBEAT` - Keep-alive ping
- `ERROR` - Error notifications
- `INJECTION` - Shell injection message
- `TOOL_USE` - Tool usage notification
- `NAVIGATION` - Navigation update
- `GOAL_PROGRESS` - Goal progress update

**Key Methods:**
```python
await server.start()                    # Start server
await server.stop()                     # Stop server
await server.broadcast(type, payload)   # Broadcast to all
await server.send_to_agent(id, type, payload)  # Send to specific agent
server.get_subagent_count()            # Get count
server.get_subagents()                 # Get list
```

### 2. Shell Injector (`shell_injector.py`)

**Injection Types:**
- `USER_PROMPT` - Inject into user prompt area
- `ASSISTANT_RESPONSE` - Inject into assistant response
- `SYSTEM_MESSAGE` - System-level message
- `TOOL_RESULT` - Tool execution result
- `NAVIGATION` - Agent navigation update
- `GOAL_PROGRESS` - Goal progress update

**Key Methods:**
```python
await injector.inject_to_opencli(type, source, content, metadata)
await injector.inject_to_agent(agent_id, type, content, metadata)
injector.get_log_summary()             # Get log stats
```

**Communication Log:**
- Location: `~/.opencli/ipc_logs/`
- Format: JSON Lines (`.jsonl`)
- Tracks all injections, findings, and agent navigation

### 3. Claude Code Bridge (`claude_code_bridge.py`)

**Usage:**
```python
from claude_code_bridge import get_claude_bridge

bridge = get_claude_bridge(session_id)
await bridge.connect()
await bridge.send_message("Hello from Claude Code!")
await bridge.send_tool_use("Read", {"file": "test.py"}, "Success")
await bridge.send_status("ready", {"progress": 50})
await bridge.disconnect()
```

**Command Line:**
```bash
# Find active sessions
python3 find_opencli_session.py

# Connect to session
python3 claude_code_bridge.py {session_id}
```

## Features

### Bidirectional Communication

**OpenCLI → Claude Code:**
```python
# From OpenCLI
await session.ipc_server.send_to_agent(
    agent_id="claude-code-id",
    msg_type="injection",
    payload={
        "type": "user_prompt",
        "content": "Please analyze this code...",
        "metadata": {"file": "test.py"}
    }
)
```

**Claude Code → OpenCLI:**
```python
# From Claude Code
await bridge.send_message(
    "Analysis complete. Found 3 issues...",
    role="assistant"
)
```

### Shell Injection

Messages can be injected into prompt areas based on:
- Agent navigation (current file/directory)
- Goal progress (percentage complete)
- Tool execution results
- System events

### Communication Logging

All injections are logged with:
- Timestamp
- Source and target agents
- Injection type
- Message content
- Metadata (navigation, goals, etc.)

View logs:
```bash
/api logs  # Summary in OpenCLI
cat ~/.opencli/ipc_logs/ipc_session_*.jsonl  # Full log file
```

## Integration Example

### 1. Start OpenCLI with IPC
```bash
opencli
/api start
```

### 2. Connect Claude Code
```bash
python3 claude_code_bridge.py {session_id}
```

### 3. Bidirectional Communication
- Claude Code receives messages from OpenCLI
- Claude Code sends responses back
- All communication logged
- Status line shows active connection count

## Status Line Integration

The status line automatically updates to show:
- Server status (on/off)
- Active subagent count
- Professional color coding:
  - Gray (#5C6773) when off
  - Soft cyan (#89B8C2) when active

Format: `S: off | Model: ... | Tokens: ... | Turn: ... | CWD: ... | HH:MM:SS`

## Files Modified

1. **simple_tui.py** - Added server status to status line
2. **async_interactive.py** - Integrated `/api` command and shell injector
3. **opencli_ipc.py** - Extended message types for injection
4. **shell_injector.py** - NEW: Bidirectional injection system
5. **claude_code_bridge.py** - NEW: Claude Code integration
6. **find_opencli_session.py** - NEW: Session discovery utility

## Testing

```bash
# Terminal 1: Start OpenCLI
opencli
/api start

# Terminal 2: Test connection
python3 find_opencli_session.py
python3 claude_code_bridge.py {session_id}

# Back in OpenCLI: Check status
/api status
/api logs
```

## Troubleshooting

**Socket not found:**
- Ensure `/api start` was run successfully
- Check `/tmp/opencli/` directory exists
- Verify session ID is correct

**Connection refused:**
- IPC server must be running first
- Check server status: `/api status`
- Review error traces in `/api start` output

**Injections not working:**
- Shell injector starts automatically with IPC server
- Check logs: `/api logs`
- Verify `~/.opencli/ipc_logs/` has write permissions
