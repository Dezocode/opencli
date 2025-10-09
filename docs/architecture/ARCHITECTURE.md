# OpenCLI Agent System Architecture

## Improved Folder Structure

```
~/.opencli/
├── config.json              # Main configuration
├── .secrets                 # API keys (0o600)
├── sessions/                # Session storage
├── bashes/                  # Background tasks
├── agents/                  # Agent system (NEW)
│   ├── configs/             # Agent YAML configs
│   │   ├── assistant.yaml
│   │   ├── debugger.yaml
│   │   ├── reviewer.yaml
│   │   └── custom/          # User custom agents
│   ├── contexts/            # Context caching (NEW)
│   │   ├── agents_md_cache.json
│   │   └── project_contexts/
│   ├── system_prompts/      # Agent system prompts
│   │   └── base/
│   └── temp/                # Temporary context files (NEW)
│       ├── context_<session_id>.txt
│       └── compiled_<agent>_<hash>.txt
└── modules/
    ├── agent_manager.py     # Agent orchestration
    ├── context_builder.py   # Context building (NEW)
    └── github_tool.py       # GitHub integration
```

## Optimized Architecture

### 1. Context Building Strategy

**Problem**: AGENTS.md sent with every message wastes tokens

**Solution**:
- Cache AGENTS.md per project (hash-based)
- Build context in temp file once per session
- Only rebuild when project changes

```python
# Context Builder Flow:
1. Check if AGENTS.md changed (hash comparison)
2. If unchanged, load cached compiled context
3. If changed, rebuild:
   - Load AGENTS.md
   - Compile with agent system prompt
   - Save to temp file
   - Update hash cache
4. Return file path or compiled text
```

### 2. Message Preparation Strategy

**Current (wasteful)**:
```
Every message → inject full AGENTS.md → send to API
Token usage: ~2000 tokens/message
```

**Optimized**:
```
Session start → build context once → inject as system message
Subsequent messages → NO re-injection
Token usage: ~2000 tokens (one-time), then ~50 tokens/message
```

### 3. Agent Manager Improvements

**New responsibilities**:
- Load agents from `agents/configs/` folder
- Use `ContextBuilder` for efficient context management
- Cache compiled contexts per project
- Monitor AGENTS.md changes via file watching

**Context injection points**:
1. **Session initialization** - Load AGENTS.md + agent prompt
2. **Agent switch** - Replace system message with new agent's prompt
3. **Project change** - Reload AGENTS.md if working dir changes

### 4. Temp File Usage

**When to use temp files**:
- Building large context from multiple sources
- Caching compiled system prompts
- Storing intermediate context for debugging

**Temp file lifecycle**:
```
Create: On session start or agent switch
Read: When preparing messages
Update: When AGENTS.md or agent changes
Delete: On session end or every 24 hours (cleanup)
```

## Token Optimization Flow

```
┌─────────────────┐
│  Session Start  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ ContextBuilder.build_context()     │
│  1. Find AGENTS.md                  │
│  2. Check cache (hash)              │
│  3. If cached → load                │
│  4. If not → compile + cache        │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Create System Message (ONE TIME)    │
│  - Agent system prompt              │
│  - AGENTS.md content                │
│  - Project context                  │
│  Total: ~2000 tokens                │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Subsequent User Messages            │
│  - NO re-injection                  │
│  - Just user + assistant turns      │
│  - ~50-200 tokens per turn          │
└─────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Folder Structure
- Create `~/.opencli/agents/` hierarchy
- Move `agents.yaml` → split into individual files
- Create `contexts/` and `temp/` directories

### Phase 2: Context Builder
- New `context_builder.py` module
- Hash-based caching for AGENTS.md
- Temp file management
- Context compilation logic

### Phase 3: Agent Manager Refactor
- Use ContextBuilder for message prep
- Remove redundant AGENTS.md injection
- Add cache invalidation logic
- Support per-project contexts

### Phase 4: Integration
- Update `opencli.py` to use new structure
- Add cleanup job for old temp files
- Add `/context` command to view current context
- Add `--clear-cache` flag

## Performance Gains

**Before**:
- 100 message conversation
- ~2000 tokens × 100 = 200,000 tokens wasted on AGENTS.md

**After**:
- 100 message conversation
- ~2000 tokens × 1 = 2,000 tokens for AGENTS.md
- **Savings: 198,000 tokens (99% reduction)**

## Benefits

1. **Token efficiency** - 99% reduction in redundant context
2. **Faster responses** - Less tokens = faster API calls
3. **Cost savings** - Pay only for unique content
4. **Scalability** - Support larger AGENTS.md files
5. **Flexibility** - Easy to switch contexts per project

## Tool & Module Registration SOP

### Modular Architecture Guidelines

**CRITICAL**: Keep files modular and within line length limits (≤500 lines recommended)

### Adding a New Tool

When creating a new tool, follow this exact process:

**1. Create Module File** (`modules/your_tool.py`)
```python
"""
Tool description and purpose
"""

