# 🎯 Permission System Runtime Flow - Complete Visual Documentation
**Created:** 2025-10-29 22:10 CT
**Purpose:** Visual documentation of permission buffer path, focus, and key handling

---

## 📊 Complete Execution Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    USER TYPES: /help + ENTER                        │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/tui/message_handler_mixin.py                               │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ async def handle_user_input(self, user_input)                │   │
│  │   - Receives: "/help"                                        │   │
│  │   - Calls: route_command_unified(app, session, "/help")     │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/command_router.py                                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ async def route_command_unified(app, session, "/help")       │   │
│  │   - Gets: app._command_router                               │   │
│  │   - Calls: router.route_command("/help")                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ async def route_command(self, "/help")                       │   │
│  │   - Looks up: executor.registry.commands["/help"]           │   │
│  │   - Calls: executor.execute_command("/help")                │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/execution/executor.py                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ class ExecutionSystem:                                       │   │
│  │                                                              │   │
│  │ async def execute_command(name="/help", **context):         │   │
│  │   └─> calls: execute(COMMAND, "/help", context)            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ async def execute(type=COMMAND, name="/help"):               │   │
│  │                                                              │   │
│  │   1. Get registration for /help                             │   │
│  │   2. Check: registration.requires_approval = TRUE           │   │
│  │   3. Get UnifiedPermissionManager                           │   │
│  │   4. Call: unified_manager.check_permission()               │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/permissions/integration.py                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ class UnifiedPermissionManager:                              │   │
│  │                                                              │   │
│  │ async def check_permission(registration, context):          │   │
│  │   1. Check: custom_prompt_func in registration.metadata    │   │
│  │   2. Found: show_help_prompt()                             │   │
│  │   3. Call: prompt_data = show_help_prompt(app, session)    │   │
│  │   4. Call: request_permission(app, session, prompt_data)   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/commands/basic_commands.py                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ def show_help_prompt(app, session, registration, context):  │   │
│  │                                                              │   │
│  │   Returns prompt_data = {                                   │   │
│  │     'title': 'System: /help',                              │   │
│  │     'message': '# Command Help\n\nView all...',            │   │
│  │     'options': [                                            │   │
│  │       {'text': 'View all commands', response: ALLOW_ONCE}, │   │
│  │       {'text': 'View by category', response: ALLOW_ONCE},  │   │
│  │       {'text': 'Export to file', response: ALLOW_ONCE},    │   │
│  │       {'text': 'Cancel', response: CANCEL}                 │   │
│  │     ]                                                        │   │
│  │   }                                                          │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/permissions/integration.py                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ async def request_permission(app, session, prompt_data):    │   │
│  │                                                              │   │
│  │   1. Create asyncio.Future() to wait for user response     │   │
│  │   2. Register temp response handler                         │   │
│  │   3. Call: show_permission_prompt(prompt_data)             │   │
│  │   4. await future (blocks until user responds)             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ def show_permission_prompt(prompt_data, handler_name):      │   │
│  │                                                              │   │
│  │   ✅ AFTER FIX (Lines 63-78):                              │   │
│  │   1. Validate prompt_data                                   │   │
│  │   2. Add handler_name to prompt_data                        │   │
│  │   3. Call: self._ui_callback(prompt_data)                  │   │
│  │      └─> This is TUI._show_permission_prompt()            │   │
│  │                                                              │   │
│  │   ❌ BEFORE FIX (Lines 66-82 - REMOVED):                   │   │
│  │   1. Create standalone PermissionPrompt widget              │   │
│  │   2. Call widget.show() and widget.focus()                 │   │
│  │   3. THEN call self._ui_callback(prompt_data)              │   │
│  │   ⚠️  Problem: Widget created but not displayed in TUI!    │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/tui/permission_handlers.py                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ def _show_permission_prompt(self, prompt_data):             │   │
│  │                                                              │   │
│  │   1. Get widget: prompt_input = query_one("#prompt-input") │   │
│  │                                                              │   │
│  │   2. 🔥 CRITICAL: Set permission data on widget             │   │
│  │      prompt_input.permission_prompt_data = None  (clear)   │   │
│  │      prompt_input.permission_prompt_data = prompt_data     │   │
│  │                                                              │   │
│  │   3. Force focus to prompt_input widget                     │   │
│  │      prompt_input.focus()                                   │   │
│  │      self.set_focus(prompt_input)                          │   │
│  │                                                              │   │
│  │   4. Widget auto-refreshes (reactive attribute)            │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/input_widget/widget.py                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ class MultiLineInput(Widget):                                │   │
│  │                                                              │   │
│  │   permission_prompt_data = reactive(None)  ← SET HERE!      │   │
│  │   permission_selected_option = reactive(0)                  │   │
│  │                                                              │   │
│  │   def render(self) -> Text:                                 │   │
│  │     if self.permission_prompt_data:                         │   │
│  │       # Render permission prompt instead of input           │   │
│  │       return render_permission_prompt(                      │   │
│  │         self.permission_prompt_data,                        │   │
│  │         self.permission_selected_option                     │   │
│  │       )                                                      │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  🎨 PERMISSION BUFFER DISPLAYS                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ ╭──────────────────────────────────────────────────────────╮ │   │
│  │ │ System: /help                                            │ │   │
│  │ │                                                          │ │   │
│  │ │ # Command Help                                           │ │   │
│  │ │                                                          │ │   │
│  │ │ View all available OpenCLI commands...                  │ │   │
│  │ │                                                          │ │   │
│  │ │ **Select viewing option:**                              │ │   │
│  │ │                                                          │ │   │
│  │ │ ▸ View all commands        ← Selected                   │ │   │
│  │ │   View by category                                      │ │   │
│  │ │   Export to file                                        │ │   │
│  │ │   Cancel                                                │ │   │
│  │ ╰──────────────────────────────────────────────────────────╯ │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Widget State:                                                      │
│  • permission_prompt_data = {title, message, options: [...]}       │
│  • permission_selected_option = 0                                  │
│  • has_focus = True                                                │
└─────────────────────────────────────────────────────────────────────┘

                      │
                      │ USER PRESSES: ↓ (DOWN ARROW)
                      ▼

