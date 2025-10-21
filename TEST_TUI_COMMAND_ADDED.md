# /test-tui Command Added ✅

**Date**: 2025-10-20
**Status**: ✅ COMPLETE - Slash command registered and ready

---

## What Was Added

### New Slash Command: `/test-tui`

**Purpose**: Generate a shell script template showing how to configure and run TUI tests via the API

**Category**: DEV
**Risk Level**: SAFE
**Requires Approval**: Yes

---

## How to Use

### In opencli TUI:

```bash
# Start opencli
opencli tui

# Run the command
/test-tui
```

### What Happens:

1. Shows permission buffer with description
2. User selects "Generate test template script" or "Cancel"
3. Creates `test_tui_template.sh` in current directory
4. Shows success message with usage instructions

---

## Template Contents

The generated script contains **6 complete test patterns**:

### Pattern 1: Quick Permission Buffer Test
- Pre-configured test for `/help` command
- Visual mode (opens LEFT and RIGHT windows)
- Shows how to check for failing functions

### Pattern 2: Custom Navigation Test
- Build custom test sequence
- Test arrow key navigation
- BEFORE/AFTER validation
- Verify selection changes

### Pattern 3: Headless Test (CI/CD Mode)
- No visual windows
- Returns test results
- Exit codes for CI/CD pipelines
- Shows failing functions

### Pattern 4: Test Multiple Commands
- Loop through command list
- Test each command
- Collect pass/fail results
- Summary report

### Pattern 5: Custom Validation
- Custom verification functions
- Your own test logic
- State-based checks

### Pattern 6: State Collection & Analysis
- Collect TUI state at checkpoints
- Before/after comparisons
- Detailed state analysis

---

## API Examples in Template

### Basic Usage
```python
from modules.testing import create_permission_buffer_test

test = create_permission_buffer_test("/help")
result = test.run_test(visual=True)
```

### Custom Test Sequence
```python
from modules.testing import TUITestFramework, TestStep

framework = TUITestFramework(sdk_init_wait=11)
framework.add_step(TestStep.TYPE, "/help", "Type command")
framework.add_step(TestStep.ENTER, description="Submit")
framework.add_step(TestStep.DOWN, description="Navigate")
result = framework.run_test(visual=True)
```

### Headless CI/CD
```python
test = create_permission_buffer_test("/help")
result = test.run_test(visual=False)
sys.exit(0 if result.passed else 1)
```

---

## Files Modified

### 1. `/Users/dezmondhollins/opencli/modules/commands/dev_commands.py`

**Added**:
- `test_tui_prompt()` - Permission buffer prompt function
- `test_tui()` - Command handler that creates template script

**Lines**: 287-562 (275 new lines)

### 2. `/Users/dezmondhollins/opencli/modules/commands/command_registry.py`

**Added**:
- Import of `test_tui` and `test_tui_prompt`
- Registration of `/test-tui` command

**Changes**:
- Line 247: Added imports
- Lines 271-276: Command registration

---

## Template Script Structure

```bash
test_tui_template.sh
├── Pattern 1: Quick Permission Buffer Test
│   └── create_permission_buffer_test() API
├── Pattern 2: Custom Navigation Test
│   └── TUITestFramework() custom sequence
├── Pattern 3: Headless Test (CI/CD)
│   └── visual=False mode
├── Pattern 4: Test Multiple Commands
│   └── Loop through command list
├── Pattern 5: Custom Validation
│   └── Custom verify_fn
├── Pattern 6: State Collection
│   └── COLLECT_STATE checkpoints
└── Usage Instructions
    ├── Available TestSteps
    ├── Auto-Detection Features
    ├── Visual Mode explanation
    └── Headless Mode explanation
```

---

## Testing the Command

### Manual Test

```bash
# Start opencli
cd ~/opencli
opencli tui

# Run command
/test-tui

# Select "Generate test template script"
# Press ENTER

# Check output
ls -la test_tui_template.sh

# Run the template
bash test_tui_template.sh
```

### Expected Output

