# Changelog

All notable changes to OpenCLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
