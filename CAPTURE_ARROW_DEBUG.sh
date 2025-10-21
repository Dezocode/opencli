#!/bin/bash
# Capture debug output when pressing arrow keys

echo "Starting opencli with debug capture..."
echo "1. Type: /help"
echo "2. Press ENTER twice to show permission buffer"
echo "3. Press DOWN arrow"
echo "4. Press UP arrow"
echo "5. Press Ctrl+C to exit"
echo ""
echo "All stderr will be saved to /tmp/arrow_debug.log"
echo ""

opencli tui 2>/tmp/arrow_debug.log

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "ANALYZING DEBUG OUTPUT"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if action methods were called
echo "Checking if action_permission_down was called:"
grep "action_permission_down" /tmp/arrow_debug.log || echo "❌ NOT CALLED"
echo ""

echo "Checking if action_permission_up was called:"
grep "action_permission_up" /tmp/arrow_debug.log || echo "❌ NOT CALLED"
echo ""

echo "Checking if on_key received DOWN/UP:"
grep "KEY='up'" /tmp/arrow_debug.log || echo "❌ UP not seen"
grep "KEY='down'" /tmp/arrow_debug.log || echo "❌ DOWN not seen"
echo ""

echo "Full log saved to: /tmp/arrow_debug.log"
echo "View with: cat /tmp/arrow_debug.log | grep -E '(KEY=|action_permission|PERMISSION)'"
