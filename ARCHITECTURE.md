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
