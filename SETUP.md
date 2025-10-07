# 🚀 OpenCLI Setup Guide

Complete guide to getting started with OpenCLI - from API keys to model selection.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [API Key Setup](#api-key-setup)
3. [Provider Configuration](#provider-configuration)
4. [Model Selection](#model-selection)
5. [GitHub CLI Setup](#github-cli-setup)
6. [First Run](#first-run)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# Install OpenCLI
curl -fsSL https://raw.githubusercontent.com/Dezocode/opencli/Main/install.sh | bash

# Run setup
opencli
```

The installer will guide you through API key setup. See below for detailed instructions.

---

## API Key Setup

OpenCLI supports **any OpenAI-compatible API provider**. We recommend OpenRouter for access to multiple models.

### Option 1: OpenRouter (Recommended)

**Why OpenRouter?**
- Access to 100+ models (Claude, GPT-4, Llama, etc.)
- Pay-per-use pricing (no subscriptions)
- One API key for all models
- Free tier available

#### Step 1: Get Your API Key

1. **Visit OpenRouter**
   ```
   https://openrouter.ai/
   ```

2. **Sign Up / Log In**
   - Click "Sign In" (top right)
   - Use GitHub, Google, or email

3. **Navigate to API Keys**
   ```
   https://openrouter.ai/keys
   ```
   Or: Dashboard → Settings → API Keys

4. **Create New Key**
   ```
   ┌─────────────────────────────────────────────┐
   │ OpenRouter Dashboard                        │
   ├─────────────────────────────────────────────┤
   │                                             │
   │  API Keys                                   │
   │  ────────────────                           │
   │                                             │
   │  ┌────────────────────────────────────┐    │
   │  │  + Create New Key                  │    │
   │  └────────────────────────────────────┘    │
   │                                             │
   │  Name: OpenCLI Key                         │
   │  Credit Limit: $10 (optional)              │
   │                                             │
   │  [ Create Key ]                             │
   │                                             │
   └─────────────────────────────────────────────┘
   ```

5. **Copy Your Key**
   - Format: `sk-or-v1-...` (starts with `sk-or-v1`)
   - **Save it immediately** - you won't see it again!

6. **Add Credits (Optional)**
   - Go to: https://openrouter.ai/credits
   - Minimum: $5 (lasts a long time)
   - Free tier available for testing

#### Step 2: Configure OpenCLI

**Method A: During Installation**
```bash
# Installer will prompt:
Enter your OpenRouter API key (starts with sk-or-v1-...):
sk-or-v1-1234567890abcdef...

✓ API key saved to ~/.opencli/.secrets
✓ Permissions set to 0600 (secure)
```

**Method B: Manual Setup**
```bash
# Create secrets file
echo "OPENROUTER_API_KEY=sk-or-v1-YOUR-KEY-HERE" > ~/.opencli/.secrets

# Secure it (important!)
chmod 600 ~/.opencli/.secrets

# Verify
ls -la ~/.opencli/.secrets
# Output: -rw------- 1 you staff ... .secrets
```

**Method C: Environment Variable**
```bash
# Add to ~/.zshrc or ~/.bashrc
export OPENROUTER_API_KEY="sk-or-v1-YOUR-KEY-HERE"

# Reload
source ~/.zshrc
```

---

### Option 2: OpenAI Direct

If you have an OpenAI API key:

```bash
# Save to .secrets
echo "OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE" > ~/.opencli/.secrets
chmod 600 ~/.opencli/.secrets
```

**Get OpenAI Key:**
```
https://platform.openai.com/api-keys
```

---

### Option 3: Anthropic Direct

If you have an Anthropic API key:

```bash
# Save to .secrets
echo "ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE" > ~/.opencli/.secrets
chmod 600 ~/.opencli/.secrets
```

**Get Anthropic Key:**
```
https://console.anthropic.com/settings/keys
```

---

### Option 4: DeepSeek

For DeepSeek API access:

```bash
# Save to .secrets
echo "DEEPSEEK_API_KEY=sk-YOUR-KEY-HERE" > ~/.opencli/.secrets
chmod 600 ~/.opencli/.secrets
```

**Get DeepSeek Key:**
```
https://platform.deepseek.com/api_keys
```

See `DEEPSEEK_INTEGRATION_GUIDE.md` for detailed setup.

---

## Provider Configuration

OpenCLI auto-detects providers from your API keys. You can configure the base URL if needed.

### Default Providers

| Provider | Base URL | Key Format |
|----------|----------|------------|
| **OpenRouter** | `https://openrouter.ai/api/v1` | `sk-or-v1-...` |
| **OpenAI** | `https://api.openai.com/v1` | `sk-proj-...` |
| **Anthropic** | `https://api.anthropic.com/v1` | `sk-ant-...` |
| **DeepSeek** | `https://api.deepseek.com` | `sk-...` |

### Custom Provider

Edit `~/.opencli/config.json`:

```json
{
  "api_base_url": "https://your-provider.com/v1",
  "api_key_env": "YOUR_PROVIDER_API_KEY",
  "default_model": "your-model-name"
}
```

---

## Model Selection

OpenCLI provides an interactive model selector with real-time model discovery.

### Using the /model Command

#### Step 1: Launch Model Selector

```bash
# Inside OpenCLI
/model
```

#### Step 2: Interactive Model Selection

```
┌─────────────────────────────────────────────────────────────────┐
│ 🤖 Available Models (OpenRouter)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Popular Models:                                                │
│  ────────────────────────────────────────────────────────────   │
│                                                                 │
│  1. anthropic/claude-3.5-sonnet              💰 $3/$15 per 1M  │
│     Provider: Anthropic                                         │
│     Context: 200K tokens                                        │
│     ★★★★★ Most capable, best for coding                        │
│                                                                 │
│  2. anthropic/claude-3-opus                  💰 $15/$75 per 1M │
│     Provider: Anthropic                                         │
│     Context: 200K tokens                                        │
│     ★★★★★ Most intelligent                                     │
│                                                                 │
│  3. openai/gpt-4-turbo                       💰 $10/$30 per 1M │
│     Provider: OpenAI                                            │
│     Context: 128K tokens                                        │
│     ★★★★☆ Fast, vision support                                 │
│                                                                 │
│  4. google/gemini-pro-1.5                    💰 FREE tier      │
│     Provider: Google                                            │
│     Context: 1M tokens                                          │
│     ★★★★☆ Huge context, free tier                              │
│                                                                 │
│  5. meta-llama/llama-3-70b                   💰 $0.9/$0.9 1M   │
│     Provider: Meta                                              │
│     Context: 8K tokens                                          │
│     ★★★☆☆ Open source, fast                                    │
│                                                                 │
│  Recent Models:                                                 │
│  ────────────────────────────────────────────────────────────   │
│  • anthropic/claude-3.5-sonnet (used 2h ago)                   │
│  • openai/gpt-4-turbo (used yesterday)                          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Enter model number or name (or 'refresh' to update list):      │
└─────────────────────────────────────────────────────────────────┘
```

#### Step 3: Select a Model

**Option A: By Number**
```
> 1

✓ Switched to: anthropic/claude-3.5-sonnet
  Pricing: $3 input / $15 output per 1M tokens
  Context: 200K tokens
```

**Option B: By Name**
```
> claude-3.5-sonnet

✓ Switched to: anthropic/claude-3.5-sonnet
```

**Option C: Refresh List**
```
> refresh

🔄 Fetching latest models from OpenRouter...
✓ Found 127 models
```

#### Step 4: Paid Model Confirmation

For paid models, OpenCLI asks for confirmation:

```
⚠️  This is a PAID model: anthropic/claude-3.5-sonnet

Pricing:
  • Input:  $3.00 per 1M tokens
  • Output: $15.00 per 1M tokens

Estimated cost for typical session:
  • Light use (10K tokens): ~$0.03
  • Medium use (50K tokens): ~$0.15
  • Heavy use (200K tokens): ~$0.60

Continue? [y/N]: y

✓ Model activated
```

### Model Categories

OpenCLI organizes models by use case:

**Coding & Development:**
- `anthropic/claude-3.5-sonnet` - Best for complex coding
- `openai/gpt-4-turbo` - Fast coding with vision
- `deepseek/deepseek-coder` - Specialized for code

**General Intelligence:**
- `anthropic/claude-3-opus` - Most capable reasoning
- `openai/gpt-4` - Excellent general purpose
- `google/gemini-pro-1.5` - Huge context window

**Speed & Efficiency:**
- `anthropic/claude-3-haiku` - Fast, affordable
- `openai/gpt-3.5-turbo` - Very fast, cheap
- `meta-llama/llama-3-70b` - Open source, fast

**Free Tier:**
- `google/gemini-pro-1.5` - Free tier available
- `meta-llama/llama-3-8b` - Free through providers
- Various free models on OpenRouter

### Switching Models Mid-Session

You can switch models anytime:

```bash
# Current conversation
You: Explain async/await in Python

# Switch model
/model
> claude-3-opus

# Continue conversation with new model
You: Now explain generators
```

**Note:** Conversation history is preserved when switching models.

---

## GitHub CLI Setup

OpenCLI integrates with GitHub for issue management, PR creation, and workflow automation.

### Step 1: Install GitHub CLI

**macOS:**
```bash
brew install gh
```

**Linux (Debian/Ubuntu):**
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

**Verify Installation:**
```bash
gh --version
# Output: gh version 2.x.x
```

### Step 2: Secure Authentication

**Recommended: Browser-based OAuth (Most Secure)**

```bash
gh auth login
```

Interactive prompts:
```
? What account do you want to log into?
> GitHub.com

? What is your preferred protocol for Git operations?
> HTTPS

? Authenticate Git with your GitHub credentials?
> Yes

? How would you like to authenticate GitHub CLI?
> Login with a web browser

! First copy your one-time code: XXXX-XXXX
Press Enter to open github.com in your browser...

✓ Authentication complete!
✓ Logged in as YourUsername
```

**Alternative: Personal Access Token**

If browser auth doesn't work:

1. **Generate Token**
   ```
   https://github.com/settings/tokens/new
   ```

2. **Required Scopes:**
   ```
   ✓ repo (Full control of private repositories)
   ✓ workflow (Update GitHub Action workflows)
   ✓ read:org (Read org and team membership)
   ```

3. **Authenticate:**
   ```bash
   gh auth login

   ? How would you like to authenticate?
   > Paste an authentication token

   Paste your token: ghp_YOUR_TOKEN_HERE

   ✓ Authentication complete!
   ```

### Step 3: Verify Authentication

```bash
# Check auth status
gh auth status

# Output:
# github.com
#   ✓ Logged in to github.com as YourUsername
#   ✓ Git operations for github.com configured to use https protocol.
#   ✓ Token: *******************

# Test access
gh repo list --limit 3
```

### Step 4: Configure Git (Optional)

Set up Git signing for commits:

```bash
# Use gh for Git operations
gh auth setup-git

# Configure commit signing
gh config set git_protocol https
```

### Security Best Practices

**Token Security:**
```bash
# NEVER share your token
# NEVER commit tokens to git
# NEVER paste tokens in chat/logs

# Store securely in system keychain
gh auth login  # Uses system keychain automatically

# Verify token is NOT in shell history
unset HISTFILE  # Before pasting tokens
```

**Token Rotation:**
```bash
# Rotate tokens every 90 days
# 1. Generate new token
# 2. Update authentication:
gh auth login --with-token < new-token.txt

# 3. Delete old token on GitHub
```

**Minimal Scopes:**
- Only grant scopes you need
- Use fine-grained tokens when possible
- Review token usage regularly

---

## First Run

After setup, launch OpenCLI:

```bash
opencli
```

### Initial Screen

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ██████╗ ██████╗ ███████╗███╗   ██╗     ██████╗██╗     ██╗     │
│ ██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██╔════╝██║     ██║     │
│ ██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║     ██║     ██║     │
│ ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██║     ██║     ██║     │
│ ╚██████╔╝██║     ███████╗██║ ╚████║    ╚██████╗███████╗██║     │
│  ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝     ╚═════╝╚══════╝╚═╝     │
│                                                                 │
│                          v1.4.0                                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Model: anthropic/claude-3.5-sonnet │ Tokens: 0 │ Turn: 1       │
│ CWD: ~/projects/myapp                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                                                                 │
│                                                                 │
│                                                                 │
│                                                                 │
│                                                                 │
│                                                                 │
│                                                                 │
│                                                                 │
│                                                                 │
│                                                                 │
│                                                                 │
│                                                                 │
│                                                                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ > Type your message...                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Try Your First Command

**Example 1: Simple Question**
```
> What is async/await in Python?

⠋ Synthesizing… (esc to interrupt · 2s · ↓ 89 tokens)
  ⎿  Tip: Press ESC to interrupt long-running responses.
```

**Example 2: Code Analysis**
```
> Read app.py and explain what it does

🔧 Reading file: app.py...
✓ File read complete (245 lines)

⠋ Synthesizing… (esc to interrupt · 1s · ↓ 34 tokens)
  ⎿  Tip: Use /performance to monitor CPU and memory.
```

**Example 3: Check Performance**
```
> /performance

✓ Performance monitoring enabled

⏺ │ CPU: 3.2% → │ MEM: 127MB │ Threads: 8
```

**Example 4: Permission System (Dangerous Operations)**
```
> Write a test script to test.py

Bash Command Permission

Claude wants to execute: Write
File: test.py
Content: #!/bin/bash\necho "test"

▸ Yes, allow this operation
  Yes, and don't ask again for Write
  No, skip this operation (esc)

[Use Up/Down arrows to select, Enter to confirm, ESC to cancel]
```

### Common First Commands

```bash
/help          # Show all commands
/model         # Change AI model
/clear         # Clear conversation history
/session       # Manage sessions
/performance   # Toggle performance monitor
/debug         # Enable debug mode
```

---

## Troubleshooting

### API Key Issues

**Problem: "Invalid API key"**
```bash
# Check secrets file
cat ~/.opencli/.secrets

# Verify format
# OpenRouter: OPENROUTER_API_KEY=sk-or-v1-...
# OpenAI:     OPENAI_API_KEY=sk-proj-...
# Anthropic:  ANTHROPIC_API_KEY=sk-ant-...

# Verify permissions
ls -la ~/.opencli/.secrets
# Should show: -rw------- (600)

# Fix permissions
chmod 600 ~/.opencli/.secrets
```

**Problem: "No API key found"**
```bash
# Check environment
env | grep API_KEY

# Add to .secrets
echo "OPENROUTER_API_KEY=your-key" >> ~/.opencli/.secrets

# Or export
export OPENROUTER_API_KEY="your-key"
```

### Model Selection Issues

**Problem: "Model not found"**
```bash
# Refresh model list
/model
> refresh

# Use full model path
> anthropic/claude-3.5-sonnet

# Check provider
# OpenRouter requires "provider/model" format
# OpenAI Direct uses "model" only
```

**Problem: "Rate limited"**
```bash
# Wait 60 seconds
# Or switch to different model
/model
> claude-3-haiku  # Cheaper, less load
```

### GitHub CLI Issues

**Problem: "gh: command not found"**
```bash
# Install gh
brew install gh  # macOS
# or
sudo apt install gh  # Linux

# Verify
gh --version
```

**Problem: "Authentication failed"**
```bash
# Re-authenticate
gh auth logout
gh auth login

# Check status
gh auth status

# Test access
gh repo list
```

**Problem: "Insufficient permissions"**
```bash
# Token needs more scopes
# 1. Go to: https://github.com/settings/tokens
# 2. Edit token
# 3. Add required scopes:
#    - repo
#    - workflow
#    - read:org
# 4. Regenerate and update
gh auth login --with-token < new-token.txt
```

### Performance Issues

**Problem: High CPU usage**
```bash
# Check performance monitor
/performance

# Should show:
# ⏺ │ CPU: <5% → │ MEM: ~130MB │ Threads: 6-10

# If high:
# 1. Restart OpenCLI
# 2. Check background processes
# 3. Update to v1.4.0+
```

**Problem: Slow streaming**
```bash
# Check token rate in performance monitor
# ⏺ │ Speed: 15.3 tok/s  # Good
# ⏺ │ Speed: 2.1 tok/s   # Slow - check connection

# Test network
ping openrouter.ai

# Try different model
/model
> claude-3-haiku  # Faster model
```

### Session Issues

**Problem: "Session not found"**
```bash
# List sessions
/session list

# Create new session
/session new my-session

# Resume session
/session resume my-session
```

**Problem: "Out of memory"**
```bash
# Clear old sessions
/session clear

# Reduce context
/clear

# Use model with smaller context window
/model
> claude-3-haiku  # 200K context
```

---

## Getting Help

### In-App Help

```bash
/help           # Show all commands
/help model     # Help for specific command
/debug          # Enable debug output
```

### Documentation

- **README.md** - Overview and features
- **CHANGELOG.md** - Version history
- **ARCHITECTURE.md** - Technical details
- **DEEPSEEK_INTEGRATION_GUIDE.md** - DeepSeek setup
- **PROVIDERS.md** - Supported providers

### Community

- **GitHub Issues**: https://github.com/Dezocode/opencli/issues
- **Discussions**: https://github.com/Dezocode/opencli/discussions
- **Contributing**: See CONTRIBUTING.md

### Debug Mode

Enable detailed logging:

```bash
# Inside OpenCLI
/debug

# Or start with debug flag
opencli --debug

# Debug output shows:
# 🐛 API Request: POST /chat/completions
# 🐛 Model: anthropic/claude-3.5-sonnet
# 🐛 Tokens: 1234 input, 567 output
# 🐛 Response time: 2.3s
```

---

## Next Steps

After setup, explore advanced features:

1. **Agent System**
   ```bash
   # Auto-loads project-specific AI instructions
   # Create AGENTS.md in your project
   ```

2. **Session Management**
   ```bash
   /session list         # View all sessions
   /session resume work  # Continue previous work
   ```

3. **Tool Usage**
   ```bash
   # OpenCLI can read, write, and edit files
   # Execute bash commands
   # Search with grep and glob
   ```

4. **GitHub Integration**
   ```bash
   # Create issues, PRs, manage workflows
   # All through natural language
   ```

5. **Performance Tuning**
   ```bash
   /performance  # Monitor resource usage
   # Adjust model selection for cost/speed
   ```

---

## Security Checklist

Before production use:

- [ ] API keys stored in `~/.opencli/.secrets` with 0600 permissions
- [ ] `.secrets` file added to `.gitignore`
- [ ] GitHub token has minimal required scopes
- [ ] Token rotation schedule set (90 days)
- [ ] No tokens in shell history or logs
- [ ] OpenCLI updated to latest version (v1.4.0+)
- [ ] Backup of important sessions created

---

## Quick Reference

### Essential Commands

| Command | Description |
|---------|-------------|
| `/model` | Select AI model |
| `/help` | Show help |
| `/clear` | Clear conversation |
| `/session` | Manage sessions |
| `/performance` | Monitor performance |
| `/debug` | Toggle debug mode |

### Key Files

| File | Purpose |
|------|---------|
| `~/.opencli/.secrets` | API keys (0600 permissions) |
| `~/.opencli/config.json` | Configuration |
| `~/.opencli/sessions/` | Session history |
| `~/.opencli/models.json` | Model cache |

### API Key Formats

| Provider | Format | Example |
|----------|--------|---------|
| OpenRouter | `sk-or-v1-...` | `sk-or-v1-abc123...` |
| OpenAI | `sk-proj-...` | `sk-proj-xyz789...` |
| Anthropic | `sk-ant-...` | `sk-ant-def456...` |
| DeepSeek | `sk-...` | `sk-ghi789...` |

---

**Ready to start?** Run `opencli` and enjoy AI-powered development! 🚀
