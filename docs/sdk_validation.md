# SDK Registration Coverage

This branch introduces guardrails that ensure the SDK refuses to start when
expected commands or tools go missing.

- Every command advertised by `CommandRegistry` is now registered with the
  unified `ExecutionSystem`.
- The eight built-in tools (Read, Write, Edit, Glob, Grep, Bash, GitHub,
  ConfigureHeaders) are registered through the SDK enforcement pipeline.
- The multi-line permission buffer now responds immediately to Enter/arrow
  keys for informational prompts.

See the PR description for the full rationale and validation steps.
