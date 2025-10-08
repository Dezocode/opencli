# Command Autocomplete System

## Goal
Implement an intelligent command autocomplete/suggestion system that intercepts slash commands (`/`) at the input level, preventing them from being sent to the chat API and providing interactive command selection.

## Problem Statement
Currently, slash commands like `/local` are being sent to the chat API instead of being caught and handled locally. This causes:
- API calls for commands that should be handled locally
- "Unknown command" responses from the AI
- Wasted API tokens
- Confusing user experience

## Success Criteria
1. ✅ Any user input starting with `/` is intercepted BEFORE being sent to the API
2. ✅ Command suggestions appear in a buffer underneath the multiline input
3. ✅ Suggestions are interactive (↑↓ arrows + Enter to select)
4. ✅ Suggestions are filtered based on:
   - Exact command name matches
   - Usage frequency
   - Command descriptions
   - Module file contents (secondary search)
5. ✅ Buffer appears within prompt area borders (stacked input fields)
6. ✅ All `/` input handling is unified in one place

## User Experience Flow

### 1. User types `/`
```
┌─────────────────────────────────────────────┐
│ Prompt Input                                │
│ /█                                          │
├─────────────────────────────────────────────┤
│ Command Suggestions (↑↓ to navigate)       │
│ ❯ /model - View or change model            │
│   /local - Local model recommendations      │
│   /reload - Hot-reload modules              │
│   /help - Show help menu                    │
│   /status - Show session info               │
└─────────────────────────────────────────────┘
```

### 2. User types `/lo`
```
┌─────────────────────────────────────────────┐
│ Prompt Input                                │
│ /lo█                                        │
├─────────────────────────────────────────────┤
│ Matching Commands (2)                       │
│ ❯ /local - Local model recommendations      │
│   /reload - Hot-reload modules (clear cache)│
└─────────────────────────────────────────────┘
```

### 3. User selects with Enter
- Command is executed immediately
- Suggestion buffer closes
- Output appears in chat area

## Technical Requirements

### 1. Input Interception
- Hook into multiline input key handler
- Detect `/` at start of input
- Prevent submission to API when showing suggestions

### 2. Command Registry Integration
- Use existing `command_registry.py` for command list
- Access command metadata (name, description, category)
- Track usage frequency per command
- Store in `~/.opencli/command_usage.json`

### 3. Suggestion Buffer Component
- New `CommandSuggestionBuffer` widget
- Positioned below `MultiLineInput` within prompt borders
- Shares parent container with input field
- Auto-sizing based on suggestion count (max 10 visible)
- Scrollable if > 10 matches

### 4. Search Algorithm Priority
1. **Exact prefix match** - Commands starting with typed text
2. **Fuzzy match** - Commands containing typed text
3. **Description match** - Descriptions containing typed text
4. **Usage frequency** - Sort by most-used commands
5. **Module content** - Search command implementation files (secondary)

### 5. Keyboard Navigation
- `↑` - Previous suggestion
- `↓` - Next suggestion
- `Enter` - Execute selected command
- `Esc` - Close suggestions, return to normal input
- `Tab` - Autocomplete to selected command (don't execute)
- Continue typing - Update suggestions in real-time

## Architecture Design

### Component Structure
```
PromptContainer
├── MultiLineInput (existing)
│   ├── Input text field
│   └── Key event handler (MODIFIED)
└── CommandSuggestionBuffer (NEW)
    ├── Suggestion list renderer
    ├── Selection state (current index)
    └── Search/filter logic
```

### Data Flow
```
User types "/"
→ MultiLineInput.on_key() detects it
→ Creates CommandSuggestionBuffer
→ Queries CommandRegistry for matches
→ Renders suggestions below input
→ Captures ↑↓Enter keys
→ On Enter: Execute command, close buffer
→ On Esc: Close buffer, normal input mode
```

### Files to Modify
1. **modules/multiline_input.py**
   - Add slash command detection in `on_key()`
   - Integrate with CommandSuggestionBuffer
   - Handle navigation key routing

2. **modules/command_suggestions.py** (NEW)
   - CommandSuggestionBuffer widget
   - Search/filter algorithm
   - Usage tracking

3. **modules/command_registry.py**
   - Add usage tracking methods
   - Add search methods
   - Persist usage stats

4. **modules/simple_tui.py**
   - Update prompt container layout
   - Handle command execution from selection

## Implementation Phases

### Phase 1: Input Interception (Foundation)
- Detect `/` at start of input
- Prevent API submission when suggestions active
- Basic suggestion display (no styling yet)

### Phase 2: Command Registry Search
- Integrate with command_registry.py
- Implement search algorithm
- Basic suggestion filtering

### Phase 3: Interactive Buffer
- Arrow key navigation
- Enter to execute
- Esc to cancel
- Visual selection highlighting

### Phase 4: Advanced Features
- Usage frequency tracking
- Module content search
- Tab autocomplete
- Fuzzy matching

### Phase 5: Polish
- Styling with Frontier colors
- Smooth animations
- Performance optimization
- Edge case handling

## Testing Strategy

### Unit Tests
- Command search algorithm accuracy
- Usage frequency sorting
- Fuzzy matching logic
- Key event handling

### Integration Tests
- Slash command interception
- Buffer positioning within borders
- Navigation state management
- Command execution flow

### User Testing
- Test with all existing commands
- Verify no API calls for local commands
- Check arrow key responsiveness
- Validate border alignment

## Edge Cases

### 1. No Matching Commands
```
┌─────────────────────────────────────────────┐
│ /xyz█                                       │
├─────────────────────────────────────────────┤
│ No matching commands                        │
│ Press Esc to cancel                         │
└─────────────────────────────────────────────┘
```

### 2. Empty Command List
- Show "Type a command name..."
- List most common commands

### 3. Long Descriptions
- Truncate with ellipsis
- Max width = prompt width - padding

### 4. Rapid Typing
- Debounce search (50ms)
- Don't block input

### 5. Command with Arguments
- `/model claude` - Execute if full command known
- Show arg hints in suggestion

## Success Metrics
- ✅ 0% of slash commands sent to API
- ✅ < 100ms suggestion display latency
- ✅ 100% of registered commands discoverable
- ✅ < 3 keystrokes average to find command
- ✅ No visual glitches or border overlap

## Related Features
- Existing command registry system
- Permission buffer (similar UI pattern)
- Multiline input with history
- Slash command handlers in async_interactive.py

## Future Enhancements
- Command aliases (e.g., `/m` → `/model`)
- Recent commands quick access
- Command categories in suggestions
- Inline parameter hints
- Command chaining (e.g., `/model x; /status`)
