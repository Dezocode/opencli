#!/bin/bash

echo "=========================================="
echo "SYNCING WORKTREE FILES TO MAIN"
echo "=========================================="
echo ""

MAIN_DIR="/Users/dezmondhollins/opencli"
WORKTREE_DIR="/Users/dezmondhollins/.cursor/worktrees/opencli/1760885693580-9b0a9f"

# Mismatched files that need syncing (worktree is newer)
SYNC_FILES=(
    "modules/tui/permission_handlers.py"
    "modules/multiline_input.py"
    "modules/command_router.py"
    "modules/execution/executor.py"
    "modules/permissions/integration.py"
)

echo "Will sync ${#SYNC_FILES[@]} files from worktree to main..."
echo ""

for file in "${SYNC_FILES[@]}"; do
    MAIN_FILE="$MAIN_DIR/$file"
    WORKTREE_FILE="$WORKTREE_DIR/$file"

    if [ ! -f "$WORKTREE_FILE" ]; then
        echo "❌ Worktree file not found: $file"
        continue
    fi

    # Show before state
    echo "📋 $file"
    if [ -f "$MAIN_FILE" ]; then
        MAIN_MD5=$(md5 -q "$MAIN_FILE")
        echo "   Before (main):     MD5=$MAIN_MD5, $(stat -f "%z bytes, %Sm" -t "%H:%M:%S" "$MAIN_FILE")"
    else
        echo "   Before (main):     NOT EXISTS"
    fi

    WORKTREE_MD5=$(md5 -q "$WORKTREE_FILE")
    echo "   From (worktree):   MD5=$WORKTREE_MD5, $(stat -f "%z bytes, %Sm" -t "%H:%M:%S" "$WORKTREE_FILE")"

    # Copy file
    cp "$WORKTREE_FILE" "$MAIN_FILE"

    # Verify
    NEW_MD5=$(md5 -q "$MAIN_FILE")
    if [ "$NEW_MD5" == "$WORKTREE_MD5" ]; then
        echo "   ✅ SYNCED"
    else
        echo "   ❌ SYNC FAILED"
    fi
    echo ""
done

echo "=========================================="
echo "SYNC COMPLETE"
echo "=========================================="
echo ""
echo "Running hash check to verify..."
echo ""

# Run the hash check again
/Users/dezmondhollins/opencli/check_all_tui_hashes.sh
