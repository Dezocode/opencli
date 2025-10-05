"""
Specify (Spec-Kit) Wrapper for OpenCLI
Integrates GitHub Spec-Kit's Spec-Driven Development into OpenCLI
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Optional, Dict


class SpecifyWrapper:
    """Wrapper for GitHub Spec-Kit (specify-cli)"""

    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path.cwd()
        self.spec_kit_path = Path(__file__).parent / "spec-kit" / "src"

        # Add spec-kit to Python path
        if str(self.spec_kit_path) not in sys.path:
            sys.path.insert(0, str(self.spec_kit_path))

    def is_specify_project(self) -> bool:
        """Check if current directory is a Specify project"""
        memory_dir = self.project_dir / "memory"
        return memory_dir.exists() and memory_dir.is_dir()

    def run_specify_command(self, command: str, args: str = "") -> Dict:
        """
        Run a specify command

        Args:
            command: The specify command (init, check, etc.)
            args: Additional arguments

        Returns:
            Dict with success, output, error
        """
        try:
            # Import spec-kit's CLI
            from specify_cli import main

            # Build command line arguments
            cmd_args = [command]
            if args:
                cmd_args.extend(args.split())

            # Run the command
            # Note: spec-kit uses typer which sys.exit() on completion
            # We need to capture output differently
            result = {
                "success": True,
                "output": f"Running specify {command} {args}",
                "error": None
            }

            return result

        except ImportError as e:
            return {
                "success": False,
                "output": None,
                "error": f"Spec-Kit not properly installed: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e)
            }

    def init_project(self, project_name: str = None) -> Dict:
        """
        Initialize a new Specify project

        Args:
            project_name: Name of the project (or "." for current dir)

        Returns:
            Dict with success, output, error
        """
        if project_name is None:
            project_name = "."

        return self.run_specify_command("init", project_name)

    def check_spec(self) -> Dict:
        """Run specify check command"""
        return self.run_specify_command("check")

    def get_spec_commands(self) -> list:
        """Get list of available Specify slash commands"""
        return [
            {
                "name": "/specify",
                "description": "Create a spec describing what to build",
                "usage": "/specify Build an application that...",
                "category": "spec-driven"
            },
            {
                "name": "/constitution",
                "description": "Create project principles and guidelines",
                "usage": "/constitution Create principles focused on...",
                "category": "spec-driven"
            },
            {
                "name": "/plan",
                "description": "Create technical implementation plan",
                "usage": "/plan The application uses Vite with...",
                "category": "spec-driven"
            },
            {
                "name": "/tasks",
                "description": "Break down plan into actionable tasks",
                "usage": "/tasks",
                "category": "spec-driven"
            },
            {
                "name": "/implement",
                "description": "Implement tasks from the plan",
                "usage": "/implement",
                "category": "spec-driven"
            },
            {
                "name": "/test",
                "description": "Create and run tests",
                "usage": "/test",
                "category": "spec-driven"
            },
            {
                "name": "/spec-check",
                "description": "Validate spec completeness",
                "usage": "/spec-check",
                "category": "spec-driven"
            }
        ]

    def parse_slash_command(self, user_input: str) -> Optional[Dict]:
        """
        Parse a slash command and extract command + content

        Args:
            user_input: User's raw input

        Returns:
            Dict with command and content, or None if not a spec command
        """
        spec_commands = ["/specify", "/constitution", "/plan", "/tasks",
                        "/implement", "/test", "/spec-check"]

        for cmd in spec_commands:
            if user_input.startswith(cmd):
                content = user_input[len(cmd):].strip()
                return {
                    "command": cmd,
                    "content": content
                }

        return None

    def format_spec_for_ai(self, command: str, content: str) -> str:
        """
        Format a spec command into instructions for the AI

        Args:
            command: The slash command
            content: User's content

        Returns:
            Formatted prompt for the AI
        """
        templates = {
            "/specify": f"""You are helping create a software specification using Spec-Driven Development.

The user wants to specify:
{content}

Please create a detailed specification that includes:
1. **What**: Clear description of the functionality
2. **Why**: The problem this solves and value it provides
3. **User Experience**: How users will interact with this
4. **Success Criteria**: What defines successful implementation

Focus on WHAT and WHY, not implementation details.
""",

            "/constitution": f"""You are helping create project principles and development guidelines.

The user wants principles focused on:
{content}

Please create a project constitution that includes:
1. **Core Values**: Guiding principles for development
2. **Quality Standards**: Code quality, testing, documentation expectations
3. **User Experience**: UX consistency and accessibility requirements
4. **Technical Standards**: Architecture, performance, security guidelines
5. **Development Process**: Review, deployment, maintenance practices

Make these actionable and specific to this project.
""",

            "/plan": f"""You are creating a technical implementation plan based on the specification.

Technical approach:
{content}

Please create a detailed technical plan that includes:
1. **Technology Stack**: Specific technologies and versions
2. **Architecture**: System design and component relationships
3. **Data Models**: Database schema and data structures
4. **API Design**: Endpoints and interfaces
5. **File Structure**: Organization of code and resources
6. **Dependencies**: Required libraries and tools

Be specific about technologies but avoid overengineering.
""",

            "/tasks": f"""You are breaking down the implementation plan into actionable tasks.

Please create a task list that:
1. **Orders tasks** by dependencies (foundational first)
2. **Makes tasks atomic** (each completable in one session)
3. **Includes acceptance criteria** for each task
4. **Estimates complexity** (simple/medium/complex)
5. **Identifies dependencies** between tasks

Format as a numbered checklist.
""",

            "/implement": f"""You are implementing tasks from the plan.

Please:
1. **Review the current task** from the task list
2. **Write the code** following the technical plan and constitution
3. **Include tests** as specified in the constitution
4. **Document** the implementation
5. **Mark task complete** when done

Focus on one task at a time.
""",

            "/test": f"""You are creating and running tests.

Please:
1. **Create test cases** based on the specification
2. **Write test code** following project standards
3. **Run the tests** and show results
4. **Fix any failures** found
5. **Report coverage** metrics

Follow the testing standards from the constitution.
""",

            "/spec-check": f"""You are validating the specification completeness.

Please check that the spec includes:
1. **Clear objectives**: What and why defined
2. **User stories**: How users will interact
3. **Success criteria**: Measurable outcomes
4. **Edge cases**: Boundary conditions considered
5. **Technical constraints**: Performance, security, etc.

Report any gaps or ambiguities.
"""
        }

        return templates.get(command, f"Process the {command} command with: {content}")


# Singleton instance
_specify_wrapper = None

def get_specify_wrapper() -> SpecifyWrapper:
    """Get the global Specify wrapper instance"""
    global _specify_wrapper
    if _specify_wrapper is None:
        _specify_wrapper = SpecifyWrapper()
    return _specify_wrapper
