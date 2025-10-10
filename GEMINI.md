# GEMINI.md

## Project Overview

This project, `opencli`, is a sophisticated, feature-rich command-line interface (CLI) designed to bring the power of large language models (LLMs) directly into the terminal. It primarily interacts with the OpenRouter API, but is architected to be provider-agnostic.

**Core Technologies:**

*   **Language:** Python 3
*   **Primary Interface:** Command-line, with a modern Textual User Interface (TUI)
*   **Key Libraries:** `openai`, `prompt_toolkit`, `pyyaml`

**Architectural Highlights:**

*   **Modular Design:** The project is broken down into distinct modules with clear responsibilities (e.g., `agent_manager`, `command_registry`, `api_client`, `simple_tui`). This is enforced by the `architecture.yml` file.
*   **Agent System:** A key feature is the intelligent agent system. It automatically selects the most appropriate AI agent (e.g., `debugger`, `reviewer`, `tester`) based on the user's prompt. This is managed in `modules/agent_manager.py`.
*   **Command System:** The CLI features a comprehensive set of slash commands (e.g., `/model`, `/agent`, `/upgrade`) with a built-in permission system. This is defined in `modules/command_registry.py`.
*   **Spec-Driven Development:** The project includes a "Spec-Kit" for goal-oriented workflows, allowing users to define specifications, constitutions, and implementation plans.
*   **Version Control:** `opencli` has a built-in upgrade and rollback system, ensuring stability and safe updates. This is managed by `modules/upgrade_manager.py` and `modules/rollback_manager.py`.
*   **Configuration:** Project configuration is handled through `config.json` and `.secrets` files stored in the `~/.opencli` directory.

## Building and Running

**Installation:**

The primary method of installation is via a one-line curl command:

```bash
curl -fsSL https://raw.githubusercontent.com/Dezocode/opencli/Main/install.sh | bash
```

Alternatively, a manual installation can be performed by cloning the repository and running the `install.sh` script.

**Running the application:**

Once installed, the application can be started by simply running:

```bash
opencli
```

This will start an interactive session. One-shot prompts are also supported:

```bash
opencli "your prompt here"
```

**Testing:**

The `CONTRIBUTING.md` file outlines a manual testing process. There is a `tests/` directory, but no specific instructions on how to run automated tests are provided in the `README.md` or `CONTRIBUTING.md`.

## Development Conventions

*   **Code Style:** The project follows PEP 8 for Python code and uses `shellcheck` for shell scripts.
*   **Commit Messages:** The project uses conventional commit messages (e.g., `feat:`, `fix:`, `docs:`).
*   **Branching:** Feature development should be done on separate feature branches (e.g., `feature/your-feature-name`).
*   **Modularity:** New features should be added as modules in the `modules/` directory.
*   **Documentation:** All new features should be accompanied by updates to the relevant documentation.
*   **Architecture:** The `architecture.yml` file serves as a blueprint for the project's structure and should be adhered to. It defines module responsibilities, dependencies, and performance budgets.
