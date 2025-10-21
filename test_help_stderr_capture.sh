#!/bin/bash
# Capture stderr during /help command execution

echo "Starting TUI and capturing stderr..."
(python3 ~/.opencli/opencli.py tui 2>&1 | tee /tmp/opencli_stderr.log) &
TUI_PID=$!

sleep 4

# Send /help via direct stdin if possible
# Since we can't easily automate input, just show instructions
echo ""
echo "================================================================"
echo "TUI is running with PID $TUI_PID"
echo "Please manually type /help and press Enter in the TUI"
echo "Then press Ctrl+C to stop"
echo "Stderr output is being captured to /tmp/opencli_stderr.log"
echo "================================================================"
echo ""

# Wait for user to test
wait $TUI_PID

# Show stderr related to permission
echo ""
echo "================================================================"
echo "PERMISSION-RELATED STDERR OUTPUT:"
echo "================================================================"
grep -i "permission" /tmp/opencli_stderr.log | head -50
