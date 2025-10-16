# OpenCLI TUI Refactor - Complete Connection Map

## Overview
This document maps all connection paths in the refactored TUI system to ensure end-to-end integration.

---

## 1. MESSAGE SUBMISSION FLOW

### Path: User Input → Message Handling
```
┌─────────────────────────────────────────────────────────────────────────┐
│ User presses Enter                                                      │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ MultiLineInput.action_submit()                                          │
│ Location: modules/multiline_input.py:456-465                            │
│                                                                           │
│ Logic:                                                                    │
│   if suggestions_active:                                                 │
│       post CommandSuggestionSelect message                               │
│       return                                                              │
│   if value.strip():                                                       │
│       post Submitted(value) message                                      │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ CommandHandlers.on_multi_line_input_submitted()                         │
│ Location: modules/tui/command_handlers.py:281-294                       │
│                                                                           │
│ Actions:                                                                  │
│   - Get user_input from event.value                                      │
│   - Clear prompt input                                                    │
│   - Call asyncio.create_task(self._handle_user_message())               │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ OpenCLITUI._handle_user_message()                                       │
│ Location: modules/tui/core.py:407-446                                   │
│                                                                           │
│ Routing:                                                                  │
│   if starts with '/':                                                     │
│       → Import route_command_unified from ..command_router              │
│       → Call route_command_unified(self, session, command, args)        │
│   else:                                                                   │
│       → Add to session                                                    │
│       → Call _generate_ai_response()                                     │
└───────────────────────────────────────────────────────────────────────┘
```

### Critical Files
- ✅ `modules/multiline_input.py` - Complete action_submit() with suggestions_active check
- ✅ `modules/tui/command_handlers.py` - Event handler for Submitted message
- ✅ `modules/tui/core.py` - _handle_user_message() implementation
- ✅ `modules/command_router.py` - route_command_unified() function

---

## 2. COMMAND SUGGESTION FLOW

### Path: Slash Detection → Suggestions Display
```
┌─────────────────────────────────────────────────────────────────────────┐
│ User types "/"                                                           │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ MultiLineInput.watch_value()                                             │
│ Location: modules/multiline_input.py:477-553                            │
│                                                                           │
│ Logic:                                                                    │
│   if new_value.startswith('/'):                                          │
│       suggestions_active = True                                          │
│       post ShowCommandSuggestions(new_value) message                     │
│   else:                                                                   │
│       if suggestions_active:                                             │
│           suggestions_active = False                                     │
│           post HideCommandSuggestions message                            │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ CommandHandlers.on_multi_line_input_show_command_suggestions()          │
│ Location: modules/tui/command_handlers.py:24-173                        │
│                                                                           │
│ Process:                                                                  │
│   1. Get suggestions buffer widget                                       │
│   2. Try to get SDK ExecutionRegistry:                                   │
│       app._command_router.executor.registry                              │
│   3. If SDK registry found:                                              │
│       → Call registry.search_commands(query)                             │
│       → Convert results to CommandMatch objects                          │
│   4. Else fallback to CommandRegistry (legacy)                           │
│   5. Update CommandSuggestionBuffer with matches                         │
│   6. Remove "hidden" class to show buffer                                │
│   7. FAILSAFE: Reset suggestions_active if no matches                    │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ CommandSuggestionBuffer.update_suggestions()                             │
│ Location: modules/command_suggestions.py:227-237                        │
│                                                                           │
│ Actions:                                                                  │
│   - Store new CommandMatch list                                          │
│   - Reset selected_index to 0                                            │
│   - Call refresh() to re-render                                          │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ CommandSuggestionBuffer.render()                                         │
│ Location: modules/command_suggestions.py:120-205                        │
│                                                                           │
│ Displays:                                                                 │
│   - Command count header                                                  │
│   - Health status indicators (✦ for SDK-compliant)                      │
│   - Command names with descriptions                                      │
│   - Usage counts                                                          │
│   - Selection indicator (❯) for current selection                       │
└───────────────────────────────────────────────────────────────────────┘
```

