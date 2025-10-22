# DEV18: Permission Buffer Focus Fix

Date: 2025-10-22
Branch: dev18

Summary:
- Standardized focus and key handling to MultiLineInput overlay for permission prompts.
- Removed focusing of standalone PermissionPrompt widget in unified manager to prevent focus conflicts and event loss.

Root cause:
- Two competing implementations: a standalone `PermissionPrompt` widget and an overlay rendered via `MultiLineInput.permission_prompt_data`.
- The TUI forcibly focuses `#prompt-input` and reclaims focus during prompts, so the standalone widget either never receives focus or immediately loses it.
- Key routing during prompts is handled by `MultiLineInput.handle_key_event(...)->handle_permission_keys`, not `PermissionPrompt.on_key`.

Key changes:
- Edited `modules/permissions/integration.py` to stop focusing the standalone `PermissionPrompt`. The UI callback is responsible for showing the prompt via `#prompt-input` and setting focus appropriately.

Files modified:
- `modules/permissions/integration.py`

Behavioral impact:
- Permission navigation keys (up/down/enter/escape) now reliably reach the overlay handler.
- Eliminates race where standalone prompt gains then loses focus.

Follow-ups:
- If any tests assert `PermissionPrompt.on_key` is used, update them to assert overlay handling through `MultiLineInput`.
- Consider removing unused standalone `PermissionPrompt` usage where applicable.
