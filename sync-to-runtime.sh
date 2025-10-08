#!/bin/bash
# Sync development modules to runtime ~/.opencli

echo "📦 Syncing modules to ~/.opencli/modules/"
echo ""

# Copy all module files
cp modules/*.py ~/.opencli/modules/ 2>/dev/null

# Clear runtime cache
rm -rf ~/.opencli/modules/__pycache__
rm -rf ~/.opencli/__pycache__

echo "✅ Modules synced"
echo "✅ Cache cleared"
echo ""
echo "🔄 Restart OpenCLI to load new code:"
echo "   cd ~/.opencli && python3 opencli.py"
