# OpenCLI Widget Naming Convention

## Two Distinct Interactive Widgets

### 1. Command Suggestion Buffer (Autocomplete)
**Widget Class**: `CommandSuggestionBuffer`
**CSS ID**: `#command-suggestions`
**Location**: `modules/command_suggestions.py`
**Purpose**: Interactive slash command discovery and autocomplete
**Trigger**: User types `/` in input
**Navigation**: Arrow keys ↑↓, Enter to execute, Esc to cancel
**Data Source**: `CommandRegistry.search_commands()`

**Usage in code:**
```python
# Get the widget
suggestions_buffer = self.query_one("#command-suggestions", CommandSuggestionBuffer)

# Update suggestions
suggestions_buffer.update_suggestions(command_matches, query)

# Show/hide
suggestions_buffer.remove_class("hidden")
suggestions_buffer.add_class("hidden")
```

**State tracking:**
- `MultiLineInput.suggestions_active` (bool) - tracks if autocomplete is shown

---

### 2. Permission Prompt Buffer
**Widget Class**: Part of `MultiLineInput` (via `permission_prompt_data`)
**CSS ID**: `#prompt-input` (renders inside MultiLineInput)
**Location**: Rendered by `MultiLineInput._render_permission_prompt()`
**Purpose**: Interactive permission selection for tool/command execution
**Trigger**: Tools or commands that need permission
**Navigation**: Arrow keys ↑↓, Enter to select, Esc to cancel
**Data Source**: `async_permissions.py` / permission handlers

**Usage in code:**
```python
# Get the widget
prompt_input = self.query_one("#prompt-input", MultiLineInput)

# Set permission prompt
prompt_input.permission_prompt_data = {
    'title': 'Permission Required',
    'message': 'Allow this action?',
    'options': [
        {'text': 'Allow', 'response': PermissionResponse.ALLOW_ONCE},
        {'text': 'Deny', 'response': PermissionResponse.DENY}
    ]
}

# Clear permission prompt
prompt_input.permission_prompt_data = None
```

**State tracking:**
- `MultiLineInput.permission_prompt_data` (dict or None) - the prompt content
- `MultiLineInput.permission_selected_option` (int) - currently selected option

---

## Visual Layout

```
┌─────────────────────────────────────────────────┐
│ Chat Content Area                               │
│ (messages, responses, etc.)                     │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│ Status Line                                     │
├─────────────────────────────────────────────────┤
│ Prompt Container                                │
│ ┌───────────────────────────────────────────┐   │
│ │ MultiLineInput (#prompt-input)            │   │  ← Normal input mode
│ │ > /local█                                 │   │
│ └───────────────────────────────────────────┘   │
│ ┌───────────────────────────────────────────┐   │
│ │ CommandSuggestionBuffer                   │   │  ← Autocomplete (hidden by default)
│ │ (#command-suggestions)                    │   │
│ │ Commands (3)                              │   │
│ │ ❯ /local - Local model recommendations    │   │
│ │   /reload - Hot-reload modules            │   │
│ │   /model - View or change model           │   │
│ └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

**OR when permissions active:**

```
┌─────────────────────────────────────────────────┐
│ Prompt Container                                │
│ ┌───────────────────────────────────────────┐   │
│ │ MultiLineInput - Permission Mode          │   │  ← Permission prompt
│ │ Permission Required                       │   │
│ │                                           │   │
│ │ Allow Read tool to access file.txt?      │   │
│ │                                           │   │
│ │ ▸ Allow Once                              │   │
│ │   Allow Always                            │   │
│ │   Deny                                    │   │
│ └───────────────────────────────────────────┘   │
│ ┌───────────────────────────────────────────┐   │
│ │ CommandSuggestionBuffer (hidden)          │   │  ← Hidden during permissions
│ └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## Priority System

When handling key events in `MultiLineInput.on_key()`:

**Priority Order:**
1. **Permission Prompt** (highest priority)
   - If `permission_prompt_data` is set
   - Captures: ↑↓ arrows, Enter, Esc

2. **Command Suggestions**
   - If `suggestions_active` is True
   - Captures: ↑↓ arrows, Enter, Esc

3. **Normal Input** (lowest priority)
   - All other keys for text input

---

## Strategic Use Cases

### Autocomplete Buffer (CommandSuggestionBuffer)
- ✅ Command discovery (typing `/`)
- ✅ Fuzzy search (typing `/mo` → `/model`)
- ✅ Usage frequency sorting
- 🔮 **Future**: Command aliases
- 🔮 **Future**: Recent commands
- 🔮 **Future**: Command with arguments preview

### Permission Buffer (MultiLineInput.permission_prompt_data)
- ✅ Tool permission prompts (Read, Write, Edit, Bash, etc.)
- ✅ Multi-step workflows (/local model selection)
- 🔮 **Future**: Command option selection (e.g., `/model` → choose from list)
- 🔮 **Future**: File-changing command confirmations
- 🔮 **Future**: Combined with autocomplete (select command → show options in permission buffer)

---

## Integration Strategy

### Current (Separate)
```
User types /local
  → CommandSuggestionBuffer shows commands
  → User selects /local
  → Command executes directly
```

### Future (Integrated)
```
User types /local
  → CommandSuggestionBuffer shows commands
  → User selects /local
  → Permission buffer shows /local options:
      ▸ Single model setup
        Dual model setup
  → User selects option
  → Permission buffer shows model choices
  → Command executes with selections
```

This allows:
1. **Discovery** via autocomplete
2. **Options** via permission buffer
3. **Confirmation** for file-changing operations
4. **Unified UX** - same navigation keys throughout

---

## Code References

**Command Suggestion Buffer:**
- Widget: `modules/command_suggestions.py:34` (CommandSuggestionBuffer)
- Search: `modules/command_registry.py:375` (search_commands)
- Handler: `modules/simple_tui.py:745` (on_multi_line_input_show_command_suggestions)

**Permission Buffer:**
- Renderer: `modules/multiline_input.py:117` (_render_permission_prompt)
- Handler: `modules/simple_tui.py:639` (on_multi_line_input_permission_response)
- Manager: `modules/async_permissions.py` (AsyncPermissionHandler)

---

## Naming in Conversation

**When discussing with Claude:**
- **"Command suggestions"** or **"autocomplete buffer"** = CommandSuggestionBuffer
- **"Permission buffer"** or **"permission prompt"** = MultiLineInput permission mode
- **"Prompt box"** = MultiLineInput in normal input mode
