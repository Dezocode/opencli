# OpenCLI Version Control System - Complete Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Version Management](#version-management)
4. [Upgrade Process](#upgrade-process)
5. [Rollback System](#rollback-system)
6. [Verification & Testing](#verification--testing)
7. [Recovery Procedures](#recovery-procedures)
8. [Advanced Usage](#advanced-usage)

---

## System Overview

OpenCLI uses a comprehensive version control system that provides:

- **Semantic Versioning**: major.minor.patch (e.g., 1.2.3)
- **Git Integration**: Change detection via diff analysis
- **Automated Archiving**: Every version preserved in `archive/`
- **Timestamped Backups**: Complete installation snapshots
- **Rollback Capability**: Restore any previous version
- **Standalone Recovery**: Rollback works even if main CLI fails
- **Step Verification**: Each upgrade stage validated
- **End-to-End Testing**: Full integration checks

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `version.json` | Version metadata & changelog | `~/opencli/version.json` |
| `bump-version.sh` | Version bumping tool | `~/opencli/bump-version.sh` |
| `upgrade.sh` | Legacy upgrade script | `~/opencli/upgrade.sh` |
| `/upgrade` command | Smart CLI upgrade with verification | Built into opencli |
| `/rollback` command | Version restoration | Built into opencli |
| `opencli --rollback` | Emergency rollback flag | Main entry point |
| `archive/` | Archived installers & docs | `~/opencli/archive/` |
| Backups | Timestamped snapshots | `~/.opencli.backup-*` |

---

## Architecture

### Version Metadata Structure

```json
{
  "version": "1.2.3",
  "release_date": "2025-10-01",
  "changelog": [
    {
      "version": "1.2.3",
      "date": "2025-10-01",
      "changes": [
        "Feature: Added new capability",
        "Fix: Resolved issue with X",
        "Enhancement: Improved Y performance"
      ],
      "bump_type": "minor",
      "verification_steps": [
        "Test agent loading",
        "Verify API connectivity",
        "Check context caching"
      ]
    }
  ]
}
```

### Directory Structure

```
opencli/
├── archive/                       # Version control archive
│   ├── VERSION_CONTROL.md        # This documentation
│   ├── VERSIONS.md               # Archive manifest
│   ├── install-v1.0.0.sh         # Archived installers
│   ├── install-v1.1.0.sh
│   ├── version-1.0.0.json        # Archived metadata
│   └── version-1.1.0.json
├── modules/
│   ├── upgrade_manager.py        # Upgrade orchestration
│   └── rollback_manager.py       # Rollback system
├── version.json                  # Current version
├── bump-version.sh               # Version bumping
├── upgrade.sh                    # Legacy upgrader
└── opencli.py                    # Main entry with --rollback

~/.opencli/                        # Installation directory
├── version.json                  # Installed version
├── modules/                      # Core modules
├── agents/                       # Agent configs
└── sessions/                     # User sessions

~/.opencli.backup-YYYYMMDD-HHMMSS  # Timestamped backups
├── version.json                  # Backup metadata
├── modules/
├── agents/
└── sessions/
```

### Version Flow Diagram

```
┌─────────────────┐
│ Developer       │
│ Makes Changes   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ./bump-version  │
│ (Interactive)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ version.json    │
│ Updated         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Git Commit +    │
│ Tag Created     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Push to Repo    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User: git pull  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ /upgrade        │
│ Command         │
└────────┬────────┘
         │
         ├─────────────────────┐
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ Git Diff        │   │ Backup Created  │
│ Analysis        │   │ (Timestamped)   │
└────────┬────────┘   └────────┬────────┘
         │                     │
         │                     ▼
         │            ┌─────────────────┐
         │            │ Archive Old     │
         │            │ Version         │
         │            └────────┬────────┘
         │                     │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────┐
         │ Install New     │
         │ Version         │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Verification    │
         │ Tests           │
         └────────┬────────┘
                  │
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
┌─────────────┐   ┌─────────────┐
│ Success!    │   │ Rollback    │
│ Complete    │   │ Triggered   │
└─────────────┘   └─────────────┘
```

---

## Version Management

### Creating a New Version

#### 1. Make Your Changes

```bash
cd ~/opencli

# Edit files
vim opencli.py
vim modules/agent_manager.py

# Test locally
./install.sh
opencli
```

#### 2. Bump Version

```bash
./bump-version.sh
```

**Interactive Prompts:**

1. **Choose bump type:**
   - `1` = Major (breaking changes): 1.0.0 → 2.0.0
   - `2` = Minor (new features): 1.0.0 → 1.1.0
   - `3` = Patch (bug fixes): 1.0.0 → 1.0.1
   - `4` = Custom (manual entry)

2. **Enter changelog entries:**
   ```
   Enter changelog entries (one per line, empty line to finish):
   Added new context caching system
   Fixed bug in agent loading
   Improved API error handling
   [press Enter]
   ```

3. **Confirm:**
   ```
   Preview:
   Version: 1.0.0 → 1.1.0
   Changelog:
     • Added new context caching system
     • Fixed bug in agent loading
     • Improved API error handling

   Confirm version bump? (y/n)
   ```

4. **Git operations:**
   ```
   Create git commit? (y/n) y
   Create git tag v1.1.0? (y/n) y
   ```

#### 3. Push Changes

```bash
git push
git push --tags
```

### Version Metadata

The `version.json` file tracks:

- **Current version number**: Semantic versioning format
- **Release date**: ISO format (YYYY-MM-DD)
- **Changelog history**: All previous versions
- **Bump type**: major/minor/patch indicator
- **Verification steps**: Testing checklist (optional)

**Best Practices:**

1. **Write clear changelog entries**: Users read these
2. **Use semantic versioning correctly**:
   - Major: Breaking changes, API incompatibility
   - Minor: New features, backwards compatible
   - Patch: Bug fixes, minor improvements
3. **Test before bumping**: Run full test suite
4. **Document breaking changes**: Warn users explicitly
5. **Tag releases**: Makes git history cleaner

---

## Upgrade Process

### Method 1: `/upgrade` Command (Recommended)

The `/upgrade` command provides intelligent, step-verified upgrades:

```bash
opencli
> /upgrade
```

**Features:**

- ✅ **Pre-flight checks**: Verifies git status, detects changes
- ✅ **Interactive confirmation**: Shows what will change
- ✅ **Automatic backup**: Creates timestamped snapshot
- ✅ **Version archiving**: Preserves old installer
- ✅ **Step verification**: Validates each stage
- ✅ **Integration testing**: Checks all features
- ✅ **Automatic rollback**: Reverts on failure
- ✅ **Detailed logging**: Records every action
- ✅ **Progress tracking**: Shows upgrade status

#### Upgrade Steps (Internal Process)

1. **Pre-Flight Checks**
   - Verify git repository exists
   - Check for uncommitted changes
   - Detect remote updates available
   - Validate current installation

2. **Change Detection**
   - Run `git diff` to analyze changes
   - Categorize changes by file type:
     - Core modules (opencli.py, modules/)
     - Agent configurations (agents/)
     - Documentation (*.md)
     - Installation scripts

3. **User Confirmation**
   - Display change summary
   - Show new version number
   - Show changelog entries
   - Request permission to proceed

4. **Backup Creation**
   - Create timestamped backup: `~/.opencli.backup-YYYYMMDD-HHMMSS`
   - Copy entire installation directory
   - Preserve sessions, contexts, API keys
   - Verify backup integrity

5. **Version Archiving**
   - Archive current installer: `archive/install-vX.Y.Z.sh`
   - Archive current metadata: `archive/version-X.Y.Z.json`
   - Update `archive/VERSIONS.md` manifest
   - Set executable permissions

6. **Installation**
   - Run new `install.sh`
   - Copy updated modules
   - Update agent configurations
   - Install version metadata

7. **Step Verification**
   - ✓ Check file integrity
   - ✓ Verify module imports
   - ✓ Test API connectivity
   - ✓ Validate agent loading
   - ✓ Check context system
   - ✓ Verify GitHub integration

8. **Integration Testing**
   - Test agent invocation
   - Test context caching
   - Test session management
   - Test all slash commands
   - Test API calls

9. **Completion or Rollback**
   - If all tests pass: Success message
   - If any test fails: Automatic rollback

### Method 2: Legacy `upgrade.sh` Script

For manual control or troubleshooting:

```bash
cd ~/opencli
git pull
./upgrade.sh
```

**When to use:**

- Debugging upgrade issues
- Custom upgrade workflows
- CI/CD automation
- Testing upgrade logic

---

## Rollback System

### Overview

OpenCLI's rollback system is **completely independent** of the main CLI. It works even if:

- The main `opencli` command fails
- Python dependencies are broken
- Modules fail to import
- API keys are corrupted
- Installation is corrupted

### Method 1: `/rollback` Command (Within CLI)

If the CLI is still functional:

```bash
opencli
> /rollback
```

**Interactive Process:**

```
🔄 OpenCLI Rollback System

Available backups:
  1. v1.1.0 (2025-10-01 14:30:00) - 10 minutes ago
  2. v1.0.0 (2025-09-30 09:15:00) - 1 day ago
  3. v0.9.0 (2025-09-25 16:45:00) - 6 days ago

Select backup to restore (1-3): 1

You are about to rollback to:
  Version: 1.1.0
  Date: 2025-10-01 14:30:00
  Current version: 1.2.0

⚠️  This will:
  • Replace all files in ~/.opencli
  • Restore previous modules
  • Restore previous agent configs
  • Keep current sessions (safe)

Continue? (y/n): y

[Creating safety backup of current state...]
[Restoring from backup...]
[Verifying installation...]

✅ Rollback complete!

Restored version: 1.1.0
Previous version archived at: ~/.opencli.backup-20251001-143000

Please restart opencli to use the restored version.
```

### Method 2: Emergency `--rollback` Flag (Standalone)

If the CLI is broken and won't start:

```bash
opencli --rollback
```

**Standalone Recovery Process:**

```bash
#!/bin/bash
# This is a STANDALONE rollback - no Python dependencies required

🚨 EMERGENCY ROLLBACK MODE

The main OpenCLI system is not functioning.
This recovery tool will restore from your last backup.

Detecting backups...

Found backups:
  1. ~/.opencli.backup-20251001-143000 (10 minutes ago)
  2. ~/.opencli.backup-20250930-091500 (1 day ago)
  3. ~/.opencli.backup-20250925-164500 (6 days ago)

Select backup to restore (1-3, or 'q' to quit): 1

⚠️  WARNING: This will replace your entire ~/.opencli installation

Current state will be backed up to: ~/.opencli.broken-20251001-144500

Continue? (y/n): y

[Backing up broken installation...]
[Restoring from backup...]
[Setting permissions...]
[Verifying basic structure...]

✅ Emergency rollback complete!

Try running: opencli

If issues persist, you can restore from an older backup by running:
  opencli --rollback
```

**Key Features:**

- **Pure Bash**: No Python, no dependencies
- **No CLI required**: Works even if opencli won't start
- **Safety backup**: Backs up broken state before rollback
- **Multiple backups**: Choose from any available backup
- **Verification**: Checks restored installation
- **Preserves sessions**: User data kept safe

### Method 3: Manual Rollback

Ultimate fallback for complete disaster recovery:

```bash
# List available backups
ls -la ~/.opencli.backup-*

# Restore manually
rm -rf ~/.opencli
mv ~/.opencli.backup-20251001-143000 ~/.opencli

# Or restore from archived installer
cd ~/opencli/archive
chmod +x install-v1.0.0.sh
./install-v1.0.0.sh
```

### Backup Management

#### Listing Backups

```bash
# List all backups with details
ls -lah ~/.opencli.backup-*

# Check backup version
cat ~/.opencli.backup-YYYYMMDD-HHMMSS/version.json
```

#### Cleaning Old Backups

```bash
# Keep only last 3 backups
ls -1dt ~/.opencli.backup-* | tail -n +4 | xargs rm -rf

# Remove specific backup
rm -rf ~/.opencli.backup-20250925-164500
```

#### Backup Storage

**Default behavior:**

- Backups are created before every upgrade
- No automatic cleanup
- Users manage their own backup retention

**Recommendations:**

- Keep at least 3 recent backups
- Keep backups before major version changes
- Clean backups older than 30 days

---

## Verification & Testing

### Automated Verification Steps

The `/upgrade` command runs these verification tests automatically:

#### 1. File Integrity Checks

```python
✓ opencli.py exists and is executable
✓ modules/ directory contains all required modules
✓ agents/configs/agents.yaml is valid YAML
✓ version.json has correct structure
```

#### 2. Module Import Tests

```python
✓ agent_manager imports successfully
✓ context_builder imports successfully
✓ github_tool imports successfully
✓ upgrade_manager imports successfully
✓ rollback_manager imports successfully
```

#### 3. API Connectivity Tests

```python
✓ .secrets file exists
✓ API key is valid format
✓ OpenRouter endpoint is reachable
✓ Test API call succeeds
```

#### 4. Agent System Tests

```python
✓ Agent configs load successfully
✓ All 7 default agents present
✓ Custom agents load correctly
✓ Agent context compilation works
```

#### 5. Context System Tests

```python
✓ Context cache directory exists
✓ AGENTS.md cache is accessible
✓ Context compilation succeeds
✓ 5-file cleanup works correctly
```

#### 6. GitHub Integration Tests

```python
✓ gh CLI is installed
✓ gh is authenticated
✓ GitHub API test succeeds
```

#### 7. Session System Tests

```python
✓ sessions/ directory exists
✓ Session files are readable
✓ Session data structure valid
```

### Manual Testing Procedures

After an upgrade, users should verify:

#### Basic Functionality Test

```bash
opencli
> Hello
[Verify: AI responds correctly]

> /agents
[Verify: All agents listed]

> @assistant What's the current version?
[Verify: Agent responds with correct version]

> /status
[Verify: Status shows correct info]

> /exit
```

#### Agent System Test

```bash
opencli
> @debugger Help me debug this code
[Verify: Debugger agent activates]

> @reviewer Review this function
[Verify: Reviewer agent activates]

> /agents
[Verify: All custom agents appear]
```

#### Context Caching Test

```bash
# First run - should compile context
opencli
> @assistant Test context caching
[Observe: Slight delay on first message]

# Second run - should use cache
> @assistant Test again
[Observe: Instant response]

# Check cache files
ls -la ~/.opencli/agents/temp/
[Verify: Only 5 most recent context files]
```

#### GitHub Integration Test

```bash
opencli
> /github status
[Verify: Shows authentication status]

> /github issues list
[Verify: Lists issues or shows appropriate error]
```

### Verification in Agent Prompt

When agents are invoked after an upgrade, they receive guidance:

```
🔄 OpenCLI v1.2.0 (Upgraded from v1.1.0)

Recent Changes:
  • Added new context caching system
  • Fixed bug in agent loading
  • Improved API error handling

Verification Checklist:
  ☐ Test agent invocation with @assistant
  ☐ Verify context caching is working
  ☐ Check session persistence
  ☐ Test GitHub integration if used

If you encounter issues:
  • Use /rollback to restore previous version
  • Check ~/opencli/archive/ for old installers
  • Report bugs at: [your repo URL]

Type "I verify" to acknowledge, or ask me to help test.
```

This helps users:
- Understand what changed
- Know what to test
- Get immediate help if needed
- Access rollback if problems occur

---

## Recovery Procedures

### Scenario 1: Upgrade Failed Mid-Installation

**Symptoms:**

- Installation script crashed
- Some files updated, others not
- CLI won't start

**Recovery:**

```bash
# Method A: Use emergency rollback
opencli --rollback

# Method B: Manual restore
rm -rf ~/.opencli
mv ~/.opencli.backup-[latest] ~/.opencli
```

### Scenario 2: Upgrade Succeeded But CLI Broken

**Symptoms:**

- Upgrade completed successfully
- CLI starts but crashes
- Missing features or errors

**Recovery:**

```bash
# If CLI partially works
opencli
> /rollback

# If CLI won't start at all
opencli --rollback

# If rollback also broken
cd ~/opencli/archive
./install-v[previous].sh
```

### Scenario 3: Corrupted Installation

**Symptoms:**

- CLI won't start
- Module import errors
- Python exceptions

**Recovery:**

```bash
# Try emergency rollback first
opencli --rollback

# If that fails, fresh install from archive
rm -rf ~/.opencli
cd ~/opencli/archive
./install-v[latest-working].sh

# If archive broken, use backup directly
rm -rf ~/.opencli
cp -r ~/.opencli.backup-[latest-working] ~/.opencli
```

### Scenario 4: Lost API Key

**Symptoms:**

- API calls fail
- "No API key" errors

**Recovery:**

```bash
# API keys are preserved in backups
# Restore just the secrets file
cp ~/.opencli.backup-[latest]/.secrets ~/.opencli/

# Or reconfigure
opencli --setup
```

### Scenario 5: Corrupted Sessions

**Symptoms:**

- Session loading fails
- Context errors

**Recovery:**

```bash
# Sessions are preserved in backups
# Restore specific session
cp ~/.opencli.backup-[latest]/sessions/[session-id].json \
   ~/.opencli/sessions/

# Or clear all sessions (safe)
rm ~/.opencli/sessions/*.json
```

### Scenario 6: Git Repository Issues

**Symptoms:**

- `git pull` fails
- Merge conflicts
- Detached HEAD state

**Recovery:**

```bash
cd ~/opencli

# Method A: Hard reset
git fetch origin
git reset --hard origin/main

# Method B: Re-clone
cd ~
mv opencli opencli.old
git clone [repo-url] opencli
cd opencli
./install.sh
```

### Scenario 7: Complete System Failure

**Symptoms:**

- Nothing works
- All recovery methods fail

**Nuclear Option:**

```bash
# 1. Save your API key
cp ~/.opencli/.secrets ~/opencli-secrets-backup.json

# 2. Save your sessions (optional)
cp -r ~/.opencli/sessions ~/opencli-sessions-backup

# 3. Complete reinstall
rm -rf ~/.opencli
rm -rf ~/opencli
git clone [repo-url] ~/opencli
cd ~/opencli
./install.sh

# 4. Restore secrets
cp ~/opencli-secrets-backup.json ~/.opencli/.secrets

# 5. Restore sessions (optional)
cp -r ~/opencli-sessions-backup/* ~/.opencli/sessions/
```

---

## Advanced Usage

### Custom Verification Steps

Add custom verification steps to `version.json`:

```json
{
  "version": "1.2.0",
  "changelog": [
    {
      "version": "1.2.0",
      "verification_steps": [
        "Test new feature X",
        "Verify performance improvement in Y",
        "Check backwards compatibility with Z"
      ]
    }
  ]
}
```

### Automated Rollback on Failure

Configure automatic rollback if verification fails:

```python
# In upgrade_manager.py
config = {
    "auto_rollback_on_failure": True,
    "verification_timeout": 300,  # 5 minutes
    "max_retry_attempts": 3
}
```

### Upgrade Hooks

Run custom scripts before/after upgrades:

```bash
# Create hooks in ~/.opencli/hooks/
~/.opencli/hooks/pre-upgrade.sh
~/.opencli/hooks/post-upgrade.sh
~/.opencli/hooks/pre-rollback.sh
~/.opencli/hooks/post-rollback.sh
```

### Selective Upgrades

Upgrade only specific components:

```bash
opencli
> /upgrade --modules-only
> /upgrade --agents-only
> /upgrade --docs-only
```

### Dry-Run Mode

Preview upgrade without applying:

```bash
opencli
> /upgrade --dry-run
```

Shows:
- What files would change
- What verification steps would run
- Estimated downtime

### Version Pinning

Pin to specific version in `~/.opencli/config.json`:

```json
{
  "version_pin": "1.1.0",
  "auto_upgrade": false
}
```

### Backup Rotation Policy

Configure automated backup cleanup:

```json
{
  "backup_retention": {
    "keep_latest": 5,
    "keep_major_versions": true,
    "max_age_days": 30
  }
}
```

### Upgrade Notifications

Enable upgrade availability notifications:

```bash
opencli
> /settings upgrade-notifications on
```

Shows notification on startup if new version available.

---

## Troubleshooting

### Common Issues

#### Issue: "No backups found"

**Cause:** First installation, no upgrades yet

**Solution:**
```bash
# Manually create backup
cp -r ~/.opencli ~/.opencli.backup-$(date +%Y%m%d-%H%M%S)
```

#### Issue: "Git diff failed"

**Cause:** Not in git repository, or git not installed

**Solution:**
```bash
# Ensure in repo
cd ~/opencli
git status

# Or install git
# macOS: xcode-select --install
# Linux: sudo apt install git
```

#### Issue: "Permission denied" during upgrade

**Cause:** File permissions incorrect

**Solution:**
```bash
chmod +x ~/bin/opencli
chmod +x ~/opencli/*.sh
chmod -R u+w ~/.opencli
```

#### Issue: "Module import failed" after upgrade

**Cause:** Incomplete installation

**Solution:**
```bash
# Rollback and retry
opencli --rollback
cd ~/opencli
git pull
./install.sh
```

### Debug Mode

Enable detailed logging:

```bash
opencli --debug
> /upgrade
```

Logs to: `~/.opencli/logs/upgrade.log`

### Support

If issues persist:

1. Check logs: `~/.opencli/logs/`
2. Verify installation: `opencli --verify`
3. Review documentation: `~/opencli/archive/VERSION_CONTROL.md`
4. Report issue with:
   - Current version: `cat ~/.opencli/version.json`
   - Error logs
   - Steps to reproduce

---

## Quick Reference

### Commands

| Command | Purpose |
|---------|---------|
| `./bump-version.sh` | Create new version |
| `opencli` → `/upgrade` | Smart upgrade with verification |
| `./upgrade.sh` | Legacy upgrade script |
| `opencli` → `/rollback` | Rollback to previous version |
| `opencli --rollback` | Emergency standalone rollback |
| `opencli --verify` | Run verification tests |

### Files

| File | Purpose |
|------|---------|
| `version.json` | Current version metadata |
| `archive/install-v*.sh` | Archived installers |
| `archive/VERSION_CONTROL.md` | This documentation |
| `~/.opencli.backup-*` | Timestamped backups |

### Verification

| Test | Command |
|------|---------|
| Check version | `cat ~/.opencli/version.json` |
| List backups | `ls -la ~/.opencli.backup-*` |
| Test agents | `opencli` → `/agents` |
| Test API | `opencli` → `Hello` |

---

**Last Updated:** 2025-10-01
**Version:** 1.0.0
**Maintainer:** OpenCLI Project