### Critical Files
- ✅ `modules/multiline_input.py` - watch_value() detects "/" and posts message
- ✅ `modules/tui/command_handlers.py` - ShowCommandSuggestions handler
- ✅ `modules/command_suggestions.py` - CommandSuggestionBuffer widget
- ✅ `modules/execution/registry.py` - search_commands() method

---

## 3. COMMAND SELECTION FLOW

### Path: Arrow Navigation → Enter Selection → Execution
```
┌─────────────────────────────────────────────────────────────────────────┐
│ User presses Up/Down (with suggestions_active=True)                     │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ MultiLineInput.on_key()                                                  │
│ Location: modules/multiline_input.py:325-455                            │
│                                                                           │
│ Priority 2 Handler (after permission prompts):                           │
│   if suggestions_active:                                                 │
│       if key == "up":                                                     │
│           post CommandSuggestionNavigate("up")                           │
│       elif key == "down":                                                 │
│           post CommandSuggestionNavigate("down")                         │
│       elif key == "escape":                                               │
│           post HideCommandSuggestions                                    │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ CommandHandlers.on_multi_line_input_command_suggestion_navigate()       │
│ Location: modules/tui/command_handlers.py:198-209                       │
│                                                                           │
│ Actions:                                                                  │
│   - Get suggestions buffer                                                │
│   - Call move_selection_up() or move_selection_down()                   │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ CommandSuggestionBuffer.move_selection_up/down()                         │
│ Location: modules/command_suggestions.py:207-215                        │
│                                                                           │
│ Updates selected_index with wrapping                                     │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                    (User presses Enter)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ MultiLineInput.action_submit()                                           │
│ Location: modules/multiline_input.py:456-465                            │
│                                                                           │
│ Detects suggestions_active=True, posts CommandSuggestionSelect message  │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ CommandHandlers.on_multi_line_input_command_suggestion_select()         │
│ Location: modules/tui/command_handlers.py:211-280                       │
│                                                                           │
│ Process:                                                                  │
│   1. Get selected CommandMatch from buffer                               │
│   2. Record usage in ExecutionRegistry:                                  │
│       executor.registry.record_usage(ExecutionType.COMMAND, name)       │
│   3. Replace input value with selected command                           │
│   4. Hide suggestions buffer                                             │
│   5. Reset suggestions_active = False                                    │
│   6. Clear input and call _handle_user_message(command)                 │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ → Routes to _handle_user_message() → command_router                     │
│ (See Command Routing Flow below)                                         │
└───────────────────────────────────────────────────────────────────────┘
```

### Critical Files
- ✅ `modules/multiline_input.py` - on_key() handles arrow keys with suggestions_active check
- ✅ `modules/tui/command_handlers.py` - Navigation and selection handlers
- ✅ `modules/command_suggestions.py` - Selection movement and get_selected_command()
- ✅ `modules/execution/registry.py` - record_usage() method

---

## 4. COMMAND ROUTING & EXECUTION FLOW

### Path: Command Router → ExecutionSystem → PermissionManager → Execution
```
┌─────────────────────────────────────────────────────────────────────────┐
│ route_command_unified(app, session, command, args)                      │
│ Location: modules/command_router.py:224-283                             │
│                                                                           │
│ Initialization:                                                           │
│   1. Create/get app._command_router (CommandRouter instance)            │
│   2. Call _initialize_registrations() if not initialized                │
│   3. Show startup buffer once (non-blocking)                             │
│   4. Call router.route_command(command, args)                            │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ CommandRouter._initialize_registrations()                                │
│ Location: modules/command_router.py:65-165                              │
│                                                                           │
│ SDK Registration:                                                         │
│   1. Import register_all from commands.registry                          │
│   2. Call await register_all(self.executor)                             │
│   3. Get enforcement stats from SDK                                      │
│   4. Set _initialized = True                                             │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ CommandRouter.route_command(command, args)                               │
│ Location: modules/command_router.py:167-212                             │
│                                                                           │
│ Execution:                                                                │
│   - Call executor.execute_command(name, app, session, args)             │
│   - Handle ValueError (not registered)                                   │
│   - Handle PermissionError (user denied)                                 │
│   - Handle Exception (execution error)                                   │
└──────────────────────────┬──────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ExecutionSystem.execute_command()                                        │
│ Location: modules/execution/executor.py                                 │
│                                                                           │
│ Flow:                                                                     │
│   1. Get registration from registry                                      │
│   2. Call PermissionManager for approval                                 │
│   3. If approved, execute handler                                        │
│   4. Return result                                                        │
└───────────────────────────────────────────────────────────────────────┘
```

