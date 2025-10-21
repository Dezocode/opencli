# Grok's Permission Buffer Fixes - NOW APPLIED ✅

## What Was Wrong (Before Grok's Fixes)

**Freezing Issue**: When `/help` was executed, the TUI would freeze and timeout after 30 seconds.

**Root Causes Identified by Grok:**

1. **Async Deadlock** - Custom prompt functions were `async` and called `await buffer_manager.request_permission()`, creating a deadlock:
   - Async function waits for user response
   - UI frozen waiting for function to return
   - User can't respond because UI is frozen
   - Result: 30-second timeout → Permission denied

2. **`permission_prompt_data` Not Reactive** - Plain attribute doesn't trigger Textual re-renders when changed

## Grok's Fixes (3 Key Files)

### 1. `modules/permissions/integration.py` (414 lines)
**UnifiedPermissionManager with complete Future-based callback system**

- ✅ Line 259-345: `check_permission()` method that:
  - Calls `custom_prompt_func()` **synchronously** (line 298)
  - Gets prompt_data back immediately
  - Then calls `await self.request_permission()` (line 334)
  - Returns True/False based on response (line 340)

- ✅ Line 75-146: `request_permission()` with Future-based async:
  - Creates asyncio.Future for response
  - Registers temporary callback handler
  - Shows prompt via `show_permission_prompt()`
  - Waits for Future with timeout
  - Returns response_data dict

**Key Pattern:**
```python
async def check_permission(self, registration, context, app, session):
    # Get custom prompt function
    custom_prompt_func = registration.metadata.get('custom_prompt_func')

    if custom_prompt_func:
        # Call synchronously - NO await!
        prompt_data = custom_prompt_func(app, session, registration, context)

        # Then handle async waiting for user response
        response_data = await self.request_permission(app, session, prompt_data, timeout=30.0)

        return response_data.get('response') in ['allow_once', 'allow_session', 'allow_always']
```

### 2. `modules/commands/basic_commands.py`
**All custom prompt functions are synchronous and return prompt_data**

**Before (BROKEN):**
```python
async def show_help_prompt(app, session, registration, context):
    prompt_data = {...}
    buffer_manager = get_permission_buffer_manager()
    return await buffer_manager.request_permission(...)  # ❌ DEADLOCK!
```

**After (FIXED):**
```python
def show_help_prompt(app, session, registration, context):
    """Interactive prompt for /help command - shows options in buffer"""
    prompt_data = {
        'title': 'System: /help',
        'message': '# Command Help\n...',
        'options': [...]
    }
    return prompt_data  # ✅ Just return data, no async!
```

**Handler uses `_command_selection` for user choice:**
```python
async def show_help(app, session, **context):
    # Get user selection from permission buffer interaction
    command_selection = context.get('_command_selection', {})
    user_selection = command_selection.get('data', {})
    action = user_selection.get('action')  # 'view_all', 'view_by_category', etc.
```

### 3. `modules/execution/executor.py` (512 lines)
**Uses UnifiedPermissionManager.check_permission() directly**

**Lines 126-149: Permission check flow**
```python
if registration.requires_approval:
    from ..permissions import get_unified_permission_manager
    unified_manager = get_unified_permission_manager()

    if unified_manager:
        approved = await unified_manager.check_permission(
            registration,
            context,
            self.app,
            self.session
        )
        if not approved:
            raise PermissionError(f"Permission denied for {name}")
```

**NOT using:** `self.permission_manager.check_permission()` anymore!

### 4. `modules/multiline_input.py` (already had this)
**permission_prompt_data is reactive**

```python
from textual.reactive import reactive

class MultiLineInput(Widget):
    permission_prompt_data = reactive(None)  # ✅ Triggers re-render
```

## The Complete Flow (Grok's Fixed Version)

