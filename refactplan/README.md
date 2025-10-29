Refactor2 Documentation
=======================

Purpose
-------
This directory contains the parity-first refactor plan, phase guides, and templates used to migrate remaining legacy behavior into the modular path without changing features. Once parity is achieved, legacy components are deprecated.

Structure
---------
- A-Z-Refactor-Plan.md: Top-level plan and guardrails
- phase-0-parity-inventory.md: Feature catalog and gaps
- phase-1-foundation.md: Modular proxies with no behavior change
- phase-2-tui-parity-and-removal.md: Async TUI parity, then remove fallback
- phase-3-cleanup.md: Delete legacy files and prune remnants
- templates/: Task, test, checklist, PR templates

Working Agreement
-----------------
- No net-new features. Exact behavior/UX preserved.
- Tests added before refactors to lock behavior.
- Each PR links to a parity checklist and is rollback-safe.


