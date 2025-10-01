# Agents Directory

This directory contains the agent system configuration and runtime files.

## Structure

```
agents/
├── configs/          # Agent configuration files
│   ├── agents.yaml   # Main agent definitions
│   └── custom/       # User custom agent configs
├── contexts/         # Context caching (generated at runtime)
│   └── project_contexts/
├── system_prompts/   # Reusable system prompt templates
│   └── base/
└── temp/             # Temporary compiled context files (auto-managed)
```

## Files

### `configs/agents.yaml`
Main agent configuration file defining all built-in agents:
- assistant (default)
- debugger
- reviewer
- refactor
- tester
- documenter
- architect

### `contexts/` (Generated)
Runtime directory for context caching:
- `agents_md_cache.json` - Maps AGENTS.md hashes to compiled contexts
- `project_contexts/` - Per-project context storage

### `temp/` (Generated)
Temporary files auto-managed by ContextBuilder:
- `compiled_<agent>_<hash>.txt` - Compiled context files
- `context_<session_id>.txt` - Session-specific contexts

**Auto-cleanup**: Only latest 5 compiled contexts are kept.

## Adding Custom Agents

Create YAML files in `configs/custom/`:

```yaml
# configs/custom/my-agent.yaml
agents:
  my-agent:
    system_prompt: |
      You are a specialized agent for...
    instructions:
      - First instruction
      - Second instruction
    context_strategy: auto
    max_context_tokens: 80000
    priority: 5
    triggers:
      - keyword1
      - keyword2
    tools:
      - Read
      - Write
      - GitHub
```

## Context Management

Context files are automatically managed:
1. **Created**: When agent processes first message
2. **Cached**: Hash-based for fast reuse
3. **Cleaned**: Automatically keeps only 5 latest
4. **Invalidated**: When AGENTS.md or CLI environment changes

## See Also

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Full system architecture
- [INTEGRATION_STATUS.md](../INTEGRATION_STATUS.md) - Integration details
