# OpenCLI Upgrade & Rollback - Quick Reference

## For Users: Upgrading

### Normal Upgrade (Recommended)

```bash
opencli
> /upgrade
```

This will:
1. Check your system is ready
2. Show you what changed
3. Create automatic backup
4. Install new version
5. Verify everything works
6. **Automatically rollback if anything fails**

### Emergency Recovery

**If opencli won't start:**

```bash
opencli --rollback
```

- Works even when CLI is broken
- Pure bash script (no Python needed)
- Restores from last backup
- Saves broken installation for debugging

**If opencli works but has issues:**

```bash
opencli
> /rollback
```

- Lists all backups with versions
- Choose which backup to restore
- Creates safety backup of current state

### Manual Upgrade

```bash
cd ~/opencli
git pull
./upgrade.sh
```

Use when:
- Debugging upgrade issues
- Need manual control
- Automating with scripts

## For Developers: Creating Releases

### 1. Make Changes

```bash
cd ~/opencli
vim opencli.py modules/*.py
# Make your changes
```

### 2. Test Locally

```bash
./install.sh
opencli
# Test your changes
```

### 3. Bump Version

```bash
./bump-version.sh
```

Interactive prompts:
1. Choose bump type (major/minor/patch)
2. Enter changelog entries
3. Confirm changes
4. Optionally create git commit + tag

### 4. Push

```bash
git push
git push --tags
```

### 5. Users Upgrade

Users run:
```bash
opencli
> /upgrade
```

## Quick Commands

| Action | Command |
|--------|---------|
| **Upgrade** | `opencli` → `/upgrade` |
| **Rollback** | `opencli` → `/rollback` |
| **Emergency rollback** | `opencli --rollback` |
| **Bump version** | `./bump-version.sh` |
| **Check version** | `cat ~/.opencli/version.json` |
| **List backups** | `ls -la ~/.opencli.backup-*` |
| **List archives** | `ls ~/opencli/archive/` |

## Verification After Upgrade

Test these after upgrading:

```bash
opencli
> Hello                    # Test basic response
> /agents                  # Test agent system
> /status                  # Check session info
> Read package.json        # Test file operations
> @assistant Test message  # Test agent invocation
```

## Backup Management

### List Backups

```bash
ls -la ~/.opencli.backup-*
```

### Restore Manually

```bash
rm -rf ~/.opencli
mv ~/.opencli.backup-20251001-120000 ~/.opencli
```

### Clean Old Backups

```bash
# Keep only last 3 backups
ls -1dt ~/.opencli.backup-* | tail -n +4 | xargs rm -rf
```

## Archive System

Old versions are preserved:

```
~/opencli/archive/
├── install-v1.0.0.sh    # Can reinstall old version
├── version-1.0.0.json   # Version metadata
└── VERSIONS.md          # Archive history
```

### Restore from Archive

```bash
cd ~/opencli/archive
./install-v1.0.0.sh
```

## Troubleshooting

### Upgrade Failed

```bash
# The system auto-rollsback, but if not:
opencli --rollback
```

### CLI Won't Start

```bash
# Emergency recovery
opencli --rollback

# Or manual restore
rm -rf ~/.opencli
mv ~/.opencli.backup-[latest] ~/.opencli
```

### Git Issues

```bash
cd ~/opencli
git fetch origin
git reset --hard origin/main
opencli
> /upgrade
```

### Complete Reinstall

```bash
# Save your API key
cp ~/.opencli/.secrets ~/opencli-secrets.json

# Reinstall
rm -rf ~/.opencli
cd ~/opencli
./install.sh

# Restore API key
cp ~/opencli-secrets.json ~/.opencli/.secrets
```

## Version Metadata

### Check Current Version

```bash
cat ~/.opencli/version.json
```

### View Changelog

```bash
python3 -c "
import json
with open('$HOME/.opencli/version.json') as f:
    data = json.load(f)
    for entry in data['changelog']:
        print(f\"v{entry['version']} ({entry['date']})\")
        for change in entry['changes']:
            print(f'  • {change}')
        print()
"
```

## Safety Features

✅ **Automatic backups** before every upgrade
✅ **Version archiving** for complete history
✅ **Step verification** during installation
✅ **Auto-rollback** on failure
✅ **Standalone recovery** tool
✅ **Session preservation** during upgrades
✅ **API key preservation** in backups

## Documentation

- **Complete guide**: `archive/VERSION_CONTROL.md`
- **Quick start**: This file
- **Main docs**: `README.md`
- **Upgrade guide**: `UPGRADING.md`

## Need Help?

1. Check logs: `~/.opencli/logs/upgrade.log`
2. Review documentation
3. Try emergency rollback: `opencli --rollback`
4. Report issue with:
   - Current version: `cat ~/.opencli/version.json`
   - Error logs
   - Steps to reproduce
