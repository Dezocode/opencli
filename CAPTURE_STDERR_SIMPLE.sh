#!/bin/bash
# Simple stderr capture for arrow key debugging
# User should run this and interact manually

echo "═══════════════════════════════════════════════════════════"
echo "ARROW KEY DEBUG - STDERR CAPTURE"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Instructions:"
echo "1. The TUI will start in 3 seconds"
echo "2. Type: /help"
echo "3. Press ENTER twice (permission buffer should show)"
echo "4. Press DOWN arrow (try to move to 'No')"
echo "5. Press UP arrow (try to move back to 'Yes')"
echo "6. Press Ctrl+C to exit"
echo ""
echo "All stderr will be saved to /tmp/arrow_stderr.log"
echo ""
echo "Starting in 3..."
sleep 1
echo "2..."
sleep 1
echo "1..."
sleep 1
echo ""

# Run opencli and capture ONLY stderr
opencli tui 2>/tmp/arrow_stderr.log

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "ANALYSIS RESULTS"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check critical findings
echo "1. Was permission buffer shown?"
if grep -q "\[TUI._show_permission_prompt\]" /tmp/arrow_stderr.log; then
    echo "   ✅ YES - _show_permission_prompt was called"
    grep "\[TUI._show_permission_prompt\]" /tmp/arrow_stderr.log | head -5
else
    echo "   ❌ NO - permission buffer was never shown!"
fi
echo ""

echo "2. Was permission_prompt_data set?"
if grep -q "PERMISSION ACTIVE" /tmp/arrow_stderr.log; then
    echo "   ✅ YES - permission_prompt_data was set"
    grep "PERMISSION ACTIVE" /tmp/arrow_stderr.log
else
    echo "   ❌ NO - permission_prompt_data was NOT set!"
fi
echo ""

echo "3. Did widget gain focus?"
if grep -q "\[MultiLineInput.on_focus\] GAINED FOCUS" /tmp/arrow_stderr.log; then
    echo "   ✅ YES - widget gained focus"
    grep "\[MultiLineInput.on_focus\] GAINED FOCUS" /tmp/arrow_stderr.log
else
    echo "   ❌ NO - widget never gained focus!"
fi
echo ""

echo "4. Was on_key() called for DOWN arrow?"
if grep -q "KEY='down'" /tmp/arrow_stderr.log; then
    echo "   ✅ YES - on_key received DOWN key"
    grep "KEY='down'" /tmp/arrow_stderr.log
else
    echo "   ❌ NO - on_key() never received DOWN key!"
fi
echo ""

echo "5. Was on_key() called for UP arrow?"
if grep -q "KEY='up'" /tmp/arrow_stderr.log; then
    echo "   ✅ YES - on_key received UP key"
    grep "KEY='up'" /tmp/arrow_stderr.log
else
    echo "   ❌ NO - on_key() never received UP key!"
fi
echo ""

echo "6. Were action_permission_* methods called?"
if grep -q "action_permission" /tmp/arrow_stderr.log; then
    echo "   ✅ YES - BINDINGS action methods were called"
    grep "action_permission" /tmp/arrow_stderr.log
else
    echo "   ❌ NO - BINDINGS action methods were NOT called!"
fi
echo ""

echo "7. Did selection change (watch_permission_selected_option)?"
if grep -q "watch_permission_selected_option.*->" /tmp/arrow_stderr.log; then
    echo "   ✅ YES - selection changed"
    grep "watch_permission_selected_option" /tmp/arrow_stderr.log
else
    echo "   ❌ NO - selection never changed!"
fi
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "FULL LOG FILE"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "View full log: cat /tmp/arrow_stderr.log"
echo "Search for specific events:"
echo "  - Permission buffer: cat /tmp/arrow_stderr.log | grep -i permission"
echo "  - Key events: cat /tmp/arrow_stderr.log | grep -i 'key='"
echo "  - Focus events: cat /tmp/arrow_stderr.log | grep -i focus"
echo ""
