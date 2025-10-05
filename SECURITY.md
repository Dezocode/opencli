# OpenCLI Security Measures

## API Key Protection

All API keys are protected through multiple security layers:

### 1. File Permissions (0o600)

All files containing API keys have restrictive permissions:

```bash
.rw-------  .opencli/.secrets       # Owner read/write only
.rw-------  .opencli/config.json    # Owner read/write only
.rw-------  .opencli/models.json    # Owner read/write only
```

**Meaning**: Only the file owner can read or write. No other users on the system can access these files.

### 2. Git Ignore Protection

All sensitive files are excluded from version control:

```gitignore
# From .gitignore
.secrets
*.secret
*.key
config.json
models.json
```

**Protection**: Even if you accidentally run `git add .`, these files will NOT be committed to GitHub.

### 3. Storage Locations

API keys are stored in three protected files:

| File | Purpose | Protection |
|------|---------|-----------|
| `~/.opencli/.secrets` | Multi-provider keys | 0o600 + .gitignore |
| `~/.opencli/models.json` | Primary key storage + model data | 0o600 + .gitignore |
| `~/.opencli/config.json` | Active session config | 0o600 + .gitignore |

**All files** are in `~/.opencli/` (home directory), **NOT** in the git repository.

## Security Verification

Check your security status:

```bash
# Verify file permissions
ls -l ~/.opencli/.secrets ~/.opencli/config.json ~/.opencli/models.json

# Should show: .rw------- (600) for all files

# Verify git protection
git status ~/.opencli/.secrets
# Should show: "not under version control" or similar
```

## Attack Vectors Protected Against

### ✅ GitHub Accidental Push
- **Protected**: All key files in `.gitignore`
- **Even if**: You run `git add .` or `git commit -a`, keys won't be included

### ✅ Local File Access (Other Users)
- **Protected**: 0o600 permissions (owner-only access)
- **Blocked**: Other users on the same machine cannot read your keys

### ✅ Directory Traversal
- **Protected**: All keys stored in `~/.opencli/` (outside git repo)
- **Blocked**: Web servers or applications can't accidentally expose keys via directory listing

### ✅ Log Exposure
- **Protected**: Keys never logged in plaintext
- **Implementation**: Key values not printed to stdout/stderr

## Attack Vectors NOT Protected Against

### ⚠️ Root/Sudo Access
- **Limitation**: Users with root access can read any file
- **Mitigation**: Standard Unix security model limitation

### ⚠️ Malware on Your Machine
- **Limitation**: If your system is compromised, keys can be stolen
- **Mitigation**: Keep your system updated, use antivirus

### ⚠️ Physical Access
- **Limitation**: Someone with physical access to unlocked machine
- **Mitigation**: Lock your screen, use disk encryption

### ⚠️ Memory Dumps
- **Limitation**: Keys exist in memory during runtime
- **Mitigation**: Standard for all applications using API keys

## Best Practices

1. **Never share your `~/.opencli/` directory**
2. **Don't copy API keys to clipboard** (can be logged by clipboard managers)
3. **Rotate keys regularly** on provider dashboards
4. **Use different keys** for different machines
5. **Enable rate limits** on provider dashboards where available
6. **Monitor usage** on provider dashboards to detect unauthorized access

## Key Rotation

If you suspect a key has been compromised:

```bash
# Remove compromised provider key
/providers remove openrouter

# Generate new key on provider dashboard
# Then add new key
/providers add <new-key>
```

## Files You Can Safely Commit

These files are safe to commit to GitHub:

```
✅ opencli.py
✅ modules/*.py
✅ PROVIDERS.md
✅ README.md
✅ .gitignore
```

These files should **NEVER** be committed:

```
❌ ~/.opencli/.secrets
❌ ~/.opencli/config.json
❌ ~/.opencli/models.json
❌ Any file containing API keys
```

## Automatic Protections Applied

When you use `/providers add`:

1. ✅ Key saved with 0o600 permissions
2. ✅ Saved to `.gitignore`'d files only
3. ✅ Never stored in repository
4. ✅ Permissions enforced on every save

## Verification Commands

```bash
# Check if any secrets leaked to git
git log --all --full-history --source --patch -- '*secret*' '*key*' '*.secrets'

# Should return empty if protected correctly

# Check current permissions
stat -f "%OLp" ~/.opencli/.secrets
# Should output: 600

# Check gitignore coverage
git check-ignore ~/.opencli/.secrets
# Should output: /Users/yourname/.opencli/.secrets
```

## Summary

**Yes** - All keys are protected from GitHub pushes ✅
**Yes** - All keys have restrictive file permissions ✅
**Yes** - Protected against common attack vectors ✅
**No** - Cannot protect against root/malware/physical access ⚠️

Your API keys are as secure as standard practice allows for CLI applications.