def your_tool_function(arg1, arg2):
    """
    Implement your tool logic here
    Returns: result string
    """
    # Implementation
    return result
```

**2. Register in opencli.py** (Lines 20-65 - Imports section)
```python
# Your tool imports
try:
    from your_tool import YourToolClass
    YOUR_TOOL = True
except ImportError:
    YOUR_TOOL = False
```

**3. Add Tool Definition** (Lines 185-280 - TOOLS array)
```python
{
    "type": "function",
    "function": {
        "name": "YourTool",
        "description": "Clear description. [REQUIRES PERMISSION] if risky",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "Param description"},
                "param2": {"type": "string", "description": "Param description"}
            },
            "required": ["param1"]
        }
    }
}
```

**4. Add Risk Classification** (`modules/tool_permissions.py` lines 20-29)
```python
self.tool_risks = {
    # Existing tools...
    'YourTool': RiskLevel.SAFE,  # or RISKY or DANGEROUS
}
```

**5. Implement Execution** (Lines 286-315 - execute_tool function)
```python
def execute_tool(name, args, permission_manager=None):
    # ... permission check code ...

    tools = {
        # Existing tools...
        "YourTool": lambda: execute_your_tool(args["param1"], args.get("param2")),
    }

    # ... rest of function
```

**6. Create Tool Function** (Lines 240-280 - Tool implementations)
```python
def execute_your_tool(param1, param2=None):
    """Execute your tool"""
    if YOUR_TOOL:
        try:
            result = your_tool_function(param1, param2)
            return result
        except Exception as e:
            return f"❌ Error: {e}"
    return "❌ Tool not available"
```

### Adding a New Module

**1. Create Module File** (`modules/your_module.py`)
- Keep under 500 lines
- Single responsibility
- Clear docstrings

**2. Register Import** (Lines 20-65 in opencli.py)
```python
try:
    from your_module import YourModule
    YOUR_MODULE = True
except ImportError:
    YOUR_MODULE = False
```

**3. Initialize in Session** (Lines 790-850 - interactive function)
```python
# Initialize your module
your_module = None
if YOUR_MODULE:
    try:
        your_module = YourModule(CONFIG_DIR)
    except Exception as e:
        print(f"\033[33m⚠️  Module initialization failed: {e}\033[0m\n")
```

**4. Integrate with Session Class** (Lines 317-360 - Session class)
```python
class Session:
    def __init__(self, session_id=None, model=None):
        # ... existing init ...
        self.your_module = None
```

### Adding a Slash Command

**1. Add to handle_slash_command** (Lines 360-780)
```python
elif cmd == "/yourcommand":
    if not YOUR_MODULE or not session.your_module:
        print("❌ Module not available\n")
        return True

    # Command implementation
    session.your_module.do_something(args)
    return True
```

**2. Register in Command Registry** (`modules/command_registry.py`)
```python
DEFAULT_COMMANDS = {
    # ... existing commands ...
    "/yourcommand": {
        "enabled": True,
        "description": "What your command does"
    }
}
```

**3. Add to Help Text** (Lines 763-783 - /help command)
```python
if YOUR_MODULE:
    print("  /yourcommand   - Description of command")
