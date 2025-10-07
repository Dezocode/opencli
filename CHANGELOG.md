# Changelog

All notable changes to OpenCLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2025-10-07

### Added

#### 🔒 Permission System
- **Interactive permission prompts** for dangerous tool operations
  - Inline prompts render inside prompt box with auto-flex height
  - Keyboard navigation: Up/Down to select, Enter to confirm, ESC to cancel
  - Risk-based classification: SAFE / RISKY / DANGEROUS / CRITICAL
  - Persistent settings saved to `~/.opencli/tool_permissions.json`
- **ToolPermissionManager**: Risk assessment and permission tracking
  - Path-based risk detection (parent dirs, system paths)
  - Per-tool permission persistence
  - Fail-open design (errors don't block execution)
- **AsyncPermissionHandler**: Non-blocking permission UI integration
  - 5-minute timeout with automatic denial
  - Tool-specific prompt templates (Bash, Write, Edit, WebFetch)
  - Response handling with allow-once/allow-always options

#### ⏸️ ESC Interrupt
- **Press ESC to cancel streaming API calls**
  - Interrupts long-running responses immediately
  - Clean cancellation with user notification
  - Non-blocking implementation

### Changed

#### 🎨 UI Integration
- **MultiLineInput permission rendering**
  - Permission prompts displayed directly in input widget
  - Prompt box flexes to accommodate full permission content (max-height: 20)
  - Clean Frontier color styling without extra borders
- **Removed debug spam** from tool execution loop
  - Silent permission checks with fail-open fallback
  - Clean stderr output for production use

### Fixed
- Import fallback patterns for permission modules
- Permission handler initialization timing issues
- Widget mounting conflicts in TUI layout

## [1.4.0] - 2025-10-05

### Added

#### 🎨 Buffered Streaming System
- **StreamBuffer**: Async queue for incoming API chunks with controlled release
  - Configurable pacing (20 chars per batch, 50ms delay)
  - Token tracking and elapsed time monitoring
  - ESC interrupt support for long responses
- **BufferStatusDisplay**: Inline animated status in chat area
  - 10 FPS braille spinner animation (⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏)
  - Live token count and elapsed time display
  - Random tips during streaming
  - Frontier color palette integration
- **Inline Buffer Status**: Progress indicator integrated into StreamingDisplay
  - Shows: `⠋ Synthesizing… (esc to interrupt · 3s · ↓ 145 tokens)`
  - Seamless chat integration with auto-removal on completion

#### 📊 Performance Monitoring System
- **PerformanceMonitor**: Background thread for live metrics tracking
  - CPU usage with trend detection (↗ rising, → stable, ↘ falling)
  - Memory usage monitoring
  - Thread count tracking
  - Token streaming rate calculation
  - CPU spike logging (>11% threshold)
- **PerformanceStatusLine**: Bottom statusline widget
  - Live CPU/MEM/Threads display
  - Streaming speed indicator (tokens/sec)
  - Frontier color states (green <11%, orange <50%, red >50%)
- **`/performance` command**: Toggle live monitoring display

#### 🌐 DeepSeek Integration
- Complete API normalization for DeepSeek compatibility
- Tool call format fixes for 422 error prevention
- Comprehensive integration guide (DEEPSEEK_INTEGRATION_GUIDE.md)

### Changed

#### ⚡ Async Architecture Improvements
- **Non-blocking UI**: All streaming operations fully async
- **Unlimited Tool Execution**: Recursive tool calls with automatic continuation
- **Removed Timeouts**: Long operations complete naturally (user choice to wait)
- **Single Markdown Render**: Buffer tokens, render once (eliminates incremental lag)
- **Always-yield policy**: Event loop yields at every chunk boundary

#### 🎨 Streaming Experience
- Replaced incremental plain text with buffered display
- Smooth token pacing prevents UI overload
- Professional loading states with tips
- Clean completion flow (status → markdown)

### Fixed

#### 🐛 Critical UI Fixes
- UI freezing during fast token streaming (Chinese text, code blocks)
- CPU spikes from incremental markdown rendering (100% → 30-50%)
- Queue processor idle CPU usage (20% → <5%, 96% reduction)
- Observer effect in performance profiling (profiler was the bottleneck!)
- Double-threading bottleneck in async_write()

#### 🔧 API Integration Fixes
- DeepSeek 422 errors from malformed tool call payloads
- Tool call normalization for provider compatibility
- Continuation API error visibility (was failing silently)

### Performance

#### Metrics
- **Idle CPU**: 11-20% → <5% (96% reduction)
- **Streaming CPU**: 100% → 30-50% (50% reduction)
- **UI Responsiveness**: Frozen → Always responsive
- **Queue Polling**: 50 wakeups/sec → 2 wakeups/sec (96% reduction)

#### Optimizations
- Batched queue processing (10→50 items, 50ms→100ms)
- Removed expensive per-token monitoring
- Strategic event loop yielding
- Disabled aggressive profiling (observer effect fix)

### Technical Details

#### New Modules (642 lines)
- `modules/stream_buffer.py` (203 lines) - StreamBuffer + BufferStatusDisplay
- `modules/buffer_widget.py` (115 lines) - Standalone widget option
- `modules/performance_monitor.py` (324 lines) - PerformanceMonitor system

#### Modified Modules
- `modules/async_interactive.py` (+150/-50 lines) - Buffered streaming integration
- `modules/simple_tui.py` (+80/-20 lines) - Performance statusline widget
- `modules/streaming_display.py` (+72/-0 lines) - Buffer status methods

#### Documentation
- `DEEPSEEK_INTEGRATION_GUIDE.md` (8.1k) - DeepSeek setup guide
- `MERGE_PLAN.md` - Complete merge documentation

### Breaking Changes
None - Fully backward compatible

### Upgrade Notes
- Just restart OpenCLI - all features auto-enabled
- Use `/performance` to monitor CPU/memory
- ESC interrupts long responses during streaming
- Buffer pacing configurable in StreamBuffer(chars_per_batch=20, batch_delay_ms=50)

---

## [Unreleased] - dev2 → Main Merge

### Major Features

#### Advanced TUI Interface
- **Multi-line input widget** with smooth text wrapping and cursor positioning
- **Live markdown rendering** during streaming - no more raw markdown text
- **Integrated spinner animations** for API activity and IPC operations
- **Status line enhancements** with IPC activity indicators (read/write modes)
- **Terminal background support** - uses native terminal background (transparent mode)
- **Rich color system** - Full RGB foreground with ANSI background compatibility
- **Frontier design system** - Professional muted color palette (#151A21, #3E4B59, #6B9E78, #9B86BD)

#### Model Management System
- **Auto-refresh model list** from OpenRouter on `/model` command
- **Local model caching** with API key-based auto-discovery
- **Popularity ranking preservation** for better model selection
- **Recent models list** for quick access to frequently used models
- **Paid model confirmation** to prevent accidental billing
- **Provider name display** in model list for clarity
- **Pricing information** shown when switching models
- **Security improvements** - models.json set to 0600 permissions and gitignored

#### IPC System
- **Session auto-save** for reliable state preservation
- **Prompt history navigation** with up/down arrow keys
- **Bidirectional Claude Code integration** via IPC bridge
- **Background process management** for shells and tasks
- **Interactive upgrade system** - upgrade OpenCLI from within Claude Code sessions

### Added

#### UI/UX Enhancements
- Multi-line input widget (`multiline_input.py`) with async spinner support
- Markdown renderer (`markdown_renderer.py`) for real-time formatting
- ANSI background support (`ansi_background.py`) with ColorManager
- Streaming display widget (`streaming_display.py`) with laser effect
- Scrollable message display with hidden scrollbars
- Rich markup support throughout chat interface
- Braille pattern spinner (⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏) with 80ms smooth animation

#### Model Management
- `/model` command with interactive model selection
- Auto-fetch models from OpenRouter API on first run
- Legacy API key auto-detection
- Model popularity ranking from OpenRouter
- Recent models tracking
- Paid model confirmation prompts
- Pricing display in model list

#### Developer Tools
- Test files organized in `tests/` directory
- Utility scripts organized in `scripts/` directory
- Claude Code bridge scripts for IPC communication
- Debug tools for chat display testing
- Session finder utilities

### Changed

#### Repository Structure
- Created `tests/` directory for all test files
- Created `scripts/` directory for utility scripts
- Moved 4 test files to `tests/`
- Moved 6 utility scripts to `scripts/`
- Removed backup file `modules/simple_tui.py.working`

#### UI Improvements
- Replaced simple input with multi-line input widget
- Changed from static prompt to animated spinner
- Enhanced status line with IPC activity indicators
- Improved scrolling behavior with VerticalScroll
- Removed message area borders for cleaner look
- Hidden scrollbars for distraction-free interface

#### Color System
- Implemented configurable dual-mode color system
- Added ColorManager for ANSI background + RGB foreground
- Patched Textual Color.parse to accept "default" keyword
- Enhanced DOMNode.rich_style for transparent backgrounds
- Fixed TextAreaTheme.apply_css for ANSI compatibility

### Fixed

#### UI Fixes
- Cursor positioning in multi-line input (race condition in backspace)
- Special character input using `event.character` instead of `event.key`
- Markdown rendering showing raw markup instead of formatted text
- Rich color markup not working in chat area
- Spinner not stopping after API response
- Mystery box artifact from Spinner widget dimensions
- Space key not working in prompt input
- VerticalScroll not scrolling properly

#### Model Management Fixes
- Markup error when switching to FREE models
- Model list not refreshing from OpenRouter
- API key exposure in models.json
- Models not auto-discovering from API keys

#### Technical Fixes
- `call_from_thread` error in finish_stream()
- Batch processor distinguishing streaming vs complete messages
- Text selection and cursor visibility issues
- Async spinner task cleanup and cancellation

### Security

- Set `models.json` to 0600 permissions to protect API keys
- Added `models.json` to `.gitignore` to prevent key leaks
- Maintained 0600 permissions on `.secrets` file

### Documentation

- Updated README.md with new TUI features
- Added IPC system documentation to README
- Updated repository structure with tests/ and scripts/
- Organized features into Core, TUI, and IPC sections
- Created comprehensive CHANGELOG.md

### Technical Debt

- Removed temporary backup files
- Cleaned up root directory clutter
- Organized test files into proper directory
- Separated utility scripts from main codebase

---

## [1.2.1] - 2025-10-01

### Added
- Video support
- UI improvements
- Public release prep

## [1.2.0] - 2025-09-28

### Added
- Intelligent prompt processing
- Image path detection

## [1.1.0] - 2025-09-25

### Added
- Version control system
- Command permissions

## [1.0.0] - 2025-09-20

### Added
- Initial release
- Agent system
- Context caching
- OpenRouter API integration
- Session management
- GitHub integration

---

[Unreleased]: https://github.com/Dezocode/opencli/compare/Main...dev2
[1.2.1]: https://github.com/Dezocode/opencli/releases/tag/v1.2.1
[1.2.0]: https://github.com/Dezocode/opencli/releases/tag/v1.2.0
[1.1.0]: https://github.com/Dezocode/opencli/releases/tag/v1.1.0
[1.0.0]: https://github.com/Dezocode/opencli/releases/tag/v1.0.0