### Critical Files
- ✅ `modules/command_router.py` - route_command_unified() and CommandRouter class
- ✅ `modules/commands/registry.py` - register_all() function
- ✅ `modules/execution/executor.py` - ExecutionSystem.execute_command()
- ✅ `modules/execution/registry.py` - ExecutionRegistry storage
- ✅ `modules/execution/permission_manager.py` - Permission checking

---

## 5. IMPORT PATHS - CRITICAL CONNECTIONS

### Correct Import Order (FIXED)
```python
# modules/tui/core.py:31-41
try:
    from ..multiline_input import MultiLineInput  # ✅ FIRST (complete implementation)
    HAS_MULTILINE = True
except Exception:
    try:
        from ..input_widget import MultiLineInput  # Fallback
        HAS_MULTILINE = True
    except Exception:
        MultiLineInput = None
        HAS_MULTILINE = False
```

### Module Resolution
```
Entry Point: modules/async_interactive/core.py
    ↓
Imports: from ..tui.core import OpenCLITUI
    ↓
Uses: modules/tui/core.py (✅ ACTIVE FILE)
    ↓
OpenCLITUI inherits from:
    - App (textual)
    - PermissionHandlers (modules/tui/permission_handlers.py)
    - CommandHandlers (modules/tui/command_handlers.py) ← ✅ Has all message handlers
    - ModelHandlers (modules/tui/model_handlers.py)
```

### Message Handler Registration
```
MultiLineInput Messages (defined in multiline_input.py):
    ✅ Submitted → on_multi_line_input_submitted
    ✅ ShowCommandSuggestions → on_multi_line_input_show_command_suggestions
    ✅ HideCommandSuggestions → on_multi_line_input_hide_command_suggestions
    ✅ CommandSuggestionNavigate → on_multi_line_input_command_suggestion_navigate
    ✅ CommandSuggestionSelect → on_multi_line_input_command_suggestion_select
    ✅ PermissionResponse → (handled in PermissionHandlers)
    ✅ PermissionCancelled → (handled in PermissionHandlers)
    ✅ NavigationEvent → (handled in PermissionHandlers)
```

---

## 6. WIDGET QUERY PATHS

### Widget IDs and Query Methods
```python
# In OpenCLITUI.compose() - modules/tui/core.py:284-316
Widgets:
    ✅ #stream-display (StreamingDisplay) - for chat content
    ✅ #command-suggestions (CommandSuggestionBuffer) - for autocomplete
    ✅ #sdk-loading-buffer (SDKLoadingBuffer) - for SDK init status
    ✅ #prompt-input (MultiLineInput) - for user input
    ✅ #performance-status (PerformanceStatusLine)
    ✅ #refactoring-status (RefactoringStatusLine)
    ✅ #status-line (StatusLine)

Query Examples:
    self.query_one("#prompt-input", MultiLineInput)
    self.query_one("#command-suggestions", CommandSuggestionBuffer)
    self.query_one("#stream-display", StreamingDisplay)
```

---

## 7. SDK REGISTRY INTEGRATION

