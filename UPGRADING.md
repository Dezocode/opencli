# OpenCLI Upgrade Guide

## For Users: Upgrading Your Installation

### Quick Upgrade

```bash
cd ~/opencli
git pull
./upgrade.sh
```

The upgrade tool will:
1. ✅ Detect all changes from git
2. ✅ Show you what's modified/new
3. ✅ Archive your current version
4. ✅ Backup your current installation
5. ✅ Install the new version
6. ✅ Show changelog

### Manual Upgrade

If you prefer manual control:

```bash
cd ~/opencli
git pull

# See what changed
git diff HEAD~1 HEAD

# Run installer
./install.sh
```

### Checking Your Version

```bash
# From command line
cat ~/.opencli/version.json

# From opencli (future feature)
opencli --version
```

### Rollback

If something goes wrong:

```bash
# List backups
ls -la ~/.opencli.backup-*

# Restore from backup (example)
rm -rf ~/.opencli
mv ~/.opencli.backup-20251001-120000 ~/.opencli

# Or use archived version
cd ~/opencli/archive
./install-v1.0.0.sh
```

## For Developers: Creating a New Version

### 1. Make Your Changes

```bash
cd ~/opencli

# Make code changes
vim opencli.py
vim modules/agent_manager.py
# etc...

# Test changes
./install.sh
opencli  # Test it works
```

### 2. Bump Version

```bash
./bump-version.sh
```

This will:
- Prompt for version bump type (major/minor/patch)
- Ask for changelog entries
- Update `version.json`
- Update `install.sh` version comment
- Optionally create git commit + tag

**Version Bump Types:**
- **Major (X.0.0)**: Breaking changes, incompatible API
- **Minor (x.X.0)**: New features, backwards compatible
- **Patch (x.x.X)**: Bug fixes, minor improvements

### 3. Test Installation

```bash
# Clean install test
rm -rf ~/.opencli ~/.opencli.backup-*
./install.sh

# Test functionality
opencli
> /agents
> /status
```

### 4. Commit and Push

```bash
# Review changes
git status
git diff

# Commit (if not already committed by bump-version.sh)
git add .
git commit -m "feat: add new feature"

# Push
git push
git push --tags
```

### 5. Users Upgrade

Users can now upgrade with:

```bash
cd ~/opencli
git pull
./upgrade.sh
```

## Version Bump Workflow

```
1. Developer makes changes
   ↓
2. Run ./bump-version.sh
   ↓
3. Choose: major/minor/patch
   ↓
4. Enter changelog entries
   ↓
5. version.json updated
   ↓
6. install.sh version updated
   ↓
7. Git commit created (optional)
   ↓
8. Git tag created (optional)
   ↓
9. Push to repo
   ↓
10. Users run ./upgrade.sh
    ↓
11. Old version archived
    ↓
12. Backup created
    ↓
13. New version installed
```

## Upgrade Tool Features

### Change Detection

The upgrade tool automatically detects:
- Modified files (git diff)
- New files
- Deleted files
- Changes to modules
- Changes to agent configs
- Documentation updates

### Archiving

Every upgrade archives:
- Previous `install.sh` → `archive/install-vX.Y.Z.sh`
- Previous `version.json` → `archive/version-X.Y.Z.json`
- Maintains `archive/VERSIONS.md` with history

### Backup

Every upgrade creates:
- Timestamped backup: `~/.opencli.backup-YYYYMMDD-HHMMSS`
- Complete copy of your installation
- Preserves API keys, sessions, contexts

## Archive Directory Structure

```
opencli/archive/
├── install-v1.0.0.sh      # Archived installer scripts
├── install-v1.1.0.sh
├── version-1.0.0.json     # Archived version metadata
├── version-1.1.0.json
└── VERSIONS.md            # Archive manifest
```

## Version Metadata

`version.json` contains:
```json
{
  "version": "1.0.0",
  "release_date": "2025-10-01",
  "changelog": [
    {
      "version": "1.0.0",
      "date": "2025-10-01",
      "changes": [
        "Feature description",
        "Bug fix description"
      ],
      "bump_type": "major|minor|patch"
    }
  ]
}
```

## Best Practices

### For Developers

1. **Always test** before bumping version
2. **Write clear changelogs** - users read these
3. **Use semantic versioning** - follow major/minor/patch rules
4. **Tag releases** - makes rollback easier
5. **Document breaking changes** - warn users

### For Users

1. **Backup important sessions** before upgrading
2. **Read changelog** before confirming upgrade
3. **Keep at least one backup** - disk space is cheap
4. **Test after upgrade** - run basic commands
5. **Report issues** - help improve the tool

## Troubleshooting

### Upgrade Failed

```bash
# Restore from backup
ls -la ~/.opencli.backup-*
rm -rf ~/.opencli
mv ~/.opencli.backup-YYYYMMDD-HHMMSS ~/.opencli
```

### Version Mismatch

```bash
# Force reinstall
rm -rf ~/.opencli
./install.sh
```

### Git Issues

```bash
# Reset to clean state
git fetch origin
git reset --hard origin/main
./upgrade.sh
```

### Missing Archive

```bash
# Archives are optional - reinstall directly
git checkout v1.0.0
./install.sh
```

## See Also

- [README.md](README.md) - Main documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [INTEGRATION_STATUS.md](INTEGRATION_STATUS.md) - What's installed
