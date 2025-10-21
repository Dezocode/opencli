#!/bin/bash

echo "=========================================="
echo "SHOWING KEY DIFFERENCES IN MISMATCHED FILES"
echo "=========================================="
echo ""

MAIN_DIR="/Users/dezmondhollins/opencli"
WORKTREE_DIR="/Users/dezmondhollins/.cursor/worktrees/opencli/1760885693580-9b0a9f"

# Check key files for important differences
check_file_for_keywords() {
    local file=$1
    shift
    local keywords=("$@")

    MAIN_FILE="$MAIN_DIR/$file"
    WORKTREE_FILE="$WORKTREE_DIR/$file"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "FILE: $file"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    for keyword in "${keywords[@]}"; do
        echo ""
        echo "Searching for: '$keyword'"

        MAIN_MATCH=$(grep -c "$keyword" "$MAIN_FILE" 2>/dev/null || echo "0")
        WORKTREE_MATCH=$(grep -c "$keyword" "$WORKTREE_FILE" 2>/dev/null || echo "0")

        echo "  Main:     $MAIN_MATCH occurrence(s)"
        echo "  Worktree: $WORKTREE_MATCH occurrence(s)"

        if [ "$MAIN_MATCH" != "$WORKTREE_MATCH" ]; then
            echo "  ⚠️  DIFFERENCE DETECTED"

            if [ "$WORKTREE_MATCH" -gt 0 ]; then
                echo ""
                echo "  Context from WORKTREE:"
                grep -B 2 -A 2 "$keyword" "$WORKTREE_FILE" | head -10
            fi
        fi
    done

    echo ""
}

# Check multiline_input.py for blur/unmount issues
check_file_for_keywords "modules/multiline_input.py" \
    "on_blur" \
    "NavigationEvent" \
    "PermissionCancelled"

# Check permission_handlers.py for permission flow
check_file_for_keywords "modules/tui/permission_handlers.py" \
    "_show_permission_prompt" \
    "permission_response" \
    "on_unmount"

# Check command_router.py for initialization
check_file_for_keywords "modules/command_router.py" \
    "_initialize_registrations" \
    "register_all" \
    "command_registry"

# Check executor.py for permission flow
check_file_for_keywords "modules/execution/executor.py" \
    "execute_command" \
    "permission_manager" \
    "_await_permission"

echo ""
echo "=========================================="
echo "LINE COUNT COMPARISON"
echo "=========================================="
echo ""

MISMATCH_FILES=(
    "modules/tui/permission_handlers.py"
    "modules/multiline_input.py"
    "modules/command_router.py"
    "modules/execution/executor.py"
    "modules/permissions/integration.py"
)

for file in "${MISMATCH_FILES[@]}"; do
    MAIN_FILE="$MAIN_DIR/$file"
    WORKTREE_FILE="$WORKTREE_DIR/$file"

    MAIN_LINES=$(wc -l < "$MAIN_FILE" 2>/dev/null || echo "0")
    WORKTREE_LINES=$(wc -l < "$WORKTREE_FILE" 2>/dev/null || echo "0")
    DIFF=$((WORKTREE_LINES - MAIN_LINES))

    if [ $DIFF -gt 0 ]; then
        echo "📈 $file: Worktree has +$DIFF lines"
    elif [ $DIFF -lt 0 ]; then
        echo "📉 $file: Worktree has $DIFF lines"
    else
        echo "➡️  $file: Same line count (content differs)"
    fi
done

echo ""
