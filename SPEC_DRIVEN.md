# Spec-Driven Development in OpenCLI

OpenCLI now integrates [GitHub Spec-Kit](https://github.com/github/spec-kit) for Spec-Driven Development - a methodology where specifications become executable, directly generating working implementations.

## Available Commands

### `/specify` - Create Specification

Create a detailed specification of what you want to build.

**Usage:**
```
/specify Build an application that can help me organize my photos in separate photo albums. Albums are grouped by date and can be re-organized by dragging and dropping on the main page.
```

**What it does:**
- Focuses on **what** and **why**, not implementation
- AI creates detailed specification including:
  - Clear functionality description
  - Problem solved and value provided
  - User experience details
  - Success criteria

### `/constitution` - Create Project Principles

Establish governing principles and development guidelines for your project.

**Usage:**
```
/constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements
```

**What it does:**
- AI creates project constitution including:
  - Core development values
  - Quality standards (code, testing, documentation)
  - UX consistency and accessibility requirements
  - Technical standards (architecture, performance, security)
  - Development process guidelines

### `/plan` - Create Technical Plan

Define the technical approach and architecture.

**Usage:**
```
/plan The application uses Vite with minimal number of libraries. Use vanilla HTML, CSS, and JavaScript as much as possible. Images are stored locally and metadata in SQLite.
```

**What it does:**
- AI creates implementation plan including:
  - Technology stack and versions
  - System architecture
  - Data models and schema
  - API design
  - File structure
  - Dependencies

### `/tasks` - Break Down into Tasks

Convert the implementation plan into actionable tasks.

**Usage:**
```
/tasks
```

**What it does:**
- AI creates task list with:
  - Dependency ordering (foundational first)
  - Atomic, completable tasks
  - Acceptance criteria
  - Complexity estimates
  - Task dependencies

### `/implement` - Implement Tasks

Execute tasks from the plan.

**Usage:**
```
/implement
```

**What it does:**
- AI reviews current task
- Writes code following plan and constitution
- Includes tests
- Documents implementation
- Marks task complete

### `/test` - Create and Run Tests

Generate and execute test cases.

**Usage:**
```
/test
```

**What it does:**
- Creates test cases from specification
- Writes test code
- Runs tests
- Fixes failures
- Reports coverage

### `/spec-check` - Validate Specification

Check specification completeness.

**Usage:**
```
/spec-check
```

**What it does:**
- Validates spec includes:
  - Clear objectives
  - User stories
  - Success criteria
  - Edge cases
  - Technical constraints
- Reports gaps or ambiguities

## Workflow Example

### 1. Start with Specification

```
You: /specify Build a todo app with drag-and-drop task reordering, categories, and due dates

AI: [Creates detailed specification]
### Todo Application Specification

**What**: A task management application with:
- Drag-and-drop task reordering
- Task categories/tags
- Due date tracking
- Visual priority indicators

**Why**: Users need an intuitive way to organize tasks...

[Full detailed spec]
```

### 2. Establish Principles

```
You: /constitution Focus on accessibility, mobile-first design, and offline capability

AI: [Creates project constitution]
# Project Constitution

## Core Values
1. Accessibility First: WCAG 2.1 AA compliance...
2. Mobile-First: Design for mobile, enhance for desktop...
3. Offline Capability: Full functionality without internet...

[Complete constitution]
```

### 3. Define Technical Approach

```
You: /plan Use vanilla JavaScript, IndexedDB for storage, service workers for offline

AI: [Creates technical plan]
# Technical Implementation Plan

## Technology Stack
- JavaScript: ES2022+ (no framework)
- Storage: IndexedDB via idb library
- Offline: Service Workers with Workbox
- Styling: CSS Grid + Custom Properties
- Testing: Vitest + Playwright

[Detailed architecture]
```

### 4. Break Into Tasks

```
You: /tasks

AI: [Creates task breakdown]
# Implementation Tasks

1. **Setup Project Structure** [Simple]
   - Initialize npm project
   - Configure Vite build
   - Setup folder structure
   - Acceptance: Build runs successfully

2. **Implement IndexedDB Schema** [Medium]
   - Create database schema
   - Write migration system
   - Test CRUD operations
   - Acceptance: All DB operations work

[Complete task list]
```

### 5. Implement Features

```
You: /implement

AI: [Implements current task]
Implementing: Setup Project Structure

[Creates files, writes code]

✓ Project structure created
✓ Build configured
✓ Tests passing

Moving to next task...
```

## Integration with OpenCLI

The spec-driven commands integrate seamlessly with OpenCLI:

- **Use Any AI Model**: Works with all models via `/model` switcher
- **Multi-Provider**: OpenRouter, Anthropic, OpenAI, DeepSeek, etc.
- **Session Persistence**: Specs saved in conversation history
- **File Operations**: AI can create/edit files directly
- **Incremental Development**: Build features step-by-step

## File Structure

Spec-Kit creates these files in your project:

```
memory/
├── constitution.md          # Project principles
├── specification.md         # What to build
├── implementation-plan.md   # Technical approach
└── tasks.md                 # Task breakdown
```

These files guide the AI throughout development, ensuring consistency with your original vision.

## Benefits

1. **Clear Vision**: Specification documents what and why
2. **Consistent Quality**: Constitution ensures standards
3. **Structured Development**: Plan provides architecture
4. **Trackable Progress**: Tasks show what's done/remaining
5. **AI-Aligned**: Guides AI to build what you actually want

## Combining with OpenCLI Features

### With `/providers`

```bash
# Use different providers for different phases
/model anthropic/claude-3-5-sonnet  # For specification/planning
/specify Build a real-time chat app...

/model deepseek/deepseek-v3         # For implementation
/implement
```

### With Streaming

All spec commands stream AI responses in real-time with:
- Proper markdown formatting (**bold**, *italic*, `code`)
- Syntax highlighting
- Professional frontier colors

### With Context Management

Specs persist in `memory/` directory and are automatically included in context for subsequent commands.

## Best Practices

1. **Start with /specify**: Always begin with what, not how
2. **Use /constitution early**: Set standards before coding
3. **Review /plan carefully**: Technical choices impact everything
4. **Follow /tasks order**: Dependencies matter
5. **Run /spec-check often**: Catch gaps early
6. **Use /test continuously**: Don't defer testing

## Example Projects

### Photo Album App
```
/specify Build a photo album organizer with drag-drop, date grouping
/constitution Focus on privacy, fast loading, mobile-first
/plan Vanilla JS, no uploads, SQLite metadata, file system access
/tasks
/implement
```

### API Service
```
/specify RESTful API for user management with auth, rate limiting
/constitution Emphasize security, scalability, comprehensive tests
/plan Node.js + Express, PostgreSQL, Redis, JWT auth
/tasks
/implement
```

## Troubleshooting

**"Unknown slash command: /specify"**
- Restart OpenCLI to load the spec-kit integration

**"Spec-Kit not properly installed"**
- The integration should be automatic, but you can manually install:
  ```bash
  cd ~/.opencli/modules/spec-kit
  pip install -e .
  ```

**AI doesn't follow specification**
- Use `/spec-check` to validate completeness
- Reference specific sections: "Following the specification's UX section..."

## Learn More

- [Spec-Kit Repository](https://github.com/github/spec-kit)
- [Spec-Driven Development Concepts](https://github.com/github/spec-kit#-what-is-spec-driven-development)
- [Video Overview](https://github.com/github/spec-kit#%EF%B8%8F-video-overview)