┌─────────────────────────────────────────────────────────────────────┐
│  modules/input_widget/widget.py                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ @on(Key)                                                     │   │
│  │ def handle_key_message(self, event: Key):                   │   │
│  │                                                              │   │
│  │   1. event.stop()  # Prevent bubbling                       │   │
│  │   2. Log: KEY=down, permission=True ✅                      │   │
│  │   3. Call: handle_key_event(self, event)                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/input_widget/event_handler.py                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ def handle_key_event(widget, event):                         │   │
│  │                                                              │   │
│  │   # PRIORITY 1: Check for permission prompt                 │   │
│  │   if widget.permission_prompt_data:  ← TRUE! ✅             │   │
│  │     return handle_permission_keys(widget, event)            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ def handle_permission_keys(widget, event):                   │   │
│  │                                                              │   │
│  │   key = event.key  # "down"                                 │   │
│  │   options = widget.permission_prompt_data['options']        │   │
│  │                                                              │   │
│  │   if key == "down":                                         │   │
│  │     if widget.permission_selected_option < len(options)-1:  │   │
│  │       widget.permission_selected_option += 1  # 0 → 1       │   │
│  │       widget.refresh()  # Trigger re-render                 │   │
│  │     event.prevent_default()                                 │   │
│  │     return True                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/input_widget/widget.py                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ def render(self) -> Text:                                    │   │
│  │   # permission_selected_option changed (0 → 1)              │   │
│  │   # Re-render with new selection!                           │   │
│  │   return render_permission_prompt(                           │   │
│  │     prompt_data,                                             │   │
│  │     selected_option=1  ← Updated!                           │   │
│  │   )                                                          │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  🎨 UPDATED DISPLAY                                  │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ ╭──────────────────────────────────────────────────────────╮ │   │
│  │ │ System: /help                                            │ │   │
│  │ │                                                          │ │   │
│  │ │ # Command Help                                           │ │   │
│  │ │                                                          │ │   │
│  │ │ **Select viewing option:**                              │ │   │
│  │ │                                                          │ │   │
│  │ │   View all commands                                     │ │   │
│  │ │ ▸ View by category         ← NEW SELECTION! ✅          │ │   │
│  │ │   Export to file                                        │ │   │
│  │ │   Cancel                                                │ │   │
│  │ ╰──────────────────────────────────────────────────────────╯ │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

                      │
                      │ USER PRESSES: ENTER
                      ▼

