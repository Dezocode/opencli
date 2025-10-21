#!/bin/bash

echo "=========================================="
echo "UNMOUNT FIX VALIDATION TEST"
echo "=========================================="
echo ""

# Clear Python cache
echo "1. Clearing Python cache..."
find /Users/dezmondhollins/opencli -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find /Users/dezmondhollins/opencli -type f -name "*.pyc" -delete 2>/dev/null
echo "   ✓ Cache cleared"
echo ""

# Show file timestamps
echo "2. Checking file modification times..."
echo ""
echo "Main file:"
ls -lh /Users/dezmondhollins/opencli/modules/async_interactive/core.py | awk '{print "   Modified: "$6, $7, $8}'
stat -f "   Size: %z bytes" /Users/dezmondhollins/opencli/modules/async_interactive/core.py
md5_main=$(md5 -q /Users/dezmondhollins/opencli/modules/async_interactive/core.py)
echo "   MD5: $md5_main"
echo ""

if [ -f "/Users/dezmondhollins/.cursor/worktrees/opencli/1760885693580-9b0a9f/modules/async_interactive/core.py" ]; then
    echo "Worktree file:"
    ls -lh /Users/dezmondhollins/.cursor/worktrees/opencli/1760885693580-9b0a9f/modules/async_interactive/core.py | awk '{print "   Modified: "$6, $7, $8}'
    stat -f "   Size: %z bytes" /Users/dezmondhollins/.cursor/worktrees/opencli/1760885693580-9b0a9f/modules/async_interactive/core.py
    md5_worktree=$(md5 -q /Users/dezmondhollins/.cursor/worktrees/opencli/1760885693580-9b0a9f/modules/async_interactive/core.py)
    echo "   MD5: $md5_worktree"
    echo ""

    if [ "$md5_main" == "$md5_worktree" ]; then
        echo "   ✓ Files match (MD5 identical)"
    else
        echo "   ⚠️  Files differ (MD5 mismatch)"
    fi
    echo ""
fi

# Check for fix markers
echo "3. Checking for fix markers in source..."
if grep -q "# NOTE: Textual handles cleanup automatically" /Users/dezmondhollins/opencli/modules/async_interactive/core.py; then
    echo "   ✓ Fix marker found"
else
    echo "   ❌ Fix marker NOT found"
fi

if grep -q "\[TUI\] Starting app.run_async\(\)" /Users/dezmondhollins/opencli/modules/async_interactive/core.py; then
    echo "   ✓ New logging found"
else
    echo "   ❌ New logging NOT found"
fi

if grep -q "if hasattr(app, 'on_unmount'):" /Users/dezmondhollins/opencli/modules/async_interactive/core.py; then
    # Check if it's in the finally block (bad) or elsewhere (maybe ok)
    echo "   ⚠️  Manual on_unmount call found (checking context...)"

    # Extract context around the line
    grep -A 2 -B 2 "if hasattr(app, 'on_unmount'):" /Users/dezmondhollins/opencli/modules/async_interactive/core.py | head -5
else
    echo "   ✓ No manual on_unmount call"
fi
echo ""

# Run pytest
echo "=========================================="
echo "RUNNING PYTEST"
echo "=========================================="
echo ""

cd /Users/dezmondhollins/opencli
python3 -m pytest test_unmount_fix_validation.py -v -s --tb=short

echo ""
echo "=========================================="
echo "TEST COMPLETE"
echo "=========================================="
