# SDK-Compliant Command Template
## 100% Compatible with ExecutionSystem → PermissionManager → PermissionBuffer Flow

```python
"""
Command: /commandname
Category: [BASIC|MODEL|DOCKER|DEV|FILE|NETWORK|SYSTEM]
Risk: [SAFE|LOW|MEDIUM|HIGH|CRITICAL]

Description: What this command does
"""

# ============================================================================
# CORRECT IMPORTS - SDK STANDARD
# ============================================================================

# NO LEGACY IMPORTS! Use these only:
from ..permission_prompt import PermissionResponse  # For response types
from ..permission_buffer_manager import get_permission_buffer_manager  # For interactive prompts

# ============================================================================
# CUSTOM PROMPT FUNCTION - INTERACTIVE BUFFER PAGES
# ============================================================================

async def command_name_prompt(app, session, registration, context):
    """
    Create INTERACTIVE prompt with markdown pages for user configuration

    This function:
    1. Shows interactive markdown pages in permission buffer
    2. Presents options for user to select/configure
    3. User navigates through pages and makes selections
    4. Returns selected configuration data

    ALL command interaction happens HERE in the buffer, not in handler!
    """

    # Build interactive prompt with markdown pages
    prompt_data = {
        'title': f'System: {registration.name}',
        'message': """# Command Configuration

**Description:** What this command does

**Risk Level:** [yellow]MEDIUM[/yellow]

**Options:**
Select your configuration below

---

**Proceed with these settings?**""",
        'options': [
            {
                'text': 'Execute with default settings',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {
                    'mode': 'default',
                    'setting1': 'value1',
                    'setting2': 'value2'
                }
            },
            {
                'text': 'Execute with custom settings',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {
                    'mode': 'custom',
                    'setting1': 'custom_value1',
                    'setting2': 'custom_value2'
                }
            },
            {
                'text': 'Show advanced options',
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {
                    'show_advanced': True
                }
            },
            {
                'text': 'Cancel',
                'response': PermissionResponse.CANCEL
            }
        ]
    }

    # Show in permission buffer - user interacts with pages
    buffer_manager = get_permission_buffer_manager()
    selection = await buffer_manager.request_permission(app, session, prompt_data, timeout=30.0)

    # Return selected configuration
    return selection

# ============================================================================
# COMMAND HANDLER - SDK SIGNATURE
# ============================================================================

async def command_name(app, session, **context):
    """
    Command handler - executes based on user selections from buffer

    Args:
        app: TUI application instance
        session: Session object
        **context: Contains '_custom_prompt_data' with user selections

    Flow:
        1. ExecutionSystem checks registration
        2. PermissionManager calls custom_prompt_func (command_name_prompt)
        3. User interacts with buffer pages and selects options
        4. THIS FUNCTION executes with selections in context
        5. Execute based on selections, write results to chat

    Notes:
        - ALL user interaction happens in permission buffer
        - Handler receives pre-selected configuration
        - NO manual permission checking needed
        - NO legacy imports
    """

    # ========================================================================
    # STEP 1: Get user selections from buffer interaction
    # ========================================================================
    prompt_data = context.get('_custom_prompt_data', {})
    user_selection = prompt_data.get('data', {})
    mode = user_selection.get('mode', 'default')

    # ========================================================================
    # STEP 2: Execute based on selected configuration
    # ========================================================================
    try:
        if mode == 'default':
            # Execute with default settings
            result = "Executed with default settings"
            setting1 = user_selection.get('setting1', 'value1')
            setting2 = user_selection.get('setting2', 'value2')

        elif mode == 'custom':
            # Execute with custom settings
            result = "Executed with custom settings"
            setting1 = user_selection.get('setting1', 'custom_value1')
            setting2 = user_selection.get('setting2', 'custom_value2')

        else:
            result = "Executed"

        # ========================================================================
        # STEP 3: Write results to chat (interaction already done in buffer)
        # ========================================================================
        app.write(f"[cyan]{result}[/cyan]\n")
        app.write(f"[dim]Setting1: {setting1}[/dim]\n")
        app.write(f"[dim]Setting2: {setting2}[/dim]\n")

    except Exception as e:
        app.write(f"[red]Error: {e}[/red]\n")
        raise


# ============================================================================
# REGISTRATION EXAMPLE (in modules/commands/registry.py)
# ============================================================================
"""
await _safe_register(
    executor,
    ExecutionType.COMMAND,
    '/commandname',
    command_name,  # Handler function
    ExecutionCategory.BASIC,  # Category
    RiskLevel.MEDIUM,  # Risk level
    requires_approval=True,  # Always True - SDK handles it
    description="What this command does",
    estimated_duration="< 1 minute",  # Optional
    resources_needed=["resource1", "resource2"],  # Optional
    # CRITICAL: Register custom prompt function for interactive buffer
    custom_prompt_func=command_name_prompt,  # Shows interactive pages
)
"""

# ============================================================================
# PERMISSION FLOW - INTERACTIVE BUFFER PAGES
# ============================================================================
"""
1. User types: /commandname args
2. CommandRouter.route_command() called
3. ExecutionSystem.execute_command() called
4. ExecutionRegistry.get() finds registration
5. PermissionManager.check_permission() called
6. PermissionManager detects custom_prompt_func in registration
7. Calls command_name_prompt(app, session, registration, context)
8. PermissionBuffer shows INTERACTIVE markdown pages with options
9. User navigates through pages, selects configuration
10. Selection data returned to PermissionManager
11. PermissionManager stores in context['_custom_prompt_data']
12. command_name() handler executes with selections
13. Handler reads selections and executes accordingly
14. Results written to chat

KEY DIFFERENCE FROM LEGACY:
- LEGACY: Simple yes/no prompt, then handler does everything
- SDK: Interactive buffer pages, user configures, handler executes configuration
"""

# ============================================================================
# COMMON MISTAKES TO AVOID
# ============================================================================
"""
❌ DON'T: Import CommandRegistry - LEGACY
❌ DON'T: Import ToolPermissionManager - LEGACY
❌ DON'T: Import permission_templates - LEGACY (use custom_prompt_func instead)
❌ DON'T: Import get_permission_manager_for_command() - LEGACY
❌ DON'T: Show prompts manually in handler - use custom_prompt_func
❌ DON'T: Ask for user input in handler - all interaction in buffer
❌ DON'T: Use inline permission checks - SDK handles via buffer

✓ DO: Create custom_prompt_func for interactive buffer pages
✓ DO: Use markdown formatting in prompt messages
✓ DO: Provide multiple options with data payloads
✓ DO: Register custom_prompt_func in _safe_register()
✓ DO: Handler reads context['_custom_prompt_data'] for selections
✓ DO: Keep ALL user interaction in permission buffer
✓ DO: Handler only executes based on pre-selected configuration
✓ DO: Use app.write() for results AFTER execution
"""

# ============================================================================
# INTERACTIVE BUFFER PATTERNS
# ============================================================================
"""
Pattern 1: Simple Configuration Choice
- Present 2-3 options (default, custom, advanced)
- Each option includes data payload
- Handler switches on selected mode

Pattern 2: Multi-Step Configuration
- First page: Select category
- Option with show_advanced=True triggers second page
- Second page: Configure details
- Handler receives final configuration

Pattern 3: Confirmation with Preview
- Show what will be changed/affected
- Options: Proceed, Preview More, Cancel
- Handler executes only if proceeded

Pattern 4: Info Display with Actions
- Show information/status
- Options: Export, Copy, Execute Action, Cancel
- Handler performs selected action

ALL patterns keep interaction in buffer, handler just executes!
"""
