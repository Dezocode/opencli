# OpenCLI IPC API Documentation

## Overview

The OpenCLI IPC (Inter-Process Communication) system enables bidirectional communication between the main OpenCLI instance and external subagents. This allows you to:

- Connect multiple agents to a single OpenCLI session
- Send and receive messages between the shell and agents
- Execute commands remotely
- Stream real-time output
- Monitor shell activity

## Architecture

```
┌─────────────────────────────────────┐
│        OpenCLI Main Instance        │
│  ┌──────────────────────────────┐   │
│  │      IPC Server              │   │
│  │  - Unix Domain Socket        │   │
│  │  - Message Routing           │   │
│  │  - Subagent Registry         │   │
│  └──────────────────────────────┘   │
│              ▲ ▼                    │
│     Status Bar shows agent count    │
└──────────────┼──────────────────────┘
               │ Unix Socket
         ┌─────┴──────┬─────────┐
         ▼            ▼         ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │Agent 1 │  │Agent 2 │  │Agent N │
    └────────┘  └────────┘  └────────┘
```

## Quick Start

### For Subagents (Connecting to OpenCLI)

```python
from ipc_shell_api import connect_to_opencli

async def my_agent():
    # Connect to OpenCLI session
    api = await connect_to_opencli(
        session_id="abc123",  # Get from OpenCLI status bar
        agent_name="MyAgent",
        description="Does cool things"
    )

    # Send a message
    await api.send("Hello from subagent!")

    # Receive a message
    response = await api.receive(timeout=10.0)
    print(f"Got: {response}")

    # Disconnect
    await api.disconnect()
```

### For OpenCLI Integration

```python
from modules.opencli_ipc import create_ipc_server

# In your OpenCLI initialization
ipc_server = create_ipc_server(session_id)
await ipc_server.start()

# Pass to TUI
tui = OpenCLITUI(session, config, ipc_server=ipc_server)

# Cleanup on exit
await ipc_server.stop()
```

## API Reference

### SubagentAPI

Main API for subagents to interact with OpenCLI.

#### Methods

**`async connect(session_id: str)`**
- Connect to an OpenCLI instance
- `session_id`: The session ID shown in OpenCLI status bar

**`async disconnect()`**
- Disconnect from OpenCLI instance

**`async send(message: str)`**
- Send a message to the OpenCLI shell
- `message`: Text to send

**`async receive(timeout: float = None) -> Optional[str]`**
- Receive a message from the shell
- `timeout`: Max seconds to wait (None = wait forever)
- Returns: Message text or None if timeout

**`async ask(question: str, timeout: float = 30.0) -> Optional[str]`**
- Send a question and wait for response
- `question`: Question to ask
- `timeout`: Max seconds to wait
- Returns: Response text or None

**`on_receive(callback: Callable[[str], None])`**
- Register a callback for incoming messages
- `callback`: Function that takes message text

**`async run_command(command: str) -> str`**
- Execute a command in the OpenCLI shell
- `command`: Command to run
- Returns: Command output
- Raises: RuntimeError if command fails

**`async stream_output(text_generator)`**
- Stream text to shell in real-time
- `text_generator`: Async generator yielding text chunks

### ShellAPI

Lower-level API with more control.

#### Methods

**`async write_to_shell(message: str, role: str = "assistant")`**
- Write a message to the shell
- `message`: Message content
- `role`: Either 'user' or 'assistant'

**`async read_from_shell(timeout: float = None) -> Optional[ShellMessage]`**
- Read next message from shell
- Returns: ShellMessage object with role, content, timestamp

**`async execute_command(command: str) -> Dict[str, Any]`**
- Execute command and get detailed response
- Returns: Dict with 'success', 'output', 'error' keys

**`async get_shell_history() -> List[ShellMessage]`**
- Get message history from the shell

**`async get_shell_status() -> Dict[str, Any]`**
- Get current status of the shell

### IPCServer

Server-side API for OpenCLI main instance.

#### Methods

**`async start()`**
- Start the IPC server

**`async stop()`**
- Stop the IPC server and disconnect all agents

**`async broadcast(msg_type: str, payload: Dict, exclude: str = None)`**
- Broadcast message to all connected agents
- `exclude`: Optional agent ID to exclude

**`async send_to_agent(agent_id: str, msg_type: str, payload: Dict)`**
- Send message to specific agent

**`register_handler(msg_type: str, handler: Callable)`**
- Register handler for message type

**`get_subagent_count() -> int`**
- Get number of connected agents (shown in status bar)

