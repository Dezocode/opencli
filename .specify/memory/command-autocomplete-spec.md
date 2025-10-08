# Command Autocomplete System Specification

## What We're Building

An intelligent command autocomplete and suggestion system that intercepts all slash commands (`/`) at the input level, prevents them from being sent to the chat API, and provides interactive command selection with keyboard navigation.

## Problem Statement

**Current Issue:**
Users type slash commands like `/local` and they are sent to the chat API instead of being handled locally, causing:
- Wasted API tokens on local commands
- "Unknown command" responses from AI
- Confusing user experience
- Slow command execution (waiting for API roundtrip)

**Example Error:**
```
User types: /local
→ Sent to Claude API
→ AI responds: "I don't recognize that command..."
→ User confused, wastes tokens
```

## Value Proposition

**For Users:**
- Discover commands easily with autocomplete
- See all available commands by typing `/`
- Navigate with arrow keys (↑↓) and Enter
- Execute commands instantly without API delay
- Zero tokens wasted on local commands

**For Developers:**
- Unified command handling in one place
- Easy to add new commands (auto-discovered)
- Usage tracking for analytics
- Clean separation between local and API interactions

## Functional Requirements

### FR-1: Input Interception
**Must**: Catch all input starting with `/` before API submission
**Must Not**: Send any slash commands to chat API
**Must**: Work for both `/command` and `/command args` formats
**Implementation**: Hook into `MultiLineInput.on_key()` to detect `/` at position 0

### FR-2: Command Discovery & Search
**Must**: Show all registered commands from `command_registry.py`
**Must**: Filter commands as user types
**Must**: Search by exact prefix match (priority 1)
**Should**: Search by fuzzy match (priority 2)
**Should**: Search by description text (priority 3)
**Should**: Sort by usage frequency (priority 4)
**Could**: Search module implementation files (priority 5)

**Example:**
```
User types: /lo
Matches:
  1. /local (exact prefix)
  2. /reload (contains 'lo')
  3. /model (description contains "local" if applicable)
```

