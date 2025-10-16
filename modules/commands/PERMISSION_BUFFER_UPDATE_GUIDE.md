# Permission Buffer Integration Guide

**ALL commands MUST be updated to use permission buffer templates.**

This guide shows how to update each command type to populate the permission buffer with interactive UI.

---

## ✅ COMPLETED: Template System

Created `permission_templates.py` with 5 template types:
1. `create_basic_command_prompt()` - Simple commands
2. `create_destructive_command_prompt()` - Dangerous operations
3. `create_info_command_prompt()` - Read-only information
4. `create_configuration_prompt()` - Configuration changes
5. `create_workflow_prompt()` - Multi-step workflows

---

## ✅ COMPLETED: Basic Commands (`basic_commands.py`)

Updated 3 commands showing each pattern:
- `/help` - Informational command with export option
- `/status` - Informational command with status preview
- `/clear` - Destructive command requiring confirmation

---

## 📋 TODO: Update Remaining Command Files

### Pattern 1: Informational Commands (Read-Only)

**Files:** `agent_commands.py`, `diff_commands.py`, `model_commands.py`

**Before:**
```python
async def list_agents(app, session, **context):
    agents = get_available_agents()
    app.write("[bold]Available Agents:[/bold]\n")
    for agent in agents:
        app.write(f"  • {agent}\n")
```

**After:**
```python
async def list_agents(app, session, **context):
    from .permission_templates import CommandPermissionTemplate, get_permission_manager_for_command

    agents = get_available_agents()

    # Create info prompt with preview
    prompt_data = CommandPermissionTemplate.create_info_command_prompt(
        command_name="/agents",
        info_summary={
            "Total Agents": str(len(agents)),
            "Types": ", ".join(agents[:3]) + ("..." if len(agents) > 3 else "")
        },
        allow_export=True
    )

    # Show in permission buffer
    permission_manager = get_permission_manager_for_command(app)
    result = await permission_manager.request_permission(prompt_data)

    if result.get('response') == 'denied':
        app.write("[yellow]Command cancelled[/yellow]\n")
        return

    # Execute
    app.write("[bold]Available Agents:[/bold]\n")
    for agent in agents:
        app.write(f"  • {agent}\n")
```

---

### Pattern 2: Configuration Commands

**Files:** `provider_commands.py`, `model_commands.py`, `system_commands.py`

**Before:**
```python
async def model_switch(app, session, model_name, **context):
    old_model = session.model
    session.model = model_name
    app.write(f"Switched to {model_name}\n")
```

**After:**
```python
async def model_switch(app, session, model_name, **context):
    from .permission_templates import CommandPermissionTemplate, get_permission_manager_for_command

    old_model = session.model

    # Create configuration prompt
    prompt_data = CommandPermissionTemplate.create_configuration_prompt(
        command_name="/model",
        current_settings={"model": old_model},
        proposed_changes={"model": model_name}
    )

    # Show in permission buffer
    permission_manager = get_permission_manager_for_command(app)
    result = await permission_manager.request_permission(prompt_data)

    if result.get('response') == 'denied':
        app.write("[yellow]Model switch cancelled[/yellow]\n")
        return

    # Execute
    session.model = model_name
    app.write(f"[green]✓ Switched to {model_name}[/green]\n")
```

---

### Pattern 3: Destructive Commands

**Files:** `system_commands.py`, `docker_commands.py`

**Before:**
```python
async def docker_ollama_stop(app, session, **context):
    subprocess.run(["docker", "stop", "ollama"])
    app.write("Stopped Ollama container\n")
```

**After:**
```python
async def docker_ollama_stop(app, session, **context):
    from .permission_templates import CommandPermissionTemplate, get_permission_manager_for_command

    # Create destructive prompt
    prompt_data = CommandPermissionTemplate.create_destructive_command_prompt(
        command_name="/docker ollama stop",
        description="Stop the running Ollama Docker container",
        affected_items=["Ollama container", "Running models", "Active API connections"],
        warning_message="This will interrupt any ongoing model operations"
    )

    # Show in permission buffer
    permission_manager = get_permission_manager_for_command(app)
    result = await permission_manager.request_permission(prompt_data)

    if result.get('response') == 'denied' or not result.get('data', {}).get('confirmed'):
        app.write("[yellow]Operation cancelled[/yellow]\n")
        return

    # Execute
    subprocess.run(["docker", "stop", "ollama"])
    app.write("[green]✓ Stopped Ollama container[/green]\n")
```

---

