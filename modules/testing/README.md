# OpenCLI TUI Test Framework

Comprehensive testing framework for OpenCLI TUI with automated data collection, visual dual-window testing, and function-level failure analysis.

## Features

- ✅ **Visual Dual-Window Testing** - See the TUI and controller simultaneously
- ✅ **Automated Data Collection** - Captures output after every command
- ✅ **Function-Level Failure Analysis** - Identifies exact failing functions
- ✅ **State Verification** - Detects selection changes, buffer states
- ✅ **ANSI Code Stripping** - Clean analysis of terminal output
- ✅ **Configurable Test Sequences** - Chain any test steps together
- ✅ **Root Cause Analysis** - Suggests fixes for failing tests

## Installation

The module is already available in `modules/testing/`:

```python
from modules.testing import TUITestFramework, TestStep, create_permission_buffer_test
```

## Quick Start

### Example 1: Run Standard Permission Buffer Test

```python
from modules.testing import create_permission_buffer_test

# Create and run pre-configured permission buffer test
test = create_permission_buffer_test(command="/help")
result = test.run_test(visual=True)

print(f"Test {'PASSED' if result.passed else 'FAILED'}")
if result.failing_functions:
    for func in result.failing_functions:
        print(f"Failing: {func['function']} at {func['file']}:{func['line']}")
```

### Example 2: Custom Test Sequence

```python
from modules.testing import TUITestFramework, TestStep

# Create framework
framework = TUITestFramework(sdk_init_wait=11)

# Add custom test steps
framework.add_step(
    TestStep.TYPE,
    "/agent switch",
    "Type agent switch command"
)

framework.add_step(
    TestStep.ENTER,
    description="Submit command",
    wait_after=2
)

framework.add_step(
    TestStep.DOWN,
    description="Navigate to second option",
    wait_after=1
)

framework.add_step(
    TestStep.ENTER,
    description="Select option"
)

# Run test
result = framework.run_test(visual=True)
```

### Example 3: Headless Testing (CI/CD)

```python
from modules.testing import TUITestFramework, TestStep

framework = TUITestFramework()

# Configure test steps
framework.add_step(TestStep.TYPE, "/help")
framework.add_step(TestStep.ENTER)
framework.add_step(TestStep.ENTER, wait_after=4)
framework.add_step(TestStep.COLLECT_STATE)

# Run without visual windows
result = framework.run_test(visual=False)

# Check results programmatically
if not result.passed:
    print("Test failed!")
    if result.failing_functions:
        for func in result.failing_functions:
            print(f"Fix required: {func['function']} in {func['file']}")
```

## API Reference

### TUITestFramework

Main testing framework class.

#### Constructor

```python
TUITestFramework(
    sdk_init_wait: int = 11,
    opencli_cmd: str = "opencli tui",
    codebase_paths: List[str] = None
)
```

**Parameters:**
- `sdk_init_wait` - Seconds to wait for SDK initialization (default: 11)
- `opencli_cmd` - Command to start OpenCLI TUI (default: "opencli tui")
- `codebase_paths` - Paths to search for code analysis (default: ~/opencli, ~/.opencli)

#### Methods

##### add_step()

Add a test step to the sequence.

```python
framework.add_step(
    step_type: TestStep,
    value: Optional[str] = None,
    description: Optional[str] = None,
    wait_after: float = 0.5,
    verify_fn: Optional[Callable] = None,
    expected_state: Optional[Dict[str, Any]] = None
) -> TUITestFramework
```

**Parameters:**
- `step_type` - Type of test step (TestStep enum)
- `value` - Value for the step (e.g., text to type)
- `description` - Human-readable description
- `wait_after` - Seconds to wait after step
- `verify_fn` - Optional verification function
- `expected_state` - Expected state after step

**Returns:** Self for method chaining

##### run_test()

Execute the configured test.

```python
framework.run_test(visual: bool = True) -> TestResult
```

**Parameters:**
- `visual` - Whether to open visual windows (default: True)

