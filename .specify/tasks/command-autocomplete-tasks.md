# Command Autocomplete System - Implementation Tasks

## Task Breakdown

This document breaks down the Command Autocomplete System implementation into actionable, trackable tasks organized by phase.

---

## Phase 1: Foundation - CommandSuggestionBuffer Widget

### Task 1.1: Create command_suggestions.py Module Structure
**Priority**: Critical
**Estimated Time**: 30 minutes
**Status**: Pending

**Description**:
Create the base file structure for `modules/command_suggestions.py` with necessary imports and data structures.

**Acceptance Criteria**:
- [ ] File created at `modules/command_suggestions.py`
- [ ] All necessary imports added (Textual, Rich, dataclasses, typing)
- [ ] CommandMatch dataclass defined with all required fields
- [ ] Basic module docstring added
- [ ] File follows project code style

**Code Template**:
```python
"""
Command Suggestions Module

Provides intelligent command autocomplete with interactive selection buffer.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.console import RenderableType

@dataclass
class CommandMatch:
    """Represents a matched command with scoring metadata"""
    name: str
    description: str
    category: str
    score: int
    usage_count: int
```

---

### Task 1.2: Implement CommandSuggestionBuffer Base Widget
**Priority**: Critical
**Estimated Time**: 1 hour
**Status**: Pending
**Dependencies**: Task 1.1

**Description**:
Create the `CommandSuggestionBuffer` widget class with reactive properties and basic structure.

**Acceptance Criteria**:
- [ ] CommandSuggestionBuffer class inherits from Static
- [ ] Reactive properties defined (selected_index, suggestions, query, visible)
- [ ] __init__ method accepts registry parameter
- [ ] Widget has unique ID capability
- [ ] Basic CSS class attributes set

**Code Template**:
```python
class CommandSuggestionBuffer(Static):
    """Interactive command suggestion buffer with keyboard navigation"""

    DEFAULT_CSS = """
    CommandSuggestionBuffer {
        height: auto;
        max-height: 12;
        border: solid $accent;
        background: $surface;
    }
    """

    selected_index: int = reactive(0)
    suggestions: List[CommandMatch] = reactive([])
    query: str = reactive("")
    visible: bool = reactive(False)

    def __init__(self, registry=None, **kwargs):
        super().__init__(**kwargs)
        self.registry = registry
```

---

### Task 1.3: Implement Basic Rendering
**Priority**: Critical
**Estimated Time**: 1.5 hours
**Status**: Pending
**Dependencies**: Task 1.2

**Description**:
Implement the `render()` method to display command suggestions with proper formatting.

**Acceptance Criteria**:
- [ ] render() method returns Text object with Rich formatting
- [ ] Shows header with command count
- [ ] Displays max 10 visible suggestions
- [ ] Selected item highlighted with marker
- [ ] Empty state handled gracefully
- [ ] Text truncation for long descriptions

**Implementation Checklist**:
- [ ] Import Frontier colors
- [ ] Create header line with count
- [ ] Loop through suggestions (max 10)
- [ ] Apply selection marker (❯) to current index
- [ ] Style command names with Frontier accent color
- [ ] Style descriptions with dim color
- [ ] Handle edge case: no suggestions
- [ ] Handle edge case: suggestions less than 10

---

### Task 1.4: Add Frontier Color Styling
**Priority**: High
**Estimated Time**: 45 minutes
**Status**: Pending
**Dependencies**: Task 1.3

**Description**:
Apply Frontier color scheme to command suggestions for visual consistency.

**Acceptance Criteria**:
- [ ] Import FRONTIER_COLORS from frontier_colors.py
- [ ] Selected command uses accent color
- [ ] Command names use primary text color
- [ ] Descriptions use secondary/dim color
- [ ] Background respects terminal theme
- [ ] Border uses accent color
- [ ] Fallback colors if Frontier unavailable

