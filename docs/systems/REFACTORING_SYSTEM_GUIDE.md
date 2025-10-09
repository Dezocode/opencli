# Intelligent Refactoring System - Complete Guide

## Overview

The Intelligent Refactoring System is a fully automated, concurrency-aware code refactoring suite that:
- **Analyzes** code for violations of architectural rules, concurrency issues, and performance problems
- **Proposes** data-driven refactorings with complete justification
- **Executes** refactorings safely in git worktree sandboxes
- **Validates** changes through automated tests and performance profiling
- **Self-heals** when performance degrades or new violations are introduced

---

## Architecture Components

### 1. **architecture.yml** - The Blueprint
Defines the desired architecture:
```yaml
modules:
  - name: async_interactive
    max_lines: 800
    forbidden_imports:
      - modules.api_client

performance_budgets:
  - function: "write_stream"
    max_time_ms: 10

threading_rules:
  - thread_name: "MainThread"
    forbidden_operations: ["blocking_io"]
```

### 2. **Code Analyzer** (`code_analyzer.py`)
- Uses AST parsing to build function call graphs
- Uses NetworkX for graph analysis and community detection
- Identifies clusters of related functions
- Calculates cohesion (internal connections) and coupling (external connections)

### 3. **Architecture Validator** (`architecture_validator.py`)
- Validates code against architecture.yml
- Checks file sizes, import restrictions, performance budgets
- Detects threading rule violations
- Generates compliance reports

### 4. **Concurrency Analyzer** (`concurrency_analyzer.py`)
- Detects blocking I/O in async functions
- Finds missing async/await
- Identifies UI thread violations
- Detects race conditions and missing locks
- Suggests automatic concurrency improvements

### 5. **Refactoring Executor** (`refactor_executor.py`)
- Creates git worktree sandboxes for safe testing
- Uses rope library for programmatic refactoring
- Moves functions between modules
- Updates imports automatically
- Runs test suite in sandbox
- Generates diffs for review

### 6. **Runtime Profiler** (`profiler.py`)
- Uses cProfile for performance profiling
- Analyzes thread states
- Detects blocked/deadlocked threads
- Tracks performance budgets
- Establishes performance baselines

### 7. **Auto Refactor Manager** (`auto_refactor.py`)
- Uses watchdog to monitor file changes
- Triggers refactoring when files exceed size limits
- Queues refactoring jobs
- Worker thread processes queue
- Integrates with permission system

### 8. **Refactoring Orchestrator** (`refactor_orchestrator.py`)
- **MASTER COORDINATOR**
- Ties all components together
- Implements self-healing loop
- Manages refactoring sessions
- Learns from approved/rejected refactorings

---

## Usage Workflows

### Workflow 1: Manual Analysis and Refactoring

```bash
# 1. Analyze a file
/refactor suggest-split modules/async_interactive.py

# Output:
# ✓ File: modules/async_interactive.py (2000 lines)
#
# CLUSTER 1: Command Handlers (cohesion: 0.85, coupling: 0.15)
#   Functions: handle_/refactor, handle_/model, handle_/provider
#   Lines: 450
#   Rationale: Functions are highly cohesive. Low coupling to rest of file
#   Suggested module: modules/command_handlers.py

# 2. Execute the refactoring
/refactor execute modules/async_interactive.py cluster-1

# System will:
# - Create git worktree at /tmp/opencli_refactor_xxx
# - Extract functions to new module
# - Update imports
# - Run tests
# - Show diff and results
# - Request your approval

# 3. Review and approve
# [Permission prompt shows test results, diff, performance impact]
# approve/reject
```

### Workflow 2: Automated Monitoring with Self-Healing

```bash
# 1. Start the intelligent refactoring system
/refactor auto start

# System will:
# ✓ Load architecture.yml blueprint
# ✓ Start watching modules/ and agents/ directories
# ✓ Start performance profiling
# ✓ Begin self-healing monitor

# 2. Make changes to your code
# (edit modules/async_interactive.py and save)

# 3. System automatically:
# ⏺ Detects file exceeded max_lines
# ⏺ Analyzes for best extraction strategy
# ⏺ Creates worktree sandbox
# ⏺ Executes refactoring
# ⏺ Runs tests and performance profiling
# ⏺ Requests your permission

# 4. Review the proposal
# [Shows comprehensive analysis, test results, performance impact]

# 5. Approve or reject
# - Approve: changes applied to your working directory
# - Reject: worktree cleaned up, learns from your feedback

# 6. System continues monitoring
# - Watches for new violations
# - Monitors performance degradation
# - Proposes fixes automatically
```