**Returns:** TestResult object with pass/fail status and details

##### cleanup()

Clean up test resources (tmux sessions, temp files).

```python
framework.cleanup()
```

### TestStep Enum

Available test step types:

```python
class TestStep(Enum):
    TYPE = "type"              # Type text
    ENTER = "enter"            # Press ENTER
    DOWN = "down"              # Press DOWN arrow
    UP = "up"                  # Press UP arrow
    ESCAPE = "escape"          # Press ESCAPE
    WAIT = "wait"              # Wait specified time
    COLLECT_STATE = "collect"  # Collect and analyze TUI state
    VERIFY_SELECTION = "verify_selection"  # Verify selection changed
    CUSTOM = "custom"          # Custom step
```

### TestResult

Result object returned from `run_test()`.

```python
@dataclass
class TestResult:
    passed: bool                              # Test passed/failed
    message: str                              # Result message
    details: Dict[str, Any]                   # Test details
    failing_functions: List[Dict[str, str]]   # Functions that failed
    log_file: Optional[str]                   # Path to output log
```

## Test Step Examples

### Basic Steps

```python
# Type text
framework.add_step(TestStep.TYPE, "/help", "Type help command")

# Press ENTER
framework.add_step(TestStep.ENTER, description="Submit")

# Press arrow keys
framework.add_step(TestStep.DOWN, description="Move down")
framework.add_step(TestStep.UP, description="Move up")

# Wait
framework.add_step(TestStep.WAIT, value="5", description="Wait 5 seconds")
```

### Advanced Steps

```python
# Collect state with verification
framework.add_step(
    TestStep.COLLECT_STATE,
    description="Verify permission buffer appeared"
)

# Verify selection changed
framework.add_step(
    TestStep.VERIFY_SELECTION,
    description="Check 'No' is selected",
    expected_state={"selected": "No"}
)

# Custom verification function
def verify_custom(output: str) -> bool:
    return "Expected text" in output

framework.add_step(
    TestStep.TYPE,
    "test",
    verify_fn=verify_custom
)
```

## Pre-configured Tests

### create_permission_buffer_test()

Creates a standard permission buffer test for any command.

```python
create_permission_buffer_test(command: str = "/help") -> TUITestFramework
```

**Test sequence:**
1. Types command
2. Presses ENTER (autocomplete)
3. Presses ENTER (submit)
4. Collects state
5. Presses DOWN arrow
6. Verifies "No" is selected
7. Presses ENTER to confirm

**Example:**

```python
# Test /agent command
test = create_permission_buffer_test(command="/agent")
result = test.run_test()
```

## Visual Testing

When `visual=True` (default), the framework opens two Terminal windows:

1. **TUI Window** (left) - Shows opencli tui running in tmux
2. **Controller Window** (right) - Shows test execution and data collection

### What You'll See:

**TUI Window:**
- Real opencli TUI interface
- Permission buffers when they appear
- Selection changes as arrow keys are pressed

**Controller Window:**
- Test step descriptions
- Real-time data collection
- Permission buffer detection (🎯)
- Selection state verification
- Final pass/fail analysis
- Failing function identification (if test fails)

## Failure Analysis

When a test fails, the framework automatically:

1. **Identifies the failing function**
   - Searches codebase for relevant files
   - Finds exact function handling the failed operation
   - Reports file path and line number

2. **Shows the relevant code**
   - Extracts and displays the failing function
   - Highlights the specific handler (e.g., DOWN arrow code)

3. **Analyzes root cause**
   - Checks for common issues (e.g., `is_active` checks)
   - Reports why the function isn't working

4. **Suggests fixes**
   - Provides specific debugging steps
   - Lists potential issues to check

### Example Failure Output:

