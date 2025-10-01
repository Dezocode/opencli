#!/bin/bash
# Version Bump Helper for OpenCLI

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
VERSION_FILE="$REPO_DIR/version.json"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "📦 OpenCLI Version Bump Tool"
echo ""

# Get current version
CURRENT_VERSION=$(python3 -c "import json; print(json.load(open('$VERSION_FILE'))['version'])")
echo -e "${BLUE}Current version:${NC} $CURRENT_VERSION"
echo ""

# Parse version
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

echo "Select bump type:"
echo "  1) Major (breaking changes) - ${MAJOR}.${MINOR}.${PATCH} → $((MAJOR+1)).0.0"
echo "  2) Minor (new features) - ${MAJOR}.${MINOR}.${PATCH} → ${MAJOR}.$((MINOR+1)).0"
echo "  3) Patch (bug fixes) - ${MAJOR}.${MINOR}.${PATCH} → ${MAJOR}.${MINOR}.$((PATCH+1))"
echo "  4) Custom version"
echo ""
read -p "Choice (1-4): " CHOICE

case $CHOICE in
    1)
        NEW_VERSION="$((MAJOR+1)).0.0"
        BUMP_TYPE="major"
        ;;
    2)
        NEW_VERSION="${MAJOR}.$((MINOR+1)).0"
        BUMP_TYPE="minor"
        ;;
    3)
        NEW_VERSION="${MAJOR}.${MINOR}.$((PATCH+1))"
        BUMP_TYPE="patch"
        ;;
    4)
        read -p "Enter new version: " NEW_VERSION
        BUMP_TYPE="custom"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}New version:${NC} $NEW_VERSION"
echo ""

# Get changelog entry
echo "Enter changelog entries (one per line, empty line to finish):"
CHANGES=()
while IFS= read -r line; do
    [ -z "$line" ] && break
    CHANGES+=("$line")
done

if [ ${#CHANGES[@]} -eq 0 ]; then
    echo -e "${RED}No changelog entries provided${NC}"
    exit 1
fi

# Confirm
echo ""
echo -e "${YELLOW}Preview:${NC}"
echo "Version: $CURRENT_VERSION → $NEW_VERSION"
echo "Changelog:"
for change in "${CHANGES[@]}"; do
    echo "  • $change"
done
echo ""
read -p "Confirm version bump? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Update version.json
echo ""
echo -e "${BLUE}Updating version.json...${NC}"

python3 << PYTHON
import json
from datetime import datetime

# Read current version file
with open('$VERSION_FILE', 'r') as f:
    data = json.load(f)

# Update version
data['version'] = '$NEW_VERSION'
data['release_date'] = datetime.now().strftime('%Y-%m-%d')

# Add changelog entry
new_entry = {
    'version': '$NEW_VERSION',
    'date': datetime.now().strftime('%Y-%m-%d'),
    'changes': [$(printf '"%s",' "${CHANGES[@]}" | sed 's/,$//')],
    'bump_type': '$BUMP_TYPE'
}

# Insert at beginning of changelog
if 'changelog' not in data:
    data['changelog'] = []
data['changelog'].insert(0, new_entry)

# Write back
with open('$VERSION_FILE', 'w') as f:
    json.dump(data, f, indent=2)

print('✓ version.json updated')
PYTHON

# Update install.sh version comment
sed -i.bak "s/^# Version: .*/# Version: $NEW_VERSION/" "$REPO_DIR/install.sh"
rm "$REPO_DIR/install.sh.bak"
echo -e "${GREEN}✓${NC} install.sh version updated"

# Git commit (if in git repo)
if [ -d "$REPO_DIR/.git" ]; then
    echo ""
    read -p "Create git commit? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add "$VERSION_FILE" "$REPO_DIR/install.sh"

        COMMIT_MSG="chore: bump version to $NEW_VERSION

Changes:
"
        for change in "${CHANGES[@]}"; do
            COMMIT_MSG+="- $change
"
        done

        git commit -m "$COMMIT_MSG"
        echo -e "${GREEN}✓${NC} Git commit created"

        # Offer to create tag
        echo ""
        read -p "Create git tag v$NEW_VERSION? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"
            echo -e "${GREEN}✓${NC} Git tag created"

            echo ""
            echo "Push changes with:"
            echo "  git push && git push --tags"
        fi
    fi
fi

echo ""
echo -e "${GREEN}✅ Version bumped successfully!${NC}"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Test installation: ./install.sh"
echo "  3. Push changes: git push && git push --tags"
echo "  4. Users upgrade with: ./upgrade.sh"
echo ""