### Pattern 4: Workflow Commands (Multi-Step)

**Files:** `spec_commands.py`, `refactor_commands.py`, `local_commands.py`

**Before:**
```python
async def run_specify(app, session, **context):
    # Step 1
    create_spec()
    # Step 2
    validate_spec()
    # Step 3
    save_spec()
```

**After:**
```python
async def run_specify(app, session, **context):
    from .permission_templates import CommandPermissionTemplate, get_permission_manager_for_command

    # Define workflow steps
    steps = [
        {"title": "Create specification template", "status": "pending"},
        {"title": "Validate specification completeness", "status": "pending"},
        {"title": "Save to .specify/ directory", "status": "pending"}
    ]

    # Create workflow prompt
    prompt_data = CommandPermissionTemplate.create_workflow_prompt(
        workflow_name="/specify",
        steps=steps,
        estimated_duration="2-3 minutes"
    )

    # Show in permission buffer
    permission_manager = get_permission_manager_for_command(app)
    result = await permission_manager.request_permission(prompt_data)

    if result.get('response') == 'denied':
        app.write("[yellow]Workflow cancelled[/yellow]\n")
        return

    # Execute workflow
    for i, step in enumerate(steps):
        app.write(f"[cyan]Step {i+1}:[/cyan] {step['title']}\n")
        # ... execute step ...
        app.write(f"[green]✓ Complete[/green]\n")
```

---

## 🔄 Files Requiring Updates

### Priority 1 (High Usage - Update First)
- [x] `basic_commands.py` - ✓ DONE (show_help, show_status, clear_history)
- [ ] `agent_commands.py` - 8 commands (agents, agent switching)
- [ ] `model_commands.py` - 5 commands (model list, switch, providers)
- [ ] `provider_commands.py` - 5 commands (add, remove, list providers)

### Priority 2 (Medium Usage)
- [ ] `docker_commands.py` - 8 commands (setup, start, stop, stats)
- [ ] `diff_commands.py` - 3 commands (diff, git diff, worktree)
- [ ] `system_commands.py` - 4 commands (restart, upgrade, rollback, api)

### Priority 3 (Specialized)
- [ ] `spec_commands.py` - 7 commands (specify, plan, tasks, etc.)
- [ ] `refactor_commands.py` - 2 commands (refactor, autorefactor)
- [ ] `local_commands.py` - 1 command (local setup)
- [ ] `inject_commands.py` - 1 command (code inject)
- [ ] `dev_commands.py` - 3 commands (debug, performance, reload)
- [ ] `api_commands.py` - Any API-related commands

---

## 🎯 Key Points

1. **EVERY command must create a permission prompt**
2. **Use appropriate template based on command type:**
   - Read-only → `create_info_command_prompt`
   - Config changes → `create_configuration_prompt`
   - Dangerous ops → `create_destructive_command_prompt`
   - Multi-step → `create_workflow_prompt`
   - Default → `create_basic_command_prompt`

3. **Check result and handle cancellation:**
   ```python
   if result.get('response') == 'denied':
       app.write("[yellow]Command cancelled[/yellow]\n")
       return
   ```

4. **For destructive ops, verify confirmation:**
   ```python
   if not result.get('data', {}).get('confirmed'):
       app.write("[yellow]Requires confirmation[/yellow]\n")
       return
   ```

5. **Add export options where useful** (status, lists, etc.)

---

## 🧪 Testing Checklist

After updating each file:
- [ ] Import permission_templates at top of function
- [ ] Create appropriate prompt using template
- [ ] Call `permission_manager.request_permission()`
- [ ] Handle denial gracefully
- [ ] Execute command only after approval
- [ ] Test in runtime with `opencli`
- [ ] Verify permission buffer shows interactive UI
- [ ] Verify options work correctly

---

## 📊 Progress Tracking

Total Commands: ~50+
- ✅ Completed: 3 (show_help, show_status, clear_history)
- 🔄 In Progress: 0
- ⏳ Remaining: ~47+

**Next Steps:**
1. Update agent_commands.py (8 commands)
2. Update model_commands.py (5 commands)
3. Continue through Priority 1, then 2, then 3

---

## 💡 Tips

- Copy-paste patterns from `basic_commands.py` examples
- Use appropriate colors: green for success, yellow for cancelled, red for errors
- Add rich previews in permission prompts when possible
- Test each command after updating to ensure buffer interaction works
- Keep prompts concise but informative

---

**CRITICAL:** No command should execute without showing in permission buffer first!
