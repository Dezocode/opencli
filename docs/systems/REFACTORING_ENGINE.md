# Intelligent Refactoring Engine

## Overview

The Intelligent Refactoring Engine is a self-maintaining code quality system that combines runtime analysis, static architecture compliance, and automated refactoring to keep the OpenCLI codebase clean and organized.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  INTELLIGENT REFACTORING ENGINE              │
└─────────────────────────────────────────────────────────────┘
                            ▼
        ┌───────────────────────────────────────┐
        │         ARCHITECTURE BLUEPRINT         │
        │         (architecture.yml)             │
        │  • Module dependencies                 │
        │  • Performance budgets                 │
        │  • Threading rules                     │
        │  • Refactoring targets                 │
        └───────────────────────────────────────┘
                ▼                    ▼                ▼
     ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
     │  PHASE 1:       │  │  PHASE 2:       │  │  PHASE 3:       │
     │  Runtime        │  │  Static         │  │  Automated      │
     │  Analysis       │  │  Analysis       │  │  Refactoring    │
     └─────────────────┘  └─────────────────┘  └─────────────────┘
            ▼                     ▼                     ▼
     ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
     │  profiler.py    │  │  architecture_  │  │  refactor_      │
     │  • cProfile     │  │  checker.py     │  │  executor.py    │
     │  • Thread       │  │  • Import       │  │  • Git          │
     │    analysis     │  │    compliance   │  │    worktrees    │
     │  • Bottlenecks  │  │  • File sizes   │  │  • Rope         │
     │  • Deadlocks    │  │  • Metrics      │  │    refactoring  │
     └─────────────────┘  └─────────────────┘  │  • Test         │
                                                │    verification │
                                                └─────────────────┘
                                                       ▼
                                                ┌─────────────────┐
                                                │  code_          │
                                                │  analyzer.py    │
                                                │  • Call graphs  │
                                                │  • Data flow    │
                                                │  • Clustering   │
                                                └─────────────────┘
                                                       ▼
                                          ┌──────────────────────┐
                                          │  PERMISSION SYSTEM   │
                                          │  (async_            │
                                          │   permissions.py)    │
                                          │  • User approval     │
                                          │  • Risk assessment   │
                                          │  • Buffered prompts  │
                                          └──────────────────────┘
```

## Phase 1: Runtime Analysis (✅ COMPLETE)

### Module: `profiler.py`

**Purpose**: Monitor runtime performance and detect threading issues

**Features**:
- Performance profiling using Python's `cProfile`
- Thread state analysis and deadlock detection
- Performance budget tracking
- Bottleneck identification

**Commands**:
```bash
/refactor profile start    # Start profiling
/refactor profile stop     # Stop and show report
/refactor threads          # Analyze thread states
/refactor blocking         # Detect blocked threads
/refactor budget <func> <ms>  # Set performance budget
```

**Example Output**:
```
PERFORMANCE PROFILE
Total Calls: 45,231
Total Time: 2.451s

⚠️ PERFORMANCE BUDGET VIOLATIONS:
  write_stream: 15.2ms (budget: 10.0ms)
  _rebuild_display: 75.3ms (budget: 50.0ms)

TOP 20 FUNCTIONS BY CUMULATIVE TIME:
  modules/async_interactive.py:process_user_input
    Cumulative: 1.234s | Calls: 1,024 | Avg: 1.21ms
  modules/streaming_display.py:write_stream
    Cumulative: 0.891s | Calls: 5,832 | Avg: 0.15ms
```

## Phase 2: Static Analysis (✅ COMPLETE)

### Module: `architecture.yml`

**Purpose**: Define desired codebase architecture

**Sections**:
1. **Module Structure** - Define responsibilities, dependencies, file size limits
2. **Performance Budgets** - Set time limits for critical functions
3. **Threading Rules** - Define allowed operations per thread
4. **Refactoring Targets** - Identify files to split with strategies
5. **Quality Rules** - Max complexity, nesting depth, etc.
6. **Architectural Patterns** - Enforce dependency injection, separation of concerns
7. **Metrics Tracking** - Monitor LOC, test coverage, etc.

### Module: `architecture_checker.py`

**Purpose**: Validate compliance against blueprint

**Checks**:
- ✅ Forbidden imports
- ✅ Module dependency violations
- ✅ File size limits
- ✅ UI/Business separation
- ✅ Code metrics

**Usage**:
```bash
python check_architecture.py
```

**Example Output**:
```
ARCHITECTURE COMPLIANCE REPORT

📊 METRICS:
  total_lines_of_code: 12,451.0
  module_count: 42.0
  average_function_length: 28.3

❌ ERRORS (2):
  [forbidden_import] modules/simple_tui.py
    Forbidden import 'modules.api_client' in simple_tui
    Rule: forbidden_imports

⚠️ WARNINGS (3):
  [max_lines] modules/async_interactive.py
    File has 2000 lines (max: 2000)