### Workflow 3: Performance Profiling and Optimization

```bash
# 1. Start profiling
/refactor profile start

# 2. Use the application normally
# (perform typical operations to capture realistic profile)

# 3. Stop profiling and get report
/refactor profile stop

# Output:
# ==============================
# PERFORMANCE PROFILE
# ==============================
# Total Calls: 45,203
# Total Time: 2.345s
#
# ⚠️  PERFORMANCE BUDGET VIOLATIONS:
#   _rebuild_display: 75.2ms (budget: 50.0ms)
#   write_stream: 15.8ms (budget: 10.0ms)
#
# TOP 20 FUNCTIONS BY CUMULATIVE TIME:
#   modules/streaming_display.py:142:_rebuild_display
#     Cumulative: 0.452s | Calls: 6 | Avg: 75.2ms

# 4. System automatically proposes optimization
# "Function _rebuild_display exceeds budget. Analyzing..."
# "Detected: Multiple list iterations. Suggest: Single-pass algorithm"
# "Execute optimization? [y/n]"
```

### Workflow 4: Thread Analysis and Concurrency Fixes

```bash
# 1. Analyze current threads
/refactor threads

# Output:
# ==============================
# THREAD ANALYSIS
# ==============================
# Total Threads: 5
#
# Thread ID: 123456
#   Name: MainThread
#   Stack Trace:
#     File "modules/simple_tui.py", line 234, in _rebuild_display
#     File "modules/streaming_display.py", line 142, in update
#
# Thread ID: 789012
#   Name: queue_processor
#   Daemon: True
#   Stack Trace:
#     File "modules/simple_tui.py", line 660, in _process_queue

# 2. Detect blocked threads
/refactor blocking

# Output:
# ⚠️  BLOCKED THREADS DETECTED:
#
# Thread: queue_processor
#   Blocked for: 2.5s
#   Stack: Waiting on Lock at modules/simple_tui.py:665
#   Issue: Potential deadlock with MainThread

# 3. Run concurrency analysis on file
/refactor concurrency modules/simple_tui.py

# Output:
# ==================================
# CONCURRENCY ANALYSIS REPORT
# ==================================
# Total Issues: 3
#
# 🔴 CRITICAL ISSUES:
#
#   modules/simple_tui.py:234 in _rebuild_display
#     Type: ui_thread_violation
#     Blocking file I/O on UI thread: open(
#     Fix: Wrap in asyncio.to_thread()
#     ✨ Auto-fixable

# 4. Auto-fix concurrency issues
# System proposes: "Wrap blocking operation in asyncio.to_thread()"
# Shows diff, test results
# Request approval
```

---

## Advanced Features

### Self-Healing Performance Monitor

The system continuously monitors performance and automatically fixes degradation:

```python
# Automatically happens in background when monitoring is active

# System detects:
# ⚠️  PERFORMANCE DEGRADATION DETECTED:
#    Function: _rebuild_display
#    Current: 125.4ms
#    Baseline: 75.2ms
#    Degradation: 66.8%
#
#    🔍 Analyzing for optimization opportunities...
#    Found: Unnecessary list comprehension in hot path
#    Proposal: Cache computed values
#
#    Execute optimization? [y/n]
```

### Learning from Approvals

The orchestrator learns your preferences:

```python
# After 5 approvals of "extract command handlers" pattern:
# System: "Detected similar pattern in modules/config_manager.py"
# System: "Auto-applying approved pattern (you can disable this)"

# After 3 rejections of "split large functions" pattern:
# System: "Skipping similar split proposal (learned from rejections)"
```

### Architecture Compliance Checks

