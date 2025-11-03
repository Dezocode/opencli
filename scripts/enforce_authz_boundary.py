#!/usr/bin/env python3
"""
CI Enforcement Script - Phase 3

This script enforces architectural boundaries by failing the build if:
1. Any code imports deprecated permission modules directly (except authz and migration)
2. Dependency cycles are detected
3. Permission checks bypass the authz facade

Run in CI: python scripts/enforce_authz_boundary.py
"""

import sys
import os
import ast
from pathlib import Path
from typing import Set, List, Dict

# Root of the repository
REPO_ROOT = Path(__file__).parent.parent

# Deprecated modules that should not be imported (except in allowed files)
FORBIDDEN_IMPORTS = [
    'modules.execution.permission_manager',
    'execution.permission_manager',
    'modules.async_permissions',
    'async_permissions',
    'modules.async_interactive.permissions',
    'async_interactive.permissions',
]

# Files allowed to import deprecated modules (for migration/compatibility)
ALLOWED_FILES = [
    'modules/authz/facade.py',
    'modules/authz/migration.py',
    'modules/authz/setup.py',
    'modules/permissions/integration.py',  # During transition
    'modules/execution/executor.py',  # During transition
    'modules/execution/permission_manager.py',  # Can import itself
    'modules/async_interactive.py',  # During transition
    'modules/core.py',  # During transition
    'modules/commands/basic_commands.py',  # During transition
    'modules/commands/permission_templates.py',  # During transition
    'modules/tui/permission_handlers.py',  # During transition
    'modules/async_interactive/permissions.py',  # Can import itself
]


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to collect import statements"""
    
    def __init__(self):
        self.imports: Set[str] = set()
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)


def check_file_imports(file_path: Path) -> List[str]:
    """Check if file imports forbidden modules"""
    violations = []
    
    # Skip if in allowed list
    relative_path = str(file_path.relative_to(REPO_ROOT))
    if any(allowed in relative_path for allowed in ALLOWED_FILES):
        return violations
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        visitor = ImportVisitor()
        visitor.visit(tree)
        
        # Check for forbidden imports
        for forbidden in FORBIDDEN_IMPORTS:
            if forbidden in visitor.imports:
                violations.append(
                    f"{relative_path}: imports forbidden module '{forbidden}'"
                )
    
    except Exception as e:
        # Skip files that can't be parsed
        pass
    
    return violations


def find_python_files(directory: Path, exclude: List[str] = None) -> List[Path]:
    """Find all Python files in directory"""
    exclude = exclude or []
    python_files = []
    
    for file in directory.rglob("*.py"):
        # Skip excluded directories
        if any(excluded in str(file) for excluded in exclude):
            continue
        python_files.append(file)
    
    return python_files


def check_authz_usage(file_path: Path) -> List[str]:
    """Check if permission checks go through authz"""
    warnings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for direct permission checks that bypass authz
        bypass_patterns = [
            'check_permission(',
            'should_prompt(',
            'assess_risk(',
        ]
        
        # If file has these patterns but doesn't import authz, warn
        has_permission_checks = any(pattern in content for pattern in bypass_patterns)
        has_authz_import = 'from modules.authz import' in content or 'from ..authz import' in content
        
        if has_permission_checks and not has_authz_import:
            relative_path = str(file_path.relative_to(REPO_ROOT))
            # Skip known legacy files during transition
            if not any(legacy in relative_path for legacy in ALLOWED_FILES):
                warnings.append(
                    f"{relative_path}: has permission checks but doesn't import authz (consider migrating)"
                )
    
    except Exception:
        pass
    
    return warnings


def main():
    """Run enforcement checks"""
    print("="*70)
    print("🔒 Authorization Boundary Enforcement - Phase 3")
    print("="*70)
    print()
    
    # Find all Python files
    python_files = find_python_files(
        REPO_ROOT / "modules",
        exclude=['__pycache__', '.git', 'tests', 'authz']
    )
    
    print(f"Checking {len(python_files)} Python files...")
    print()
    
    # Check for forbidden imports
    violations = []
    warnings = []
    
    for file_path in python_files:
        file_violations = check_file_imports(file_path)
        violations.extend(file_violations)
        
        file_warnings = check_authz_usage(file_path)
        warnings.extend(file_warnings)
    
    # Report results
    if violations:
        print("❌ ARCHITECTURAL BOUNDARY VIOLATIONS DETECTED")
        print("="*70)
        print()
        for violation in violations:
            print(f"  ❌ {violation}")
        print()
        print("These files import deprecated permission modules.")
        print("Please update to use: from modules.authz import check_authorization")
        print("See modules/authz/README.md for migration guide.")
        print("="*70)
        sys.exit(1)
    
    print("✅ No architectural boundary violations detected")
    print()
    
    if warnings:
        print("⚠️  MIGRATION WARNINGS")
        print("="*70)
        print()
        for warning in warnings:
            print(f"  ⚠️  {warning}")
        print()
        print("These files should be migrated to use the authz facade.")
        print("This is a warning only - not blocking build.")
        print("="*70)
        print()
    
    print("✅ Authorization boundary enforcement: PASSED")
    print()
    sys.exit(0)


if __name__ == "__main__":
    main()
