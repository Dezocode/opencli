#!/bin/bash
# OpenCLI Upgrade Tool
# Detects changes from git, archives old version, and upgrades installation

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directories
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.opencli"
BIN_DIR="$HOME/bin"
ARCHIVE_DIR="$REPO_DIR/archive"

echo "🔄 OpenCLI Upgrade Tool"
echo ""

# Check if we're in a git repo
if [ ! -d "$REPO_DIR/.git" ]; then
    echo -e "${RED}❌ Not a git repository${NC}"
    echo "This tool requires a git repository to detect changes."
    exit 1
fi

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  gh CLI not found${NC}"
    echo "Install from: https://cli.github.com"
    echo ""
    echo "Continuing with local git diff..."
    USE_GH=false
else
    USE_GH=true
fi

# Get current installed version
if [ -f "$INSTALL_DIR/version.json" ]; then
    CURRENT_VERSION=$(python3 -c "import json; print(json.load(open('$INSTALL_DIR/version.json'))['version'])" 2>/dev/null || echo "unknown")
else
    CURRENT_VERSION="unknown"
fi

# Get new version from repo
NEW_VERSION=$(python3 -c "import json; print(json.load(open('$REPO_DIR/version.json'))['version'])" 2>/dev/null || echo "unknown")

echo -e "${BLUE}Current version:${NC} $CURRENT_VERSION"
echo -e "${BLUE}New version:${NC} $NEW_VERSION"
echo ""

# Compare versions
if [ "$CURRENT_VERSION" = "$NEW_VERSION" ] && [ "$CURRENT_VERSION" != "unknown" ]; then
    echo -e "${YELLOW}⚠️  Same version detected${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Detect changes
echo -e "${BLUE}Detecting changes...${NC}"
echo ""

CHANGES_DETECTED=false

# Function to check if file changed
check_changes() {
    local file=$1
    local description=$2

    if [ -f "$file" ]; then
        if git diff --quiet HEAD -- "$file" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $description (unchanged)"
        else
            echo -e "  ${YELLOW}↻${NC} $description (modified)"
            CHANGES_DETECTED=true
        fi
    else
        echo -e "  ${YELLOW}+${NC} $description (new)"
        CHANGES_DETECTED=true
    fi
}

# Check main files
check_changes "opencli.py" "Main executable"
check_changes "install.sh" "Installation script"
check_changes "version.json" "Version metadata"

# Check modules
echo ""
echo "Modules:"
for module in modules/*.py; do
    if [ -f "$module" ]; then
        check_changes "$module" "$(basename $module)"
    fi
done

# Check agents
echo ""
echo "Agents:"
check_changes "agents/configs/agents.yaml" "Agent configurations"

# Check for new custom agents
if [ -d "agents/configs/custom" ]; then
    for agent in agents/configs/custom/*.yaml; do
        if [ -f "$agent" ]; then
            check_changes "$agent" "$(basename $agent)"
        fi
    done
fi

# Check documentation
echo ""
echo "Documentation:"
check_changes "README.md" "Main documentation"
check_changes "ARCHITECTURE.md" "Architecture docs"
check_changes "INTEGRATION_STATUS.md" "Integration status"

echo ""

if [ "$CHANGES_DETECTED" = false ]; then
    echo -e "${GREEN}No changes detected${NC}"
    echo "Installation is up to date."
    exit 0
fi

# Get git diff summary
echo -e "${BLUE}Change summary:${NC}"
git diff --stat HEAD 2>/dev/null || echo "Unable to generate diff"
echo ""

# Confirm upgrade
read -p "Proceed with upgrade? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Upgrade cancelled."
    exit 0
fi

# Archive old installation
if [ "$CURRENT_VERSION" != "unknown" ]; then
    echo ""
    echo -e "${BLUE}Archiving current installation...${NC}"

    ARCHIVE_NAME="install-v${CURRENT_VERSION}.sh"
    mkdir -p "$ARCHIVE_DIR"

    # Archive old install.sh
    if [ -f "$REPO_DIR/install.sh" ]; then
        cp "$REPO_DIR/install.sh" "$ARCHIVE_DIR/$ARCHIVE_NAME"
        echo -e "${GREEN}✓${NC} Archived install.sh as $ARCHIVE_NAME"
    fi

    # Archive old version.json
    if [ -f "$INSTALL_DIR/version.json" ]; then
        cp "$INSTALL_DIR/version.json" "$ARCHIVE_DIR/version-${CURRENT_VERSION}.json"
        echo -e "${GREEN}✓${NC} Archived version.json"
    fi

    # Create archive manifest
    cat > "$ARCHIVE_DIR/VERSIONS.md" << EOF
# Archived Versions

## v${CURRENT_VERSION} (Archived: $(date +%Y-%m-%d))
- Install script: $ARCHIVE_NAME
- Version metadata: version-${CURRENT_VERSION}.json
- Archived on: $(date)

EOF

    # Append to existing manifest if it exists
    if [ -f "$ARCHIVE_DIR/VERSIONS.md.tmp" ]; then
        cat "$ARCHIVE_DIR/VERSIONS.md" "$ARCHIVE_DIR/VERSIONS.md.tmp" > "$ARCHIVE_DIR/VERSIONS.md.new"
        mv "$ARCHIVE_DIR/VERSIONS.md.new" "$ARCHIVE_DIR/VERSIONS.md"
        rm "$ARCHIVE_DIR/VERSIONS.md.tmp"
    fi

    echo -e "${GREEN}✓${NC} Archive created in $ARCHIVE_DIR"
fi

# Backup current installation
echo ""
echo -e "${BLUE}Backing up current installation...${NC}"
BACKUP_DIR="$INSTALL_DIR.backup-$(date +%Y%m%d-%H%M%S)"
if [ -d "$INSTALL_DIR" ]; then
    cp -r "$INSTALL_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✓${NC} Backup created at $BACKUP_DIR"
fi

# Run installation
echo ""
echo -e "${BLUE}Installing new version...${NC}"
echo ""

# Copy new version metadata first
cp "$REPO_DIR/version.json" "$INSTALL_DIR/version.json"

# Run installer
"$REPO_DIR/install.sh"

# Upgrade complete
echo ""
echo -e "${GREEN}✅ Upgrade complete!${NC}"
echo ""
echo "Upgraded from v${CURRENT_VERSION} to v${NEW_VERSION}"
echo ""
echo "📦 Backup location: $BACKUP_DIR"
if [ "$CURRENT_VERSION" != "unknown" ]; then
    echo "📜 Archived version: $ARCHIVE_DIR/$ARCHIVE_NAME"
fi
echo ""
echo "📖 Changelog:"
python3 << 'PYTHON'
import json
with open("$REPO_DIR/version.json") as f:
    data = json.load(f)
    for entry in data.get("changelog", []):
        if entry["version"] == "$NEW_VERSION":
            for change in entry.get("changes", []):
                print(f"  • {change}")
PYTHON
echo ""
echo "🚀 Run 'opencli' to start using the new version"
echo ""
