# TUI Test Framework - UPDATED WITH PIPE-BASED SERVER

**Date**: 2025-10-19
**Status**: ✅ COMPLETE - NOW WITH DUAL-SHELL SERVER ARCHITECTURE

## CRITICAL UPDATE

**The framework now uses the PIPE-BASED SERVER COMMUNICATION method!**

### Architecture Change

**Before (WRONG)**:
- Used simple `tmux send-keys`
- No bidirectional communication
- No server validation

**After (CORRECT)**:
- ✅ **Named pipes** for command/response communication
- ✅ **Expect-based TUI server** listening on pipes
- ✅ **Controller client** sending commands to server
- ✅ **Bidirectional data flow** with response validation
- ✅ **Server captures and validates** each command

## How It Works Now

### 1. Named Pipes Created

```bash
PIPE="/tmp/tui_command_pipe_$$"           # Command pipe
RESPONSE_PIPE="/tmp/tui_response_pipe_$$" # Response pipe
```

### 2. TUI Server (Expect Script)

The framework generates an expect script that:
- Spawns `opencli tui` process
- Listens on command pipe
- Processes commands: `TYPE:text`, `ENTER`, `DOWN`, `UP`, `COLLECT_DATA`
- Sends responses back via response pipe
- Captures all output for analysis

**Server Command Handling**:
```tcl
switch -glob $cmd {
    "TYPE:*" {
        # Extract and type text
        send "$text"
        # Capture output
        # Send response with data
    }
    "ENTER" {
        send "\r"
        # Send response
    }
    "DOWN" {
        send "\033\[B"  # DOWN arrow
        # Send response
    }
    "COLLECT_DATA" {
        # Analyze current state
        # Send detailed response
    }
}
```

### 3. Controller Client (Bash)

Controller sends commands and waits for responses:

```bash
send_and_collect() {
    local cmd="$1"
    echo "$cmd" > "$PIPE"              # Send command

    read -r response < "$RESPONSE_PIPE" # Wait for response

    # Analyze response data
    # Show results
}
```

### 4. Communication Flow

```
Controller                    Pipe                    TUI Server
    |                          |                          |
    |--- "TYPE:/help" -------->|                          |
    |                          |-------- command -------->|
    |                          |                          | (types text)
    |                          |                          | (captures output)
    |                          |<------- response --------|
    |<--- "TYPED:/help|..." ---|                          |
    | (analyzes data)          |                          |
    |                          |                          |
    |--- "ENTER" ------------->|                          |
    |                          |-------- command -------->|
    |                          |                          | (sends ENTER)
    |                          |<------- response --------|
    |<--- "ENTER_SENT|..." ----|                          |
```

## Updated API Usage

### Example: Permission Buffer Test

```python
from modules.testing import create_permission_buffer_test

# Create test
test = create_permission_buffer_test("/help")

# Run with pipe-based server communication
result = test.run_test(visual=True)

# Server automatically:
# 1. Creates named pipes
# 2. Starts TUI with command listener
# 3. Sends commands via pipe
# 4. Receives responses via pipe
# 5. Validates each step
# 6. Analyzes results
```

## What You See

### TUI Window
- Real opencli TUI running
- Server messages: `[SERVER] Processing command: TYPE:/help`
- Server messages: `[SERVER] Typing: /help`
- Server messages: `[CAPTURED] <output>`
- **Shows actual TUI interface responding to commands**

### Controller Window
```
▶ Creating communication pipes...
✅ Communication pipes created
   Command pipe: /tmp/tui_command_pipe_12345
   Response pipe: /tmp/tui_response_pipe_12345

✅ TUI server started with command listener

⏳ Waiting 11 seconds for SDK...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1: Type /help command
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Typing /help
  ✅ Server responded
  📊 Response: TYPED:/help|RECENT_OUTPUT:...
  🎯 PERMISSION BUFFER DETECTED in response!
  ✅ Command sent
```

## Key Differences From Simple Approach

| Feature | Simple (tmux send-keys) | Pipe-Based Server |
|---------|------------------------|-------------------|
| **Communication** | One-way | Bidirectional |
| **Validation** | None | Server confirms each command |
| **Data Collection** | Manual log parsing | Server sends structured data |
| **Response Timing** | Fixed waits | Wait for actual server response |
| **Error Detection** | Post-test | Real-time per command |
| **Architecture** | Direct keystokes | Client-server with pipes |

## Command Protocol

### Commands Sent to Server