```bash
/refactor validate

# Output:
# ==============================
# ARCHITECTURE COMPLIANCE REPORT
# ==============================
# Files Checked: 45
# Status: ❌ FAILED
# Errors: 3
# Warnings: 7
#
# 🔴 ERRORS:
#
#   modules/async_interactive.py:?
#     Rule: max_lines
#     File has 2000 lines, exceeds limit of 800
#     💡 Run /refactor suggest-split modules/async_interactive.py
#
#   modules/simple_tui.py:142
#     Rule: forbidden_import
#     Forbidden import: modules.api_client
#     💡 Remove or refactor to eliminate modules.api_client dependency
```

---

## Configuration

### Customizing architecture.yml

```yaml
# Add your own modules
modules:
  - name: my_module
    path: modules/my_module.py
    max_lines: 500
    allowed_imports:
      - modules.utils
    forbidden_imports:
      - modules.api_client

# Set performance budgets
performance_budgets:
  - function: "my_critical_function"
    max_time_ms: 20
    location: "modules/my_module.py"
    rationale: "Called in hot path"

# Define threading rules
threading_rules:
  - thread_name: "MyWorkerThread"
    allowed_operations: ["network_io", "file_io"]
    forbidden_operations: ["ui_updates"]
    max_blocking_time_ms: 1000
```

### Auto-Refactor Configuration

```bash
# Start with custom config
/refactor auto start --max-lines 600 --min-cluster-size 5

# Or via Python:
from modules.auto_refactor import AutoRefactorConfig

config = AutoRefactorConfig(
    max_file_lines=600,
    min_cluster_size=5,
    min_cluster_lines=150,
    watch_paths=['modules/', 'my_code/'],
    exclude_patterns=['test_', 'venv', '__pycache__']
)
```

---

## Best Practices

### 1. Start with Manual Analysis
Before enabling auto-refactoring, run manual analysis:
```bash
/refactor suggest-split <file>
/refactor concurrency <file>
/refactor validate
```

### 2. Set Realistic Budgets
Start with measured budgets, not aspirational ones:
```bash
# Profile first
/refactor profile start
# (use application)
/refactor profile stop

# Then set budgets based on actual measurements
```

### 3. Review Auto-Refactorings
Always review the diff and test results before approving.

### 4. Monitor Performance Baselines
The system learns "normal" performance. Unusual spikes trigger analysis.

### 5. Use Git Worktrees
All refactorings happen in isolated worktrees. Your working directory is safe.

---

## Troubleshooting

### "Refactoring failed - no changes made"
- Check if functions are actually defined in the file
- Verify file is valid Python (no syntax errors)
- Check function names in cluster match actual definitions

### "Tests failed in worktree"
- Review test output in permission prompt
- Tests may need updating for new module structure
- Check import paths are correct

### "Permission timeout"
- System waits 5 minutes for approval
- Increase timeout in code if needed
- Check permission handler is properly connected

### "Performance degradation false positive"
- Baselines are established during first run
- Cold starts may show degradation
- Adjust degradation threshold (default 50%)

---

## Integration with OpenCLI

The refactoring system is fully integrated into OpenCLI:

```bash
# In OpenCLI TUI:
> /refactor auto start

# System monitors in background
# You continue using OpenCLI normally
# Permission prompts appear in TUI when refactorings are ready
# Approve/reject without leaving the chat
```

---

## Summary

**The Intelligent Refactoring System gives you:**

✅ **Automated code analysis** - AST, graphs, metrics
✅ **Architecture enforcement** - Validates against blueprint
✅ **Concurrency detection** - Finds threading issues, suggests fixes
✅ **Safe execution** - Git worktree sandboxes, automated tests
✅ **Performance monitoring** - Profiles, budgets, degradation detection
✅ **Self-healing** - Detects and fixes regressions automatically
✅ **Learning** - Adapts to your approval patterns
✅ **Full automation** - File watching, queueing, execution

**Master workflow:**
1. Define architecture in architecture.yml
2. Start monitoring: `/refactor auto start`
3. System watches, analyzes, proposes, tests, requests approval
4. You review and approve/reject
5. System learns and improves
6. Performance stays optimal, architecture stays clean

**You focus on features. The system maintains quality.**
