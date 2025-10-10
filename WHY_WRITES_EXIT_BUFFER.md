# Why app.write() Exits the Permission Buffer

## The Core Issue

**Permission buffer and main chat area are mutually exclusive** - only one can be visible at a time.

### UI State Management

```python
# In MultiLineInput widget
permission_prompt_data = reactive(None)

# When permission_prompt_data is set:
#   → Permission buffer renders (multiline_input.py:88-224)
#   → Main chat is hidden
#   → Input widget shows the permission prompt

# When app.write() is called:
#   → Writes to main content area (RichLog or StreamingDisplay)
#   → UI updates to show main content
#   → Permission buffer is implicitly hidden
#   → Input widget returns to normal prompt
```

## Example: What Was Happening

### Before (BROKEN)

```python
# User approves initial permission
session._ollama_setup_approved = True

# Re-run command handler
# async_interactive.py handles /docker ollama setup

# Check approval
if has_approval:
    # PROBLEM: These writes go to MAIN CHAT
    app.write("[green]✓ Permission GRANTED[/green]\n")  # ← Exits buffer!
    app.write("🐳 Ollama Docker Setup\n\n")              # ← Exits buffer!

    # Check Docker daemon
    is_running, _ = await check_docker()
    app.write(f"Docker: {is_running}\n")                 # ← Exits buffer!

    # Show resource selection in buffer
    # But buffer was already cleared by previous writes!
    prompt_input.permission_prompt_data = resource_prompt
```

**Result:** Buffer exits after first approval, user sees main chat, no progress visibility.

### After (FIXED)

```python
# User approves initial permission
session._ollama_setup_approved = True

# Re-run command handler
# async_interactive.py handles /docker ollama setup

# Check approval
if has_approval:
    # NO WRITES - stay in buffer
    pass

# Get system resources SILENTLY
resources = await app.docker_async.get_system_resources()

# Show resource selection in buffer
# Buffer stays visible!
prompt_input.permission_prompt_data = resource_prompt
```

**Result:** Buffer stays visible, user selects resources, unified executor takes over with live progress.

## Why Not Just Keep Both Visible?

The permission buffer is rendered **in place of** the normal input widget. It's not a separate overlay - it's the input widget itself transforming:

```
Normal mode:
╭─────────────────────────────────────╮
│ > Type your message...              │  ← MultiLineInput normal render
╰─────────────────────────────────────╯

Permission mode:
╭─────────────────────────────────────╮
│ Permission Prompt Title             │  ← MultiLineInput permission render
│                                     │
│ Message                             │
│                                     │
│ ▸ Option 1                         │
│   Option 2                         │
╰─────────────────────────────────────╯
```

When `permission_prompt_data` is set, the `render()` method returns the permission prompt instead of the normal input field.

## The Fix

### Rule 1: No Writes During Permission Flow

```python
# ✗ WRONG - Exits buffer
if has_approval:
    app.write("Processing...\n")  # ← Exits!
    await do_work()
    show_next_permission()

# ✓ CORRECT - Stays in buffer
if has_approval:
    # No writes!
    await do_work_silently()
    show_next_permission()
```

### Rule 2: All Progress Goes Through Buffer

```python
# ✗ WRONG - Progress in main chat
app.write("[cyan]▸ Pulling image...[/cyan]\n")
await pull_image()
app.write("[green]✓ Image pulled[/green]\n")

# ✓ CORRECT - Progress in buffer via workflow_status
workflow_status = {
    'steps': [
        {'title': 'Pull image', 'status': 'in_progress'}
    ]
}
prompt_input.permission_prompt_data['workflow_status'] = workflow_status
prompt_input.refresh()
```

### Rule 3: Only Clear Buffer When Done

```python
# After ALL steps complete
await asyncio.sleep(2)  # Show final status
prompt_input.permission_prompt_data = None  # ← Now clear it
prompt_input.refresh()
```

## Thread Safety

The `app.write()` method IS thread-safe - it uses a queue:

```python
# simple_tui.py:756
def write(self, text, end="\n"):
    self._write_queue_threadsafe.put((text, end))
```

**BUT** thread safety doesn't matter if the write **changes the UI state** by clearing the buffer!

## The Unified Flow Solution

The unified executor solves this by:

1. **Showing initial permission** → User approves
2. **NO writes to main chat** during execution
3. **All progress updates via `workflow_status`** in the buffer
4. **Buffer stays visible** with live step indicators
5. **Only clears buffer** after completion + 2s delay

## Example: Complete Flow

```python
User: /docker ollama setup
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Set up Ollama Docker Container?

This will:
• Check Docker daemon status
• Pull Ollama Docker image (~2.7GB)
• Create and configure container
• Allocate system resources

Proceed with setup?

▸ Yes, set up Ollama in Docker
  No, cancel
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓ User clicks "Yes"
    ↓ NO app.write() calls!
    ↓ Resources detected silently
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Docker Ollama Setup

Choose resource allocation:

Your system: 8 CPUs, 16.0GB RAM

▸ Conservative (4 CPUs, 8GB RAM)
  Balanced (6 CPUs, 12GB RAM)
  Cancel
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓ User selects "Conservative"
    ↓ NO app.write() calls!
    ↓ Unified executor starts
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Docker: /docker ollama setup

Progress: 2/5 steps

✓ Check Docker daemon status
✓ Check for existing Ollama containers
⋯ Pull Ollama Docker image (~2.7GB)  ← LIVE UPDATE
· Create Ollama container (4 CPUs, 8g RAM)
· Verify container is running

  Cancel execution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓ All steps complete
    ↓ Sleep 2s
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: 5/5 steps - Complete!

✓ Check Docker daemon status
✓ Check for existing Ollama containers
✓ Pull Ollama Docker image (~2.7GB)
✓ Create Ollama container (4 CPUs, 8g RAM)
✓ Verify container is running

✓ Docker Ollama setup complete!

Ollama is now available at: http://localhost:11434
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓ After 2s delay
    ↓ permission_prompt_data = None
    ↓ Buffer clears
    ↓
Normal input prompt returns
```

## Summary

- **app.write() doesn't block threads** - it's queued
- **app.write() DOES exit the buffer** - by writing to main chat
- **Main chat and permission buffer are mutually exclusive**
- **Solution: NO writes during permission flow** - all updates via workflow_status
- **Unified executor enforces this pattern** for all commands

The fix isn't about threading - it's about **UI state management** and keeping the buffer visible.