┌─────────────────────────────────────────────────────────────────────┐
│  modules/input_widget/event_handler.py                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ def handle_permission_keys(widget, event):                   │   │
│  │                                                              │   │
│  │   if key == "enter":                                        │   │
│  │     selected = options[widget.permission_selected_option]   │   │
│  │     # selected = {'text': 'View by category', ...}          │   │
│  │                                                              │   │
│  │     widget.post_message(                                    │   │
│  │       widget.PermissionResponse(selected)                   │   │
│  │     )                                                        │   │
│  │     return True                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/tui/permission_handlers.py                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ @on(MultiLineInput.PermissionResponse)                      │   │
│  │ async def on_permission_response(self, event):               │   │
│  │                                                              │   │
│  │   1. Get response data from event.option_data               │   │
│  │   2. Call permission manager with response                  │   │
│  │   3. Clear permission buffer                                │   │
│  │   4. Permission future resolves                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/permissions/integration.py                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ async def request_permission():                              │   │
│  │                                                              │   │
│  │   # Future resolves with user's selection                   │   │
│  │   result = {'response': 'allow_once', data: {...}}          │   │
│  │   return result  # Back to check_permission()              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ async def check_permission():                                │   │
│  │                                                              │   │
│  │   response_data = await request_permission(...)             │   │
│  │                                                              │   │
│  │   if response_data['response'] == 'allow_once':             │   │
│  │     context['_command_selection'] = response_data['data']   │   │
│  │     return True  # APPROVED! ✅                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/execution/executor.py                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ async def execute():                                         │   │
│  │                                                              │   │
│  │   # Permission check returned True!                         │   │
│  │   # Execute the command handler                             │   │
│  │   result = await registration.handler(                      │   │
│  │     app, session, **context                                 │   │
│  │   )                                                          │   │
│  │   # context includes: _command_selection with user choice   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  modules/commands/basic_commands.py                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ async def show_help(app, session, **context):                │   │
│  │                                                              │   │
│  │   selection = context.get('_command_selection', {})         │   │
│  │   action = selection.get('data', {}).get('action')          │   │
│  │   # action = 'view_by_category'                             │   │
│  │                                                              │   │
│  │   # Execute the selected action                             │   │
│  │   if action == 'view_by_category':                          │   │
│  │     # Display commands grouped by category                  │   │
│  │     app.write(categorized_output)                           │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  ✅ COMMAND EXECUTED SUCCESSFULLY                    │
│                                                                     │
│  Help output displayed in chat area showing commands by category    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Focus Management Timeline

