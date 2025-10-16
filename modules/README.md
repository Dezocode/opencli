# Modules Directory

Python modules that power OpenCLI's advanced features.

## Files

### `agent_manager.py`
**Agent orchestration and management**

- Loads agent configurations from `agents/configs/`
- Routes user input to appropriate agents based on triggers
- Manages context preparation and optimization
- Handles agent switching and state

Key classes:
- `AgentConfig` - Represents single agent configuration
- `ContextManager` - Smart context compression strategies
- `AgentManager` - Main orchestration class

### `context_builder.py`
**Intelligent context building and caching**

- Discovers AGENTS.md files in project tree
- Hash-based caching for efficient context reuse
- Scans ~/bin for available CLI tools
- Auto-cleanup (keeps only 5 latest contexts)
- Builds comprehensive CLI environment info

Key features:
- 99% token reduction through smart caching
- Auto-invalidation on AGENTS.md or CLI changes
- Temp file management in `agents/temp/`
- Latest-5 guarantee

### `github_tool.py`
**GitHub integration via gh CLI**

- Wraps gh CLI for authenticated GitHub operations
- Auth status checking and validation
- Repository, issue, PR, workflow management
- Gist creation
- Graceful fallback if gh CLI not installed

Available actions:
- `auth_status`, `repo_view`
- `issue_list`, `issue_view`, `issue_create`
- `pr_list`, `pr_view`, `pr_create`, `pr_checkout`
- `workflow_list`, `workflow_run`, `run_list`
- `gist_create`

## Import Chain

```
opencli.py (~/bin/opencli)
    ↓ (adds ~/.opencli/modules to sys.path)
    ├─→ agent_manager.py
    │      └─→ context_builder.py
    └─→ github_tool.py
```

## Development

All modules are:
- Pure Python (no compiled extensions)
- Self-contained with minimal dependencies
- Error-tolerant (graceful fallbacks)
- Documented with docstrings

## Dependencies

- `pyyaml` - For agent configuration parsing
- `openai` - For API communication (in main opencli.py)
- `prompt_toolkit` - For rich terminal UI (in main opencli.py)

## Testing

To test module imports:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".opencli" / "modules"))

from agent_manager import AgentManager
from context_builder import ContextBuilder
from github_tool import GitHubTool

print("All modules imported successfully!")
```
