#!/bin/bash
# Comprehensive Arrow Key Diagnostic Test - Shell Wrapper
# Uses TUI Test Framework API to gather ALL data

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ARROW KEY COMPREHENSIVE DIAGNOSTIC                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "This diagnostic test will:"
echo "  • Launch opencli tui in LEFT window"
echo "  • Send commands from RIGHT window"
echo "  • Capture ALL debug output during arrow key presses"
echo "  • Show which functions fire (on_key vs BINDINGS)"
echo "  • Display state changes (before/after)"
echo "  • Identify root cause without assumptions"
echo ""
echo "Coverage (maps to ARROW_KEY_DEBUG_SUMMARY.md):"
echo "  ✓ Key event names and types"
echo "  ✓ Widget focus state"
echo "  ✓ Function call tracing"
echo "  ✓ Reactive property updates"
echo "  ✓ BINDINGS vs on_key() execution"
echo "  ✓ UI refresh calls"
echo ""
echo "Press Enter to run comprehensive diagnostic..."
read

# Run the Python diagnostic test
python3 test_arrow_key_diagnostic.py 2>&1 | tee /tmp/arrow_diagnostic_full.log

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "STDERR DEBUG ANALYSIS"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Searching for key debug markers..."
echo ""

# Extract key debug output
if grep -q "\[MultiLineInput.on_key\]" /tmp/arrow_diagnostic_full.log; then
    echo "✅ FOUND: on_key() method IS being called"
    echo ""
    echo "Key events detected:"
    grep "\[MultiLineInput.on_key\] KEY=" /tmp/arrow_diagnostic_full.log | head -10
    echo ""
else
    echo "❌ NOT FOUND: on_key() method NOT being called"
    echo "   → Root cause: Widget doesn't have focus OR event not reaching widget"
    echo ""
fi

if grep -q "\[ACTION_PERMISSION_DOWN\]" /tmp/arrow_diagnostic_full.log; then
    echo "✅ FOUND: action_permission_down() IS being called"
    echo ""
    grep "\[ACTION_PERMISSION_DOWN\]" /tmp/arrow_diagnostic_full.log
    echo ""
else
    echo "❌ NOT FOUND: action_permission_down() NOT being called"
    echo "   → BINDINGS may not be configured OR event blocked earlier"
    echo ""
fi

if grep -q "DOWN - changed" /tmp/arrow_diagnostic_full.log; then
    echo "✅ FOUND: Selection value IS changing in code"
    echo ""
    grep "DOWN - changed" /tmp/arrow_diagnostic_full.log
    echo ""
else
    echo "❌ NOT FOUND: Selection value NOT changing"
    echo "   → Logic may not be executing OR conditional check failing"
    echo ""
fi

if grep -q "refresh() called" /tmp/arrow_diagnostic_full.log; then
    echo "✅ FOUND: refresh() IS being called"
    echo ""
else
    echo "❌ NOT FOUND: refresh() NOT being called"
    echo "   → UI update not triggered"
    echo ""
fi

echo "═══════════════════════════════════════════════════════════════"
echo "VISUAL STATE COMPARISON"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ -f /tmp/before_down_*.txt ] 2>/dev/null; then
    echo "BEFORE DOWN arrow:"
    cat /tmp/before_down_*.txt 2>/dev/null | grep -i "▸\|yes\|no" | head -5
    echo ""
fi

if [ -f /tmp/after_down_*.txt ] 2>/dev/null; then
    echo "AFTER DOWN arrow:"
    cat /tmp/after_down_*.txt 2>/dev/null | grep -i "▸\|yes\|no" | head -5
    echo ""
fi

echo "═══════════════════════════════════════════════════════════════"
echo "ROOT CAUSE ANALYSIS"
echo "═══════════════════════════════════════════════════════════════"
echo ""

HAS_ON_KEY=$(grep -c "\[MultiLineInput.on_key\]" /tmp/arrow_diagnostic_full.log)
HAS_ACTION=$(grep -c "\[ACTION_PERMISSION_DOWN\]" /tmp/arrow_diagnostic_full.log)
HAS_CHANGE=$(grep -c "DOWN - changed" /tmp/arrow_diagnostic_full.log)
HAS_REFRESH=$(grep -c "refresh() called" /tmp/arrow_diagnostic_full.log)

if [ "$HAS_ON_KEY" -eq 0 ] && [ "$HAS_ACTION" -eq 0 ]; then
    echo "🔍 ROOT CAUSE: No code executed when DOWN pressed"
    echo ""
    echo "   Likely causes:"
    echo "   1. Widget doesn't have focus"
    echo "   2. Event not reaching MultiLineInput widget"
    echo "   3. Parent widget consuming event"
    echo ""
    echo "   Fix: Check focus state in _show_permission_prompt()"
    echo ""
elif [ "$HAS_ON_KEY" -eq 0 ] && [ "$HAS_ACTION" -gt 0 ]; then
    echo "🔍 ROOT CAUSE: BINDINGS firing but on_key() blocked"
    echo ""
    echo "   Likely causes:"
    echo "   1. BINDINGS executing action_permission_down()"
    echo "   2. on_key() prevent_default() not working"
    echo "   3. Event order: BINDINGS before on_key()"
    echo ""
    echo "   Fix: Remove BINDINGS or ensure on_key() executes first"
    echo ""
elif [ "$HAS_ON_KEY" -gt 0 ] && [ "$HAS_CHANGE" -eq 0 ]; then
    echo "🔍 ROOT CAUSE: on_key() called but logic not executing"
    echo ""
    echo "   Likely causes:"
    echo "   1. key name mismatch ('Down' vs 'down')"
    echo "   2. permission_prompt_data is None/false"
    echo "   3. options list is empty"
    echo "   4. Conditional check failing"
    echo ""
    echo "   Fix: Check key name and conditional logic"
    echo ""
elif [ "$HAS_CHANGE" -gt 0 ] && [ "$HAS_REFRESH" -eq 0 ]; then
    echo "🔍 ROOT CAUSE: Selection changes but refresh() not called"
    echo ""
    echo "   Fix: Add self.refresh() after selection change"
    echo ""
elif [ "$HAS_REFRESH" -gt 0 ]; then
    echo "🔍 ROOT CAUSE: Code executes correctly but UI not updating"
    echo ""
    echo "   Likely causes:"
    echo "   1. refresh() not triggering re-render"
    echo "   2. Reactive property not watched"
    echo "   3. render() using wrong property"
    echo "   4. Layout/display issue"
    echo ""
    echo "   Fix: Check reactive watchers and render() implementation"
    echo ""
else
    echo "🔍 Unable to determine root cause from debug output"
    echo ""
    echo "   Manual review needed of:"
    echo "   - Full log: /tmp/arrow_diagnostic_full.log"
    echo "   - Visual captures: /tmp/before_down_*.txt and /tmp/after_down_*.txt"
    echo ""
fi

echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Full diagnostic log saved to: /tmp/arrow_diagnostic_full.log"
echo ""
echo "To review full debug output:"
echo "  cat /tmp/arrow_diagnostic_full.log | grep -E '(KEY EVENT|DOWN|ACTION|changed|refresh)'"
echo ""
