<div align="center">

```
 ██████╗ ██████╗ ███████╗███╗   ██╗     ██████╗██╗     ██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██╔════╝██║     ██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║     ██║     ██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██║     ██║     ██║
╚██████╔╝██║     ███████╗██║ ╚████║    ╚██████╗███████╗██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝     ╚═════╝╚══════╝╚═╝
```

# OpenCLI

</div>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"/></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+"/></a>
  <a href="https://github.com/Dezocode/opencli/releases"><img src="https://img.shields.io/badge/version-1.4.0-green.svg" alt="Version"/></a>
</p>

<p align="center">
  <strong>A fast, feature-rich terminal interface for OpenRouter API with Claude Code capabilities.</strong>
</p>

<p align="center">
  OpenCLI is an open-source, upgradeable CLI tool that brings powerful AI assistance directly to your terminal. Built with modularity and reliability in mind, it features an intelligent agent system, version control with automatic rollback, and seamless integration with your development workflow.
</p>

---

## Features

### Core Features
- 🚀 **Buffered streaming** - Smooth token display with inline progress indicator (v1.4.0+)
- 🤖 **Smart agent system** - Auto-switching agents based on task type (debug, review, test, etc.)
- 🔧 **Full tool support** - Read, Write, Edit, Bash, Glob, Grep
- 🐙 **GitHub integration** - Manage issues, PRs, workflows via gh CLI
- 💾 **Session management** - Resume and continue conversations
- 📊 **Context optimization** - Smart context compression maintains max throughput
- 🎯 **AGENTS.md support** - Auto-loads project-specific AI instructions
- 🔐 **Secure secrets** - API keys stored with 0o600 permissions
- ⚡ **Slash commands** - Quick access to common operations
- 🔄 **Version control** - Built-in upgrade/rollback system with verification
- 🛡️ **Safe upgrades** - Automatic backups and rollback on failure
- 📦 **Version archiving** - Complete version history preservation

### Advanced TUI Interface (v1.4.0+)
- 🎨 **Modern terminal UI** - Non-blocking interface with Frontier design system
- ✨ **Inline buffer status** - Animated spinner with token count and tips while streaming
- ✍️ **Multi-line input** - Smooth text wrapping with cursor positioning
- 📝 **Single markdown render** - Buffer tokens, render once (eliminates lag)
- ⚡ **Always responsive** - Scroll and type during AI responses
- 📊 **Performance monitor** - Live CPU/memory tracking with `/performance` command
- 🎯 **Enhanced statusline** - Real-time session info, IPC status, and performance metrics
- 🖥️ **Terminal background** - Uses native terminal background (transparent mode)
- 🎭 **Frontier colors** - Professional muted palette throughout

### IPC System
- 🔗 **Claude Code bridge** - Bidirectional communication with Claude Code
- 📡 **Interactive sessions** - Send commands and receive responses via IPC
- 🔄 **Auto-upgrade** - Upgrade OpenCLI from within Claude Code sessions
- 📊 **Status monitoring** - Track IPC read/write operations with visual indicators
- 🛠️ **Background tasks** - Manage multiple background processes and shells

## Installation

### One-Line Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/Dezocode/opencli/Main/install.sh | bash
```

This will:
- Clone the repository to `~/opencli`
- Install all dependencies
- Set up configuration directories
- Configure your API key interactively

📖 **New to OpenCLI?** See **[SETUP.md](SETUP.md)** for complete setup guide including:
- How to get API keys from OpenRouter
- Model selection with `/model` command
- GitHub CLI secure authentication
- Troubleshooting and best practices

### Manual Install

```bash
# Clone the repository
git clone https://github.com/Dezocode/opencli.git ~/opencli
cd ~/opencli