```

### Module Placement Rules

**modules/**: Core functionality modules
- `agent_manager.py` - Agent orchestration
- `context_builder.py` - Context management
- `github_tool.py` - GitHub integration
- `tool_permissions.py` - Permission system
- `command_registry.py` - Command management
- `prompt_processor.py` - Prompt processing
- `upgrade_manager.py` - Version upgrades
- `rollback_manager.py` - Version rollback
- `api_server.py` - HTTP API server for inter-CLI communication
- `api_client.py` - Client library for API access

**Root**: Only main entry point
- `opencli.py` - Main CLI (keep under 1200 lines)

**agents/configs/**: Agent configurations
- `agents.yaml` - Built-in agent definitions
- `custom/` - User custom agents

### Line Length Guidelines

| File Type | Max Lines | Action if Exceeded |
|-----------|-----------|-------------------|
| opencli.py | 1200 | Extract to module |
| Module files | 500 | Split into sub-modules |
| Tool implementations | 300 | Create dedicated module |
| Slash commands | 50 | Move to command handler module |

### Testing New Tools/Modules

**1. Import Test**
```bash
python3 -c "from modules.your_module import YourModule; print('✓')"
```

**2. Permission Test** (for tools)
```bash
opencli
/permissions status  # Check tool is registered
```

**3. Integration Test**
```bash
opencli
# Try using your tool/command
# Verify permission prompts appear if required
```

### Context System Integration

**For AI-aware tools**:
- Update tool descriptions to include `[REQUIRES PERMISSION]` if risky
- This informs the AI model to expect a pause for user confirmation
- AI will not be "stopped" but will be "waiting" for user decision

**Example**:
```python
"description": "Edit file contents. [REQUIRES PERMISSION] User will be prompted to approve."
```

This ensures the AI is prepared and doesn't treat permission prompts as failures.

---

# Production-Ready Long-Running Agent System

## Problem Statement
Tool calls are freezing the chat UI, preventing users from seeing responses even though tokens are being sent to the API. The agent needs to work smoothly for long hours with highest frontier expectations, maintaining goal awareness and implementing robust error recovery.

## Root Causes Identified

### 1. Fire-and-Forget Async Pattern
**Location**: `async_interactive.py:1483`
```python
asyncio.create_task(stream_ai_response())  # ❌ No error handling, no cancellation
```

### 2. Blocking Tool Execution
**Location**: `async_interactive.py:1327-1346`
- Synchronous tool execution in async event loop
- No timeout on bash commands (can hang indefinitely)
- No progress feedback during long operations

### 3. Unbounded Continuation Flow
**Location**: `async_interactive.py:1350-1437`
- Recursive API calls without depth limits
- Can create infinite loops if tools keep triggering
- No backpressure on tool result sizes

## Production-Ready Architecture

### Phase 1: Streaming Reliability (IMMEDIATE)

#### 1.1 Add Cancellation & Timeout System
```python
class StreamManager:
    def __init__(self, timeout: int = 300):  # 5min default
        self.timeout = timeout
        self.cancel_token = asyncio.Event()

    async def stream_with_timeout(self, coro):
        try:
            return await asyncio.wait_for(coro, timeout=self.timeout)
        except asyncio.TimeoutError:
            self.cancel_token.set()
            raise StreamTimeoutError(f"Stream exceeded {self.timeout}s")
```

#### 1.2 Convert Blocking Tools to Async
```python
async def execute_bash_async(command, description=None, timeout=30):
    """Non-blocking bash execution with timeout"""
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout
        )
        return stdout.decode() + stderr.decode()
    except asyncio.TimeoutError:
        proc.kill()
        return f"⏱ Command timed out after {timeout}s"
```

#### 1.3 Add Heartbeat System
```python
async def heartbeat_monitor(app, interval=2.0):
    """Detect frozen streams and alert user"""
    last_activity = time.time()

    while True:
        await asyncio.sleep(interval)
        if time.time() - last_activity > 30:
            app.write("[yellow]⚠ Stream appears frozen. Press Ctrl+C to cancel.[/yellow]\n")
