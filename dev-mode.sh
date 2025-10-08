#!/bin/bash
# OpenCLI Development Mode
# Runs OpenCLI with bytecode cache disabled and auto-clears stale cache

OPENCLI_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔧 OpenCLI Development Mode"
echo ""

# Clear existing cache
echo "▸ Clearing Python bytecode cache..."
find "$OPENCLI_DIR" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find "$OPENCLI_DIR" -name "*.pyc" -delete 2>/dev/null
echo "✓ Cache cleared"
echo ""

# Set dev mode environment variable
export OPENCLI_DEV=1
export PYTHONDONTWRITEBYTECODE=1

echo "▸ Starting OpenCLI in development mode"
echo "  (bytecode caching disabled)"
echo ""

# Run OpenCLI
cd "$OPENCLI_DIR"
python3 opencli.py "$@"
