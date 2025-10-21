# 100-Task Debug Plan - Arrow Keys Not Working in Permission Buffer

## Phase 1: READ ALL RELATED FILES (Tasks 1-50)

### Core Widget Files
- [ ] 1. Read `/Users/dezmondhollins/.opencli/cli/modules/multiline_input.py` COMPLETE FILE
- [ ] 2. Read `/Users/dezmondhollins/opencli/modules/multiline_input.py` COMPLETE FILE (source)
- [ ] 3. Compare source vs runtime multiline_input.py for differences
- [ ] 4. Read BINDINGS declaration (lines 29-35) in detail
- [ ] 5. Read action_permission_up method (line ~505) COMPLETE
- [ ] 6. Read action_permission_down method (line ~527) COMPLETE
- [ ] 7. Read on_key method (line ~328-400) COMPLETE
- [ ] 8. Read render method - check permission_selected_option usage
- [ ] 9. Read watch_permission_prompt_data method
- [ ] 10. Read watch_permission_selected_option method

### TUI Handler Files
- [ ] 11. Read `/Users/dezmondhollins/.opencli/cli/modules/tui/permission_handlers.py` COMPLETE
- [ ] 12. Read `/Users/dezmondhollins/opencli/modules/tui/permission_handlers.py` COMPLETE (source)
- [ ] 13. Read _show_permission_prompt method in detail
- [ ] 14. Read _clear_permission_prompt method
- [ ] 15. Read on_multi_line_input_permission_response handler
- [ ] 16. Read on_multi_line_input_permission_cancelled handler

### TUI Core Files
- [ ] 17. Read `/Users/dezmondhollins/.opencli/cli/modules/tui/core.py` COMPLETE
- [ ] 18. Read `/Users/dezmondhollins/opencli/modules/tui/core.py` COMPLETE (source)
- [ ] 19. Read OpenCLITUI class BINDINGS if any
- [ ] 20. Read compose() method - check layout
- [ ] 21. Read on_mount() method - check initialization
- [ ] 22. Read CSS styles section
- [ ] 23. Read _setup_permission_system method

### Command Handler Files
- [ ] 24. Read `/Users/dezmondhollins/opencli/modules/tui/command_handlers.py` COMPLETE
- [ ] 25. Check if command_handlers intercepts key events
- [ ] 26. Read any on_key methods in command_handlers

### Permission System Files
- [ ] 27. Read `/Users/dezmondhollins/opencli/modules/permissions/widget.py` COMPLETE
- [ ] 28. Read PermissionPrompt class - check if it's used
- [ ] 29. Read PermissionPrompt on_key method
- [ ] 30. Read PermissionPrompt BINDINGS if any
- [ ] 31. Read `/Users/dezmondhollins/opencli/modules/permissions/integration.py` COMPLETE
- [ ] 32. Read show_permission_prompt method
- [ ] 33. Read how PermissionPrompt widgets are created
- [ ] 34. Read `/Users/dezmondhollins/opencli/modules/permissions/manager.py` COMPLETE
- [ ] 35. Read permission buffer manager flow

### Display/Buffer Files
- [ ] 36. Read `/Users/dezmondhollins/opencli/modules/streaming_display/core.py` COMPLETE
- [ ] 37. Read StreamingDisplay on_key if exists
- [ ] 38. Read `/Users/dezmondhollins/opencli/modules/streaming_display/selection.py` COMPLETE
- [ ] 39. Read `/Users/dezmondhollins/opencli/modules/buffer_widget.py` COMPLETE
- [ ] 40. Read `/Users/dezmondhollins/opencli/modules/command_suggestions.py` COMPLETE

### Execution Flow Files
- [ ] 41. Read `/Users/dezmondhollins/opencli/cli/modules/execution_flow.py` COMPLETE
- [ ] 42. Read `/Users/dezmondhollins/opencli/modules/execution/executor.py` COMPLETE
- [ ] 43. Read execute_command method - check if it blocks
- [ ] 44. Read `/Users/dezmondhollins/opencli/modules/execution/permission_manager.py` COMPLETE
- [ ] 45. Read `/Users/dezmondhollins/opencli/modules/execution/unified_executor.py` COMPLETE

