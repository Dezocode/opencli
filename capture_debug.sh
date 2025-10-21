#!/bin/bash
# Quick Debug Capture Script
# This will capture ALL debug output from opencli tui

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  DEBUG CAPTURE - Permission Buffer Key Events           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Instructions:"
echo "  1. opencli tui will start with debug logging"
echo "  2. Type: /help"
echo "  3. Press: ENTER (to submit)"
echo "  4. Press: ENTER again (to show permission buffer)"
echo "  5. Press: DOWN arrow (to test navigation)"
echo "  6. Press: ENTER (to test selection)"
echo "  7. Press: Ctrl+C (to exit)"
echo ""
echo "All debug output will be saved to: /tmp/opencli_debug.log"
echo ""
echo "Press ENTER to start..."
read

echo "Starting opencli tui..."
echo ""

# Start opencli with stderr redirected to file
opencli tui 2>/tmp/opencli_debug.log

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "DEBUG OUTPUT ANALYSIS"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if log file exists
if [ ! -f /tmp/opencli_debug.log ]; then
    echo "❌ No debug log found!"
    exit 1
fi

echo "✅ Debug log captured: $(wc -l < /tmp/opencli_debug.log) lines"
echo ""

# Check critical events
echo "═══════════════════════════════════════════════════════════"
echo "1. PERMISSION PROMPT SETUP"
echo "═══════════════════════════════════════════════════════════"
grep -E "\[TUI\._show_permission_prompt\]" /tmp/opencli_debug.log | head -20
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "2. WIDGET FOCUS EVENTS"
echo "═══════════════════════════════════════════════════════════"
grep -E "\[MultiLineInput\.on_focus\]|\[MultiLineInput\.on_blur\]" /tmp/opencli_debug.log | head -20
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "3. KEY EVENTS RECEIVED"
echo "═══════════════════════════════════════════════════════════"
grep -E "====== KEY EVENT ======" /tmp/opencli_debug.log | wc -l | xargs echo "Total key events:"
grep -E "KEY EVENT|KEY='|has_focus=" /tmp/opencli_debug.log | head -40
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "4. ACTION METHODS CALLED"
echo "═══════════════════════════════════════════════════════════"
grep -E "\[ACTION_PERMISSION_DOWN\]|\[ACTION_PERMISSION_UP\]|\[ACTION_SUBMIT\]" /tmp/opencli_debug.log | head -20
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "5. PERMISSION DATA CHANGES"
echo "═══════════════════════════════════════════════════════════"
grep -E "PERMISSION DATA CHANGED|PERMISSION ACTIVE|selected_option=" /tmp/opencli_debug.log | head -20
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "DIAGNOSIS"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if focus was gained
if grep -q "GAINED FOCUS" /tmp/opencli_debug.log; then
    echo "✅ Widget DID gain focus"
else
    echo "❌ Widget DID NOT gain focus - FOCUS ISSUE!"
fi

# Check if key events received
if grep -q "KEY EVENT" /tmp/opencli_debug.log; then
    echo "✅ Widget DID receive key events"

    # Check if has_focus was true
    if grep -q "has_focus=True" /tmp/opencli_debug.log; then
        echo "✅ Widget had focus during key events"
    else
        echo "❌ Widget did NOT have focus during key events - FOCUS ISSUE!"
    fi
else
    echo "❌ Widget DID NOT receive ANY key events - EVENT ROUTING ISSUE!"
fi

# Check if action methods fired
if grep -q "ACTION_PERMISSION" /tmp/opencli_debug.log; then
    echo "✅ Action methods WERE called"
else
    echo "❌ Action methods were NOT called - BINDING ISSUE!"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Full log saved to: /tmp/opencli_debug.log"
echo "═══════════════════════════════════════════════════════════"
