#!/bin/bash

# Diagnostic script to identify permission buffer navigation issues

echo "================================"
echo "OpenCLI Navigation Diagnostic"
echo "================================"
echo ""

echo "Starting OpenCLI with debug logging..."
echo "Debug log will be saved to: /tmp/opencli-navigation-debug.log"
echo ""
echo "Instructions:"
echo "  1. Type: /help"
echo "  2. When buffer appears, try pressing:"
echo "     - DOWN arrow (should move selection down)"
echo "     - UP arrow (should move selection up)"
echo "     - ENTER (should select)"
echo "  3. Press Ctrl+C to exit"
echo "  4. This script will analyze the debug log"
echo ""
echo "Press ENTER to start..."
read

# Run OpenCLI with stderr redirected to debug log
opencli tui 2>&1 | tee /tmp/opencli-navigation-debug.log

echo ""
echo "================================"
echo "Debug Log Analysis"
echo "================================"
echo ""

LOG="/tmp/opencli-navigation-debug.log"

# Check if permission prompt data was set
echo "1. Checking if permission_prompt_data was set..."
if grep -q "Permission data changed" "$LOG"; then
    echo "   ✅ permission_prompt_data WAS set"
    grep "PERMISSION ACTIVE:" "$LOG" | tail -1
else
    echo "   ❌ permission_prompt_data was NOT set!"
    echo "      This is why navigation doesn't work!"
fi
echo ""

# Check if keys reached MultiLineInput
echo "2. Checking if arrow keys reached MultiLineInput..."
KEY_COUNT=$(grep -c "\[MultiLineInput.on_key\] KEY=" "$LOG")
if [ "$KEY_COUNT" -gt 0 ]; then
    echo "   ✅ Keys reached MultiLineInput ($KEY_COUNT key presses detected)"
    echo "   Recent keys:"
    grep "\[MultiLineInput.on_key\] KEY=" "$LOG" | tail -5
else
    echo "   ❌ No keys reached MultiLineInput!"
    echo "      Focus might be on a different widget!"
fi
echo ""

# Check if permission handler was triggered
echo "3. Checking if permission handler processed keys..."
HANDLER_COUNT=$(grep -c "INSIDE PERMISSION HANDLER" "$LOG")
if [ "$HANDLER_COUNT" -gt 0 ]; then
    echo "   ✅ Permission handler processed $HANDLER_COUNT keys"
else
    echo "   ❌ Permission handler was NOT triggered!"
    echo "      Either:"
    echo "      - permission_prompt_data is None"
    echo "      - Keys not reaching on_key method"
fi
echo ""

# Check permission result
echo "4. Checking permission check result..."
if grep -q "Permission result = False" "$LOG"; then
    echo "   ⚠️  WARNING: Permission returned FALSE!"
    echo "      Command was denied, but why is buffer showing?"
    grep "Permission result" "$LOG" | tail -3
elif grep -q "Permission result = True" "$LOG"; then
    echo "   ✅ Permission granted"
else
    echo "   ❓ No permission result found in logs"
fi
echo ""

# Summary
echo "================================"
echo "Summary"
echo "================================"
echo ""

if grep -q "INSIDE PERMISSION HANDLER" "$LOG" && grep -q "Permission data changed" "$LOG"; then
    echo "✅ Navigation should be working!"
    echo "   - Buffer data is set"
    echo "   - Keys are being processed"
    echo ""
    echo "If you still can't navigate, check:"
    echo "  - Is the visual selection changing?"
    echo "  - Try number keys (1, 2, 3) as alternative"
elif grep -q "Permission data changed" "$LOG" && ! grep -q "INSIDE PERMISSION HANDLER" "$LOG"; then
    echo "❌ ISSUE: Buffer shows but keys not processed!"
    echo ""
    echo "Check these in log:"
    grep "\[MultiLineInput.on_key\] KEY=down" "$LOG" | head -3
    echo ""
    echo "If you see 'prompt=False', permission_prompt_data is None"
    echo "If you see 'focused=False', focus is on wrong widget"
elif ! grep -q "Permission data changed" "$LOG"; then
    echo "❌ ISSUE: Buffer data never set!"
    echo ""
    echo "The _show_permission_prompt() method might not be called"
    echo "or is failing silently."
    echo ""
    echo "Check permission flow:"
    grep "show_permission_prompt\|Permission data changed" "$LOG" | tail -10
fi

echo ""
echo "Full debug log available at: $LOG"
echo "Send this file to support if issue persists"