```
┌─────────────────────────────────────────────────────────────────────┐
│ TIME  │ FOCUS STATE        │ LOCATION                              │
├───────┼────────────────────┼───────────────────────────────────────┤
│ T0    │ MultiLineInput     │ User typing in input box              │
│       │ has_focus=TRUE     │                                       │
├───────┼────────────────────┼───────────────────────────────────────┤
│ T1    │ MultiLineInput     │ User presses ENTER on /help           │
│       │ has_focus=TRUE     │ Event: handle_user_input()            │
├───────┼────────────────────┼───────────────────────────────────────┤
│ T2    │ MultiLineInput     │ Permission check starts               │
│       │ has_focus=TRUE     │ Executing through router/executor     │
├───────┼────────────────────┼───────────────────────────────────────┤
│ T3    │ MultiLineInput     │ _show_permission_prompt() called      │
│       │ has_focus=TRUE     │ Setting permission_prompt_data        │
│       │                    │ prompt_input.focus() (ensure focus)   │
├───────┼────────────────────┼───────────────────────────────────────┤
│ T4    │ MultiLineInput     │ Permission buffer rendered            │
│       │ has_focus=TRUE ✅  │ Widget shows options                  │
│       │ permission=TRUE ✅ │ Ready for arrow key input             │
├───────┼────────────────────┼───────────────────────────────────────┤
│ T5    │ MultiLineInput     │ User presses DOWN arrow               │
│       │ has_focus=TRUE ✅  │ handle_permission_keys() routes key   │
│       │                    │ permission_selected_option += 1       │
├───────┼────────────────────┼───────────────────────────────────────┤
│ T6    │ MultiLineInput     │ User presses ENTER                    │
│       │ has_focus=TRUE ✅  │ Posts PermissionResponse message      │
│       │                    │ Future resolves                       │
├───────┼────────────────────┼───────────────────────────────────────┤
│ T7    │ MultiLineInput     │ Permission cleared                    │
│       │ has_focus=TRUE     │ permission_prompt_data = None         │
│       │                    │ Back to normal input mode             │
└───────┴────────────────────┴───────────────────────────────────────┘
```

**Key Points:**
- ✅ MultiLineInput **NEVER loses focus** during permission flow
- ✅ Same widget handles both normal input AND permission display
- ✅ Focus management is simple: always focused on #prompt-input
- ✅ No focus transfers needed between widgets

---

## 🔑 Key Event Routing Decision Tree

```
                    User Presses Key
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │ MultiLineInput.handle_key_message() │
        │ • event.stop() - prevent bubbling   │
        │ • Log to /tmp/opencli_keys.log      │
        └─────────────┬───────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────────┐
        │ handle_key_event(widget, event)     │
        │ Main dispatcher with priorities     │
        └─────────────┬───────────────────────┘
                      │
                      ▼
            ┌─────────┴─────────┐
            │                   │
  ┌─────────▼─────────┐   ┌────▼────────────┐
  │ permission_prompt │   │ permission_     │
  │ _data exists?     │   │ prompt_data     │
  │                   │   │ is None?        │
  └─────────┬─────────┘   └────┬────────────┘
            │ YES              │ NO
            │                  │
            ▼                  ▼
  ┌──────────────────┐   ┌──────────────────┐
  │ PRIORITY 1:      │   │ Check suggestions│
  │ PERMISSION KEYS  │   │ active?          │
  └─────────┬────────┘   └────┬─────────────┘
            │                  │
            │                  ▼
            │        ┌──────────────────┐
            │        │ PRIORITY 2:      │
            │        │ SUGGESTION KEYS  │
            │        │ (if suggestions) │
            │        └────┬─────────────┘
            │             │
            │             │ Fall through
            │             ▼
            │        ┌──────────────────┐
            │        │ PRIORITY 3:      │
            │        │ NORMAL KEYS      │
            │        │ (text editing)   │
            │        └──────────────────┘
            │
            ▼
  ┌────────────────────────────────┐
  │ handle_permission_keys()       │
  │                                │
  │ switch (event.key):            │
  │   case "up":                   │
  │     selected_option -= 1       │
  │     widget.refresh()           │
  │     return TRUE                │
  │                                │
  │   case "down":                 │
  │     selected_option += 1       │
  │     widget.refresh()           │
  │     return TRUE                │
  │                                │
  │   case "enter":                │
  │     post PermissionResponse    │
  │     return TRUE                │
  │                                │
  │   case "escape":               │
  │     post PermissionCancelled   │
  │     return TRUE                │
  │                                │
  │   default:                     │
  │     Block all other keys       │
  │     return TRUE                │
  └────────────────────────────────┘
```