### FR-3: Interactive Selection Buffer
**Must**: Display suggestions in a buffer below multiline input
**Must**: Keep buffer within prompt area borders
**Must**: Support arrow key navigation (↑↓)
**Must**: Execute command on Enter key
**Must**: Close buffer on Esc key
**Should**: Auto-complete on Tab key (fill input, don't execute)
**Should**: Show max 10 visible suggestions, scroll if more
**Could**: Show command category/icons

**Visual Design:**
```
┌─────────────────────────────────────────────┐
│ Input:  /█                                  │  ← MultiLineInput
├─────────────────────────────────────────────┤
│ Commands (15 total, showing 10)             │  ← CommandSuggestionBuffer
│ ❯ /model - View or change model            │  ← Selected (Frontier accent)
│   /local - Local model recommendations      │
│   /reload - Hot-reload modules              │
│   /help - Show help menu                    │
│   /status - Show session info               │
│   /debug - Toggle debug mode                │
│   /performance - Performance monitoring     │
│   /providers - Manage API providers         │
│   /api - IPC server control                 │
│   /clear - Clear conversation history       │
│   ↓ 5 more...                               │
└─────────────────────────────────────────────┘
```

### FR-4: Usage Tracking
**Must**: Track how often each command is used
**Must**: Persist usage stats to `~/.opencli/command_usage.json`
**Should**: Sort suggestions by frequency when no search text
**Could**: Show usage count next to command name

**Data Structure:**
```json
{
  "/model": 127,
  "/local": 43,
  "/help": 89,
  "/status": 12,
  ...
}
```

### FR-5: Command Execution
**Must**: Execute selected command immediately
**Must**: Close suggestion buffer after execution
**Must**: Pass command arguments if provided
**Must**: Work with all existing command handlers
**Should**: Show command output in chat area

## Technical Architecture

### Component Structure
```
SimpleTUI
└── PromptContainer (Vertical layout)
    ├── MultiLineInput
    │   ├── Input field
    │   ├── on_key() handler [MODIFIED]
    │   └── History navigation
    └── CommandSuggestionBuffer [NEW]
        ├── Command list renderer
        ├── Selection state
        ├── Search/filter logic
        └── Navigation handler
```

### Files to Create

#### `modules/command_suggestions.py` (NEW - ~300 lines)
```python
class CommandSuggestionBuffer(Static):
    """Interactive command suggestion buffer with keyboard navigation"""

    selected_index: int = 0
    suggestions: List[CommandMatch] = []
    query: str = ""

    def on_key(self, event: Key):
        """Handle arrow keys and Enter"""

    def search_commands(self, query: str) -> List[CommandMatch]:
        """Search commands with priority ranking"""

    def render(self) -> RenderResult:
        """Render suggestion list with Frontier colors"""
```

### Files to Modify

#### `modules/multiline_input.py` (MODIFY - add ~50 lines)
```python
class MultiLineInput(TextArea):
    def on_key(self, event: Key):
        # Check if input starts with '/'
        if self.text.startswith('/'):
            # Show/update suggestion buffer
            self.show_command_suggestions(self.text)

            # Route navigation keys to buffer
            if event.key in ('up', 'down', 'enter'):
                return # Let buffer handle

        # Normal input handling...
```

#### `modules/command_registry.py` (MODIFY - add ~100 lines)
```python
class CommandRegistry:
    def search_commands(self, query: str) -> List[Dict]:
        """Search commands with fuzzy matching"""

    def record_usage(self, command: str):
        """Increment usage counter"""

    def get_usage_stats(self) -> Dict[str, int]:
        """Load usage stats from JSON"""

    def _save_usage_stats(self, stats: Dict[str, int]):
        """Persist to ~/.opencli/command_usage.json"""
```

#### `modules/simple_tui.py` (MODIFY - add ~30 lines)
```python
class SimpleTUI(App):
    def compose(self):
        # Update prompt container
        with Container(id="prompt-container"):
            yield MultiLineInput(id="prompt-input")
            yield CommandSuggestionBuffer(id="command-suggestions")

    def on_command_selected(self, command: str):
        """Execute selected command"""
        # Route to existing command handlers
```

## Data Flow

### 1. User Types `/`
```
MultiLineInput.on_key('/')
→ Detect slash at start
→ Create CommandSuggestionBuffer
→ Query CommandRegistry.get_all_commands()
→ Render all commands sorted by usage
→ Show buffer below input
```

### 2. User Types `/lo`
```
MultiLineInput.on_key('lo')
→ Update buffer with query "/lo"
→ CommandSuggestionBuffer.search_commands("/lo")
→ Filter: exact prefix → fuzzy → description
→ Sort: priority then usage frequency
→ Render filtered list
```

### 3. User Presses ↓
```
MultiLineInput.on_key('down')
→ Route to CommandSuggestionBuffer
→ Increment selected_index
→ Re-render with new selection
→ Scroll if needed
```

### 4. User Presses Enter
```
MultiLineInput.on_key('enter')
→ Route to CommandSuggestionBuffer
→ Get selected command
→ Post CommandSelected message
→ SimpleTUI.on_command_selected()
→ Execute command via existing handlers
→ Close suggestion buffer
→ Clear input field
```

## Search Algorithm

### Priority Levels
1. **Exact Prefix Match** (score: 1000)
   - `/model` matches `/model`, `/model add`, `/model list`

2. **Fuzzy Match** (score: 500)
   - `/lo` matches `/local`, `/reload`, `/ollama`

3. **Description Match** (score: 250)
   - `model` matches commands with "model" in description

4. **Usage Frequency** (score: 1-100)
   - Most used commands ranked higher

5. **Module Content** (score: 10)
   - Search implementation files (low priority, expensive)

### Scoring Algorithm
```python
def score_command(command: Command, query: str, usage: int) -> int:
    score = 0

    # Exact prefix match
    if command.name.startswith(query):
        score += 1000

    # Fuzzy match
    elif query.lower() in command.name.lower():
        score += 500

    # Description match
    elif query.lower() in command.description.lower():
        score += 250

    # Add usage frequency
    score += min(usage, 100)

    return score
```

## Non-Functional Requirements

### Performance
- **Suggestion display**: < 100ms from keypress
- **Search filtering**: < 50ms for 50+ commands
- **No input lag**: 0ms perceived delay
- **Memory efficient**: < 10MB for buffer

### Usability
- **Visual clarity**: Clear selection highlighting
- **Keyboard feel**: Natural navigation (same as terminal history)
- **Error tolerance**: Typos handled with fuzzy matching
- **Discoverability**: Typing `/` shows all commands

### Maintainability
- **Separation of concerns**: Buffer is independent widget
- **Reusable**: Could be used for other autocomplete needs
- **Well-documented**: Clear docstrings and comments
- **Testable**: Unit tests for search algorithm

## Edge Cases

### 1. No Matching Commands
```
Input: /xyz
Display: "No matching commands. Press Esc to cancel."
```

### 2. Single Match
```
Input: /local
Matches: 1
Display: Single command auto-selected
Action: Still require Enter to execute
```

### 3. Empty Query (`/` only)
```
Input: /
Display: All commands sorted by usage frequency
```

### 4. Long Command List
```
Matches: 25 commands
Display: First 10 visible, "↓ 15 more..."
Navigation: Page Up/Down or continuous ↑↓ scrolling
```

### 5. Command with Arguments
```
Input: /model claude-3
Match: /model command
Action: Execute with "claude-3" as argument
```

### 6. Rapid Typing
```
User types: /modellist (quickly)
System: Debounce search (50ms)
Display: Final query "/modellist" result
```

### 7. Invalid Command After Selection
```
Input: /invalidcmd
Display: No matches
Action: User presses Esc → normal input mode → sent to API
```

## Success Metrics

### Functionality
- ✅ 0% of slash commands sent to chat API
- ✅ 100% of registered commands discoverable
- ✅ < 3 average keystrokes to find command
- ✅ 100% keyboard navigation works

### Performance
- ✅ < 100ms suggestion display time
- ✅ < 50ms search filter time
- ✅ 0ms perceived input lag
- ✅ < 10MB memory usage

### User Experience
- ✅ No visual glitches or clipping
- ✅ Selection always visible (auto-scroll)
- ✅ Works with all existing commands
- ✅ Intuitive keyboard shortcuts

## Implementation Phases

### Phase 1: Foundation (Day 1)
- Create `CommandSuggestionBuffer` widget
- Basic rendering of command list
- Hook into `MultiLineInput.on_key()`
- Detect `/` and show buffer

### Phase 2: Search & Filter (Day 1-2)
- Implement exact prefix matching
- Add fuzzy matching algorithm
- Implement description search
- Basic sorting by match quality

### Phase 3: Navigation (Day 2)
- Arrow key navigation (↑↓)
- Enter to execute
- Esc to cancel
- Tab to autocomplete
- Visual selection highlighting

### Phase 4: Integration (Day 2-3)
- Connect to `CommandRegistry`
- Route to existing command handlers
- Handle command arguments
- Error handling

### Phase 5: Polish (Day 3)
- Usage tracking persistence
- Frontier color styling
- Smooth animations
- Performance optimization
- Edge case handling

### Phase 6: Testing (Day 3-4)
- Unit tests for search algorithm
- Integration tests for key routing
- E2E tests for command execution
- Performance benchmarks

## Future Enhancements

### Near-term
- Command aliases (e.g., `/m` → `/model`)
- Recent commands quick access
- Command parameter hints inline
- Command categories in UI

### Long-term
- Custom user shortcuts
- Command history search (Ctrl+R style)
- Regex pattern matching
- Natural language command search
- Command chaining (e.g., `/model x; /status`)

## Testing Strategy

### Unit Tests
```python
def test_exact_prefix_match():
    assert search_commands("/mod") includes "/model"

def test_fuzzy_match():
    assert search_commands("/lo") includes "/local" and "/reload"

def test_usage_frequency_sorting():
    # /help used 100 times, /model used 50 times
    results = search_commands("/")
    assert results[0] == "/help"
```

### Integration Tests
```python
def test_slash_intercepted():
    # User types "/model"
    # Verify NOT sent to API
    # Verify command executed locally

def test_arrow_navigation():
    # Show suggestions
    # Press down arrow 3 times
    # Verify 4th item selected
```

### E2E Tests
```python
def test_full_workflow():
    # Type "/lo"
    # Press down arrow once
    # Press Enter
    # Verify /reload executed
    # Verify buffer closed
```

## Documentation Updates

### User Documentation
- Add to `/help` command output
- Update README.md with command discovery section
- Add GIF demo of autocomplete in action

### Developer Documentation
- API docs for `CommandSuggestionBuffer`
- Search algorithm explanation
- How to add new search strategies

## Risk Mitigation

### Risk: Input lag from search
**Mitigation**: Debounce search, use efficient algorithms, profile performance

### Risk: Buffer positioning issues
**Mitigation**: Use Textual's layout system, test on different terminal sizes

### Risk: Key event conflicts
**Mitigation**: Clear precedence: buffer keys > input keys > global keys

### Risk: Command execution errors
**Mitigation**: Reuse existing error handling, comprehensive testing

## Acceptance Criteria

- ✅ Typing `/` immediately shows command suggestions
- ✅ Typing continues filters suggestions in real-time
- ✅ Arrow keys navigate, Enter executes, Esc cancels
- ✅ Zero slash commands sent to chat API (verified in logs)
- ✅ All registered commands appear in suggestions
- ✅ Search results feel instant (< 100ms)
- ✅ No visual glitches or UI blocking
- ✅ Usage tracking persists across sessions
- ✅ Works on all terminal sizes (80x24 minimum)
- ✅ No regressions in existing command functionality