**Color Mapping**:
- Selection marker: `FRONTIER_COLORS["accent"]` (#89B8C2)
- Command name (selected): `FRONTIER_COLORS["command"]`
- Command name (normal): `FRONTIER_COLORS["text_secondary"]`
- Description: `FRONTIER_COLORS["dim"]`
- Border: `FRONTIER_COLORS["accent"]`

---

## Phase 2: Search & Scoring Algorithm

### Task 2.1: Implement Command Scoring Algorithm
**Priority**: Critical
**Estimated Time**: 1.5 hours
**Status**: Pending
**Dependencies**: Task 1.2

**Description**:
Create the scoring algorithm that ranks commands based on exact match, fuzzy match, description match, and usage frequency.

**Acceptance Criteria**:
- [ ] score_command() method created
- [ ] Exact prefix match scores 1000 points
- [ ] Fuzzy match (contains) scores 500 points
- [ ] Description match scores 250 points
- [ ] Usage frequency adds 0-100 points
- [ ] Case-insensitive matching
- [ ] Handles empty query gracefully

**Test Cases to Validate**:
```python
# Exact prefix: "/model" with query "/mod" → 1000
# Fuzzy match: "/reload" with query "/lo" → 500
# Description: command with "local" in desc, query "local" → 250
# Usage bonus: any command with 50 uses → +50 to score
```

---

### Task 2.2: Implement Search Method
**Priority**: Critical
**Estimated Time**: 1 hour
**Status**: Pending
**Dependencies**: Task 2.1

**Description**:
Create `search_commands()` method that filters and ranks all commands based on query.

**Acceptance Criteria**:
- [ ] search_commands() method accepts query string and registry
- [ ] Retrieves all commands from registry
- [ ] Gets usage stats from registry
- [ ] Scores each command
- [ ] Filters out zero-score matches
- [ ] Sorts by score (descending)
- [ ] Returns List[CommandMatch]
- [ ] Handles empty/None query (show all by usage)

**Edge Cases**:
- [ ] Empty query → show all commands sorted by usage
- [ ] No matches → return empty list
- [ ] Single character query → still works
- [ ] Special characters in query → handled safely

---

### Task 2.3: Add Reactive Query Watcher
**Priority**: High
**Estimated Time**: 30 minutes
**Status**: Pending
**Dependencies**: Task 2.2

**Description**:
Implement reactive watcher for query changes to auto-update suggestions.

**Acceptance Criteria**:
- [ ] watch_query() method defined
- [ ] Triggered on self.query changes
- [ ] Calls search_commands() with new query
- [ ] Updates self.suggestions with results
- [ ] Resets selected_index to 0
- [ ] Triggers re-render automatically

**Implementation**:
```python
def watch_query(self, old_value: str, new_value: str) -> None:
    """Reactive handler for query changes"""
    if new_value:
        self.suggestions = self.search_commands(new_value, self.registry)
    else:
        self.suggestions = self.get_all_sorted_by_usage()
    self.selected_index = 0
```

---

## Phase 3: CommandRegistry Integration

### Task 3.1: Add Usage Tracking Infrastructure
**Priority**: Critical
**Estimated Time**: 1 hour
**Status**: Pending
**Dependencies**: None

**Description**:
Modify `modules/command_registry.py` to add usage tracking file path and initialization.

**Acceptance Criteria**:
- [ ] Usage file path added to __init__ (~/.opencli/command_usage.json)
- [ ] _usage_stats property added
- [ ] _load_usage_stats() method implemented
- [ ] Handles missing file gracefully
- [ ] Handles corrupt JSON gracefully
- [ ] Returns empty dict {} as fallback

**File Location**: `modules/command_registry.py`

**Changes**:
```python
def __init__(self, config_dir=None):
    # Existing code...
    self.usage_file = self.config_dir / "command_usage.json"
    self._usage_stats = self._load_usage_stats()
```

---

### Task 3.2: Implement Usage Persistence
**Priority**: Critical
**Estimated Time**: 45 minutes
**Status**: Pending
**Dependencies**: Task 3.1

**Description**:
Create methods to save and load usage statistics from JSON file.

**Acceptance Criteria**:
- [ ] _load_usage_stats() reads from JSON file
- [ ] _save_usage_stats() writes to JSON file
- [ ] JSON formatted with indent=2 for readability
- [ ] Silent failure on write errors (non-critical feature)
- [ ] File created automatically if missing
- [ ] Parent directory created if needed

**Error Handling**:
- [ ] FileNotFoundError → return {}
- [ ] JSONDecodeError → return {}, log warning
- [ ] PermissionError → silent fail on write

---

### Task 3.3: Add Usage Tracking Methods
**Priority**: Critical
**Estimated Time**: 30 minutes
**Status**: Pending
**Dependencies**: Task 3.2

**Description**:
Implement `record_usage()` and `get_usage_stats()` methods for tracking command frequency.

**Acceptance Criteria**:
- [ ] record_usage(command) increments counter
- [ ] Normalizes command names (adds / if missing)
- [ ] Saves to JSON after increment
- [ ] get_usage_stats() returns copy of dict
- [ ] Thread-safe (no concurrent write issues)

**Implementation**:
```python
def record_usage(self, command: str):
    """Increment usage counter for command"""
    if not command.startswith('/'):
        command = f'/{command}'

    self._usage_stats[command] = self._usage_stats.get(command, 0) + 1
    self._save_usage_stats()

def get_usage_stats(self) -> Dict[str, int]:
    """Get usage statistics"""
    return self._usage_stats.copy()
```

---

### Task 3.4: Add Search Helper Method
**Priority**: Medium
**Estimated Time**: 30 minutes
**Status**: Pending
**Dependencies**: Task 3.3

**Description**:
Create `get_all_commands_with_metadata()` helper for easy searching.

**Acceptance Criteria**:
- [ ] Returns dict of all enabled commands
- [ ] Includes name, description, category
- [ ] Filters out disabled commands
- [ ] Returns defensive copy (not reference to internal state)
- [ ] Used by CommandSuggestionBuffer for search

---

## Phase 4: MultiLineInput Integration

### Task 4.1: Add Slash Command Detection
**Priority**: Critical
**Estimated Time**: 1 hour
**Status**: Pending
**Dependencies**: None

**Description**:
Modify `modules/multiline_input.py` to detect when input starts with `/` character.

**Acceptance Criteria**:
- [ ] on_key() method checks if text starts with '/'
- [ ] Detection happens on every keystroke
- [ ] Works for both '/' typed first and pasted text
- [ ] Doesn't interfere with normal input
- [ ] Performance impact < 1ms

**File Location**: `modules/multiline_input.py`

**Implementation Approach**:
```python
def on_key(self, event: events.Key) -> None:
    current_text = self.text

    if current_text and current_text[0] == '/':
        self._handle_command_input(current_text)
        # Route special keys to buffer...

    super().on_key(event)
```

---

### Task 4.2: Implement Command Input Handler
**Priority**: Critical
**Estimated Time**: 45 minutes
**Status**: Pending
**Dependencies**: Task 4.1

**Description**:
Create `_handle_command_input()` method to manage command suggestion buffer state.

**Acceptance Criteria**:
- [ ] Posts ShowCommandSuggestions message on first '/'
- [ ] Posts UpdateCommandSuggestions message on continued typing
- [ ] Tracks buffer state (created vs updating)
- [ ] Passes query text in message
- [ ] Doesn't create multiple buffers

---

### Task 4.3: Add Navigation Key Routing
**Priority**: Critical
**Estimated Time**: 1 hour
**Status**: Pending
**Dependencies**: Task 4.2

**Description**:
Route arrow keys and Enter to suggestion buffer when active, preventing default input behavior.

**Acceptance Criteria**:
- [ ] Detects if suggestion buffer is visible
- [ ] Routes up/down/enter/escape/tab keys to buffer
- [ ] Calls event.prevent_default() to stop propagation
- [ ] Calls event.stop() to prevent bubbling
- [ ] Only routes when buffer actually visible
- [ ] Normal keys (letters) still work for typing

**Keys to Route**:
- ↑ (up) → Navigate to previous suggestion
- ↓ (down) → Navigate to next suggestion
- Enter → Execute selected command
- Esc → Close buffer
- Tab → Autocomplete (fill input, don't execute)

---

### Task 4.4: Prevent API Submission for Commands
**Priority**: Critical
**Estimated Time**: 30 minutes
**Status**: Pending
**Dependencies**: Task 4.3

**Description**:
Override submit behavior to prevent slash commands from being sent to chat API.

**Acceptance Criteria**:
- [ ] on_submit() checks if text starts with '/'
- [ ] Checks if suggestion buffer is visible
- [ ] If both true, prevent default submission
- [ ] Don't post message to chat handler
- [ ] Allow normal text submission (non-slash)

**Critical**: This task directly fixes the bug where `/local` is sent to API!

---

### Task 4.5: Create Message Classes
**Priority**: High
**Estimated Time**: 30 minutes
**Status**: Pending
**Dependencies**: None

**Description**:
Define Textual message classes for command suggestion communication.

**Acceptance Criteria**:
- [ ] ShowCommandSuggestions message class created
- [ ] UpdateCommandSuggestions message with query parameter
- [ ] CommandSelected message with command and args
- [ ] AutocompleteCommand message for Tab key
- [ ] All inherit from textual.message.Message
- [ ] Proper type hints for all parameters

**Message Definitions**:
```python
class ShowCommandSuggestions(Message):
    """Posted when slash command first detected"""
    pass

class UpdateCommandSuggestions(Message):
    """Posted when query text changes"""
    query: str

class CommandSelected(Message):
    """Posted when user executes a command"""
    command: str
    args: Optional[str] = None
```

---

## Phase 5: SimpleTUI Orchestration

### Task 5.1: Update Compose Method
**Priority**: Critical
**Estimated Time**: 30 minutes
**Status**: Pending
**Dependencies**: Task 1.2

**Description**:
Modify SimpleTUI's compose() to include CommandSuggestionBuffer in layout.

**Acceptance Criteria**:
- [ ] Buffer added to prompt container
- [ ] Positioned below MultiLineInput
- [ ] Initially hidden (classes="hidden")
- [ ] ID set to "command-suggestions"
- [ ] Vertical layout container used
- [ ] Registry passed to buffer constructor

**File Location**: `modules/simple_tui.py`

**Layout Structure**:
```python
with Vertical(id="prompt-container"):
    yield MultiLineInput(id="prompt-input")
    yield CommandSuggestionBuffer(
        id="command-suggestions",
        registry=self.command_registry,
        classes="hidden"
    )
```

---

### Task 5.2: Implement Show Suggestions Handler
**Priority**: Critical
**Estimated Time**: 45 minutes
**Status**: Pending
**Dependencies**: Task 5.1, Task 4.5

**Description**:
Handle ShowCommandSuggestions message to display the buffer.

**Acceptance Criteria**:
- [ ] on_show_command_suggestions() method created
- [ ] Queries buffer from DOM (#command-suggestions)
- [ ] Sets buffer.visible = True
- [ ] Initializes buffer.query = "/"
- [ ] Passes command registry reference
- [ ] Triggers buffer refresh

---

### Task 5.3: Implement Update Suggestions Handler
**Priority**: Critical
**Estimated Time**: 30 minutes
**Status**: Pending
**Dependencies**: Task 5.2

**Description**:
Handle UpdateCommandSuggestions message to update search query.

**Acceptance Criteria**:
- [ ] on_update_command_suggestions() method created
- [ ] Queries buffer from DOM
- [ ] Updates buffer.query with event.query
- [ ] Reactive system auto-triggers re-render
- [ ] No manual refresh needed

---

### Task 5.4: Implement Command Execution Handler
**Priority**: Critical
**Estimated Time**: 1 hour
**Status**: Pending
**Dependencies**: Task 5.3

**Description**:
Handle CommandSelected message to execute the chosen command and close buffer.

**Acceptance Criteria**:
- [ ] on_command_selected() method created
- [ ] Hides suggestion buffer (visible = False)
- [ ] Records usage via registry.record_usage()
- [ ] Parses command and arguments
- [ ] Routes to existing _handle_user_message()
- [ ] Clears input field after execution
- [ ] Handles errors gracefully

**Execution Flow**:
1. Hide buffer
2. Record usage
3. Execute command via existing handler
4. Clear input
5. If error, show message but don't crash

---

### Task 5.5: Add Buffer Navigation Message Handler
**Priority**: High
**Estimated Time**: 45 minutes
**Status**: Pending
**Dependencies**: Task 5.4

**Description**:
Handle navigation messages from the buffer (arrow keys, Enter, Esc).

**Acceptance Criteria**:
- [ ] Handles BufferNavigate message
- [ ] Up arrow decrements selected_index
- [ ] Down arrow increments selected_index
- [ ] Bounds checking (0 to len-1)
- [ ] Enter triggers CommandSelected message
- [ ] Esc hides buffer
- [ ] Tab triggers autocomplete

---

## Phase 6: Keyboard Navigation & Polish

### Task 6.1: Implement Full Keyboard Handler
**Priority**: Critical
**Estimated Time**: 1.5 hours
**Status**: Pending
**Dependencies**: Task 1.2

**Description**:
Add comprehensive keyboard event handling to CommandSuggestionBuffer.

**Acceptance Criteria**:
- [ ] on_key() method handles all navigation keys
- [ ] Up arrow: decrement selection
- [ ] Down arrow: increment selection
- [ ] Enter: post CommandSelected message
- [ ] Esc: hide buffer
- [ ] Tab: post AutocompleteCommand message
- [ ] All keys call event.prevent_default()
- [ ] Boundary checking prevents index out of range

**File Location**: `modules/command_suggestions.py`

---

### Task 6.2: Add Scrolling Logic
**Priority**: Medium
**Estimated Time**: 1 hour
**Status**: Pending
**Dependencies**: Task 6.1

**Description**:
Implement virtual scrolling to ensure selected item is always visible.

**Acceptance Criteria**:
- [ ] _scroll_to_selection() method created
- [ ] Calculates scroll_offset based on selected_index
- [ ] Ensures selected item in visible range (10 items)
- [ ] Smooth scrolling feel (no jumps)
- [ ] Called after selection changes

**Algorithm**:
```python
def _scroll_to_selection(self):
    # Keep selected item in middle of viewport when possible
    viewport_size = 10
    if self.selected_index > self.scroll_offset + viewport_size - 1:
        self.scroll_offset = self.selected_index - viewport_size + 1
    elif self.selected_index < self.scroll_offset:
        self.scroll_offset = self.selected_index
```

---

### Task 6.3: Add Show/Hide Animations
**Priority**: Low
**Estimated Time**: 45 minutes
**Status**: Pending
**Dependencies**: Task 1.2

**Description**:
Add smooth CSS transitions for buffer appearance/disappearance.

**Acceptance Criteria**:
- [ ] watch_visible() reactive watcher created
- [ ] Adds/removes CSS classes (shown/hidden)
- [ ] CSS transition property set (200ms)
- [ ] Opacity fade-in/out
- [ ] Height animation (0 to auto)
- [ ] No layout jumping

**CSS**:
```css
CommandSuggestionBuffer.hidden {
    height: 0;
    opacity: 0;
    transition: all 200ms ease-out;
}

CommandSuggestionBuffer.shown {
    opacity: 1;
    transition: all 200ms ease-in;
}
```

---

### Task 6.4: Add Usage Count Display
**Priority**: Low
**Estimated Time**: 30 minutes
**Status**: Pending
**Dependencies**: Task 6.1

**Description**:
Optionally display usage count next to frequently used commands.

**Acceptance Criteria**:
- [ ] Usage count shown for commands used > 10 times
- [ ] Format: "command - description (used 25x)"
- [ ] Dim color for usage count
- [ ] Doesn't clutter UI for infrequently used commands

---

## Testing Tasks

### Task T.1: Write Unit Tests for Scoring
**Priority**: High
**Estimated Time**: 1 hour
**Status**: Pending
**Dependencies**: Task 2.1

**Description**:
Create unit tests for command scoring algorithm.

**Test Cases**:
- [ ] Exact prefix match scores correctly
- [ ] Fuzzy match scores correctly
- [ ] Description match scores correctly
- [ ] Usage frequency adds bonus points
- [ ] Case-insensitive matching works
- [ ] Empty query handled
- [ ] Special characters handled

**File**: `tests/test_command_suggestions.py`

---

### Task T.2: Write Integration Tests for Key Routing
**Priority**: High
**Estimated Time**: 1.5 hours
**Status**: Pending
**Dependencies**: Task 4.3

**Description**:
Test that keyboard events are routed correctly between input and buffer.

**Test Cases**:
- [ ] Slash detection works
- [ ] Buffer appears on '/'
- [ ] Arrow keys routed to buffer when visible
- [ ] Arrow keys work normally when buffer hidden
- [ ] Enter executes command
- [ ] Esc closes buffer
- [ ] Normal keys continue typing

**File**: `tests/test_command_flow.py`

---

### Task T.3: Write E2E Tests for Full Workflow
**Priority**: High
**Estimated Time**: 2 hours
**Status**: Pending
**Dependencies**: Task 5.4

**Description**:
End-to-end tests covering complete user workflows.

**Test Scenarios**:
- [ ] Type '/', see suggestions, navigate, execute
- [ ] Type '/lo', see filtered results
- [ ] Select command, verify execution
- [ ] Verify no API call made
- [ ] Verify usage recorded
- [ ] Multiple executions increment usage

**File**: `tests/test_e2e_commands.py`

---

### Task T.4: Performance Benchmarks
**Priority**: Medium
**Estimated Time**: 1 hour
**Status**: Pending
**Dependencies**: Task 2.2

**Description**:
Benchmark search performance with large command sets.

**Benchmarks**:
- [ ] Search 100 commands: < 50ms
- [ ] Render buffer: < 16ms (60 FPS)
- [ ] Keystroke to display: < 100ms
- [ ] Memory overhead: < 10MB

---

## Documentation Tasks

### Task D.1: Update Help Command
**Priority**: Medium
**Estimated Time**: 30 minutes
**Status**: Pending
**Dependencies**: Task 5.4

**Description**:
Add command autocomplete info to `/help` output.

**Content**:
- [ ] Mention typing '/' for autocomplete
- [ ] Document arrow key navigation
- [ ] Explain Enter to execute
- [ ] Note usage tracking

---

### Task D.2: Create User Documentation
**Priority**: Medium
**Estimated Time**: 1 hour
**Status**: Pending
**Dependencies**: Task D.1

**Description**:
Add "Command Discovery" section to README.md.

**Sections**:
- [ ] How to trigger autocomplete
- [ ] Keyboard shortcuts
- [ ] Search behavior
- [ ] GIF demo

---

### Task D.3: Create Developer Documentation
**Priority**: Low
**Estimated Time**: 1 hour
**Status**: Pending
**Dependencies**: All Phase 6 tasks

**Description**:
Document architecture and extension points.

**Content**:
- [ ] API docs for CommandSuggestionBuffer
- [ ] Search algorithm explanation
- [ ] Message flow diagrams
- [ ] How to customize search

---

## Summary

**Total Tasks**: 39 tasks
- **Phase 1**: 4 tasks (3.75 hours)
- **Phase 2**: 3 tasks (3 hours)
- **Phase 3**: 4 tasks (2.75 hours)
- **Phase 4**: 5 tasks (4 hours)
- **Phase 5**: 5 tasks (3.5 hours)
- **Phase 6**: 4 tasks (3.75 hours)
- **Testing**: 4 tasks (5.5 hours)
- **Documentation**: 3 tasks (2.5 hours)

**Total Estimated Time**: ~28.75 hours (includes testing and documentation)

**Critical Path**: Tasks 1.1 → 1.2 → 1.3 → 2.1 → 2.2 → 4.1 → 4.4 → 5.4

**Next Actions**:
1. Start with Task 1.1 (Create module structure)
2. Complete Phase 1 to have working widget
3. Add search (Phase 2)
4. Integrate with input (Phase 4)
5. Wire up TUI (Phase 5)
6. Polish and test (Phases 6, Testing)
