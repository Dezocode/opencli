# OpenCLI Constitution

## Core Principles

### I. Tool-First Development
- Every operation uses available tools (Read, Write, Edit, Bash, Glob, Grep)
- Tools provide structured, reliable interaction with the system
- Always prefer tools over manual operations

### II. File Operation Standards
- **Read**: Use for reading any file content
- **Write**: Use for creating new files only when necessary
- **Edit**: Use for modifying existing files with precise string replacement
- **Glob**: Use for finding files by pattern
- **Grep**: Use for searching file contents

### III. Command Execution
- Use Bash tool for all system commands
- Prefer specialized tools over bash for file operations
- Always provide clear descriptions for bash commands
- Handle errors gracefully with appropriate feedback

### IV. Context Awareness
- Always consider current working directory
- Check file existence before operations
- Validate paths and permissions
- Respect project structure and conventions

### V. Quality Standards
- Write clean, maintainable code
- Follow project coding conventions
- Add appropriate error handling
- Document significant changes

## Tool Usage Guidelines

### Bash Tool
**Purpose**: Execute system commands, run scripts, manage processes
**When to use**:
- Running build commands (npm, pip, etc.)
- Git operations
- System utilities
- Background processes

**Best practices**:
- Quote paths with spaces
- Chain related commands with &&
- Use timeout for long-running commands
- Provide clear descriptions

### Read Tool
**Purpose**: Read file contents
**When to use**:
- Examining source code
- Reading configuration files
- Analyzing logs
- Understanding project structure

**Best practices**:
- Use offset and limit for large files
- Read relevant sections only
- Check file path validity first

### Edit Tool
**Purpose**: Make precise changes to existing files
**When to use**:
- Updating code
- Fixing bugs
- Modifying configuration
- Refactoring

**Best practices**:
- Ensure old_string is unique
- Use replace_all for renaming
- Preserve exact indentation
- Validate changes after editing

### Write Tool
**Purpose**: Create new files
**When to use**:
- Creating new modules
- Adding test files
- Generating documentation
- Creating configuration files

**Best practices**:
- Read existing file first if updating
- Prefer Edit over Write for changes
- Follow project file conventions
- Set appropriate permissions

### Glob Tool
**Purpose**: Find files matching patterns
**When to use**:
- Locating files by extension
- Finding configuration files
- Discovering project structure
- Pattern-based searches

**Best practices**:
- Use specific patterns when possible
- Combine with Grep for content search
- Consider directory scope

### Grep Tool
**Purpose**: Search file contents
**When to use**:
- Finding code references
- Locating definitions
- Searching for patterns
- Analyzing codebase

**Best practices**:
- Use appropriate output_mode
- Add context lines when helpful
- Use case-insensitive search when needed
- Combine with type filters

## Development Workflow

1. **Understand**: Read relevant files and context
2. **Plan**: Determine best approach and tools
3. **Execute**: Use appropriate tools for changes
4. **Verify**: Check results and test changes
5. **Document**: Update relevant documentation

## Error Handling

- Always handle tool errors gracefully
- Provide helpful error messages
- Suggest fixes when errors occur
- Log important errors for debugging

## Security

- Never expose API keys or secrets
- Validate all input paths
- Check permissions before operations
- Follow security best practices

---

**Version**: 1.0.0 | **Last Updated**: 2025-10-04
