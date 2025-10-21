#!/usr/bin/env python3
"""
OpenCLI TUI Test Framework
===========================

A comprehensive testing framework for OpenCLI TUI with:
- Visual dual-window testing
- Automated data collection
- Function-level failure analysis
- Configurable test sequences

Usage:
    from modules.testing.tui_test_framework import TUITestFramework, TestStep

    framework = TUITestFramework()
    framework.add_step(TestStep.TYPE, "/help", "Type help command")
    framework.add_step(TestStep.ENTER, description="Submit command")
    framework.run_test()
"""

import subprocess
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any, Callable
import tempfile


class TestStep(Enum):
    """Test step types"""
    TYPE = "type"
    ENTER = "enter"
    DOWN = "down"
    UP = "up"
    ESCAPE = "escape"
    WAIT = "wait"
    COLLECT_STATE = "collect"
    VERIFY_SELECTION = "verify_selection"
    CUSTOM = "custom"


@dataclass
class TestStepConfig:
    """Configuration for a single test step"""
    step_type: TestStep
    value: Optional[str] = None
    description: Optional[str] = None
    wait_after: float = 0.5
    verify_fn: Optional[Callable] = None
    expected_state: Optional[Dict[str, Any]] = None


@dataclass
class TestResult:
    """Result from a test execution"""
    passed: bool
    message: str
    details: Dict[str, Any]
    failing_functions: List[Dict[str, str]] = None
    log_file: Optional[str] = None


