#!/bin/bash
# Test script to see where message flow breaks
# Shows stderr in real-time to see debug logs

echo "=========================================="
echo "MESSAGE FLOW DEBUG TEST"
echo "=========================================="
echo ""
echo "Instructions:"
echo "1. TUI will launch"
echo "2. Type 'hi' in the input box"
echo "3. Press Enter"
echo "4. Watch the debug output below"
echo ""
echo "Looking for:"
echo "  [MultiLineInput.on_key] - Shows Enter key was pressed"
echo "  [ACTION_SUBMIT] - Shows action_submit was called"
echo "  [HANDLER] - Shows handler received the message"
echo ""
echo "Press Ctrl+C to exit TUI when done"
echo ""
echo "=========================================="
echo "STARTING TUI (debug logs will appear below):"
echo "=========================================="
echo ""

# Run opencli tui with stderr visible
opencli tui 2>&1 | grep -E '\[MultiLineInput\]|\[ACTION_SUBMIT\]|\[HANDLER\]|ERROR|Error' || opencli tui
