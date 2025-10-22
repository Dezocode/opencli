# Copilot Instructions for OpenCLI

## Project Overview

OpenCLI is a fast, feature-rich terminal interface for OpenRouter API with Claude Code capabilities. It's built in Python and designed to be modular, reliable, and user-friendly.

**Key Features:**
- Buffered streaming with inline progress indicators
- Smart agent system with auto-switching based on task type
- Full tool support (Read, Write, Edit, Bash, Glob, Grep)
- GitHub integration via gh CLI
- Session management and context optimization
- Version control with upgrade/rollback system
- Advanced TUI interface with permission system

## Architecture

### Core Components

1. **Main Entry Point**: `opencli.py` - Single-file Python script that orchestrates the CLI
2. **Modules**: Located in `modules/` directory
   - `agent_manager.py` - Agent orchestration and context management
   - `context_builder.py` - Context caching and optimization
   - `github_tool.py` - GitHub CLI integration
   - `simple_tui.py` - Advanced TUI interface
   - `upgrade_manager.py` - Version control system
   - `rollback_manager.py` - Rollback functionality
   - `command_registry.py` - Command permission system

3. **Agent System**: Located in `agents/` directory
   - `configs/agents.yaml` - Built-in agent definitions
   - Context caching and AGENTS.md support
   - Specialized agents: assistant, debugger, reviewer, refactor, tester, documenter, architect

4. **Installation Structure**: After installation
   - Config directory: `~/.opencli/`
   - Executable: `~/bin/opencli`
   - Sessions: `~/.opencli/sessions/`
   - API keys: `~/.opencli/.secrets` (0o600 permissions)

## Code Style and Conventions

### Python Guidelines
- Follow PEP 8 style guidelines
- Use descriptive variable names
- Add docstrings for functions and classes
- Handle errors gracefully with try-except blocks
- Use pathlib.Path for file operations

### Module Organization
- Keep modules focused on single responsibilities
- Import only what's needed
- Handle ImportError gracefully for optional features
- Use absolute imports from modules directory

### Security Best Practices
- Never commit API keys or secrets
- Use 0o600 permissions for sensitive files
- Store credentials in `~/.opencli/.secrets`
- Validate user input for dangerous operations

## Development Workflow

### Making Changes

1. **For Core Features**: Modify `opencli.py` or add new modules to `modules/`
2. **For Agent System**: Update `agents/configs/agents.yaml` or add new agent modules
3. **For Installation**: Modify `install.sh` with backward compatibility in mind
4. **For Version Control**: Update `version.json` with semantic versioning

### Version Control
- Use semantic versioning: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes
- Update `version.json` with changelog entries
- Use `bump-version.sh` for version bumps

### Testing
- Test files are in `tests/` directory
- Manual testing is primary method (no automated test suite yet)
- Test checklist:
  - Installation works cleanly
  - Core commands work (`/status`, `/agents`, `/model`)
  - Tool calls function properly
  - Upgrade/rollback system works
  - No secrets in committed code

## Important Files and Directories

### Configuration
- `config.json` - Main configuration (model, baseURL, maxTurns, contextWindow)
- `.secrets` - API keys (never commit this!)
- `agents/configs/agents.yaml` - Agent definitions

### Documentation
- `README.md` - Main documentation and feature list
- `ARCHITECTURE.md` - System architecture details
- `CONTRIBUTING.md` - Contribution guidelines
- `SETUP.md` - Complete setup guide
- `UPGRADING.md` - Version control documentation
- `COMMAND_SYSTEM.md` - Command permission system

### Scripts
- `install.sh` - Installation script
- `upgrade.sh` - Upgrade script (legacy)
- `emergency-rollback.sh` - Emergency recovery
- `bump-version.sh` - Version management

## Common Patterns

### Tool Call System
```python
# Tools are defined with specific schemas
# Results are returned in structured format
# Permission system validates dangerous operations
```

### Agent System
```python
# Agents auto-switch based on trigger words
# Each agent has specialized system prompts
# AGENTS.md files provide project context
# Context is cached for efficiency
```

### Context Management
- Use context builder for efficient token usage
- Cache AGENTS.md per project (hash-based)
- Temp files in `agents/temp/` for compiled contexts
- Auto-compaction keeps system prompt + recent messages

### Error Handling
```python
try:
    # Feature code
except ImportError:
    # Gracefully disable feature if module unavailable
    FEATURE_ENABLED = False
```

## When Working on OpenCLI

### Adding New Features
1. Check if it fits with the project philosophy (fast, modular, reliable)
2. Add new modules to `modules/` directory
3. Register commands in `command_registry.py` if applicable
4. Update relevant documentation files
5. Update `version.json` with changes

### Fixing Bugs
1. Identify the affected module or component
2. Make minimal changes to fix the issue
3. Test thoroughly before committing
4. Add to changelog in `version.json`

### Improving Documentation
1. Keep README.md as the main entry point
2. Link to detailed docs (ARCHITECTURE.md, SETUP.md, etc.)
3. Use clear examples and code snippets
4. Maintain consistency with existing documentation style

## Dependencies

Primary dependencies (see `requirements.txt`):
- `openai>=1.0.0` - OpenAI API client
- `prompt_toolkit>=3.0.0` - Terminal UI
- `pyyaml>=6.0` - YAML parsing for agent configs
- `requests>=2.28.0` - HTTP requests
- `textual>=0.40.0` - TUI components
- `rich>=13.0.0` - Rich text rendering
- `psutil>=5.9.0` - System monitoring

Optional dependencies:
- `gh` CLI - For GitHub integration features

## Key Concepts

### IPC System
- Bidirectional communication with Claude Code
- Located in `scripts/` directory
- Enables remote control of OpenCLI sessions

### Permission System
- Three risk levels: SAFE, RISKY, DANGEROUS
- Inline prompts for user confirmation
- Persistent settings in `~/.opencli/tool_permissions.json`
- ESC key for interrupt

### Session Management
- Sessions stored in `~/.opencli/sessions/`
- Each session has unique ID
- Resume with `-c` (continue) or `-r <session-id>`
- Contains full message history

### Streaming Display
- Buffered streaming for smooth token display
- Non-blocking TUI with Frontier design system
- Inline spinner with token count during streaming
- Single markdown render per response (eliminates lag)

## Notes for Copilot

- This is a production CLI tool used by real users
- Prioritize stability and backward compatibility
- Test changes thoroughly before committing
- Never commit secrets or API keys
- Follow the existing code style and patterns
- Update documentation when adding features
- Consider token efficiency in agent system changes
- Maintain the modular architecture