```
1. User types /help
   ↓
2. CommandRouter.route_command('/help')
   ↓
3. ExecutionSystem.execute(type=COMMAND, name='/help')
   ↓
4. Check registration.requires_approval → TRUE
   ↓
5. unified_manager.check_permission(registration, context, app, session)
   ↓
6. Found custom_prompt_func in metadata → show_help_prompt
   ↓
7. Call show_help_prompt() SYNCHRONOUSLY
   ↓
8. Returns prompt_data immediately:
   {
     'title': 'System: /help',
     'message': '# Command Help...',
     'options': [
       {'text': 'View all commands', 'response': 'allow_once', 'data': {'action': 'view_all'}},
       {'text': 'View by category', 'response': 'allow_once', 'data': {'action': 'view_by_category'}},
       {'text': 'Export to file', 'response': 'allow_once', 'data': {'action': 'export'}},
       {'text': 'Cancel', 'response': 'cancel'}
     ]
   }
   ↓
9. unified_manager calls await self.request_permission(app, session, prompt_data, timeout=30.0)
   ↓
10. request_permission() creates Future and callback
    ↓
11. Calls show_permission_prompt() which sets widget.permission_prompt_data
    ↓
12. permission_prompt_data is REACTIVE → Textual calls widget.render()
    ↓
13. widget.render() sees permission_prompt_data is set → _render_permission_prompt()
    ↓
14. Buffer displays visually with 4 options
    ↓
15. User navigates with arrow keys (up/down)
    ↓
16. User presses Enter
    ↓
17. MultiLineInput posts PermissionSelected event
    ↓
18. Event handler calls handle_permission_response()
    ↓
19. Callback resolves Future with response_data
    ↓
20. request_permission() returns: {'response': 'allow_once', 'data': {'action': 'view_all'}}
    ↓
21. check_permission() checks response in ['allow_once', ...] → TRUE
    ↓
22. Permission granted! ✅
    ↓
23. Executor stores user selection in context['_command_selection']
    ↓
24. Executor calls show_help(app, session, **context)
    ↓
25. show_help() reads context['_command_selection'] to get user's choice
    ↓
26. Executes based on action ('view_all', 'view_by_category', etc.)
```

## Files Synced to Runtime

✅ `/Users/dezmondhollins/opencli/modules/permissions/integration.py` → `~/.opencli/modules/permissions/integration.py`
✅ `/Users/dezmondhollins/opencli/modules/permissions/integration.py` → `~/.opencli/cli/modules/permissions/integration.py`
✅ `/Users/dezmondhollins/opencli/modules/commands/basic_commands.py` → `~/.opencli/modules/commands/basic_commands.py`
✅ `/Users/dezmondhollins/opencli/modules/commands/basic_commands.py` → `~/.opencli/cli/modules/commands/basic_commands.py`
✅ `/Users/dezmondhollins/opencli/modules/execution/executor.py` → `~/.opencli/modules/execution/executor.py`
✅ `/Users/dezmondhollins/opencli/modules/execution/executor.py` → `~/.opencli/cli/modules/execution/executor.py`

✅ Python cache cleared from all locations

## Key Differences from My Earlier Reversion

**I Was Wrong About:**
1. ❌ Executor should use `PermissionManager.check_permission()` - WRONG!
   - ✅ Executor actually uses `UnifiedPermissionManager.check_permission()` directly

2. ❌ Custom prompt functions should call buffer_manager themselves - WRONG!
   - ✅ Custom prompt functions just return prompt_data (synchronous)
   - ✅ UnifiedPermissionManager handles the async request_permission()

3. ❌ Context key is `_custom_prompt_data` - WRONG!
   - ✅ Grok uses `_command_selection` for user's choice

## What Should Happen Now

When you type `/help` in TUI:
1. ✅ Buffer should render immediately (no 30-second freeze)
2. ✅ You should see 4 options:
   - View all commands
   - View by category
   - Export to file
   - Cancel
3. ✅ Arrow keys should navigate (up/down)
4. ✅ Enter should select
5. ✅ Command executes based on your selection

## Testing

```bash
opencli tui
```

Then type `/help` and press Enter. You should see the permission buffer with 4 interactive options.

---

**Status**: Grok's complete fixes now applied ✅
**All 3 critical files copied from Grok's worktree**
**Synced to all runtime paths**
**Python cache cleared**
**Ready for testing**
