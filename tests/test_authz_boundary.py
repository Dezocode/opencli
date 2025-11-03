"""
Architectural Tests for Authorization Boundary

These tests enforce the architectural constraints:
1. Only authz module makes authorization decisions
2. No direct imports of deprecated permission modules (except in migration shims)
3. All authorization goes through check_authorization()

Run with: pytest tests/test_authz_boundary.py -v
"""

import ast
import os
from pathlib import Path
from typing import List, Set
import pytest


# Root directory of the project
PROJECT_ROOT = Path(__file__).parent.parent


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


def get_python_files(directory: Path, exclude: List[str] = None) -> List[Path]:
    """Get all Python files in directory"""
    exclude = exclude or []
    python_files = []
    
    for file in directory.rglob("*.py"):
        # Skip excluded directories
        if any(excluded in str(file) for excluded in exclude):
            continue
        python_files.append(file)
    
    return python_files


def get_imports_from_file(file_path: Path) -> Set[str]:
    """Extract all imports from a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        visitor = ImportVisitor()
        visitor.visit(tree)
        return visitor.imports
    except Exception as e:
        # If we can't parse the file, skip it
        print(f"Warning: Could not parse {file_path}: {e}")
        return set()


class TestAuthorizationBoundary:
    """Tests to enforce authorization boundary"""
    
    # Deprecated modules that should not be imported (except in authz and migration shims)
    DEPRECATED_PERMISSION_MODULES = [
        'modules.execution.permission_manager',
        'execution.permission_manager',
        'modules.async_permissions',
        'async_permissions',
        'modules.async_interactive.permissions',
        'async_interactive.permissions',
    ]
    
    # Files that are allowed to import deprecated modules (migration shims)
    ALLOWED_LEGACY_IMPORTS = [
        'modules/authz/facade.py',  # Needs to integrate with legacy
        'modules/authz/migration.py',  # Migration utilities
        'modules/permissions/integration.py',  # During transition
        'modules/execution/executor.py',  # During transition
    ]
    
    def test_no_new_permission_imports(self):
        """
        Enforce that new code does not import deprecated permission modules
        
        This test ensures that:
        1. Only authorized files can import legacy permission modules
        2. New code uses the authz facade instead
        """
        violations = []
        
        # Get all Python files except those in allowed list
        python_files = get_python_files(
            PROJECT_ROOT / "modules",
            exclude=['__pycache__', '.git', 'tests', 'authz']
        )
        
        for file_path in python_files:
            # Skip files that are explicitly allowed to import legacy modules
            relative_path = str(file_path.relative_to(PROJECT_ROOT))
            if any(allowed in relative_path for allowed in self.ALLOWED_LEGACY_IMPORTS):
                continue
            
            imports = get_imports_from_file(file_path)
            
            # Check for deprecated imports
            for deprecated in self.DEPRECATED_PERMISSION_MODULES:
                if deprecated in imports:
                    violations.append({
                        'file': relative_path,
                        'import': deprecated,
                        'fix': 'Use modules.authz.check_authorization instead'
                    })
        
        # Report violations
        if violations:
            error_msg = "\n\n❌ ARCHITECTURAL BOUNDARY VIOLATION DETECTED\n"
            error_msg += "="*70 + "\n"
            error_msg += "The following files import deprecated permission modules:\n\n"
            
            for v in violations:
                error_msg += f"  File: {v['file']}\n"
                error_msg += f"  Import: {v['import']}\n"
                error_msg += f"  Fix: {v['fix']}\n\n"
            
            error_msg += "Please migrate to the canonical authorization facade:\n"
            error_msg += "  from modules.authz import check_authorization, AuthzSubject\n"
            error_msg += "\nSee modules/authz/README.md for migration guide.\n"
            error_msg += "="*70 + "\n"
            
            pytest.fail(error_msg)
    
    def test_authz_module_exists(self):
        """Verify that the authz module is properly set up"""
        authz_dir = PROJECT_ROOT / "modules" / "authz"
        assert authz_dir.exists(), "authz module directory must exist"
        
        # Check required files
        required_files = [
            "__init__.py",
            "facade.py",
            "deprecation.py",
            "README.md"
        ]
        
        for file in required_files:
            file_path = authz_dir / file
            assert file_path.exists(), f"Required file {file} must exist in authz module"
    
    def test_authz_exports_canonical_api(self):
        """Verify that authz module exports the canonical API"""
        try:
            from modules.authz import (
                check_authorization,
                AuthzContext,
                AuthzDecision,
                AuthzSubject,
                get_authz_manager
            )
            
            # Verify types
            assert callable(check_authorization), "check_authorization must be callable"
            assert callable(get_authz_manager), "get_authz_manager must be callable"
            assert AuthzContext is not None, "AuthzContext must be defined"
            assert AuthzDecision is not None, "AuthzDecision must be defined"
            assert AuthzSubject is not None, "AuthzSubject must be defined"
            
        except ImportError as e:
            pytest.fail(f"Could not import canonical authz API: {e}")
    
    def test_authz_manager_singleton(self):
        """Verify that authorization manager is a singleton"""
        from modules.authz import get_authz_manager
        
        manager1 = get_authz_manager()
        manager2 = get_authz_manager()
        
        assert manager1 is manager2, "Authorization manager must be a singleton"
        assert id(manager1) == id(manager2), "Same instance must be returned"
    
    def test_authz_decision_logging(self):
        """Verify that authorization decisions are logged"""
        from modules.authz import get_authz_manager
        
        manager = get_authz_manager()
        
        # Should have decision log functionality
        assert hasattr(manager, 'get_decision_log'), "Manager must have get_decision_log"
        assert hasattr(manager, 'get_metrics'), "Manager must have get_metrics"
        
        # Get metrics should return dict
        metrics = manager.get_metrics()
        assert isinstance(metrics, dict), "Metrics must be a dictionary"
        assert 'total_decisions' in metrics, "Metrics must include total_decisions"


class TestDeprecationWarnings:
    """Tests for deprecation warnings"""
    
    def test_deprecation_utilities_exist(self):
        """Verify deprecation utilities are available"""
        try:
            from modules.authz.deprecation import (
                deprecated_permission_import,
                deprecated_module,
                DeprecatedPermissionManagerWarning
            )
            
            assert callable(deprecated_permission_import)
            assert callable(deprecated_module)
            assert issubclass(DeprecatedPermissionManagerWarning, DeprecationWarning)
            
        except ImportError as e:
            pytest.fail(f"Could not import deprecation utilities: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
