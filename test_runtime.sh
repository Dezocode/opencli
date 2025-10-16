#!/bin/bash
# Test script for refactored OpenCLI runtime

echo "=========================================="
echo "OpenCLI Runtime Test"
echo "=========================================="
echo ""

# Change to runtime directory
cd /Users/dezmondhollins/.opencli

echo "1. Testing help command..."
python3 opencli.py --help
echo ""

echo "=========================================="
echo "2. Testing basic prompt (non-interactive)..."
echo "This will make an API call - press Ctrl+C to skip"
echo "=========================================="
python3 opencli.py --print "Say hello in one word"
echo ""

echo "=========================================="
echo "3. To test interactive mode, run:"
echo "   cd ~/.opencli && python3 opencli.py"
echo ""
echo "4. To test with fallback mode (no TUI):"
echo "   cd ~/.opencli && python3 opencli.py --fallback"
echo ""
echo "=========================================="
echo "✅ Runtime tests complete!"
echo "=========================================="