---

## 🐛 The Bug (Before Fix)

```
❌ BEFORE FIX - modules/permissions/integration.py:66-82

┌─────────────────────────────────────────────────────────────────────┐
│ def show_permission_prompt(prompt_data, handler_name):              │
│                                                                     │
│   1. ❌ Create standalone PermissionPrompt widget                  │
│      self._current_widget = PermissionPrompt(                      │
│        title=..., message=..., options=...                         │
│      )                                                              │
│                                                                     │
│   2. ❌ Activate the widget                                        │
│      self._current_widget.show()                                   │
│      self._current_widget.is_active = True                         │
│                                                                     │
│   3. ❌ Try to focus the widget                                    │
│      self._current_widget.focus()                                  │
│                                                                     │
│   4. ✅ Call UI callback (renders buffer)                          │
│      self._ui_callback(prompt_data)                                │
│                                                                     │
│ PROBLEM:                                                            │
│   • Created widget is NOT added to TUI widget tree!                │
│   • Widget can't receive focus (not in app)                        │
│   • _ui_callback renders buffer but doesn't set                    │
│     permission_prompt_data on MultiLineInput!                      │
│   • Arrow keys check: if widget.permission_prompt_data → FALSE     │
│   • Keys routed to normal handler instead                          │
└─────────────────────────────────────────────────────────────────────┘

RESULT:
  ✅ Buffer displays (via _ui_callback rendering)
  ❌ Navigation doesn't work (permission_prompt_data not set)
  ❌ Key logs show: permission=False
```

---

## ✅ The Fix (After)

```
✅ AFTER FIX - modules/permissions/integration.py:63-78

┌─────────────────────────────────────────────────────────────────────┐
│ def show_permission_prompt(prompt_data, handler_name):              │
│                                                                     │
│   1. ✅ Validate prompt_data                                       │
│      is_valid, error = _buffer_manager.validate_prompt_data(...)   │
│                                                                     │
│   2. ✅ Add handler name to prompt_data                            │
│      if handler_name:                                              │
│        prompt_data['_handler_name'] = handler_name                 │
│                                                                     │
│   3. ✅ Call UI callback directly                                  │
│      self._ui_callback(prompt_data)                                │
│      └─> This is TUI._show_permission_prompt()                    │
│                                                                     │
│ WHAT HAPPENS IN _ui_callback:                                      │
│                                                                     │
│   TUI._show_permission_prompt(prompt_data):                        │
│     1. Get widget: prompt_input = query_one("#prompt-input")       │
│     2. 🔥 SET DATA: prompt_input.permission_prompt_data = data     │
│     3. Focus widget: prompt_input.focus()                          │
│     4. Widget auto-refreshes (reactive)                            │
│                                                                     │
│ NOW:                                                                │
│   • permission_prompt_data IS SET on MultiLineInput! ✅            │
│   • Arrow keys check: if widget.permission_prompt_data → TRUE ✅   │
│   • Keys routed to handle_permission_keys() ✅                     │
│   • Navigation works! ✅                                           │
└─────────────────────────────────────────────────────────────────────┘

RESULT:
  ✅ Buffer displays
  ✅ Navigation works (UP/DOWN arrows)
  ✅ Selection works (ENTER)
  ✅ Key logs show: permission=True
```

---

## 📝 Key Logging Example

**File:** `/tmp/opencli_keys.log`

### Before Fix:
```
[widget.on_key] KEY=slash, permission=False
[widget.on_key] KEY=h, permission=False
[widget.on_key] KEY=e, permission=False
[widget.on_key] KEY=l, permission=False
[widget.on_key] KEY=p, permission=False
[widget.on_key] KEY=enter, permission=False
[widget.on_key] KEY=down, permission=False     ❌ Should be True!
[handle_normal_keys] char='down' old='' new=''  ❌ Wrong handler!
```