### ExecutionRegistry Access Path
```
TUI Context (any handler method in CommandHandlers):
    ↓
self.app._command_router (CommandRouter instance)
    ↓
.executor (ExecutionSystem instance)
    ↓
.registry (ExecutionRegistry instance)
    ↓
Methods:
    ✅ .search_commands(query) → Returns List[Dict] with 'registration', 'name', 'score'
    ✅ .record_usage(ExecutionType.COMMAND, name) → Tracks usage
    ✅ .get(ExecutionType.COMMAND, name) → Get registration
```

### ExecutionRegistry.search_commands() Return Format
```python
# modules/execution/registry.py:231-288
Returns: List[Dict] where each dict has:
{
    'registration': ExecutionRegistration object,
    'name': str (command name including /),
    'score': int (relevance score)
}

ExecutionRegistration fields:
    .handler: Callable
    .description: str
    .category: ExecutionCategory
    .usage_count: int
    .enabled: bool
    .requires_approval: bool
```

---

## 8. FAILSAFE MECHANISMS

### Suggestions State Management
```python
# CRITICAL FAILSAFES in command_handlers.py:

1. No matches found (line 131-137):
    if not command_matches:
        prompt_input.suggestions_active = False  # ✅ Reset
        suggestions_buffer.add_class("hidden")   # ✅ Hide

2. Error handling (line 155-168):
    except Exception as e:
        prompt_input.suggestions_active = False  # ✅ Always reset on error

3. Hide suggestions (line 190-196):
    finally:
        if prompt_input:
            prompt_input.suggestions_active = False  # ✅ Always reset

4. Selection complete (line 237-239):
    suggestions_buffer.add_class("hidden")
    suggestions_buffer.clear()
    prompt_input.suggestions_active = False  # ✅ Reset after selection
```

---

## 9. VERIFICATION CHECKLIST

### ✅ All Connections Verified
- [x] MultiLineInput imports from correct module (multiline_input.py)
- [x] action_submit() checks suggestions_active before posting messages
- [x] All Message classes have corresponding handlers in CommandHandlers
- [x] ExecutionRegistry.search_commands() returns correct format
- [x] Usage tracking goes to ExecutionRegistry (not legacy CommandRegistry)
- [x] route_command_unified uses relative import (..command_router)
- [x] OpenCLITUI inherits from all required mixins
- [x] All widgets can be queried by ID
- [x] Failsafes reset suggestions_active in all edge cases

### ✅ End-to-End Paths Traced
- [x] User types message → Submitted → _handle_user_message → AI response
- [x] User types "/" → ShowCommandSuggestions → search_commands → display
- [x] User presses arrow → CommandSuggestionNavigate → move_selection
- [x] User presses Enter (suggestions) → CommandSuggestionSelect → record_usage → execute
- [x] Command routing → route_command_unified → executor.execute_command

---

## 10. KNOWN WORKING COMPONENTS

### Files with Complete Implementation
1. ✅ `modules/multiline_input.py` - Full featured input widget
2. ✅ `modules/tui/core.py` - Main TUI with correct imports
3. ✅ `modules/tui/command_handlers.py` - All message handlers
4. ✅ `modules/command_suggestions.py` - Suggestion buffer with health indicators
5. ✅ `modules/execution/registry.py` - Unified registry with search
6. ✅ `modules/command_router.py` - Command routing and initialization

### Files Needing No Changes
1. ✅ `modules/async_interactive/core.py` - Entry point (already has cleanup)
2. ✅ `modules/tui/permission_handlers.py` - Permission prompts
3. ✅ `modules/tui/model_handlers.py` - Model switching
4. ✅ `modules/tui/status_lines.py` - Status line widgets

---

## Summary

All critical paths are now properly connected:
1. **Message submission** works via complete MultiLineInput implementation
2. **Command suggestions** integrate with SDK ExecutionRegistry
3. **Command selection** tracks usage and routes to ExecutionSystem
4. **Command execution** flows through unified permission system
5. **Import paths** are consistent and correct
6. **Failsafes** prevent stuck states

The refactored TUI is fully integrated end-to-end.
