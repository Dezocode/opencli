# Intelligent Refactoring System - Quick Start

## What You Now Have

A **fully automated, self-healing refactoring system** that safely modularizes excessive line-length files and automatically establishes/fixes multi-threading concurrency.

## 30-Second Quick Start

```bash
# 1. Ensure dependencies are installed
pip install rope watchdog networkx pyyaml

# 2. Start intelligent monitoring
opencli
> /refactor auto start

# 3. That's it! The system now:
✓ Watches your files
✓ Detects violations of architecture.yml
✓ Analyzes concurrency issues
✓ Proposes refactorings automatically
✓ Executes in safe sandbox
✓ Runs tests and performance checks
✓ Requests your approval
✓ Self-heals performance degradation
```

## How It Works

### The Four-Step Cycle

```
1. ANALYZE    → File exceeds max_lines, has blocking I/O, violates rules
2. PROPOSE    → Generate refactoring plan with full justification
3. VERIFY     → Execute in worktree, run tests, check performance
4. EXECUTE    → Request approval, apply if approved, learn from feedback
```

### Automatic Concurrency Fixes

The system detects and auto-fixes:
- ❌ Blocking I/O in async functions → ✅ Wrapped in `asyncio.to_thread()`
- ❌ Missing `async`/`await` → ✅ Converted to async function
- ❌ File I/O on UI thread → ✅ Moved to background thread
- ❌ Race conditions without locks → ✅ Adds `asyncio.Lock` or `threading.Lock`

### Architecture Enforcement

Validates against `architecture.yml`:
```yaml
modules:
  - name: async_interactive
    max_lines: 800
    forbidden_imports:
      - modules.api_client  # UI shouldn't call API directly

threading_rules:
  - thread_name: "MainThread"
    forbidden_operations: ["blocking_io"]
```

Violations trigger automatic refactoring proposals.

## Common Workflows

### Manual: Analyze and Refactor a File

```bash
> /refactor suggest-split modules/async_interactive.py

# Shows:
# CLUSTER 1: Command Handlers
#   Functions: handle_/refactor, handle_/model (15 functions)
#   Lines: 450
#   Cohesion: 0.85 (high)
#   Coupling: 0.15 (low)
#   Suggested: modules/command_handlers.py
#
# Execute refactoring? [y/n]

> y

# System creates worktree, extracts functions, runs tests
# Shows diff and results, requests approval
```

### Automated: Set It and Forget It

```bash
> /refactor auto start

# System monitors in background
# Automatically proposes refactorings when violations detected
# Permission prompts appear in TUI
# You review and approve/reject without leaving chat
```

### Performance: Profile and Optimize

```bash
> /refactor profile start
# (use application normally)
> /refactor profile stop

# Shows:
# ⚠️  PERFORMANCE BUDGET VIOLATIONS:
#   _rebuild_display: 75ms (budget: 50ms)
#
# System analyzes and proposes optimization
```

### Concurrency: Find and Fix Threading Issues

```bash
> /refactor concurrency modules/simple_tui.py

# Shows:
# 🔴 CRITICAL: Blocking file I/O on UI thread
#   Fix: Wrap in asyncio.to_thread()
#   ✨ Auto-fixable
#
# Execute fix? [y/n]
```

### Architecture: Validate Compliance

```bash
> /refactor validate

# Shows:
# ❌ ERRORS: 3
#   modules/async_interactive.py: 2000 lines (limit: 800)
#   modules/simple_tui.py: Forbidden import: modules.api_client
#
# System auto-proposes fixes for each violation
```

## Key Features

### 1. Safe Execution
- All refactorings happen in isolated git worktrees
- Your working directory is never touched until you approve
- Full rollback capability

### 2. Comprehensive Validation
- AST parsing and graph analysis
- Automated test suite execution
- Performance profiling before/after
- Architecture compliance checks

### 3. Self-Healing
- Monitors performance baselines
- Detects degradation automatically
- Proposes optimizations
- Fixes regressions without manual intervention

### 4. Learning System
- Tracks your approval patterns
- Auto-applies similar approved refactorings
- Skips patterns you've rejected
- Improves suggestions over time

## Architecture Blueprint (architecture.yml)

The blueprint defines your ideal architecture. The system enforces it.

**Example:**
```yaml
modules:
  - name: async_interactive
    max_lines: 800
    responsibility: "Async mode, command handling"
    allowed_imports:
      - modules.tool_executor
      - modules.session_manager
    forbidden_imports:
      - modules.api_client

performance_budgets:
  - function: "write_stream"
    max_time_ms: 10
    location: "modules/streaming_display.py"

threading_rules:
  - thread_name: "MainThread"
    allowed_operations: ["ui_render", "event_handling"]
    forbidden_operations: ["blocking_io", "network_requests"]

refactoring_targets:
  - file: "modules/async_interactive.py"
    split_strategy:
      - extract: "Command handlers"
        to: "modules/command_handlers.py"
        functions: ["handle_/refactor", "handle_/model"]
```

## Dependencies

Required:
```bash
pip install rope watchdog networkx pyyaml
```

Optional (for visualization):
```bash
pip install pyan3  # Call graph visualization
```

## Under the Hood

### Components

1. **CodeAnalyzer**: AST + NetworkX graph analysis
2. **ArchitectureValidator**: Validates against blueprint
3. **ConcurrencyAnalyzer**: Detects threading issues
4. **RefactoringExecutor**: Worktree sandbox + rope library
5. **RuntimeProfiler**: Performance monitoring
6. **AutoRefactorManager**: File watching with watchdog
7. **RefactoringOrchestrator**: Master coordinator

### Data Flow

```
File Change (watchdog)
  ↓
Architecture Validation (architecture_validator)
  ↓
Concurrency Analysis (concurrency_analyzer)
  ↓
Code Clustering (code_analyzer)
  ↓
Refactoring Plan (refactor_orchestrator)
  ↓
Worktree Execution (refactor_executor)
  ↓
Test + Profile Validation (profiler)
  ↓
Permission Request
  ↓
Apply or Reject
```

## Troubleshooting

**"No refactoring needed"**
- File is within limits
- No clear clusters detected
- Increase `min_cluster_size` in config

**"Tests failed in sandbox"**
- Review test output in prompt
- Tests may need import updates
- Check for missing dependencies

**"Performance false positive"**
- Baselines established on first run
- System learns normal performance over time
- Adjust degradation threshold if needed

## Best Practices

1. **Start with validation**: `/refactor validate` to see current state
2. **Profile before monitoring**: Establish performance baselines
3. **Review architecture.yml**: Ensure it matches your design goals
4. **Approve incrementally**: Start with small refactorings
5. **Monitor learning**: Check approved/rejected patterns

## Read More

See `REFACTORING_SYSTEM_GUIDE.md` for comprehensive documentation, advanced features, and detailed workflows.

---

**You now have a self-maintaining, architecture-enforcing, concurrency-aware codebase.**

The system ensures:
- ✅ Files stay within size limits
- ✅ Imports follow architectural rules
- ✅ Performance budgets are met
- ✅ Threading rules are enforced
- ✅ Blocking operations are async
- ✅ Code stays modular and maintainable

**Focus on features. The system maintains quality.**
