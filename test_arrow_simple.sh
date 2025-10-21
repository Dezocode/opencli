#!/bin/bash
# Simple Direct Arrow Key Test - No complex framework

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  SIMPLE ARROW KEY TEST                                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "This will:"
echo "  1. Start opencli tui with stderr logging"
echo "  2. You manually type /help and press ENTER twice"
echo "  3. You manually press DOWN arrow"
echo "  4. Press Ctrl+C to exit"
echo "  5. We'll analyze the debug output"
echo ""
echo "Press ENTER to start..."
read

# Run opencli with stderr capture
echo "Starting opencli tui (stderr will be captured)..."
opencli tui 2>/tmp/arrow_test_stderr.log

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "ANALYZING DEBUG OUTPUT"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check what we captured
if [ -f /tmp/arrow_test_stderr.log ]; then
    echo "Debug log file size: $(wc -l < /tmp/arrow_test_stderr.log) lines"
    echo ""

    # Check for key events
    if grep -q "\[MultiLineInput.on_key\]" /tmp/arrow_test_stderr.log; then
        echo "✅ FOUND: on_key() method was called"
        echo ""
        echo "Key events detected:"
        grep "\[MultiLineInput.on_key\] KEY=" /tmp/arrow_test_stderr.log | head -20
        echo ""
    else
        echo "❌ NOT FOUND: on_key() was NOT called"
        echo ""
    fi

    # Check for action method
    if grep -q "\[ACTION_PERMISSION_DOWN\]" /tmp/arrow_test_stderr.log; then
        echo "✅ FOUND: action_permission_down() was called"
        echo ""
        grep "\[ACTION_PERMISSION_DOWN\]" /tmp/arrow_test_stderr.log
        echo ""
    else
        echo "❌ NOT FOUND: action_permission_down() was NOT called"
        echo ""
    fi

    # Check for selection changes
    if grep -q "DOWN - changed" /tmp/arrow_test_stderr.log; then
        echo "✅ FOUND: Selection value DID change"
        echo ""
        grep "DOWN - changed" /tmp/arrow_test_stderr.log
        echo ""
    else
        echo "❌ NOT FOUND: Selection value did NOT change"
        echo ""
    fi

    # Check for refresh calls
    if grep -q "refresh() called" /tmp/arrow_test_stderr.log; then
        echo "✅ FOUND: refresh() was called"
        echo ""
    else
        echo "❌ NOT FOUND: refresh() was NOT called"
        echo ""
    fi

    echo "═══════════════════════════════════════════════════════════════"
    echo "FULL DEBUG OUTPUT"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    cat /tmp/arrow_test_stderr.log | grep -E "(MultiLineInput|ACTION_PERMISSION|KEY EVENT|DOWN|changed|refresh)"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Full log saved to: /tmp/arrow_test_stderr.log"
    echo ""
else
    echo "❌ No debug log file found"
fi