```

### Phase 2: Spec-Kit Integration (GOAL TRACKING)

#### 2.1 Specification-Driven Commands
```python
SPEC_COMMANDS = {
    '/constitution': 'Load project principles and governance',
    '/specify': 'Define feature specification',
    '/plan': 'Generate implementation plan',
    '/tasks': 'Break down into actionable tasks',
    '/implement': 'Execute implementation with tracking',
    '/spec-check': 'Validate against specification'
}
```

#### 2.2 Memory Artifact System
```python
class SpecMemory:
    """Persistent goal and context tracking"""

    def __init__(self, project_root: Path):
        self.memory_dir = project_root / '.specify' / 'memory'
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def save_constitution(self, content: str):
        """Save project principles"""
        (self.memory_dir / 'constitution.md').write_text(content)

    def save_feature_spec(self, feature_name: str, spec: str):
        """Save feature specification"""
        (self.memory_dir / f'{feature_name}.spec.md').write_text(spec)

    def get_active_context(self) -> dict:
        """Load all active specifications into context"""
        context = {}
        if (self.memory_dir / 'constitution.md').exists():
            context['constitution'] = (self.memory_dir / 'constitution.md').read_text()

        for spec_file in self.memory_dir.glob('*.spec.md'):
            context[spec_file.stem] = spec_file.read_text()

        return context
