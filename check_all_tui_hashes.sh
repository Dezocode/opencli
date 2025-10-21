#!/bin/bash

echo "=========================================="
echo "COMPREHENSIVE TUI FILE HASH CHECK"
echo "Comparing main opencli vs worktree state"
echo "=========================================="
echo ""

MAIN_DIR="/Users/dezmondhollins/opencli"
WORKTREE_DIR="/Users/dezmondhollins/.cursor/worktrees/opencli/1760885693580-9b0a9f"

# All TUI-related files that could affect startup/unmount behavior
TUI_FILES=(
    "modules/async_interactive/core.py"
    "modules/async_interactive/__init__.py"
    "modules/async_interactive/client.py"
    "modules/async_interactive/session.py"
    "modules/async_interactive/permissions.py"
    "modules/async_interactive/ui_handlers.py"
    "modules/async_interactive/tools.py"
    "modules/async_interactive/streaming.py"
    "modules/async_interactive/buffer_system.py"
    "modules/tui/core.py"
    "modules/tui/__init__.py"
    "modules/tui/permission_handlers.py"
    "modules/tui/command_handlers.py"
    "modules/tui/model_handlers.py"
    "modules/tui/message_handler_mixin.py"
    "modules/tui/response_generator_mixin.py"
    "modules/tui/action_mixin.py"
    "modules/tui/status_lines.py"
    "modules/multiline_input.py"
    "modules/command_router.py"
    "modules/command_suggestions.py"
    "modules/buffer_widget.py"
    "modules/streaming_display/core.py"
    "modules/streaming_display/buffers.py"
    "modules/execution/executor.py"
    "modules/execution/permission_manager.py"
    "modules/execution/registry.py"
    "modules/permissions/integration.py"
    "modules/permissions/manager.py"
    "modules/permissions/validation.py"
    "modules/commands/command_registry.py"
    "modules/commands/registry.py"
)

MATCH_COUNT=0
MISMATCH_COUNT=0
MISSING_COUNT=0
TOTAL_COUNT=${#TUI_FILES[@]}

echo "Checking $TOTAL_COUNT TUI-related files..."
echo ""

for file in "${TUI_FILES[@]}"; do
    MAIN_FILE="$MAIN_DIR/$file"
    WORKTREE_FILE="$WORKTREE_DIR/$file"

    # Check if files exist
    if [ ! -f "$MAIN_FILE" ]; then
        echo "❌ MISSING IN MAIN: $file"
        ((MISSING_COUNT++))
        continue
    fi

    if [ ! -f "$WORKTREE_FILE" ]; then
        echo "⚠️  NOT IN WORKTREE: $file"
        ((MISSING_COUNT++))
        continue
    fi

    # Compare MD5 hashes
    MAIN_MD5=$(md5 -q "$MAIN_FILE")
    WORKTREE_MD5=$(md5 -q "$WORKTREE_FILE")

    if [ "$MAIN_MD5" == "$WORKTREE_MD5" ]; then
        echo "✅ MATCH: $file"
        ((MATCH_COUNT++))
    else
        echo ""
        echo "❌ MISMATCH: $file"
        echo "   Main MD5:     $MAIN_MD5"
        echo "   Worktree MD5: $WORKTREE_MD5"

        # Show modification times
        echo "   Main modified:     $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$MAIN_FILE")"
        echo "   Worktree modified: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$WORKTREE_FILE")"

        # Show file sizes
        MAIN_SIZE=$(stat -f "%z" "$MAIN_FILE")
        WORKTREE_SIZE=$(stat -f "%z" "$WORKTREE_FILE")
        echo "   Main size:     $MAIN_SIZE bytes"
        echo "   Worktree size: $WORKTREE_SIZE bytes"
        echo ""

        ((MISMATCH_COUNT++))
    fi
done

echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "Total files checked: $TOTAL_COUNT"
echo "✅ Matching:         $MATCH_COUNT"
echo "❌ Mismatched:       $MISMATCH_COUNT"
echo "⚠️  Missing:          $MISSING_COUNT"
echo ""

if [ $MISMATCH_COUNT -eq 0 ] && [ $MISSING_COUNT -eq 0 ]; then
    echo "🎉 ALL FILES MATCH - Runtime using worktree state!"
    exit 0
elif [ $MISMATCH_COUNT -gt 0 ]; then
    echo "⚠️  MISMATCHES FOUND - Runtime may be using old code!"
    echo ""
    echo "To sync mismatched files from worktree to main:"
    echo "  cp <worktree_file> <main_file>"
    exit 1
else
    echo "⚠️  Some files missing - partial sync"
    exit 1
fi