# Run installer
./install.sh
```

The installer will:
- ✅ Create `~/.opencli/` directory structure
- ✅ Install all modules and configurations
- ✅ Copy `opencli` to `~/bin/`
- ✅ Check and install Python dependencies
- ✅ Verify gh CLI installation
- ✅ Guide you through API key setup

### Manual Installation

If you prefer manual installation:

1. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Run the installer**:
   ```bash
   ./install.sh
   ```

3. **Or copy files manually**:
   ```bash
   mkdir -p ~/.opencli/{agents/{configs/custom,contexts,system_prompts,temp},modules,sessions,bashes}
   cp modules/*.py ~/.opencli/modules/
   cp agents/configs/agents.yaml ~/.opencli/agents/configs/
   cp opencli.py ~/bin/opencli
   chmod +x ~/bin/opencli
   ```

4. **Add to PATH** (if not already):
   ```bash
   # Add to ~/.zshrc or ~/.bashrc
   export PATH="$HOME/bin:$PATH"
   alias opencli='~/bin/opencli'
   ```

5. **Configure API key**:
   ```bash
   opencli --setup
   ```

### Prerequisites

- Python 3.7+
- OpenRouter API key ([Get one here](https://openrouter.ai/keys))
- (Optional) gh CLI for GitHub integration ([Install](https://cli.github.com))

## Usage

### Basic Commands

```bash
# Start interactive session
opencli

# One-shot prompt
opencli "What is the meaning of life?"

# Print mode (non-interactive)
opencli -p "Generate a hello world script"

# Continue last session
opencli -c

# Resume specific session
opencli -r <session-id>

# Change model
opencli --model x-ai/grok-4-fast:free
```

### Slash Commands

Inside the interactive session:

- `/model [name]` - View or change model
- `/agent [name]` - Switch to specific agent (debugger, reviewer, tester, etc.)
- `/agents` - List all available agents
- `/status` - Show session info (tokens, messages, etc.)
- `/clear` - Clear conversation history
- `/bashes` - List background tasks
- `/upgrade` - Upgrade to latest version with verification
- `/rollback` - Rollback to previous version
- `/help` - Show help menu
- `exit` or `quit` - Exit the session

### File Operations

OpenCLI has full file operation capabilities through tool calling:

```
> Read the contents of config.json
> Write a new file at ./test.py with a hello world script
> Edit main.py and replace "old_function" with "new_function"
> Find all Python files in this directory
> Search for "TODO" in all files
```

### GitHub Integration

OpenCLI includes GitHub tool integration via `gh` CLI:

```bash
# Check GitHub auth status
> Check my GitHub authentication status

# List issues
> Show me the open issues in this repo

# View pull request
> Show details of PR #42

# Create issue
> Create a GitHub issue titled "Fix login bug" with description "Users can't login"

# List workflows
> Show all GitHub Actions workflows

# View workflow runs
> Show recent workflow runs
```

**Prerequisites:**
- Install `gh` CLI: https://cli.github.com
- Authenticate: `gh auth login`

**Available GitHub actions:**
- `auth_status` - Check authentication
- `repo_view` - View repository info
- `issue_list`, `issue_view`, `issue_create` - Manage issues
- `pr_list`, `pr_view`, `pr_create`, `pr_checkout` - Manage PRs
- `workflow_list`, `workflow_run` - GitHub Actions
- `run_list` - View workflow runs
- `gist_create` - Create gists

### Session Management

Sessions are automatically saved to `~/.opencli/sessions/`:

```bash
# Continue where you left off
opencli -c

# Resume a specific session
opencli -r abc123def
```

## Version Control & Upgrades

OpenCLI includes a comprehensive version management system with safe upgrades and easy rollback.

### Upgrading

**Method 1: `/upgrade` command (Recommended)**

```bash
opencli
> /upgrade
```

Features:
- ✅ Pre-flight checks (git status, dependencies)
- ✅ Change detection and review
- ✅ Automatic backup creation
- ✅ Step-by-step verification
- ✅ Automatic rollback on failure
- ✅ Detailed logging

**Method 2: Legacy script**

```bash
cd ~/opencli
git pull
./upgrade.sh
```

### Emergency Rollback

If OpenCLI is broken and won't start:

```bash
opencli --rollback
```

This standalone recovery tool:
- Works even if main CLI is broken
- No Python dependencies required
- Lists all available backups
- Interactive backup selection
- Preserves broken state as backup

### Version Rollback (within CLI)

If the CLI still works:

```bash
opencli
> /rollback
```

Features:
- Lists all available backups with versions and timestamps
- Shows what will be restored
- Creates safety backup before rollback
- Verifies restored installation

### Creating New Versions (Developers)

```bash
cd ~/opencli

# Make your changes
vim opencli.py modules/*.py

# Bump version
./bump-version.sh

# Choose: major (breaking), minor (features), or patch (fixes)
# Enter changelog entries
# Optionally create git commit + tag

# Push changes
git push && git push --tags
```

### Version Metadata

All version information is tracked in `version.json`:

```json
{
  "version": "1.0.0",
  "release_date": "2025-10-01",
  "changelog": [...]
}
```

### Backups

- Created automatically before every upgrade
- Stored at `~/.opencli.backup-YYYYMMDD-HHMMSS`
- Include complete installation (modules, configs, sessions)
- Never automatically deleted (manual cleanup recommended)

### Archive

Old version installers are archived:

```
~/opencli/archive/
├── install-v1.0.0.sh
├── install-v1.1.0.sh
├── version-1.0.0.json
└── VERSIONS.md
```

**See** `archive/VERSION_CONTROL.md` for complete documentation.

## Configuration

Configuration is stored in `~/.opencli/config.json`:

```json
{
  "model": "x-ai/grok-4-fast:free",
  "baseURL": "https://openrouter.ai/api/v1",
  "maxTurns": 25,
  "contextWindow": 128000
}
```

### API Key Storage

API keys are stored securely in `~/.opencli/.secrets` with 0o600 permissions:

```json
{
  "apiKey": "sk-or-v1-..."
}
```

## Available Models

OpenCLI works with all OpenRouter models. Some popular free options:

- `x-ai/grok-4-fast:free` - Grok 4 Fast (free tier)
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet
- `openai/gpt-4-turbo` - GPT-4 Turbo
- `google/gemini-pro` - Gemini Pro

Full model list: https://openrouter.ai/models

## Agent System

OpenCLI includes a smart agent system that automatically selects specialized agents based on your task.

### Built-in Agents

- **assistant** (default) - General-purpose coding assistant
- **debugger** - Specialized in finding and fixing bugs (triggers: debug, error, bug, fix)
- **reviewer** - Code review and quality analysis (triggers: review, check, analyze, audit)
- **refactor** - Code refactoring and improvement (triggers: refactor, clean, improve)
- **tester** - Writing tests and verification (triggers: test, spec, coverage)
- **documenter** - Documentation and explanations (triggers: document, docs, readme, explain)
- **architect** - System design and architecture (triggers: architecture, design, plan, structure)

### Agent Features

- **Auto-switching**: Agents are automatically selected based on trigger words in your prompt
- **Context optimization**: Each agent has optimized context management for its specialty
- **AGENTS.md support**: Automatically loads project-specific instructions from `AGENTS.md` file
- **Custom configuration**: Define your own agents in `~/.opencli/agents.yaml`

### Using Agents

```bash
# Auto-switch by using trigger words
> debug this function  # Switches to debugger agent

# Manual agent selection
> /agent reviewer
> /agents  # List all available agents

# The agent info is shown in the session header
Session: abc12345 | Model: x-ai/grok-4-fast:free | Agent: debugger
```

### AGENTS.md Support

Create an `AGENTS.md` file in your project root with project-specific instructions:

```markdown
# AGENTS.md

## Setup
- Install: `npm install`
- Test: `npm test`
- Build: `npm run build`

## Code Style
- TypeScript strict mode
- Use functional patterns
- No semicolons

## Architecture
- React + TypeScript
- State management with Zustand
- API calls via tRPC
```

OpenCLI will automatically load this context for all agents.

### Context Optimization

The agent system uses smart context management strategies:

- **Auto compaction**: Keeps system prompt + first messages + recent messages
- **Tool result truncation**: Large file reads are automatically truncated
- **Sliding window**: Some agents use sliding window for maximum recent context
- **Token monitoring**: Real-time tracking ensures you stay within limits

## UI Features

### Input Border
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ > Your prompt here
└──────────────────────────────────────────────────────────────────────────────┘
```

### Status Bar
- **Purple text**: Session ID | Model | Token usage
- **Cyan text**: Current directory
- **Blue text**: Git repo name (if in repo)
- **Gray text**: Git branch (if in repo)

## Troubleshooting

### No API key found
Run `opencli --setup` or set `OPENROUTER_API_KEY` environment variable.

### Module not found
Install dependencies: `pip3 install openai prompt_toolkit pyyaml`

### Permission denied
Make executable: `chmod +x ~/bin/opencli`

## Development

OpenCLI is a single-file Python script (`opencli.py`) for easy distribution and modification.

### Repository Structure

```
opencli/
├── agents/                    # Agent system
│   ├── configs/               # Agent configurations
│   │   ├── agents.yaml        # Built-in agents
│   │   └── custom/            # Custom agent configs
│   ├── contexts/              # Context cache (generated)
│   ├── system_prompts/        # Prompt templates
│   ├── temp/                  # Compiled contexts (generated)
│   └── README.md
├── modules/                   # Python modules
│   ├── agent_manager.py       # Agent orchestration
│   ├── context_builder.py     # Context caching
│   ├── github_tool.py         # GitHub integration
│   ├── simple_tui.py          # Advanced TUI interface
│   ├── streaming_display.py   # Markdown streaming widget
│   ├── multiline_input.py     # Multi-line input with spinner
│   ├── markdown_renderer.py   # Markdown processor
│   ├── ansi_background.py     # Terminal background support
│   └── README.md
├── scripts/                   # Utility scripts
│   ├── claude_code_bridge.py  # Claude Code IPC bridge
│   ├── claude_code_executor.py # Claude Code executor
│   ├── claude_code_interactive.py # Interactive IPC
│   ├── claude_code_persistent.py # Persistent session
│   ├── find_opencli_session.py # Session finder
│   └── send_message_to_opencli.py # Message sender
├── tests/                     # Test files
│   ├── test_async_write.py    # Async write tests
│   ├── test_claude_ipc.py     # IPC tests
│   ├── test_upgrade_via_ipc.py # Upgrade tests
│   └── debug_chat_display.py  # Display debugging
├── opencli.py                 # Main CLI script
├── install.sh                 # Installation script
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── ARCHITECTURE.md            # System architecture docs
└── INTEGRATION_STATUS.md      # Integration details
```

### Installation Structure

After installation, files are located at:

```
~/.opencli/                    # Config directory
├── agents/                    # Agent system (runtime)
│   ├── configs/
│   │   └── agents.yaml
│   ├── contexts/              # Generated cache
│   │   └── agents_md_cache.json
│   └── temp/                  # Compiled contexts (max 5 files)
├── modules/                   # Python modules
│   ├── agent_manager.py
│   ├── context_builder.py
│   └── github_tool.py
├── sessions/                  # Session storage
├── bashes/                    # Background tasks
├── .secrets                   # API key (0o600 permissions)
└── config.json                # Configuration (optional)

~/bin/opencli                  # Executable
```

## 🌟 Open Source & Upgradeability

### Why Open Source?

OpenCLI is **100% open source** under the MIT License. This means:

- ✅ **Free forever** - No hidden costs, subscriptions, or paywalls
- ✅ **Transparent** - Inspect, audit, and understand every line of code
- ✅ **Customizable** - Modify and extend to fit your workflow
- ✅ **Community-driven** - Contributions welcome from everyone
- ✅ **No vendor lock-in** - Your data and configurations stay local

### Built-in Upgrade System

OpenCLI includes a sophisticated version control system:

```bash
/upgrade   # Upgrade to latest version with automatic backup
/rollback  # Rollback to previous version if anything breaks
```

**Safety features:**
- 📦 **Automatic backups** before every upgrade
- 🔍 **Step-by-step verification** during installation
- 🔄 **Instant rollback** if upgrade fails
- 📝 **Complete changelog** for every version
- 🛡️ **Non-destructive** - keeps your settings and sessions

See [UPGRADING.md](UPGRADING.md) for details.

### Version History

Current: **v1.2.1** (2025-10-01)

**Recent updates:**
- v1.2.1: Video support, UI improvements, public release prep
- v1.2.0: Intelligent prompt processing, image path detection
- v1.1.0: Version control system, command permissions
- v1.0.0: Initial release with agent system and context caching

View the full [changelog](version.json) for details.

## 🤝 Contributing

Contributions are welcome! Whether it's:

- 🐛 Bug reports
- 💡 Feature requests
- 📝 Documentation improvements
- 🔧 Code contributions

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

Copyright (c) 2025 dezocode

**You are free to:**
- Use commercially
- Modify and distribute
- Use privately
- Sublicense

**The only requirement:** Include the original license notice.

## Credits

Built with:
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)
- [OpenRouter API](https://openrouter.ai)
- [AGENTS.md](https://agents.md) - Open-source specification for AI coding agent instructions