```
✓ Test template created: test_tui_template.sh

The template contains 6 patterns:
  1. Quick Permission Buffer Test
  2. Custom Navigation Test
  3. Headless Test (CI/CD)
  4. Test Multiple Commands
  5. Custom Validation
  6. State Collection & Analysis

Run with: bash test_tui_template.sh
Or execute individual patterns from the file
```

---

## Integration with Existing System

### Command Flow

```
User types: /test-tui
     ↓
command_router.py detects slash command
     ↓
Routes to command_registry
     ↓
Finds registration: /test-tui → test_tui()
     ↓
Calls test_tui_prompt() for permission buffer
     ↓
Shows interactive buffer with options
     ↓
User selects "Generate test template script"
     ↓
Calls test_tui() handler with selection
     ↓
Creates test_tui_template.sh
     ↓
chmod +x test_tui_template.sh
     ↓
Shows success message
```

### SDK Compliance

✅ **Follows SDK pattern**:
- Prompt function returns `prompt_data` dict
- Handler receives `_custom_prompt_data` in context
- Handles ALLOW_ONCE and CANCEL responses
- Uses permission buffer for user interaction
- No direct execution without permission

---

## Available TestSteps (Documented in Template)

| TestStep | Description |
|----------|-------------|
| `TYPE` | Type text into TUI |
| `ENTER` | Press Enter key |
| `DOWN` | Press DOWN arrow (auto BEFORE/AFTER) |
| `UP` | Press UP arrow (auto BEFORE/AFTER) |
| `ESCAPE` | Press ESC key |
| `WAIT` | Wait specified seconds |
| `COLLECT_STATE` | Capture current TUI state |
| `VERIFY_SELECTION` | Verify selection matches expected |

---

## Auto-Detection Features (Documented in Template)

✅ **Automatically detects**:
1. Permission buffer presence
2. Yes/No options displayed
3. Navigation (arrow keys working)
4. Selection changes (BEFORE/AFTER)
5. Failing functions (exact file + line number)

---

## Visual vs Headless Modes (Documented in Template)

### Visual Mode
- Opens 2 Terminal windows
- LEFT: Shows actual `opencli tui`
- RIGHT: Shows controller commands
- Use: `run_test(visual=True)`

### Headless Mode
- No windows
- Background execution
- Returns TestResult object
- Use: `run_test(visual=False)`

---

## Example Use Cases

### Use Case 1: Quick Test After Code Changes
```bash
# After modifying permission buffer code
opencli tui
/test-tui
# Select generate
bash test_tui_template.sh  # Run pattern 1
```

### Use Case 2: CI/CD Integration
```bash
# Extract pattern 3 from template
python3 << 'EOF'
from modules.testing import create_permission_buffer_test
test = create_permission_buffer_test("/help")
result = test.run_test(visual=False)
exit(0 if result.passed else 1)
EOF
```

### Use Case 3: Custom Test Development
```bash
# Get template
opencli tui -> /test-tui
# Edit test_tui_template.sh
# Modify pattern 2 for your custom test
# Run: bash test_tui_template.sh
```

---

## Benefits

1. **Easy Access**: Single slash command generates complete template
2. **6 Patterns**: Cover all common testing scenarios
3. **Executable**: Template is ready to run immediately
4. **Documented**: Each pattern includes comments and explanations
5. **API Reference**: Shows exact API usage for all features
6. **Copy-Paste Ready**: Use patterns as starting point for custom tests

---

## Next Steps

### For Users:
1. Type `/test-tui` in opencli
2. Generate template script
3. Run `bash test_tui_template.sh` to see examples
4. Copy patterns you need for custom tests

### For Developers:
1. Template shows all API capabilities
2. Use as reference for writing new tests
3. Modify patterns for specific test scenarios
4. Integrate patterns into CI/CD pipelines

---

## Summary

✅ **Command Added**: `/test-tui`
✅ **Registered**: In command_registry.py
✅ **SDK Compliant**: Uses permission buffer
✅ **Template Created**: 6 complete test patterns
✅ **Documentation**: In-template comments and usage guide
✅ **Executable**: chmod +x, ready to run
✅ **API Reference**: Shows all TUI test framework features

**The `/test-tui` command provides instant access to comprehensive TUI testing examples via a single slash command!** 🎯
