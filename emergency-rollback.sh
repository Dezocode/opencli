#!/bin/bash
# OpenCLI Emergency Rollback - Standalone Recovery Tool
# This script works independently of the main CLI
# Use when opencli command is broken or won't start

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${RED}🚨 EMERGENCY ROLLBACK MODE${NC}"
echo ""
echo "The main OpenCLI system is not functioning."
echo "This recovery tool will restore from your last backup."
echo ""

# Detect backups
INSTALL_DIR="$HOME/.opencli"
BACKUPS=($(ls -1dt "$HOME"/.opencli.backup-* 2>/dev/null))

if [ ${#BACKUPS[@]} -eq 0 ]; then
    echo -e "${RED}❌ No backups found${NC}"
    echo ""
    echo "Cannot perform rollback without backups."
    echo "Your installation may be unrecoverable."
    echo ""
    echo "Try manual recovery:"
    echo "  1. Check ~/opencli/archive/ for old installers"
    echo "  2. Run: cd ~/opencli/archive && ./install-v[version].sh"
    echo ""
    exit 1
fi

echo -e "${BLUE}Found backups:${NC}"
echo ""

# List backups
for i in "${!BACKUPS[@]}"; do
    backup="${BACKUPS[$i]}"
    backup_name=$(basename "$backup")
    timestamp=$(echo "$backup_name" | sed 's/.opencli.backup-//')

    # Get version from backup
    version="unknown"
    if [ -f "$backup/version.json" ]; then
        version=$(python3 -c "import json; print(json.load(open('$backup/version.json'))['version'])" 2>/dev/null || echo "unknown")
    fi

    # Calculate age
    backup_date=$(echo "$timestamp" | cut -d'-' -f1)
    backup_time=$(echo "$timestamp" | cut -d'-' -f2)

    formatted_date="${backup_date:0:4}-${backup_date:4:2}-${backup_date:6:2}"
    formatted_time="${backup_time:0:2}:${backup_time:2:2}:${backup_time:4:2}"

    # Calculate time difference
    backup_epoch=$(date -j -f "%Y-%m-%d %H:%M:%S" "$formatted_date $formatted_time" "+%s" 2>/dev/null || echo "0")
    now_epoch=$(date "+%s")
    diff_seconds=$((now_epoch - backup_epoch))

    if [ $diff_seconds -lt 3600 ]; then
        minutes=$((diff_seconds / 60))
        age="${minutes} minute(s) ago"
    elif [ $diff_seconds -lt 86400 ]; then
        hours=$((diff_seconds / 3600))
        age="${hours} hour(s) ago"
    else
        days=$((diff_seconds / 86400))
        age="${days} day(s) ago"
    fi

    echo "  $((i+1)). v${version} (${formatted_date} ${formatted_time}) - ${age}"
done

echo ""
echo -n "Select backup to restore (1-${#BACKUPS[@]}, or 'q' to quit): "
read -r CHOICE

if [ "$CHOICE" = "q" ] || [ "$CHOICE" = "Q" ]; then
    echo "Cancelled."
    exit 0
fi

# Validate choice
if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt ${#BACKUPS[@]} ]; then
    echo -e "${RED}Invalid choice${NC}"
    exit 1
fi

SELECTED_BACKUP="${BACKUPS[$((CHOICE-1))]}"

echo ""
echo -e "${YELLOW}⚠️  WARNING: This will replace your entire ~/.opencli installation${NC}"
echo ""
echo "Selected backup: $(basename "$SELECTED_BACKUP")"
echo ""

# Get current version if possible
CURRENT_VERSION="unknown"
if [ -f "$INSTALL_DIR/version.json" ]; then
    CURRENT_VERSION=$(python3 -c "import json; print(json.load(open('$INSTALL_DIR/version.json'))['version'])" 2>/dev/null || echo "unknown")
fi

# Get backup version
BACKUP_VERSION="unknown"
if [ -f "$SELECTED_BACKUP/version.json" ]; then
    BACKUP_VERSION=$(python3 -c "import json; print(json.load(open('$SELECTED_BACKUP/version.json'))['version'])" 2>/dev/null || echo "unknown")
fi

echo "Current version: v${CURRENT_VERSION}"
echo "Backup version: v${BACKUP_VERSION}"
echo ""

# Create safety backup of broken state
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SAFETY_BACKUP="$HOME/.opencli.broken-$TIMESTAMP"

echo "Current state will be backed up to: $SAFETY_BACKUP"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}Starting emergency rollback...${NC}"
echo ""

# Step 1: Backup broken installation
echo -n "Backing up broken installation... "
if [ -d "$INSTALL_DIR" ]; then
    cp -r "$INSTALL_DIR" "$SAFETY_BACKUP"
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ No installation to backup${NC}"
fi

# Step 2: Remove current installation
echo -n "Removing current installation... "
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ Already removed${NC}"
fi

# Step 3: Restore from backup
echo -n "Restoring from backup... "
cp -r "$SELECTED_BACKUP" "$INSTALL_DIR"
echo -e "${GREEN}✓${NC}"

# Step 4: Set permissions
echo -n "Setting permissions... "
chmod -R u+w "$INSTALL_DIR"
chmod +x "$HOME/bin/opencli" 2>/dev/null || true
echo -e "${GREEN}✓${NC}"

# Step 5: Verify basic structure
echo -n "Verifying installation... "
VERIFY_FAILED=false

if [ ! -d "$INSTALL_DIR/modules" ]; then
    echo -e "${RED}✗${NC}"
    echo "  ❌ modules/ directory missing"
    VERIFY_FAILED=true
fi

if [ ! -d "$INSTALL_DIR/agents" ]; then
    echo -e "${RED}✗${NC}"
    echo "  ❌ agents/ directory missing"
    VERIFY_FAILED=true
fi

if [ ! -f "$INSTALL_DIR/version.json" ]; then
    echo -e "${RED}✗${NC}"
    echo "  ❌ version.json missing"
    VERIFY_FAILED=true
fi

if [ "$VERIFY_FAILED" = false ]; then
    echo -e "${GREEN}✓${NC}"
fi

echo ""

if [ "$VERIFY_FAILED" = true ]; then
    echo -e "${RED}⚠️  Verification failed - installation may be incomplete${NC}"
    echo ""
    echo "You can:"
    echo "  1. Try another backup: ./emergency-rollback.sh"
    echo "  2. Restore broken state: mv $SAFETY_BACKUP ~/.opencli"
    echo "  3. Fresh install: cd ~/opencli && ./install.sh"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Emergency rollback complete!${NC}"
echo ""
echo "Restored version: v${BACKUP_VERSION}"
echo "Previous (broken) installation backed up at:"
echo "  $SAFETY_BACKUP"
echo ""
echo "Try running: opencli"
echo ""
echo "If issues persist:"
echo "  • Try an older backup: $(basename $0)"
echo "  • Check logs: ~/.opencli/logs/"
echo "  • Fresh install: cd ~/opencli && ./install.sh"
echo ""