```
❌ FAIL: DOWN arrow did NOT change selection

🔍 AUTO-ANALYZING: Identifying failing function...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 File: /Users/you/opencli/modules/permissions/widget.py

🎯 FAILING FUNCTION:
   Function: on_key()
   Line: 172

📋 DOWN arrow code:
    if key == "down":
        if self.selected_option < len(self.options) - 1:
            self.selected_option += 1
        event.prevent_default()

⚠️  ROOT CAUSE:
   Function exists but not responding to key presses

   ❌ Widget has is_active check at line: 174
      Problem: Widget may not be active/focused

💡 FIX SUGGESTIONS:
   1. Ensure widget receives focus when displayed
   2. Set self.is_active = True
   3. Verify on_key() is bound to key events
   4. Check event propagation chain
```

## Integration Examples

### CI/CD Integration

```python
# test_tui_commands.py
from modules.testing import create_permission_buffer_test
import sys

def test_help_command():
    test = create_permission_buffer_test("/help")
    result = test.run_test(visual=False)
    assert result.passed, f"Help command test failed: {result.message}"

def test_agent_command():
    test = create_permission_buffer_test("/agent")
    result = test.run_test(visual=False)
    assert result.passed, f"Agent command test failed: {result.message}"

if __name__ == "__main__":
    try:
        test_help_command()
        test_agent_command()
        print("✅ All tests passed")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
```

### Regression Testing

```python
# regression_tests.py
from modules.testing import TUITestFramework, TestStep

def run_regression_suite():
    """Run full regression test suite"""

    tests = [
        ("Help Command", create_help_test()),
        ("Agent Switch", create_agent_test()),
        ("Permission Buffer", create_permission_test()),
    ]

    results = []
    for name, test in tests:
        print(f"Running: {name}...")
        result = test.run_test(visual=False)
        results.append((name, result))
        print(f"  {'✅ PASSED' if result.passed else '❌ FAILED'}")

    # Summary
    passed = sum(1 for _, r in results if r.passed)
    total = len(results)
    print(f"\n{passed}/{total} tests passed")

    return all(r.passed for _, r in results)

def create_help_test():
    framework = TUITestFramework()
    framework.add_step(TestStep.TYPE, "/help")
    framework.add_step(TestStep.ENTER)
    framework.add_step(TestStep.ENTER, wait_after=4)
    framework.add_step(TestStep.COLLECT_STATE)
    return framework

def create_agent_test():
    framework = TUITestFramework()
    framework.add_step(TestStep.TYPE, "/agent")
    framework.add_step(TestStep.ENTER)
    framework.add_step(TestStep.ENTER, wait_after=4)
    return framework

def create_permission_test():
    return create_permission_buffer_test()

if __name__ == "__main__":
    success = run_regression_suite()
    sys.exit(0 if success else 1)
```

## Troubleshooting

### Test hangs during SDK initialization

**Solution:** Increase `sdk_init_wait`:

```python
framework = TUITestFramework(sdk_init_wait=20)
```

### Can't see TUI window

**Solution:** Check if tmux is installed:

```bash
brew install tmux
```

### Permission denied for Terminal automation

**Solution:** Grant Terminal accessibility permissions:
1. System Settings → Privacy & Security → Accessibility
2. Add Terminal.app

### Tests fail but visual testing works

**Solution:** This usually means headless mode needs longer waits:

```python
framework.add_step(TestStep.ENTER, wait_after=5)  # Increase wait
```

## Advanced Configuration

### Custom Codebase Paths

```python
framework = TUITestFramework(
    codebase_paths=[
        "/custom/path/to/opencli",
        "/another/path"
    ]
)
```

### Custom OpenCLI Command

```python
framework = TUITestFramework(
    opencli_cmd="python -m opencli.tui --debug"
)
```

### Chain Multiple Tests

```python
# Test 1
test1 = create_permission_buffer_test("/help")
result1 = test1.run_test(visual=False)

# Test 2
test2 = create_permission_buffer_test("/agent")
result2 = test2.run_test(visual=False)

# Both must pass
assert result1.passed and result2.passed
```

## License

Part of OpenCLI project.

## Contributing

When adding new test types:

1. Add to `TestStep` enum
2. Implement step handling in `create_test_script()`
3. Add verification logic if needed
4. Update documentation with examples
