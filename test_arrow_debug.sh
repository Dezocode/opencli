#!/bin/bash
# Simple test to capture debug output when pressing arrow keys

echo "Starting opencli tui with stderr capture..."
echo "Type /help, press ENTER twice, then press DOWN arrow"
echo "Press Ctrl+C to exit and see debug output"
echo ""

# Run opencli tui and capture stderr
opencli tui 2>/tmp/opencli_arrow_debug.log

echo ""
echo "==================================="
echo "DEBUG OUTPUT (from stderr):"
echo "==================================="
cat /tmp/opencli_arrow_debug.log | grep -E "(MultiLineInput|ACTION_PERMISSION|DOWN KEY|UP KEY|permission_selected|on_key)" | tail -50
echo ""
echo "Full log saved to: /tmp/opencli_arrow_debug.log"