### Async/Message Handling Files
- [ ] 46. Read `/Users/dezmondhollins/opencli/modules/async_interactive/core.py` COMPLETE
- [ ] 47. Read message handling in async_interactive
- [ ] 48. Read `/Users/dezmondhollins/opencli/modules/tui/response_generator_mixin.py` COMPLETE
- [ ] 49. Read any event handlers in response_generator
- [ ] 50. Read `/Users/dezmondhollins/opencli/modules/unified_command_executor.py` COMPLETE

## Phase 2: VERIFY BINDINGS SYSTEM (Tasks 51-65)

- [ ] 51. Verify BINDINGS syntax matches Textual API
- [ ] 52. Check Binding("up", "permission_up", ...) is correct format
- [ ] 53. Verify action method name matches exactly: action_permission_up
- [ ] 54. Check action method signature: def action_permission_up(self) -> None
- [ ] 55. Verify BINDINGS is class-level attribute not instance
- [ ] 56. Check if show=False affects BINDINGS behavior
- [ ] 57. Verify priority parameter not needed
- [ ] 58. Check if parent class has conflicting BINDINGS
- [ ] 59. Grep ALL files for Binding("up") to find conflicts
- [ ] 60. Grep ALL files for Binding("down") to find conflicts
- [ ] 61. Check OpenCLITUI.BINDINGS for conflicts
- [ ] 62. Verify Widget inheritance chain
- [ ] 63. Check if BINDINGS are registered in Textual
- [ ] 64. Verify imports: from textual.binding import Binding
- [ ] 65. Test BINDINGS in minimal standalone app

## Phase 3: VERIFY EVENT FLOW (Tasks 66-80)

- [ ] 66. Check on_key() for early returns that block BINDINGS
- [ ] 67. Verify line 385: if key in ("up", "down") condition
- [ ] 68. Check if prevent_default() blocks BINDINGS
- [ ] 69. Grep for event.stop() calls
- [ ] 70. Check if suggestions_active interferes
- [ ] 71. Verify permission_prompt_data is set when buffer shows
- [ ] 72. Check if focus() is actually called
- [ ] 73. Verify has_focus returns True
- [ ] 74. Check can_focus = True in __init__
- [ ] 75. Verify widget is mounted and in DOM
- [ ] 76. Check CSS for display:none or visibility
- [ ] 77. Verify z-index doesn't hide widget
- [ ] 78. Check if modal/overlay blocks keys
- [ ] 79. Verify event routing from App to Widget
- [ ] 80. Check parent widgets don't consume events

## Phase 4: VERIFY DATA STATE (Tasks 81-90)

- [ ] 81. Check permission_prompt_data is not None
- [ ] 82. Verify options list is not empty
- [ ] 83. Check permission_selected_option starts at 0
- [ ] 84. Verify permission_selected_option is int not str
- [ ] 85. Check options structure matches expected format
- [ ] 86. Verify reactive() decorator on properties
- [ ] 87. Check watch methods trigger on changes
- [ ] 88. Verify refresh() is called in action methods
- [ ] 89. Check render() uses permission_selected_option
- [ ] 90. Verify UI actually updates on refresh()

## Phase 5: DEBUG AND TEST (Tasks 91-100)

- [ ] 91. Add debug logging to action_permission_up entry
- [ ] 92. Add debug logging to action_permission_down entry
- [ ] 93. Add debug to BINDINGS key event if possible
- [ ] 94. Capture stderr during manual test
- [ ] 95. Verify action methods are ENTERED (check logs)
- [ ] 96. Check if key events reach on_key
- [ ] 97. MD5 verify runtime matches source
- [ ] 98. Clear ALL Python cache
- [ ] 99. Test with opencli tui and capture ALL output
- [ ] 100. Create minimal reproduction case

---

## Progress Tracking

**Completed:** 0/100
**In Progress:** 0/100
**Pending:** 100/100

## Critical Findings

(Will be updated as tasks are completed)

---

Generated: 2025-10-21
