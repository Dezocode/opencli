#!/bin/bash
# Clear Python bytecode cache before running OpenCLI
# This ensures code changes are always loaded

OPENCLI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🧹 Clearing Python cache..."
find "$OPENCLI_DIR/modules" -name "*.pyc" -delete 2>/dev/null
find "$OPENCLI_DIR/modules" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
echo "✅ Cache cleared"

# Kill any zombie OpenCLI processes
if pgrep -f "opencli.py" > /dev/null; then
    echo "🔪 Killing existing OpenCLI processes..."
    pkill -9 -f "opencli.py"
    sleep 1
    echo "✅ Processes killed"
fi

echo "🚀 Ready to start OpenCLI"