class TUITestFramework:
    """
    Comprehensive TUI testing framework for OpenCLI

    Features:
    - Visual dual-window testing with tmux
    - Automated command sending and data collection
    - Function-level failure analysis
    - ANSI code stripping for clean analysis
    - State verification (e.g., selection changes)
    """

    def __init__(self,
                 sdk_init_wait: int = 11,
                 opencli_cmd: str = "opencli tui",
                 codebase_paths: List[str] = None):
        """
        Initialize test framework

        Args:
            sdk_init_wait: Seconds to wait for SDK initialization
            opencli_cmd: Command to start OpenCLI TUI
            codebase_paths: Paths to search for code analysis
        """
        self.sdk_init_wait = sdk_init_wait
        self.opencli_cmd = opencli_cmd
        self.codebase_paths = codebase_paths or [
            os.path.expanduser("~/opencli"),
            os.path.expanduser("~/.opencli")
        ]

        self.steps: List[TestStepConfig] = []
        self.session_name = f"tui_test_{os.getpid()}"
        self.output_log = f"/tmp/tui_output_log_{os.getpid()}.txt"
        self.temp_dir = tempfile.gettempdir()

    def add_step(self,
                 step_type: TestStep,
                 value: Optional[str] = None,
                 description: Optional[str] = None,
                 wait_after: float = 0.5,
                 verify_fn: Optional[Callable] = None,
                 expected_state: Optional[Dict[str, Any]] = None) -> 'TUITestFramework':
        """
        Add a test step to the sequence

        Args:
            step_type: Type of test step
            value: Value for the step (e.g., text to type)
            description: Human-readable description
            wait_after: Seconds to wait after step
            verify_fn: Optional verification function
            expected_state: Expected state after step

        Returns:
            Self for chaining
        """
        self.steps.append(TestStepConfig(
            step_type=step_type,
            value=value,
            description=description,
            wait_after=wait_after,
            verify_fn=verify_fn,
            expected_state=expected_state
        ))
        return self

    def create_test_script(self) -> str:
        """Generate bash test script from configured steps using pipe-based server communication"""
        script = f"""#!/bin/bash

# Handle --tui-only flag for visual mode (LEFT window = TUI, RIGHT window = Controller)
TUI_ONLY_MODE=false
if [ "$1" == "--tui-only" ]; then
    TUI_ONLY_MODE=true
fi

SESSION="{self.session_name}"
OUTPUT_LOG="{self.output_log}"
# Use fixed pipe names based on session (not $$) so both windows use same pipes
PIPE="/tmp/tui_command_pipe_{self.session_name}"
RESPONSE_PIPE="/tmp/tui_response_pipe_{self.session_name}"

# Create named pipes for server communication
if [ "$TUI_ONLY_MODE" == "false" ]; then
    echo "▶ Creating communication pipes..."
    mkfifo "$PIPE" 2>/dev/null || true
    mkfifo "$RESPONSE_PIPE" 2>/dev/null || true

    echo "✅ Communication pipes created"
    echo "   Command pipe: $PIPE"
    echo "   Response pipe: $RESPONSE_PIPE"
    echo ""
fi

# Create expect script that runs TUI with command server
TUI_EXPECT_SCRIPT="/tmp/tui_expect_server_$$.exp"
cat > "$TUI_EXPECT_SCRIPT" <<'EXPECT_EOF'
#!/usr/bin/expect -f

set timeout -1
log_user 1

puts "\\n╔════════════════════════════════════════════════════════════╗"
puts "║  TUI PROCESS WITH COMMAND SERVER                          ║"
puts "║  Listening for commands via pipe...                       ║"
puts "╚════════════════════════════════════════════════════════════╝\\n"

# Get pipe paths from environment
set pipe_path $::env(PIPE_PATH)
set response_pipe $::env(RESPONSE_PIPE_PATH)
set output_log $::env(OUTPUT_LOG)

# Spawn opencli tui with output logging
log_file -a $output_log
spawn {self.opencli_cmd}

# Start background command listener
set listener_pid [exec bash -c "
    while IFS= read -r cmd; do
        echo \\"\\$cmd\\" > /tmp/tui_cmd_received_$$
    done < $pipe_path
" &]

puts "Command server PID: $listener_pid"
puts "Waiting for SDK initialization...\\n"

# Wait for SDK to initialize (expect the prompt to appear)
set timeout {self.sdk_init_wait}
expect {{
    -re ".*>" {{
        puts "\\n✅ TUI READY - SDK initialized, prompt detected"
        puts "   Signaling controller that TUI is ready..."

        # Signal that TUI is ready
        set ready_flag "/tmp/tui_ready_${{::env(SESSION)}}"
        set ready_file [open $ready_flag w]
        puts $ready_file "READY"
        close $ready_file
    }}
    timeout {{
        puts "\\n⚠️  Timeout waiting for TUI prompt - continuing anyway"
        # Signal ready even on timeout
        set ready_flag "/tmp/tui_ready_${{::env(SESSION)}}"
        set ready_file [open $ready_flag w]
        puts $ready_file "READY_TIMEOUT"
        close $ready_file
    }}
}}

set timeout -1
puts "\\nTUI server ready, listening for commands from controller...\\n"

# Main loop - check for commands and send to TUI
while {{1}} {{
    # Check if command file exists
    if {{[file exists "/tmp/tui_cmd_received_$$"]}} {{
        set cmd_file [open "/tmp/tui_cmd_received_$$" r]
        set cmd [gets $cmd_file]
        close $cmd_file
        file delete "/tmp/tui_cmd_received_$$"

        puts "\\n[SERVER] Processing command: $cmd"

        switch -glob $cmd {{
            "TYPE:*" {{
                set text [string range $cmd 5 end]
                puts "[SERVER] Typing: $text"
                send "$text"

                # Capture output after typing
                expect {{
                    -re ".+" {{
                        set captured $expect_out(buffer)
                        puts "[CAPTURED] $captured"
                    }}
                    timeout {{ }}
                }}

                # Send response with captured data
                set log_content [exec tail -20 $output_log 2>/dev/null || echo ""]
                puts $response_pipe "TYPED:$text|RECENT_OUTPUT:$log_content"
            }}
            "ENTER" {{
                puts "[SERVER] Sending ENTER"
                send "\\r"

                # Wait and capture output after ENTER
                sleep 0.5
                expect {{
                    -re ".+" {{
                        set captured $expect_out(buffer)
                        puts "[CAPTURED] $captured"
                    }}
                    timeout {{ }}
                }}

                set log_content [exec tail -20 $output_log 2>/dev/null || echo ""]
                puts $response_pipe "ENTER_SENT|RECENT_OUTPUT:$log_content"
            }}
            "DOWN" {{
                puts "[SERVER] Sending DOWN arrow"
                send "\\033\\[B"

                sleep 0.3
                set log_content [exec tail -20 $output_log 2>/dev/null || echo ""]
                puts $response_pipe "DOWN_SENT|RECENT_OUTPUT:$log_content"
            }}
            "UP" {{
                puts "[SERVER] Sending UP arrow"
                send "\\033\\[A"

                sleep 0.3
                set log_content [exec tail -20 $output_log 2>/dev/null || echo ""]
                puts $response_pipe "UP_SENT|RECENT_OUTPUT:$log_content"
            }}
            "COLLECT_DATA" {{
                puts "[SERVER] Collecting current TUI state"

                # Get recent output
                set log_content [exec tail -50 $output_log 2>/dev/null || echo ""]

                # Check for permission buffer indicators
                set has_permission [string match "*System:*help*" $log_content]
                set has_yes_no [string match "*Yes*No*" $log_content]

                puts $response_pipe "DATA_COLLECTED|PERMISSION_BUFFER:$has_permission|YES_NO_OPTIONS:$has_yes_no|RECENT_OUTPUT:$log_content"
            }}
            "QUIT" {{
                puts "[SERVER] Shutting down"
                send "\\003"
                puts $response_pipe "SHUTDOWN"
                break
            }}
        }}
    }}

    # Small delay to prevent CPU spinning
    after 100
}}

# Cleanup
catch {{exec kill $listener_pid}}
expect eof
EXPECT_EOF

chmod +x "$TUI_EXPECT_SCRIPT"

# TUI-ONLY MODE: Launch opencli alias in tmux (LEFT window)
if [ "$TUI_ONLY_MODE" == "true" ]; then
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  TUI WINDOW (LEFT) - opencli Launch                      ║"
    echo "║  Launching actual opencli alias in tmux...               ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    # Check if opencli alias/command exists
    if ! command -v opencli &> /dev/null; then
        echo "❌ 'opencli' command not found"
        echo "   Make sure opencli is installed and in PATH"
        echo ""
        read -p "Press ENTER to close..."
        exit 1
    fi

    echo "✅ opencli command found: $(which opencli)"
    echo "   Creating tmux session: $SESSION"
    echo "   Running: opencli tui"
    echo ""

    # Create detached tmux session first
    tmux new-session -d -s "$SESSION"

    # Send opencli tui command to the session
    tmux send-keys -t "$SESSION" "cd {os.getcwd()}" C-m
    sleep 1
    tmux send-keys -t "$SESSION" "opencli tui 2>&1 | tee $OUTPUT_LOG" C-m

    # Attach to the session (so user sees opencli TUI)
    tmux attach-session -t "$SESSION"

    # When user exits opencli, cleanup
    echo ""
    echo "opencli session ended"
    exit 0
fi

# CONTROLLER MODE: Detect opencli and send commands (RIGHT window)
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  CONTROLLER WINDOW (RIGHT) - Sending Commands             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "▶ Waiting for LEFT window to launch opencli..."
echo "   Session: $SESSION"
sleep 3

# Check if tmux session exists (created by LEFT window)
OPENCLI_RUNNING=false
if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "✅ Tmux session found"

    # Check if opencli process is actually running in the session
    OPENCLI_PID=$(tmux list-panes -t "$SESSION" -F "#{{pane_pid}}" 2>/dev/null | head -1)
    if [ -n "$OPENCLI_PID" ]; then
        # Check if there's an opencli process under this pane
        if pgrep -P "$OPENCLI_PID" | xargs ps -p 2>/dev/null | grep -q "opencli"; then
            echo "   ✅ opencli process detected (PID: $OPENCLI_PID)"
            OPENCLI_RUNNING=true
        else
            echo "   ⚠️  No opencli process found in tmux session"
        fi
    fi
else
    echo "⚠️  Tmux session not found"
    echo "   LEFT window may not have launched opencli yet"
fi

# Decide whether to use visual control or skip
if [ "$OPENCLI_RUNNING" = "true" ]; then
    echo ""
    echo "✅ opencli is running - will send commands via expect"

    # Start expect script to control the running opencli
    echo "▶ Attaching expect controller to opencli session..."
    tmux send-keys -t "$SESSION" "" # Wake up the session

    # TODO: Attach expect script to send keystrokes
    # For now, we'll use tmux send-keys directly
else
    echo ""
    echo "⚠️  opencli NOT detected in LEFT window"
    echo "   Continuing with configured test (headless mode)..."
    echo "   Visual verification will not be available"
    echo ""
fi

# Check if LEFT window has attached clients
ATTACHED_COUNT=$(tmux list-clients -t "$SESSION" 2>/dev/null | wc -l)
if [ "$ATTACHED_COUNT" -gt 0 ]; then
    echo "   ✅ LEFT window is viewing opencli ($ATTACHED_COUNT client(s) attached)"
else
    echo "   ⚠️  LEFT window not attached (running in background)"
fi

# Wait for TUI to be ready by checking tmux pane content persistently
if [ "$OPENCLI_RUNNING" = "true" ]; then
    echo ""
    echo "⏳ Waiting for opencli to fully initialize..."
    WAIT_COUNT=0
    MAX_WAIT={self.sdk_init_wait + 5}
    OPENCLI_READY=false

    while [ "$OPENCLI_READY" = "false" ]; do
        sleep 0.5
        WAIT_COUNT=$((WAIT_COUNT + 1))

        # Check tmux pane content for "Ready" status
        PANE_CONTENT=$(tmux capture-pane -t "$SESSION" -p 2>/dev/null || echo "")

        # Look for Ready indicator in opencli output
        if echo "$PANE_CONTENT" | grep -qi "Ready"; then
            echo "   ✅ opencli is READY - detected 'Ready' status in TUI"
            OPENCLI_READY=true
            break
        fi

        # Show progress every 2 seconds
        if [ $((WAIT_COUNT % 4)) -eq 0 ]; then
            ELAPSED=$((WAIT_COUNT / 2))
            echo "   ⏱  Waiting for opencli initialization... (${{ELAPSED}}s elapsed)"
        fi

        if [ $WAIT_COUNT -gt $((MAX_WAIT * 2)) ]; then
            echo "   ⚠️  Timeout waiting for opencli ready status"
            echo "   Continuing anyway..."
            break
        fi
    done
else
    echo ""
    echo "⚠️  Skipping initialization wait (opencli not detected)"
fi
echo ""

# Function to send keystroke to opencli tmux session
send_keystroke() {{
    local key="$1"
    local description="$2"

    echo "▶ $description"

    # Send keystroke directly to tmux session
    tmux send-keys -t "$SESSION" "$key"
    sleep 0.5

    # Capture pane content to see result
    PANE_CONTENT=$(tmux capture-pane -t "$SESSION" -p 2>/dev/null || echo "")

    # Check for permission buffer indicators
    if echo "$PANE_CONTENT" | grep -qi "System.*help"; then
        echo "  🎯 PERMISSION BUFFER DETECTED in TUI!"
    fi

    if echo "$PANE_CONTENT" | grep -qi "Yes.*No\\|No.*Yes"; then
        echo "  🎯 YES/NO OPTIONS DETECTED in TUI!"
    fi

    echo "  ✅ Keystroke sent to opencli"
}}

# Function to collect current state
collect_state() {{
    echo ""
    echo "  📊 Collecting TUI state..."

    # Capture current pane content
    PANE_CONTENT=$(tmux capture-pane -t "$SESSION" -p 2>/dev/null || echo "")

    # Check for permission buffer
    if echo "$PANE_CONTENT" | grep -qi "System.*help\\|Permission\\|Execute command"; then
        echo "  ✅ PERMISSION BUFFER: PRESENT"
    else
        echo "  ❌ PERMISSION BUFFER: NOT FOUND"
    fi

    # Check for Yes/No options
    if echo "$PANE_CONTENT" | grep -qi "Yes.*No\\|No.*Yes"; then
        echo "  ✅ YES/NO OPTIONS: PRESENT"
    else
        echo "  ❌ YES/NO OPTIONS: NOT FOUND"
    fi
}}

# Wait for SDK initialization
echo "⏳ Waiting {self.sdk_init_wait} seconds for SDK..."
sleep {self.sdk_init_wait}

"""

        # Generate step commands using pipe-based communication
        for i, step in enumerate(self.steps, 1):
            script += f"\necho ''\n"
            script += f"echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'\n"
            script += f"echo 'STEP {i}: {step.description or step.step_type.value}'\n"
            script += f"echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'\n"

            if step.step_type == TestStep.TYPE:
                script += f'send_keystroke "{step.value}" "Typing {step.value}"\n'
            elif step.step_type == TestStep.ENTER:
                script += f'send_keystroke "Enter" "Pressing ENTER"\n'
            elif step.step_type == TestStep.DOWN:
                # Add BEFORE/AFTER state comparison for DOWN arrow
                script += """
# Capture state BEFORE down arrow
tmux capture-pane -t "$SESSION" -p > /tmp/before_down_$$.txt
echo "  📊 State BEFORE down arrow:"
if grep -qi "▸.*Yes\\|>.*Yes" /tmp/before_down_$$.txt; then
    echo "     ✅ 'Yes' is selected (default)"
else
    echo "     ❌ 'Yes' is NOT selected"
fi

"""
                script += f'send_keystroke "Down" "Pressing DOWN arrow"\n'
                script += """
sleep 1  # Give opencli time to update

# Capture state AFTER down arrow
tmux capture-pane -t "$SESSION" -p > /tmp/after_down_$$.txt
echo "  📊 State AFTER down arrow:"
if grep -qi "▸.*No\\|>.*No" /tmp/after_down_$$.txt; then
    echo "     ✅ 'No' is now selected - DOWN ARROW WORKED!"
else
    echo "     ❌ 'No' is NOT selected - DOWN ARROW FAILED!"
fi

# Show the actual selection indicators
echo "  📄 Selection state:"
grep -i "yes\|no" /tmp/after_down_$$.txt | tail -5 | sed 's/^/     /'

"""
            elif step.step_type == TestStep.UP:
                # ADD BEFORE/AFTER state comparison for UP arrow
                script += """
# Capture state BEFORE up arrow
tmux capture-pane -t "$SESSION" -p > /tmp/before_up_$$.txt
echo "  📊 State BEFORE up arrow:"
if grep -qi "▸.*No\\|>.*No" /tmp/before_up_$$.txt; then
    echo "     ✅ 'No' is selected"
else
    echo "     ❌ 'No' is NOT selected"
fi

"""
                script += f'send_keystroke "Up" "Pressing UP arrow"\n'
                script += """
sleep 1  # Give opencli time to update

# Capture state AFTER up arrow
tmux capture-pane -t "$SESSION" -p > /tmp/after_up_$$.txt
echo "  📊 State AFTER up arrow:"
if grep -qi "▸.*Yes\\|>.*Yes" /tmp/after_up_$$.txt; then
    echo "     ✅ 'Yes' is now selected - UP ARROW WORKED!"
else
    echo "     ❌ 'Yes' is NOT selected - UP ARROW FAILED!"
fi

# Show the actual selection indicators
echo "  📄 Selection state:"
grep -i "yes\|no" /tmp/after_up_$$.txt | tail -5 | sed 's/^/     /'

"""
            elif step.step_type == TestStep.WAIT:
                wait_time = step.value or "1"
                script += f'echo "Waiting {wait_time} seconds..."\n'
                script += f'sleep {wait_time}\n'
            elif step.step_type == TestStep.COLLECT_STATE:
                script += "collect_state\n"
            elif step.step_type == TestStep.VERIFY_SELECTION:
                script += self._generate_selection_verification(step.expected_state)

            script += f"sleep {step.wait_after}\n"

        # Add final analysis
        script += self._generate_final_analysis()

        # Add final analysis
        script += self._generate_final_analysis()

        # Cleanup FIRST, then write results
        script += """
# Shutdown server via pipe
echo "QUIT" > "$PIPE"
read -r response < "$RESPONSE_PIPE"

echo ""
echo "Cleaning up..."
tmux kill-session -t "$SESSION" 2>/dev/null
READY_FLAG="/tmp/tui_ready_$SESSION"
rm -f "$PIPE" "$RESPONSE_PIPE" "$TUI_EXPECT_SCRIPT" "$READY_FLAG"

echo ""
"""

        # Write test results to file for Python to read (AFTER cleanup, BEFORE user prompt)
        script += f"""
# Write test results to file (so Python can read while window is still open)
RESULT_FILE="/tmp/tui_test_result_{self.session_name}.txt"
echo "Writing results to $RESULT_FILE..."

# Check if any failures occurred
if grep -q "❌ FAIL" $OUTPUT_LOG; then
    echo "TEST_RESULT=FAIL" > "$RESULT_FILE"
    echo "FAILED_CHECKS<<EOF" >> "$RESULT_FILE"
    grep "❌ FAIL" $OUTPUT_LOG >> "$RESULT_FILE"
    echo "EOF" >> "$RESULT_FILE"
else
    echo "TEST_RESULT=PASS" > "$RESULT_FILE"
fi

# Copy full output to result file
echo "FULL_OUTPUT<<EOF" >> "$RESULT_FILE"
cat $OUTPUT_LOG >> "$RESULT_FILE"
echo "EOF" >> "$RESULT_FILE"

echo ""
echo "Test complete. Log saved to: $OUTPUT_LOG"
echo "Results saved to: $RESULT_FILE"
echo ""
echo "Press ENTER to close this window (Python has already read results)..."
read
"""

        return script


    def _generate_selection_verification(self, expected_state: Optional[Dict[str, Any]]) -> str:
        """Generate bash code for selection verification using server data"""
        expected = expected_state.get('selected', 'No') if expected_state else 'No'
        return f"""
# Capture state before verification
tail -30 "$OUTPUT_LOG" | sed 's/\\x1b\\[[0-9;]*m//g' > /tmp/selection_check_$$.txt
echo "📊 Verifying selection state..."

if grep -qi "▸.*{expected}" /tmp/selection_check_$$.txt || grep -qi "> {expected}" /tmp/selection_check_$$.txt; then
    echo "  ✅ '{expected}' is selected"
else
    echo "  ❌ '{expected}' is NOT selected - VERIFICATION FAILED"
    echo "  📄 Actual selection state:"
    grep -i "▸\\|>" /tmp/selection_check_$$.txt | grep -i "yes\\|no" | tail -3 | sed 's/^/     /'
fi
"""

    def _generate_final_analysis(self) -> str:
        """Generate bash code for final analysis and function identification"""
        return """
echo ''
echo '╔════════════════════════════════════════════════════════════╗'
echo '║  FINAL ANALYSIS                                           ║'
echo '╚════════════════════════════════════════════════════════════╝'
echo ''

# Strip ANSI for analysis
cat "$OUTPUT_LOG" | sed 's/\\x1b\\[[0-9;]*m//g' > /tmp/final_clean_$$.txt

# Check permission buffer
if grep -qi "System.*help" /tmp/final_clean_$$.txt; then
    echo "  ✅ PASS: Permission buffer appeared"
else
    echo "  ❌ FAIL: Permission buffer did NOT appear"
fi

# Check Yes/No options
if grep -qi "Yes" /tmp/final_clean_$$.txt && grep -qi "No" /tmp/final_clean_$$.txt; then
    echo "  ✅ PASS: Yes/No options shown"
else
    echo "  ❌ FAIL: Yes/No options NOT found"
fi

# Check command execution
if grep -qi "Executing command" /tmp/final_clean_$$.txt; then
    echo "  ✅ PASS: Command execution detected"
else
    echo "  ❌ FAIL: Command execution NOT detected"
fi

# Check if DOWN arrow worked (if applicable)
if [ -f /tmp/after_down_$$.txt ]; then
    if grep -qi "▸.*No" /tmp/after_down_$$.txt || grep -qi "> No" /tmp/after_down_$$.txt; then
        echo "  ✅ PASS: DOWN arrow changed selection"
    else
        echo "  ❌ FAIL: DOWN arrow did NOT change selection"
        echo ""
        echo "  🔍 AUTO-ANALYZING: Identifying failing function..."
        echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        # Find permission widget
        WIDGET_FILE=$(find ~/opencli ~/.opencli -path "*/permissions/widget.py" 2>/dev/null | head -1)

        if [ -n "$WIDGET_FILE" ]; then
            echo "  📁 File: $WIDGET_FILE"

            KEY_HANDLER_LINE=$(grep -n "def on_key" "$WIDGET_FILE" | head -1 | cut -d: -f1)

            if [ -n "$KEY_HANDLER_LINE" ]; then
                echo "  🎯 FAILING FUNCTION:"
                echo "     Function: on_key()"
                echo "     Line: $KEY_HANDLER_LINE"
                echo ""
                echo "  📋 DOWN arrow code:"
                sed -n "${KEY_HANDLER_LINE},$((KEY_HANDLER_LINE + 20))p" "$WIDGET_FILE" | grep -A 5 "down" | head -8 | sed 's/^/     /'
                echo ""
                echo "  ⚠️  ROOT CAUSE:"
                echo "     Function exists but not responding to key presses"
                echo ""

                if grep -q "if not self.is_active" "$WIDGET_FILE"; then
                    echo "     ❌ Widget has is_active check at line: $(grep -n "if not self.is_active" "$WIDGET_FILE" | head -1 | cut -d: -f1)"
                    echo "        Problem: Widget may not be active/focused"
                fi

                echo ""
                echo "  💡 FIX SUGGESTIONS:"
                echo "     1. Ensure widget receives focus when displayed"
                echo "     2. Set self.is_active = True"
                echo "     3. Verify on_key() is bound to key events"
                echo "     4. Check event propagation chain"
            fi
        fi
    fi
fi

echo ''
echo 'Selection state changes:'
echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
if [ -f /tmp/before_down_$$.txt ]; then
    echo 'Before DOWN arrow:'
    grep -i "▸\\|>" /tmp/before_down_$$.txt | grep -i "yes\\|no" | sed 's/^/  /'
fi
if [ -f /tmp/after_down_$$.txt ]; then
    echo 'After DOWN arrow:'
    grep -i "▸\\|>" /tmp/after_down_$$.txt | grep -i "yes\\|no" | sed 's/^/  /'
fi

echo ''
echo "Full log: $OUTPUT_LOG"
"""

    def cleanup_old_tests(self):
        """Kill all old test sessions and processes before starting new test"""
        import subprocess
        import glob

        # Kill old controller scripts
        subprocess.run(["pkill", "-f", "tui_controller"], stderr=subprocess.DEVNULL)

        # Kill old expect scripts
        subprocess.run(["pkill", "-f", "tui_expect"], stderr=subprocess.DEVNULL)

        # Kill old tmux sessions
        try:
            result = subprocess.run(["tmux", "ls"], capture_output=True, text=True, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "tui_test" in line:
                        session_name = line.split(":")[0]
                        subprocess.run(["tmux", "kill-session", "-t", session_name], stderr=subprocess.DEVNULL)
        except:
            pass

        # Clean up old temp files
        for pattern in ["/tmp/tui_*", "/tmp/*tui_test*"]:
            for file in glob.glob(pattern):
                try:
                    if os.path.isfile(file):
                        os.remove(file)
                except:
                    pass

    def run_test(self, visual: bool = True) -> TestResult:
        """
        Execute the test

        Args:
            visual: Whether to open visual windows (default True)

        Returns:
            TestResult with pass/fail status and details
        """
        # CRITICAL: Clean up old tests before starting new one
        print("🧹 Cleaning up old test sessions...")
        self.cleanup_old_tests()
        time.sleep(1)  # Give processes time to die
        print("✅ Cleanup complete\n")

        # Generate controller script
        script_content = self.create_test_script()
        script_path = f"{self.temp_dir}/tui_controller_{os.getpid()}.sh"

        with open(script_path, 'w') as f:
            f.write(script_content)

        os.chmod(script_path, 0o755)

        # Generate main test launcher
        launcher = self._generate_launcher(script_path, visual)
        launcher_path = f"{self.temp_dir}/tui_test_launcher_{os.getpid()}.sh"

        with open(launcher_path, 'w') as f:
            f.write(launcher)

        os.chmod(launcher_path, 0o755)

        if visual:
            # Run with visual windows (non-blocking)
            subprocess.Popen([launcher_path])

            # Wait for result file to be created (with timeout)
            result_file = f"/tmp/tui_test_result_{self.session_name}.txt"
            timeout = 60  # 60 seconds max wait
            start_time = time.time()

            print(f"Waiting for test to complete... (result file: {result_file})")
            while not os.path.exists(result_file):
                if time.time() - start_time > timeout:
                    return TestResult(
                        passed=False,
                        message=f"Test timeout - result file not created after {timeout}s",
                        details={},
                        log_file=self.output_log
                    )
                time.sleep(2)
                print(".", end="", flush=True)

            print("\nTest complete! Reading results...")
            time.sleep(1)  # Give it a moment to finish writing

            with open(result_file, 'r') as f:
                result_content = f.read()
            return self._parse_results_from_file(result_content)
        else:
            # Run headless
            result = subprocess.run([script_path], capture_output=True, text=True)
            return self._parse_results(result.stdout)

    def _generate_launcher(self, controller_script: str, visual: bool) -> str:
        """Generate main test launcher script with pipe-based server communication"""
        return f"""#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  TUI Test Framework - Pipe-Based Server Communication     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

{"" if not visual else '''
# Visual mode - open two Terminal windows
# CRITICAL NEW ORDER: LEFT window FIRST (launches opencli), then RIGHT (detects it)
# LEFT window = Launches opencli tui in tmux
# RIGHT window = Detects opencli and sends commands

# Open LEFT window FIRST (launches opencli)
echo "▶ Opening LEFT window - Launches opencli tui..."
osascript <<TUI_WINDOW
tell application "Terminal"
    set tuiWindow to do script "cd ''' + os.getcwd() + ''' && ''' + controller_script + ''' --tui-only"
    set custom title of tuiWindow to "opencli TUI (LEFT)"
    set position of window 1 to {50, 50}
    set size of window 1 to {800, 600}
    activate
end tell
TUI_WINDOW

echo "✅ LEFT window opened (launching opencli)"
echo "   Waiting for opencli to start..."
sleep 5

# Open RIGHT window SECOND (detects and controls opencli)
echo "▶ Opening RIGHT window - Detects opencli and sends commands..."
osascript <<CONTROLLER_WINDOW
tell application "Terminal"
    set controllerWindow to do script "cd ''' + os.getcwd() + ''' && ''' + controller_script + '''"
    set custom title of controllerWindow to "CONTROLLER (RIGHT)"
    set position of window 1 to {900, 50}
    set size of window 1 to {600, 600}
    activate
end tell
CONTROLLER_WINDOW

echo "✅ RIGHT window opened (detecting opencli)"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  WATCH:                                                   ║"
echo "║  • LEFT window (TUI) - Shows opencli tui responding       ║"
echo "║  • RIGHT window (Controller) - Shows commands being sent  ║"
echo "╚════════════════════════════════════════════════════════════╝"
'''}

{"" if visual else f'''
# Headless mode - run controller directly
echo "▶ Running test in headless mode..."
{controller_script}
'''}
"""

    def _parse_results(self, output: str) -> TestResult:
        """Parse test output and create result object"""
        passed = "❌ FAIL" not in output
        failing_functions = []

        # Extract failing function info if present
        if "FAILING FUNCTION:" in output:
            # Parse function details from output
            lines = output.split('\n')
            func_info = {}
            for line in lines:
                if "Function:" in line:
                    func_info['function'] = line.split(':')[1].strip()
                elif "Line:" in line:
                    func_info['line'] = line.split(':')[1].strip()
                elif "File:" in line:
                    func_info['file'] = line.split(':')[1].strip()

            if func_info:
                failing_functions.append(func_info)

        return TestResult(
            passed=passed,
            message="Test completed",
            details={"output": output},
            failing_functions=failing_functions if failing_functions else None,
            log_file=self.output_log
        )

    def _parse_results_from_file(self, content: str) -> TestResult:
        """Parse test results from result file"""
        lines = content.split('\n')
        passed = lines[0].strip() == "TEST_RESULT=PASS" if lines else False

        # Extract full output
        full_output = ""
        in_output = False
        for line in lines:
            if line.startswith("FULL_OUTPUT<<EOF"):
                in_output = True
                continue
            elif line == "EOF" and in_output:
                break
            elif in_output:
                full_output += line + "\n"

        # Parse for failing functions
        failing_functions = []
        if "FAILING FUNCTION:" in full_output:
            lines_list = full_output.split('\n')
            func_info = {}
            for line in lines_list:
                if "Function:" in line:
                    func_info['function'] = line.split(':')[1].strip()
                elif "Line:" in line:
                    func_info['line'] = line.split(':')[1].strip()
                elif "File:" in line:
                    func_info['file'] = line.split(':')[1].strip()
            if func_info:
                failing_functions.append(func_info)

        message = "Test passed" if passed else "Test failed - arrow keys not working"

        return TestResult(
            passed=passed,
            message=message,
            details={"output": full_output},
            failing_functions=failing_functions if failing_functions else None,
            log_file=self.output_log
        )

    def cleanup(self):
        """Clean up test resources"""
        subprocess.run(["tmux", "kill-session", "-t", self.session_name],
                      stderr=subprocess.DEVNULL)


# Convenience API functions
def create_permission_buffer_test(command: str = "/help") -> TUITestFramework:
    """
    Create a standard permission buffer test

    Args:
        command: Command to test (default "/help")

    Returns:
        Configured TUITestFramework
    """
    framework = TUITestFramework()

    framework.add_step(
        TestStep.TYPE,
        command,
        f"Type {command} command"
    )

    framework.add_step(
        TestStep.ENTER,
        description="Autocomplete command"
    )

    framework.add_step(
        TestStep.ENTER,
        description="Submit command",
        wait_after=4
    )

    framework.add_step(
        TestStep.COLLECT_STATE,
        description="Collect permission buffer state"
    )

    framework.add_step(
        TestStep.DOWN,
        description="Press DOWN arrow to select No",
        wait_after=2
    )

    framework.add_step(
        TestStep.VERIFY_SELECTION,
        description="Verify No is selected",
        expected_state={"selected": "No"}
    )

    framework.add_step(
        TestStep.ENTER,
        description="Confirm selection",
        wait_after=2
    )

    return framework


if __name__ == "__main__":
    # Example usage
    print("Creating permission buffer test...")
    test = create_permission_buffer_test()
    result = test.run_test(visual=True)
    print(f"\nTest result: {'PASSED' if result.passed else 'FAILED'}")
    if result.failing_functions:
        print("\nFailing functions:")
        for func in result.failing_functions:
            print(f"  - {func.get('function')} at {func.get('file')}:{func.get('line')}")
