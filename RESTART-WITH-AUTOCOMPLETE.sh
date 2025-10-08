#!/bin/bash
# Foolproof script to restart OpenCLI with autocomplete enabled

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  OpenCLI Autocomplete Restart Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Change to opencli directory
cd "$(dirname "$0")"

echo "Step 1: Killing any running OpenCLI processes..."
pkill -f "python3 opencli.py" 2>/dev/null && echo "   ✅ Killed running processes" || echo "   ℹ️  No running processes found"
sleep 1

echo ""
echo "Step 2: Clearing ALL Python bytecode cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo "   ✅ Cache cleared"

echo ""
echo "Step 3: Verifying autocomplete files..."
files_ok=true
if grep -q "CommandSuggestionBuffer" modules/simple_tui.py; then
    echo "   ✅ simple_tui.py has autocomplete"
else
    echo "   ❌ simple_tui.py missing autocomplete!"
    files_ok=false
fi

if grep -q "ShowCommandSuggestions" modules/multiline_input.py; then
    echo "   ✅ multiline_input.py has slash detection"
else
    echo "   ❌ multiline_input.py missing slash detection!"
    files_ok=false
fi

if [ -f "modules/command_suggestions.py" ]; then
    echo "   ✅ command_suggestions.py exists"
else
    echo "   ❌ command_suggestions.py missing!"
    files_ok=false
fi

if [ "$files_ok" = false ]; then
    echo ""
    echo "❌ AUTOCOMPLETE FILES INCOMPLETE!"
    echo "   Run: git pull or git stash && git pull"
    exit 1
fi

echo ""
echo "Step 4: Testing autocomplete components..."
python3 test_autocomplete.py > /tmp/autocomplete-test.log 2>&1
if grep -q "ALL TESTS PASSED" /tmp/autocomplete-test.log; then
    echo "   ✅ All components working"
else
    echo "   ⚠️  Some tests failed - check /tmp/autocomplete-test.log"
fi

echo ""
echo "Step 5: Setting environment for debug (optional)..."
export OPENCLI_DEBUG_AUTOCOMPLETE=1
echo "   ✅ Debug logging enabled"
echo "   📝 Log location: /tmp/opencli-autocomplete-debug.log"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Starting OpenCLI with Autocomplete..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 TO TEST AUTOCOMPLETE:"
echo "   1. Type: /"
echo "   2. You should see a buffer with commands"
echo "   3. Use ↑↓ arrows to navigate"
echo "   4. Press Enter to execute"
echo "   5. Press Esc to cancel"
echo ""
echo "📊 Commands available: 27 total"
echo "   /model, /local, /reload, /help, /status, etc."
echo ""
echo "🐛 If it doesn't work:"
echo "   cat /tmp/opencli-autocomplete-debug.log"
echo ""
echo "Starting in 3 seconds..."
sleep 3

# Start OpenCLI
python3 opencli.py