### After Fix:
```
[widget.on_key] KEY=slash, permission=False
[widget.on_key] KEY=h, permission=False
[widget.on_key] KEY=e, permission=False
[widget.on_key] KEY=l, permission=False
[widget.on_key] KEY=p, permission=False
[widget.on_key] KEY=enter, permission=False
[widget.on_key] KEY=down, permission=True      ✅ Correct!
[handle_permission_keys] KEY=down              ✅ Right handler!
[handle_permission_keys] DOWN: selected=1      ✅ Navigation works!
[widget.on_key] KEY=enter, permission=True
[handle_permission_keys] ENTER: confirming option=View by category
```

---

## 🎯 Widget State During Permission Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ MultiLineInput Widget State Tracking                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ NORMAL INPUT MODE:                                                  │
│   • value = "some text"                                            │
│   • permission_prompt_data = None                                  │
│   • suggestions_active = False                                     │
│   • has_focus = True                                               │
│   • render() → Shows editable text input                           │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ PERMISSION PROMPT MODE:                                             │
│   • value = ""  (cleared when prompt shown)                        │
│   • permission_prompt_data = {                                     │
│       'title': 'System: /help',                                    │
│       'message': '# Command Help\n...',                            │
│       'options': [                                                 │
│         {'text': 'View all commands', ...},                        │
│         {'text': 'View by category', ...},                         │
│         ...                                                        │
│       ]                                                             │
│     }                                                               │
│   • permission_selected_option = 0                                 │
│   • has_focus = True                                               │
│   • render() → Shows permission buffer with options                │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ USER NAVIGATES (DOWN ARROW):                                        │
│   • permission_prompt_data = {...}  (unchanged)                    │
│   • permission_selected_option = 0 → 1  (incremented)              │
│   • has_focus = True                                               │
│   • render() → Re-renders with new selection                       │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ USER SELECTS (ENTER):                                               │
│   • Posts: PermissionResponse(selected_option_data)                │
│   • permission_prompt_data = None  (cleared)                       │
│   • permission_selected_option = 0  (reset)                        │
│   • has_focus = True                                               │
│   • render() → Back to normal input mode                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Message Flow Sequence

```
User Action: Press ENTER on /help command
  │
  ├─> MultiLineInput.Submitted("/help")
  │     ├─> TUI.on_user_input_submitted()
  │     │     ├─> handle_user_input("/help")
  │     │           ├─> route_command_unified("/help")
  │     │                 ├─> ExecutionSystem.execute_command("/help")
  │     │                       ├─> UnifiedPermissionManager.check_permission()
  │     │                             ├─> show_permission_prompt(prompt_data)
  │     │                                   ├─> _ui_callback(prompt_data)
  │     │                                         └─> TUI._show_permission_prompt()
  │     │                                               └─> Sets permission_prompt_data
  │     │
  │     └─> [AWAIT] request_permission() blocks until user responds
  │
  ▼
User Action: Press DOWN arrow
  │
  ├─> MultiLineInput.Key(key="down")
  │     ├─> handle_key_message()
  │           ├─> handle_key_event()
  │                 ├─> handle_permission_keys()  [permission=True]
  │                       ├─> permission_selected_option += 1
  │                       └─> widget.refresh()
  │
  ▼
User Action: Press ENTER
  │
  ├─> MultiLineInput.Key(key="enter")
  │     ├─> handle_permission_keys()
  │           ├─> widget.post_message(PermissionResponse(option_data))
  │
  ├─> TUI.on_permission_response(event)
  │     ├─> Gets selected option data
  │     └─> Calls permission manager with response
  │
  ├─> UnifiedPermissionManager processes response
  │     ├─> Future resolves with response_data
  │     └─> request_permission() returns response_data
  │
  ├─> check_permission() returns True
  │
  ├─> ExecutionSystem.execute() continues
  │     ├─> Calls show_help() handler
  │     │     ├─> Gets action from _command_selection
  │     │     └─> Displays help output
  │
  └─> Command execution complete!
```