**`get_subagents() -> List[SubagentInfo]`**
- Get list of all connected agents

## Message Types

- `REGISTER` - Subagent registration
- `UNREGISTER` - Subagent deregistration
- `MESSAGE` - Chat message
- `COMMAND` - Command execution request
- `RESPONSE` - Response to a command
- `STATUS` - Status update
- `HEARTBEAT` - Keep-alive ping
- `ERROR` - Error notification

## Examples

### Echo Agent

```python
async def echo_agent(session_id):
    api = await connect_to_opencli(session_id, "EchoAgent")

    while True:
        msg = await api.receive(timeout=1.0)
        if msg:
            await api.send(f"Echo: {msg}")
```

### Assistant Agent

```python
async def assistant_agent(session_id):
    async with SubagentAPI("Assistant", "AI Helper") as api:
        await api.connect(session_id)

        while True:
            msg = await api.receive()
            response = process_with_ai(msg)
            await api.send(response)
```

### Monitoring Agent

```python
async def monitor_agent(session_id):
    api = await connect_to_opencli(session_id, "Monitor")

    while True:
        await asyncio.sleep(30)
        status = await api.shell.get_shell_status()
        await api.send(f"Status: {status}")
```

### Streaming Agent

```python
async def streaming_agent(session_id):
    api = await connect_to_opencli(session_id, "Streamer")

    async def generate_text():
        for word in "Hello from streaming agent".split():
            yield word + " "
            await asyncio.sleep(0.2)

    await api.stream_output(generate_text())
```

## Running Subagents

### From Command Line

```bash
# Run example subagent
python examples/example_subagent.py <session_id> echo

# Run assistant agent
python examples/example_subagent.py <session_id> assistant

# Run monitor agent
python examples/example_subagent.py <session_id> monitor
```

### Getting Session ID

The session ID is displayed in the OpenCLI status bar at the bottom of the screen.

### Status Bar Display

When subagents are connected, the status bar shows:
```
Model: grok-4-fast │ Tokens: 1,234 │ Turn: 5 │ Agents: 2 │ CWD: opencli │ 14:23:45
                                                    ^
                                              Shows agent count
```

## Socket Location

By default, IPC sockets are created at:
```
/tmp/opencli/opencli_<session_id>.sock
```

## Error Handling

```python
try:
    api = await connect_to_opencli(session_id, "MyAgent")
except ConnectionError as e:
    print(f"Failed to connect: {e}")

try:
    result = await api.run_command("ls")
except RuntimeError as e:
    print(f"Command failed: {e}")
```

## Best Practices

1. **Always disconnect properly** - Use `async with` or call `disconnect()`
2. **Use heartbeats** - For long-running agents, send periodic heartbeats
3. **Handle timeouts** - Always specify timeouts for `receive()` operations
4. **Error handling** - Wrap IPC operations in try/except blocks
5. **Message validation** - Validate message content before processing
6. **Resource cleanup** - Clean up connections and tasks on shutdown

## Security Considerations

- Unix domain sockets are local-only (no network exposure)
- Socket permissions default to user-only access
- Validate all incoming messages
- Don't expose sensitive data in message payloads
- Use session IDs as authentication tokens

## Troubleshooting

### Agent won't connect
- Check session ID is correct
- Verify OpenCLI instance is running
- Check socket file exists: `/tmp/opencli/opencli_<session_id>.sock`

### Messages not received
- Check agent is registered (status bar shows count)
- Verify message handlers are registered
- Check for exceptions in agent code

### Performance issues
- Use message batching for high-frequency updates
- Implement backpressure for slow consumers
- Monitor socket buffer sizes

## Advanced Usage

### Custom Message Handlers

```python
from opencli_ipc import MessageType

async def custom_handler(message):
    print(f"Received: {message.payload}")

server.register_handler(MessageType.CUSTOM.value, custom_handler)
```

### Multiple Agents

```python
# Run multiple agents in parallel
agents = [
    echo_agent(session_id),
    monitor_agent(session_id),
    assistant_agent(session_id)
]

await asyncio.gather(*agents)
```

### Persistent Agents

Use system services (systemd, launchd) to run agents as background services.

## Future Enhancements

- [ ] Authentication/authorization system
- [ ] Encrypted communication option
- [ ] Remote network support (TCP sockets)
- [ ] Agent discovery mechanism
- [ ] Message persistence/replay
- [ ] Agent-to-agent communication
- [ ] Rate limiting and quotas