| Command | Format | Response |
|---------|--------|----------|
| Type text | `TYPE:text` | `TYPED:text\|RECENT_OUTPUT:...` |
| Press ENTER | `ENTER` | `ENTER_SENT\|RECENT_OUTPUT:...` |
| Press DOWN | `DOWN` | `DOWN_SENT\|RECENT_OUTPUT:...` |
| Press UP | `UP` | `UP_SENT\|RECENT_OUTPUT:...` |
| Collect state | `COLLECT_DATA` | `DATA_COLLECTED\|PERMISSION_BUFFER:1\|YES_NO_OPTIONS:1\|...` |
| Quit | `QUIT` | `SHUTDOWN` |

### Response Format

Responses include:
- **Status**: Command executed
- **Captured output**: Recent TUI output
- **State indicators**: Permission buffer presence, Yes/No options, etc.

Example response:
```
TYPED:/help|RECENT_OUTPUT:System: /help\nYes, allow this once\nNo, cancel
```

## Files Generated at Runtime

```
/tmp/
├── tui_command_pipe_<pid>          # Named pipe for commands
├── tui_response_pipe_<pid>         # Named pipe for responses
├── tui_expect_server_<pid>.exp     # Expect script (TUI server)
├── tui_controller_<pid>.sh         # Controller script (sends commands)
├── tui_output_log_<pid>.txt        # Captured TUI output
└── tui_cmd_received_<pid>          # Temp file for command passing
```

## Example Generated Expect Server

```tcl
#!/usr/bin/expect -f

set timeout -1
log_user 1

# Get pipe paths
set pipe_path $::env(PIPE_PATH)
set response_pipe $::env(RESPONSE_PIPE_PATH)
set output_log $::env(OUTPUT_LOG)

# Spawn TUI
log_file -a $output_log
spawn opencli tui

# Start command listener (background)
set listener_pid [exec bash -c "
    while read -r cmd; do
        echo \"$cmd\" > /tmp/tui_cmd_received_$$
    done < $pipe_path
" &]

# Main loop - process commands
while {1} {
    if {[file exists "/tmp/tui_cmd_received_$$"]} {
        # Read command
        set cmd [read_command_file]

        # Execute command
        switch $cmd {
            "TYPE:*" { send_text }
            "ENTER" { send "\r" }
            "DOWN" { send "\033\[B" }
            # ...
        }

        # Send response with data
        send_response_with_data
    }
    after 100
}
```

## Why This Architecture

### ✅ Advantages

1. **True Client-Server Model**
   - Controller is a client
   - TUI server validates commands
   - Real communication protocol

2. **Bidirectional Communication**
   - Controller sends: Commands
   - Server responds: Status + Data
   - Enables validation at each step

3. **Structured Data Exchange**
   - Commands follow protocol format
   - Responses include structured data
   - Easy to parse and validate

4. **Real-Time Validation**
   - Server confirms each command execution
   - Controller verifies response before continuing
   - Immediate error detection

5. **Scalable**
   - Can add new commands easily
   - Can extend response format
   - Multiple clients could connect (future)

### ❌ What We DON'T Do Anymore

- ❌ Simple `tmux send-keys` (no feedback)
- ❌ Fixed sleep timings (wait for responses now)
- ❌ Manual log parsing (server sends structured data)
- ❌ One-way communication (bidirectional now)

## Testing The Framework

```bash
cd ~/opencli
python examples/test_permission_buffer.py
```

You'll see:
1. **Two Terminal windows open**
2. **TUI window** shows server processing commands
3. **Controller window** shows commands being sent and responses received
4. **Real-time bidirectional communication** via pipes

## Summary of Changes

| Component | Old Approach | New Approach |
|-----------|-------------|--------------|
| **Communication** | tmux send-keys | Named pipes |
| **TUI Control** | Direct keystroke injection | Expect script with command listener |
| **Data Flow** | One-way | Bidirectional |
| **Validation** | Post-test log analysis | Real-time server responses |
| **Architecture** | Simple automation | Client-server with protocol |
| **Reliability** | Fixed timings | Response-based synchronization |

## The Framework NOW:

✅ Creates named pipes for communication
✅ Generates expect script as TUI server
✅ Server listens on command pipe
✅ Controller sends commands via pipe
✅ Server sends responses via response pipe
✅ Controller validates responses
✅ Captures all TUI output
✅ Analyzes state after each command
✅ Identifies failing functions on errors
✅ Visual dual-window display
✅ True client-server architecture

**This is the CORRECT implementation you demanded!**