---

## 📊 Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         COMPONENT LAYERS                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    UI LAYER (TUI)                          │    │
│  │  ┌──────────────────────────────────────────────────────┐  │    │
│  │  │ OpenCLITUI (Textual App)                            │  │    │
│  │  │  • Manages widget tree                              │  │    │
│  │  │  • Routes messages                                  │  │    │
│  │  │  • Provides _show_permission_prompt()              │  │    │
│  │  └─────────────┬────────────────────────────────────────┘  │    │
│  │                │                                           │    │
│  │                ▼                                           │    │
│  │  ┌──────────────────────────────────────────────────────┐  │    │
│  │  │ MultiLineInput Widget (#prompt-input)               │  │    │
│  │  │  • Reactive: permission_prompt_data                 │  │    │
│  │  │  • Reactive: permission_selected_option             │  │    │
│  │  │  • Handles: Key events                              │  │    │
│  │  │  • Renders: Input or permission buffer              │  │    │
│  │  │  • Posts: PermissionResponse messages               │  │    │
│  │  └──────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                │                                    │
│                                ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                 EXECUTION LAYER                            │    │
│  │  ┌──────────────────────────────────────────────────────┐  │    │
│  │  │ CommandRouter                                        │  │    │
│  │  │  • Routes commands to ExecutionSystem                │  │    │
│  │  │  • Manages command registry                          │  │    │
│  │  └─────────────┬────────────────────────────────────────┘  │    │
│  │                │                                           │    │
│  │                ▼                                           │    │
│  │  ┌──────────────────────────────────────────────────────┐  │    │
│  │  │ ExecutionSystem                                      │  │    │
│  │  │  • Validates registrations                           │  │    │
│  │  │  • Checks permissions (via UnifiedPermissionMgr)    │  │    │
│  │  │  • Executes handlers                                 │  │    │
│  │  │  • Manages workflows                                 │  │    │
│  │  └─────────────┬────────────────────────────────────────┘  │    │
│  └────────────────┼────────────────────────────────────────────┘    │
│                   │                                                │
│                   ▼                                                │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              PERMISSION LAYER                              │    │
│  │  ┌──────────────────────────────────────────────────────┐  │    │
│  │  │ UnifiedPermissionManager                             │  │    │
│  │  │  • check_permission() - Main entry point            │  │    │
│  │  │  • request_permission() - Async waiting             │  │    │
│  │  │  • show_permission_prompt() - Display UI            │  │    │
│  │  │  • Callback: _ui_callback → TUI._show_permission   │  │    │
│  │  └─────────────┬────────────────────────────────────────┘  │    │
│  │                │                                           │    │
│  │                ▼                                           │    │
│  │  ┌──────────────────────────────────────────────────────┐  │    │
│  │  │ PermissionBufferManager                              │  │    │
│  │  │  • Validates prompt_data                             │  │    │
│  │  │  • Manages buffer queue                              │  │    │
│  │  │  • Worker thread for rendering                       │  │    │
│  │  └──────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

COMMUNICATION:
  UI Layer ←──(Messages)──→ Execution Layer
  Execution Layer ←──(Permission Checks)──→ Permission Layer
  Permission Layer ──(UI Callback)──→ UI Layer
```

---

## 🎬 Complete Runtime Example

```bash
# User types in TUI:
/help
[ENTER]

# Log sequence:
[TUI] handle_user_input: /help
[Router] route_command_unified: /help
[Router] route_command: /help
[Executor] execute_command: /help
[Executor] execute(COMMAND, /help)
[Executor] Registration requires_approval=True
[UPM] check_permission: /help
[UPM] Found custom_prompt_func
[UPM] Calling show_help_prompt()
[UPM] request_permission()
[UPM] show_permission_prompt()
[UPM] Calling _ui_callback
[TUI] _show_permission_prompt()
[TUI] Setting permission_prompt_data on widget
[TUI] prompt_input.permission_prompt_data = {...}
[Widget] watch_permission_prompt_data triggered
[Widget] Refreshing render
[Widget] render() → permission buffer displayed

# User presses DOWN arrow:
[Widget] handle_key_message: KEY=down
[Widget] permission=True ✅
[EventHandler] handle_key_event: down
[EventHandler] Routing to handle_permission_keys
[PermissionHandler] KEY=down
[PermissionHandler] permission_selected_option: 0 → 1
[Widget] refresh() triggered
[Widget] render() → new selection highlighted

# User presses ENTER:
[Widget] handle_key_message: KEY=enter
[PermissionHandler] KEY=enter
[PermissionHandler] Confirming option: View by category
[Widget] post_message(PermissionResponse)
[TUI] on_permission_response
[TUI] Calling permission manager with response
[UPM] Future resolves
[UPM] request_permission returns: {response: allow_once, data: {...}}
[UPM] check_permission returns: True
[Executor] Permission approved, executing handler
[Executor] Calling show_help(app, session, **context)
[Help] action=view_by_category
[Help] Displaying categorized help
[TUI] Output written to chat area
```

---

## 📚 Files Reference

| File | Purpose | Key Functions |
|------|---------|---------------|
| `modules/tui/core.py` | Main TUI app | `_setup_permission_system()`, sets `_ui_callback` |
| `modules/tui/permission_handlers.py` | TUI permission UI | `_show_permission_prompt()` - sets widget data |
| `modules/tui/message_handler_mixin.py` | User input handling | `handle_user_input()` - routes commands |
| `modules/command_router.py` | Command routing | `route_command_unified()`, `route_command()` |
| `modules/execution/executor.py` | Execution system | `execute()`, `execute_command()` |
| `modules/execution/registry.py` | Command registry | Stores all registrations |
| `modules/permissions/integration.py` | Permission manager | `check_permission()`, `request_permission()`, **`show_permission_prompt()`** ← FIXED |
| `modules/permissions/manager.py` | Buffer manager | `validate_prompt_data()` |
| `modules/input_widget/widget.py` | Input widget | `render()`, `handle_key_message()`, **permission_prompt_data** |
| `modules/input_widget/event_handler.py` | Key routing | **`handle_key_event()`**, **`handle_permission_keys()`** |
| `modules/input_widget/permission_renderer.py` | Buffer rendering | `render_permission_prompt()` |
| `modules/commands/basic_commands.py` | Basic commands | `show_help()`, `show_help_prompt()` |
| `modules/commands/command_registry.py` | Registration | `register_all_commands()`, `_safe_register()` |

---

## ✅ Testing Checklist

After applying the fix, test these scenarios:

### 1. Basic Navigation
- [x] Type `/help` and press ENTER
- [ ] Permission buffer displays
- [ ] Press DOWN arrow → selection moves down
- [ ] Press UP arrow → selection moves up
- [ ] Press ENTER → option selected and executed

### 2. All Arrow Keys
- [ ] DOWN arrow navigates to next option
- [ ] UP arrow navigates to previous option
- [ ] DOWN on last option → stays on last
- [ ] UP on first option → stays on first

### 3. Selection
- [ ] ENTER selects current option
- [ ] Command executes with selected action
- [ ] Buffer clears after selection

### 4. Cancellation
- [ ] ESC cancels permission prompt
- [ ] Command execution aborted
- [ ] Buffer clears

### 5. Key Logging
- [ ] Check `/tmp/opencli_keys.log`
- [ ] Verify `permission=True` when buffer shown
- [ ] Verify arrow keys logged
- [ ] Verify routing to `handle_permission_keys()`

### 6. Other Commands
- [ ] Test `/status` command
- [ ] Test `/agent` command
- [ ] Test `/model` command
- [ ] All show navigable permission buffers

---

**END OF VISUAL DOCUMENTATION**
