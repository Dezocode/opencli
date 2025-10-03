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
