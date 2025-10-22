# DEV20: Modularization and Legacy Removal

Date: 2025-10-22
Branch: dev20

Goals:
- Extract conversation orchestration from CLI legacy execution flow
- Prefer Async TUI by default; reduce reliance on legacy interactive mode
- Remove/neutralize legacy display/input components

Changes:
- Added `modules/conversation_manager.py`: Async conversation orchestration used by CLI/TUI
- Updated `cli/modules/execution_flow.py`: Delegate handle_user_prompt to ConversationManager
- Updated `cli/main.py`: Prefer Async TUI by default; fallback only when `--fallback` is explicitly provided
- Removed `modules/streaming_display_legacy.py`
- Kept compatibility shim `modules/multiline_input.py.legacy` (re-export to new widget)

Rationale:
- Breaks the monolith in `execution_flow.py` by moving conversation handling into a reusable module
- Aligns CLI and TUI flows on the same conversation engine
- Eliminates legacy display path and nudges users to the modern TUI

Follow-ups:
- Continue extracting residual responsibilities from `execution_flow.py` (agent selection, error handling, streaming processor) into modular services
- Update tests that import `modules.multiline_input` to rely on the shim or new path
- Eventually delete `modules/multiline_input.py.legacy` once references are removed