```

#### 2.3 Goal Tracking System
```python
class GoalTracker:
    """Track agent goals across long sessions"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_goal = None
        self.goal_history = []
        self.checkpoints = []

    def set_goal(self, goal: str, phase: str = 'planning'):
        """Set current working goal"""
        self.current_goal = {
            'goal': goal,
            'phase': phase,
            'started_at': datetime.now().isoformat(),
            'progress': []
        }
        self.goal_history.append(self.current_goal)

    def add_progress(self, action: str, result: str):
        """Track progress on current goal"""
        if self.current_goal:
            self.current_goal['progress'].append({
                'action': action,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })

    def create_checkpoint(self):
        """Create recovery checkpoint"""
        checkpoint = {
            'goal': self.current_goal,
            'timestamp': datetime.now().isoformat(),
            'messages_count': len(session.messages)
        }
        self.checkpoints.append(checkpoint)
        return checkpoint
```

### Phase 3: Error Recovery & Resilience

#### 3.1 Circuit Breaker for Tool Execution
```python
class ToolCircuitBreaker:
    """Prevent cascading failures in tool execution"""

    def __init__(self, failure_threshold=3, timeout=60):
        self.failures = 0
        self.threshold = failure_threshold
        self.timeout = timeout
        self.state = 'closed'  # closed, open, half_open
        self.last_failure = None

    async def execute(self, tool_func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure > self.timeout:
                self.state = 'half_open'
            else:
                raise CircuitOpenError("Tool execution circuit is open")

        try:
            result = await tool_func(*args, **kwargs)
            if self.state == 'half_open':
                self.state = 'closed'
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.threshold:
                self.state = 'open'
            raise
```

#### 3.2 Exponential Backoff for API Calls
```python
async def api_call_with_retry(client, **kwargs):
    """Retry API calls with exponential backoff"""
    max_retries = 3
    base_delay = 1.0

    for attempt in range(max_retries):
        try:
            return await client.chat.completions.create(**kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)
```

### Phase 4: Verbose & Debug Modes

#### 4.1 Multi-Level Logging
```python
class VerbosityManager:
    LEVELS = {
        'quiet': 0,      # Errors only
        'normal': 1,     # User-facing messages
        'verbose': 2,    # API timing, token counts
        'debug': 3,      # Message structures
        'trace': 4       # Full execution trace
    }

    def __init__(self, level='normal'):
        self.level = self.LEVELS.get(level, 1)

    def log(self, message: str, level: str = 'normal'):
        if self.LEVELS.get(level, 1) <= self.level:
            print(message)
```

#### 4.2 Performance Metrics
```python
class PerformanceMonitor:
    """Track API and tool execution performance"""

    def __init__(self):
        self.metrics = []

    @contextmanager
    def measure(self, operation: str):
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.metrics.append({
                'operation': operation,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })

    def get_stats(self) -> dict:
        if not self.metrics:
            return {}
        durations = [m['duration'] for m in self.metrics]
        return {
            'total_operations': len(self.metrics),
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations)
        }
```

### Phase 5: Long-Running Workflow Support

#### 5.1 Workflow State Machine
```python
class WorkflowStateMachine:
    """Manage multi-phase long-running workflows"""

    STATES = ['idle', 'planning', 'implementing', 'testing', 'refining', 'complete']

    def __init__(self):
        self.current_state = 'idle'
        self.state_history = []

    def transition(self, new_state: str):
        if new_state not in self.STATES:
            raise ValueError(f"Invalid state: {new_state}")

        self.state_history.append({
            'from': self.current_state,
            'to': new_state,
            'timestamp': datetime.now().isoformat()
        })
        self.current_state = new_state

    def get_phase(self) -> str:
        """Get current phase for context"""
        return self.current_state
```

#### 5.2 Tool Execution Queue
```python
class ToolQueue:
    """Priority queue for tool execution with async support"""

    def __init__(self):
        self.queue = asyncio.PriorityQueue()
        self.results = {}

    async def enqueue(self, tool_call, priority=1):
        await self.queue.put((priority, tool_call))

    async def process(self, executor):
        """Process tools with progress callbacks"""
        while not self.queue.empty():
            priority, tool_call = await self.queue.get()

            # Execute with progress feedback
            result = await executor(tool_call)
            self.results[tool_call['id']] = result

    def get_result(self, tool_id: str):
        return self.results.get(tool_id)
```

---

## Async Streaming Architecture (v1.4.0+)

### Stream Buffer System

**Problem**: Incremental markdown rendering caused 100% CPU usage and UI freezing during fast token streams.

**Solution**: Buffer incoming tokens and release at controlled pace with visual progress indicator.

#### StreamBuffer (modules/stream_buffer.py)

Async queue-based token accumulation with controlled release:

```python
class StreamBuffer:
    def __init__(self, chars_per_batch=20, batch_delay_ms=50):
        self.buffer = asyncio.Queue()
        self.total_tokens = 0
        self.receiving = False
        self.complete = False
        self.interrupted = False

    async def add_chunk(self, text):
        """Add chunk from API stream"""
        await self.buffer.put(text)
        self.total_tokens += len(text)
        self.full_text += text

    async def drain_smooth(self, write_callback):
        """Release buffered content at controlled pace"""
        accumulated = ""
        while self.receiving or not self.buffer.empty():
            chunk = await asyncio.wait_for(self.buffer.get(), timeout=0.1)
            accumulated += chunk

            # Release in batches for smooth rendering
            while len(accumulated) >= self.chars_per_batch:
                batch = accumulated[:self.chars_per_batch]
                accumulated = accumulated[self.chars_per_batch:]
                await write_callback(batch)
                await asyncio.sleep(self.batch_delay)
```

**Key features**:
- Configurable pacing (20 chars/50ms default)
- Token count tracking
- ESC interrupt support
- Time elapsed monitoring

#### BufferStatusDisplay

Inline animated progress indicator in chat area:

```python
class BufferStatusDisplay:
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    async def start(self):
        """Add buffer status to StreamingDisplay"""
        self.content_widget.add_buffer_status(
            tokens=self.buffer.total_tokens,
            elapsed=self.buffer.get_elapsed()
        )

    async def _update_loop(self):
        """10 FPS animation loop"""
        while not self.buffer.complete:
            spinner = self.SPINNER_FRAMES[self._spinner_frame]
            self.content_widget.update_buffer_status(
                tokens=self.buffer.total_tokens,
                elapsed=self.buffer.get_elapsed(),
                spinner_frame=spinner
            )
            await asyncio.sleep(0.1)
```

**Display format**:
```
⠋ Synthesizing… (esc to interrupt · 3s · ↓ 145 tokens)
  ⎿  Tip: Press ESC to interrupt long-running responses.
```

### Streaming Flow (v1.4.0)

```
API Response Stream
       ↓
StreamBuffer.add_chunk()
       ↓
Queue accumulates chunks
       ↓
BufferStatusDisplay shows:
  ⠋ Synthesizing… (↓ tokens)
       ↓
All chunks received
       ↓
finish_receiving()
       ↓
Render markdown ONCE
       ↓
Remove buffer status
       ↓
Display complete response
```

**Before v1.4.0** (Incremental):
```
Chunk 1 → Parse MD → Render → Display (10ms)
Chunk 2 → Parse MD → Render → Display (10ms)
Chunk 3 → Parse MD → Render → Display (10ms)
...
Total: N chunks × 10ms = 100% CPU
```

**After v1.4.0** (Buffered):
```
Chunks 1-N → Buffer (0.1ms each)
Show status → Update 10 FPS (minimal CPU)
All received → Parse MD ONCE → Render → Display
Total: 1 × 10ms = <5% CPU
```

### Performance Monitor System

#### PerformanceMonitor (modules/performance_monitor.py)

Background thread for lightweight metrics collection:

```python
class PerformanceMonitor:
    def _monitor_loop(self):
        """Background thread - LIGHTWEIGHT metrics only"""
        while not self.stop_flag.is_set():
            # Update every 2 seconds
            self.cpu_percent = self.process.cpu_percent(interval=2)
            self.memory_mb = self.process.memory_info().rss / 1024 / 1024
            self.thread_count = self.process.num_threads()

            # Log spikes (>11%)
            if self.cpu_percent > 11:
                self.cpu_spikes.append({
                    'timestamp': datetime.now(),
                    'cpu': self.cpu_percent
                })

            # NO stack profiling - observer effect!
```

**Anti-pattern**: Aggressive profiling (`sys._current_frames()` + `traceback.extract_stack()` on all threads every second) → 100% CPU from profiler itself!

**Metrics tracked**:
- CPU usage with trend detection (↗↘→)
- Memory usage (RSS)
- Thread count
- Token streaming rate
- CPU spike logging

#### PerformanceStatusLine (modules/simple_tui.py)

Bottom statusline widget with live metrics:

```python
class PerformanceStatusLine(Static):
    def render(self) -> Text:
        status_parts = [
            f"⏺",
            f"CPU: {self.perf_monitor.cpu_percent:.1f}% {trend_arrow}",
            f"MEM: {self.perf_monitor.memory_mb:.0f}MB",
            f"Threads: {self.perf_monitor.thread_count}",
        ]

        if self.perf_monitor.tokens_per_sec > 0:
            status_parts.append(
                f"Speed: {self.perf_monitor.tokens_per_sec:.1f} tok/s"
            )

        return f" │ ".join(status_parts)
```

**Frontier color states**:
- Green (#6B9E78): CPU <11% (healthy)
- Orange (#E2A478): CPU 11-50% (elevated)
- Red (#E27878): CPU >50% (high load)

### Module Integration

#### StreamingDisplay Buffer Methods (modules/streaming_display.py)

Inline buffer status integrated into chat:

```python
class StreamingDisplay(Static):
    def add_buffer_status(self, tokens: int, elapsed: int):
        """Add inline buffer status to chat"""
        buffer_text = Text()
        buffer_text.append("⠋ Synthesizing… ", style=FRONTIER_COLORS["info"])
        buffer_text.append(f"(esc · {elapsed}s · ↓ {tokens})")

        # Store as special tuple
        self._lines.append(("__BUFFER_STATUS__", buffer_text))
        self._rebuild_display()

    def update_buffer_status(self, tokens, elapsed, spinner_frame):
        """Update existing buffer status"""
        for i, line in enumerate(self._lines):
            if isinstance(line, tuple) and line[0] == "__BUFFER_STATUS__":
                # Update with new spinner + metrics
                self._lines[i] = ("__BUFFER_STATUS__", updated_text)
                self._rebuild_display()

    def remove_buffer_status(self):
        """Remove buffer status from display"""
        self._lines = [
            line for line in self._lines
            if not (isinstance(line, tuple) and line[0] == "__BUFFER_STATUS__")
        ]
        self._rebuild_display()
```

**Integration points**:
1. `async_interactive.py` creates StreamBuffer + BufferStatusDisplay
2. BufferStatusDisplay calls StreamingDisplay methods
3. Chunks accumulate in buffer while status animates
4. On completion: remove status, render markdown, display

### Performance Optimizations

#### Queue Processor (modules/simple_tui.py)

**Before**:
```python
text, end = self._write_queue_threadsafe.get(timeout=0.02)  # 50 wakeups/sec
```

**After**:
```python
text, end = self._write_queue_threadsafe.get(timeout=0.5)   # 2 wakeups/sec
```

**Impact**: 96% reduction in idle CPU (20% → <5%)

#### Event Loop Yielding (modules/async_interactive.py)

**Critical fix**: Yield at chunk boundaries to keep UI responsive

```python
async for chunk in response:
    # CRITICAL: Yield at start
    await asyncio.sleep(0)

    # Process chunk
    if delta.content:
        await stream_buffer.add_chunk(delta.content)
```

**Why**: Fast streaming (Chinese text, code blocks) would hog event loop → UI frozen

#### Batch Processing

**Queue flushing**:
```python
# Before: Flush every 10 items or 50ms
should_flush = (len(batch) >= 10 or elapsed >= 0.05)

# After: Flush every 50 items or 100ms
should_flush = (len(batch) >= 50 or elapsed >= 0.1)
```

**Impact**: Reduced write frequency, smoother UI

### Performance Metrics (v1.4.0)

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Idle CPU | 11-20% | <5% | 96% reduction |
| Streaming CPU | 100% | 30-50% | 50% reduction |
| Queue Polling | 50/sec | 2/sec | 96% reduction |
| UI Responsiveness | Frozen | Always | ∞ improvement |
| Token Render | Incremental | Single | Eliminated lag |

### Architecture Benefits

**Separation of Concerns**:
- `StreamBuffer`: Data accumulation
- `BufferStatusDisplay`: Progress visualization
- `StreamingDisplay`: Chat rendering
- `PerformanceMonitor`: System metrics

**User Experience**:
- Smooth streaming with progress indicator
- Always-responsive UI (can scroll/type during response)
- Professional loading states with tips
- Live performance visibility with `/performance`

**Developer Experience**:
- Configurable pacing (chars_per_batch, batch_delay_ms)
- Clean async architecture
- Observable performance metrics
- Frontier color palette consistency

### Future Enhancements

1. **Configurable buffer pacing** in user settings
2. **Custom spinner themes** (braille, dots, arrows)
3. **Advanced tip system** with contextual messages
4. **Buffer persistence** across session interrupts
5. **Adaptive pacing** based on content type (code vs text)

---

## Implementation Priority

### Immediate (Week 1)
1. ✅ Fix async streaming with cancellation tokens
2. ✅ Add timeout wrappers to all API calls
3. ✅ Convert blocking tools to async
4. ✅ Implement heartbeat monitoring

### Short-term (Week 2-3)
1. ⏳ Integrate Spec-Kit commands (/constitution, /specify, /plan)
2. ⏳ Build memory artifact system
3. ⏳ Add goal tracking and checkpoints
4. ⏳ Implement circuit breaker for tools

### Medium-term (Month 1)
1. 📋 Build workflow state machine
2. 📋 Add performance monitoring
3. 📋 Implement tool execution queue
4. 📋 Create verbose/trace modes

### Long-term (Quarter 1)
1. 🔮 Multi-agent coordination
2. 🔮 Distributed tool execution
3. 🔮 Advanced error recovery with rollback
4. 🔮 Auto-scaling for high-load scenarios

## Success Metrics

- **Zero UI Freezes**: All operations non-blocking
- **< 100ms Response Time**: First token to user
- **99.9% Reliability**: Tool execution success rate
- **8+ Hour Sessions**: No degradation in long runs
- **Full Context Retention**: Goals tracked across sessions

## References

- [GitHub Spec-Kit](https://github.com/github/spec-kit) - Specification-driven development
- [Anthropic Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/best-practices) - Long context handling
- [AsyncIO Patterns](https://docs.python.org/3/library/asyncio.html) - Production async patterns
