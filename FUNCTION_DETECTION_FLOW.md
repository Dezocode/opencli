# Function Detection Flow in TUI Test Framework

## How the Framework Detects Failing Functions

### Step-by-Step Process

```
1. Test Executes
   ↓
2. Server sends commands via pipe
   ↓
3. Server sends back response data
   ↓
4. Controller analyzes response
   ↓
5. Detects failure (e.g., "DOWN arrow didn't change selection")
   ↓
6. AUTOMATIC FUNCTION ANALYSIS TRIGGERED
```

### Automatic Analysis Process

```bash
# 1. Find relevant code file
WIDGET_FILE=$(find ~/opencli ~/.opencli -path "*/permissions/widget.py" 2>/dev/null | head -1)

# 2. Locate the function that handles this operation
KEY_HANDLER_LINE=$(grep -n "def on_key" "$WIDGET_FILE" | head -1 | cut -d: -f1)

# 3. Extract and display the function code
sed -n "${KEY_HANDLER_LINE},$((KEY_HANDLER_LINE + 20))p" "$WIDGET_FILE" | grep -A 5 "down"

# 4. Analyze for common issues
if grep -q "if not self.is_active" "$WIDGET_FILE"; then
    echo "Widget has is_active check - may not be receiving focus"
fi

# 5. Report findings
echo "Function: on_key()"
echo "Line: $KEY_HANDLER_LINE"
echo "Issue: Widget not responding to key presses"
```

### Detection Triggers

| Test Failure | Function Detected | Analysis |
|--------------|-------------------|----------|
| DOWN arrow doesn't change selection | `on_key()` in widget.py | Checks for focus/active issues |
| Permission buffer doesn't appear | Command routing functions | Checks command flow |
| Command not executed | Executor functions | Checks permission manager |

### What Gets Reported

1. **📁 File Path**: Exact file location
   ```
   File: /Users/you/opencli/modules/permissions/widget.py
   ```

2. **🎯 Function Name**: The failing function
   ```
   Function: on_key()
   ```

3. **📍 Line Number**: Where it's defined
   ```
   Line: 172
   ```

4. **📋 Code Snippet**: The relevant code
   ```python
   if key == "down":
       if self.selected_option < len(self.options) - 1:
           self.selected_option += 1
       event.prevent_default()
   ```

5. **⚠️ Root Cause**: Why it's failing
   ```
   Widget has is_active check at line 174
   Problem: Widget may not be active/focused
   ```

6. **💡 Fix Suggestions**: How to fix it
   ```
   1. Ensure widget receives focus when displayed
   2. Set self.is_active = True
   3. Verify on_key() is bound to key events
   ```

### Example Test Run

```python
from modules.testing import create_permission_buffer_test

# Run test
test = create_permission_buffer_test("/help")
result = test.run_test(visual=True)

# Check results
if not result.passed:
    print("Test failed!")

    # Access failing functions
    if result.failing_functions:
        for func in result.failing_functions:
            print(f"\n🔧 FIX REQUIRED:")
            print(f"   Function: {func['function']}")
            print(f"   File: {func['file']}")
            print(f"   Line: {func['line']}")
```

### Visual Output

When running with `visual=True`, you see in the **Controller window**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ PASS: Permission buffer appeared
✅ PASS: Yes/No options shown
✅ PASS: Command execution detected
❌ FAIL: DOWN arrow did NOT change selection

🔍 AUTO-ANALYZING: Identifying failing function...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 File: ~/opencli/modules/permissions/widget.py

🎯 FAILING FUNCTION:
   Function: on_key()
   Line: 172

📋 DOWN arrow code:
    def on_key(self, event) -> None:
        if not self.is_active:
            return
        if key == "down":
            if self.selected_option < len(self.options) - 1:
                self.selected_option += 1

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

### Integration with CI/CD

In headless mode, function information is captured:

```python
result = test.run_test(visual=False)

if not result.passed:
    # Get failing functions
    functions = result.failing_functions

    # Create bug report
    for func in functions:
        bug_report = f"""
        Bug: {result.message}
        Function: {func['function']}
        File: {func['file']}
        Line: {func['line']}
        """
        # Submit to bug tracker
        create_jira_ticket(bug_report)
```

### Extensibility

Add custom function detection:

```python
def _generate_final_analysis(self):
    analysis = super()._generate_final_analysis()

    # Add custom function detection
    analysis += """
# Check for custom failures
if grep -qi "custom error" /tmp/final_clean_$$.txt; then
    CUSTOM_FILE=$(find ~/opencli -name "custom_module.py")
    CUSTOM_FUNC=$(grep -n "def custom_function" "$CUSTOM_FILE")
    echo "Custom function failing: $CUSTOM_FUNC"
fi
"""
    return analysis
```

## Summary

✅ **Automatic Detection**: Framework automatically finds failing functions
✅ **Codebase Search**: Searches ~/opencli and ~/.opencli directories
✅ **Function Identification**: Uses grep to find function definitions
✅ **Code Extraction**: Shows relevant code snippets
✅ **Root Cause Analysis**: Identifies common issues (focus, active state, etc.)
✅ **Fix Suggestions**: Provides actionable steps
✅ **Programmatic Access**: TestResult.failing_functions for automation
✅ **Visual Display**: Shows in controller window during test
✅ **CI/CD Integration**: Capture function info for bug tracking

**The framework does all the detective work for you!**
