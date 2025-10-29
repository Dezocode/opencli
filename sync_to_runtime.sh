#!/bin/bash

echo "=========================================="
echo "⚠️  SYNC SCRIPT DISABLED"
echo "=========================================="
echo ""
echo "This sync script has been DISABLED because it was reverting code."
echo ""
echo "Work directly in ~/.opencli (runtime) - DO NOT use this script!"
echo "All changes should be made in ~/.opencli/modules/ directly."
echo ""
echo "To re-enable, remove this exit statement."
echo ""
exit 0

DEV_DIR="/Users/dezmondhollins/opencli"
RUNTIME_DIR="$HOME/.opencli"

# All files that need to be in runtime (synced to ~/.opencli/modules/)
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
    "modules/input_widget/widget.py"
    "modules/input_widget/event_handler.py"
    "modules/input_widget/permission_renderer.py"
    "modules/input_widget/__init__.py"
    "modules/sdk/executor.py"
    "modules/sdk/__init__.py"
    "modules/command_router.py"
    "modules/command_suggestions.py"
    "modules/buffer_widget.py"
    "modules/docker_commands.py"
    "modules/docker_commands_unified.py"
    "modules/async_permissions.py"
    "modules/streaming_display/core.py"
    "modules/streaming_display/buffers.py"
    "modules/execution/executor.py"
    "modules/execution/permission_manager.py"
    "modules/execution/registry.py"
    "modules/permissions/__init__.py"
    "modules/permissions/integration.py"
    "modules/permissions/manager.py"
    "modules/permissions/validation.py"
    "modules/permissions/risk_assessment.py"
    "modules/permissions/templates.py"
    "modules/permissions/enums.py"
    "modules/permissions/analytics.py"
    "modules/permissions/audit.py"
    "modules/permissions/cache.py"
    "modules/permissions/i18n.py"
    "modules/permissions/task.py"
    "modules/permissions/widget.py"
    "modules/commands/command_registry.py"
    "modules/commands/registry.py"
    "modules/argument_parser.py"
    "modules/initialization.py"
    "modules/execution_flow.py"
    "modules/interactive_helpers.py"
)

SYNC_COUNT=0
SKIP_COUNT=0
ERROR_COUNT=0

echo "Syncing ${#TUI_FILES[@]} files to ~/.opencli/modules/ (single source of truth)..."
echo ""

for file in "${TUI_FILES[@]}"; do
    DEV_FILE="$DEV_DIR/$file"
    RUNTIME_FILE="$RUNTIME_DIR/$file"

    if [ ! -f "$DEV_FILE" ]; then
        echo "⚠️  SKIP: Dev file not found: $file"
        ((SKIP_COUNT++))
        continue
    fi

    # Create directory if needed
    RUNTIME_DIR_PATH=$(dirname "$RUNTIME_FILE")
    if [ ! -d "$RUNTIME_DIR_PATH" ]; then
        mkdir -p "$RUNTIME_DIR_PATH"
        echo "📁 Created directory: $(dirname "$file")"
    fi

    # Check if sync needed
    if [ -f "$RUNTIME_FILE" ]; then
        DEV_MD5=$(md5 -q "$DEV_FILE")
        RUNTIME_MD5=$(md5 -q "$RUNTIME_FILE")

        if [ "$DEV_MD5" == "$RUNTIME_MD5" ]; then
            echo "✓ Already synced: $file"
            ((SYNC_COUNT++))
            continue
        fi

        echo "📝 Updating: $file"
        echo "   Runtime MD5: $RUNTIME_MD5"
        echo "   Dev MD5:     $DEV_MD5"
    else
        echo "➕ Creating: $file"
    fi

    # Copy file
    if cp "$DEV_FILE" "$RUNTIME_FILE"; then
        # Verify
        NEW_MD5=$(md5 -q "$RUNTIME_FILE")
        DEV_MD5=$(md5 -q "$DEV_FILE")

        if [ "$NEW_MD5" == "$DEV_MD5" ]; then
            echo "   ✅ Synced successfully"
            SYNC_SUCCESS=true
        else
            echo "   ❌ Verification failed"
            SYNC_SUCCESS=false
        fi
    else
        echo "   ❌ Copy failed"
        SYNC_SUCCESS=false
    fi

    if [ "$SYNC_SUCCESS" = true ]; then
        ((SYNC_COUNT++))
    else
        ((ERROR_COUNT++))
    fi

    echo ""
done

echo "=========================================="
echo "SYNC SUMMARY"
echo "=========================================="
echo "Total files:        ${#TUI_FILES[@]}"
echo "✅ Synced:          $SYNC_COUNT"
echo "⚠️  Skipped:         $SKIP_COUNT"
echo "❌ Errors:          $ERROR_COUNT"
echo ""

if [ $ERROR_COUNT -eq 0 ]; then
    echo "🎉 Runtime directory successfully updated!"
    echo ""
    echo "Clearing Python cache in ~/.opencli..."
    find ~/.opencli -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find ~/.opencli -type f -name "*.pyc" -delete 2>/dev/null
    echo "✅ Cache cleared"
    echo ""
    echo "✅ SINGLE SOURCE OF TRUTH: ~/.opencli/modules/"
    echo "Runtime is now ready - opencli will use the updated code!"
    exit 0
else
    echo "⚠️  Some files failed to sync"
    exit 1
fi
