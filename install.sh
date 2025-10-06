#!/bin/bash
# OpenCLI Installation Script
# Version: 1.2.1

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check for required commands
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is required but not installed.${NC}"
    echo "Please install git first:"
    echo "  macOS:  brew install git"
    echo "  Ubuntu: sudo apt-get install git"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is required but not installed.${NC}"
    exit 1
fi

# Check if running from curl (stdin is not a terminal)
if [ -t 0 ]; then
    # Running from a cloned repo
    REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
else
    # Running from curl - need to clone first
    echo -e "${BLUE}Installing OpenCLI...${NC}"
    echo ""

    REPO_DIR="$HOME/opencli"

    if [ -d "$REPO_DIR" ]; then
        echo -e "${YELLOW}⚠️  Directory ~/opencli already exists${NC}"
        read -p "Update existing installation? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled."
            exit 1
        fi
        cd "$REPO_DIR"
        git pull origin Main || {
            echo -e "${RED}Failed to update repository${NC}"
            exit 1
        }
    else
        echo -e "${BLUE}Cloning repository...${NC}"
        git clone https://github.com/Dezocode/opencli.git "$REPO_DIR" || {
            echo -e "${RED}Failed to clone repository${NC}"
            exit 1
        }
        cd "$REPO_DIR"
    fi
fi

# Get version from version.json
VERSION=$(python3 -c "import json; print(json.load(open('$REPO_DIR/version.json'))['version'])" 2>/dev/null || echo "unknown")

echo "🚀 Installing OpenCLI v${VERSION}..."
echo ""

# Directories
INSTALL_DIR="$HOME/.opencli"
BIN_DIR="$HOME/bin"

# Create directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p "$INSTALL_DIR"/{agents/{configs/custom,contexts/project_contexts,system_prompts/base,temp},modules,sessions,bashes}
mkdir -p "$BIN_DIR"

# Copy modules with orphan detection
echo -e "${BLUE}Installing modules...${NC}"

# Check for new modules that aren't in the installation yet
NEW_MODULES=()
for module in "$REPO_DIR/modules/"*.py; do
    module_name=$(basename "$module")
    if [ ! -f "$INSTALL_DIR/modules/$module_name" ]; then
        NEW_MODULES+=("$module_name")
    fi
done