✅ No critical violations found
```

## Phase 3: Automated Refactoring (✅ COMPLETE)

### Module: `code_analyzer.py`

**Purpose**: Identify code clusters for extraction

**Analysis**:
- Call graph construction (which functions call each other)
- Data flow analysis (which functions share state)
- Community detection (identify tightly coupled clusters)
- Cohesion/coupling scoring

**Metrics**:
- **Cohesion**: How tightly functions in cluster are related (higher = better)
- **Coupling**: How dependent cluster is on external code (lower = better)

### Module: `refactor_executor.py`

**Purpose**: Safely execute refactorings in git worktree sandbox

**Workflow**:
```
1. Create git worktree (isolated sandbox)
2. Perform refactoring (using rope library)
3. Run tests in worktree
4. Generate diff for review
5. Request permission via TUI
6. If approved: Apply changes to main branch
7. If rejected: Delete worktree
```

**Safety Features**:
- ✅ All changes in isolated git worktree
- ✅ Test verification before approval
- ✅ Permission system integration
- ✅ Automatic cleanup on rejection
- ✅ Your working code never touched until approved

## Integration with Permission System

All refactoring file changes go through the existing permission buffer:

```python
# Refactoring generates changes
result = executor.execute_extraction(plan)

# Permission prompt shown in TUI
prompt_data = {
    'title': 'Refactoring Permission',
    'message': f'Extract {len(plan.functions_to_move)} functions to {plan.target_file}?',
    'details': {
        'files_modified': result.changes,
        'lines_moved': plan.estimated_lines,
        'test_results': result.test_results,
        'diff': result.diff
    },
    'options': ['approve', 'reject']
}

# User approves/rejects via TUI
if approved:
    executor.apply_refactoring(result)
else:
    executor.reject_refactoring(result)
```

## Commands (All Available Now)

### Runtime Analysis
```bash
/refactor profile start           # Start profiling
/refactor profile stop            # Show performance report
/refactor threads                 # Analyze thread states
/refactor blocking                # Detect deadlocks
/refactor budget <func> <ms>      # Set performance budget
```

### Code Analysis
```bash
/refactor suggest-split <file>    # Suggest module extractions and show clusters
```

### Automated Refactoring
```bash
/autorefactor start               # Start file watcher for auto-refactoring
/autorefactor stop                # Stop file watching
/autorefactor status              # Show current status and queue
```

### Static Analysis
```bash
# Run from terminal
python check_architecture.py      # Check compliance against architecture.yml
```

## Current Refactoring Targets

From `architecture.yml`:

### 1. `async_interactive.py` (2000 lines → 800 lines target)
**Clusters to Extract**:
- Command handlers → `command_handlers.py`
- Tool execution flow → `tool_flow.py`

### 2. `simple_tui.py` (1200 lines → 600 lines target)
**Clusters to Extract**:
- Mouse event handling → `mouse_handler.py`

### 3. `streaming_display.py` (800 lines → 500 lines target)
**Clusters to Extract**:
- Text selection logic → `text_selector.py`

## System Status: ✅ FULLY OPERATIONAL

All phases complete and ready to use:

1. ✅ **Runtime profiling** - Monitor performance and thread states
2. ✅ **Static analysis** - Enforce architecture compliance
3. ✅ **Code analysis** - Identify refactoring opportunities with call graphs
4. ✅ **Rope integration** - Intelligent function extraction
5. ✅ **File watcher** - Automatic monitoring with watchdog
6. ✅ **Permission system** - User approval workflow for all refactorings
7. ✅ **Git worktree sandbox** - Safe testing before applying changes

## Usage

### Quick Start
```bash
# Start auto-refactoring - monitors files >500 lines
/autorefactor start

# Analyze a specific file
/refactor suggest-split modules/async_interactive.py

# Monitor performance
/refactor profile start
# ... run operations ...
/refactor profile stop
```

## Benefits

### For Developers
- 📊 **Visibility** - Know exactly where performance issues are
- 🔍 **Insights** - Understand code dependencies and coupling
- 🛡️ **Safety** - All refactorings tested and approved before application
- ⚡ **Speed** - Automated analysis and refactoring suggestions

### For Codebase
- 📉 **Reduced Complexity** - Files automatically split when too large
- 🎯 **Better Organization** - Related code grouped together
- ⚙️ **Compliance** - Architecture rules automatically enforced
- 🧪 **Quality** - Performance budgets and threading rules monitored

## Philosophy

> "The code should maintain itself. Developers should focus on features, not file organization."

The Intelligent Refactoring Engine embodies this philosophy by:
1. **Monitoring** - Continuously watching for violations
2. **Analyzing** - Understanding code structure and relationships
3. **Suggesting** - Proposing improvements with rationale
4. **Executing** - Safely applying approved changes
5. **Verifying** - Ensuring no functionality is broken

All while keeping the developer in control through the permission system.