if [ ${#NEW_MODULES[@]} -gt 0 ]; then
    echo -e "${YELLOW}📦 New modules detected:${NC}"
    for module in "${NEW_MODULES[@]}"; do
        echo -e "  • $module"
    done
fi

# Copy all modules
cp "$REPO_DIR/modules/"*.py "$INSTALL_DIR/modules/"

# Check for orphaned modules (in installation but not in repo)
ORPHANED_MODULES=()
for module in "$INSTALL_DIR/modules/"*.py; do
    module_name=$(basename "$module")
    if [ ! -f "$REPO_DIR/modules/$module_name" ]; then
        ORPHANED_MODULES+=("$module_name")
    fi
done

if [ ${#ORPHANED_MODULES[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Orphaned modules detected (removed from repo):${NC}"
    for module in "${ORPHANED_MODULES[@]}"; do
        echo -e "  • $module"
    done
    echo -e "${YELLOW}These modules are still in your installation but not in the repo.${NC}"
    echo -e "${YELLOW}They will remain unless manually removed.${NC}"
fi

# Copy agent configs
echo -e "${BLUE}Installing agent configurations...${NC}"
cp "$REPO_DIR/agents/configs/agents.yaml" "$INSTALL_DIR/agents/configs/"

# Copy main executable
echo -e "${BLUE}Installing opencli executable...${NC}"
cp "$REPO_DIR/opencli.py" "$BIN_DIR/opencli"
chmod +x "$BIN_DIR/opencli"

# Copy version metadata
echo -e "${BLUE}Installing version metadata...${NC}"
cp "$REPO_DIR/version.json" "$INSTALL_DIR/version.json"

# Copy emergency rollback script (stays in repo, not installation)
echo -e "${BLUE}Installing emergency rollback script...${NC}"
if [ -f "$REPO_DIR/emergency-rollback.sh" ]; then
    chmod +x "$REPO_DIR/emergency-rollback.sh"
    echo -e "${GREEN}✓${NC} Emergency rollback available at: ~/opencli/emergency-rollback.sh"
fi

# Check dependencies
echo ""
echo -e "${BLUE}Checking dependencies...${NC}"

check_dependency() {
    if ! python3 -c "import $1" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Missing: $1${NC}"
        MISSING_DEPS="$MISSING_DEPS $1"
    else
        echo -e "${GREEN}✓${NC} $1"
    fi
}

MISSING_DEPS=""
check_dependency "openai"
check_dependency "prompt_toolkit"
check_dependency "yaml"
check_dependency "textual"
check_dependency "rich"
check_dependency "psutil"

if [ -n "$MISSING_DEPS" ]; then
    echo ""
    echo -e "${YELLOW}Missing dependencies detected.${NC}"

    # Check if pip3 is available
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}Error: pip3 is required to install dependencies${NC}"
        echo "Install with:"
        echo "  macOS:  python3 -m ensurepip --upgrade"
        echo "  Ubuntu: sudo apt-get install python3-pip"
        exit 1
    fi

    echo "Install with: pip3 install$MISSING_DEPS"
    echo ""
    read -p "Install now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install$MISSING_DEPS || {
            echo -e "${RED}Failed to install dependencies${NC}"
            echo "Try manually: pip3 install openai prompt_toolkit pyyaml textual rich psutil"
            exit 1
        }
        echo -e "${GREEN}✓ Dependencies installed${NC}"
    fi
fi

# Check gh CLI
echo ""
if command -v gh &> /dev/null; then
    echo -e "${GREEN}✓${NC} gh CLI installed"
    if gh auth status &> /dev/null; then
        echo -e "${GREEN}✓${NC} gh CLI authenticated"
    else
        echo -e "${YELLOW}⚠️  gh CLI not authenticated${NC}"
        echo "  Run: gh auth login"
    fi
else
    echo -e "${YELLOW}⚠️  gh CLI not installed (GitHub features will be disabled)${NC}"
    echo "  Install from: https://cli.github.com"
fi

# Setup API key
echo ""
if [ -f "$INSTALL_DIR/.secrets" ]; then
    echo -e "${GREEN}✓${NC} API key already configured"
else
    echo -e "${YELLOW}⚠️  No API key found${NC}"
    echo ""
    read -p "Configure OpenRouter API key now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        opencli --setup
    else
        echo ""
        echo "You can configure it later with: opencli --setup"
    fi
fi

# Add to PATH reminder
echo ""
if ! echo "$PATH" | grep -q "$BIN_DIR"; then
    echo -e "${YELLOW}⚠️  $BIN_DIR is not in your PATH${NC}"
    echo ""
    echo "Add to your shell config (~/.zshrc or ~/.bashrc):"
    echo ""
    echo "  export PATH=\"\$HOME/bin:\$PATH\""
    echo "  alias opencli='~/bin/opencli'"
    echo ""
fi

# Installation complete
echo ""
echo -e "${GREEN}✅ OpenCLI installed successfully!${NC}"
echo ""
echo "📚 Quick start:"
echo "  opencli              # Start interactive session"
echo "  opencli --help       # Show help"
echo "  opencli --setup      # Configure API key"
echo ""
echo "📖 Documentation:"
echo "  $REPO_DIR/README.md"
echo "  $REPO_DIR/ARCHITECTURE.md"
echo "  $REPO_DIR/INTEGRATION_STATUS.md"
echo ""
echo "🎯 Try it:"
echo "  opencli"
echo "  > /agents  # List available agents"
echo ""
