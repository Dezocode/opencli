"""
Architecture Compliance Validator
Ensures code adheres to architecture.yml blueprint
"""

import ast
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class ComplianceViolation:
    """A violation of architectural rules"""
    severity: str  # "error", "warning", "info"
    rule_type: str  # "max_lines", "forbidden_import", "performance_budget", etc.
    file: str
    line: Optional[int]
    message: str
    suggestion: Optional[str] = None


@dataclass
class ComplianceReport:
    """Report of architecture compliance"""
    total_files_checked: int
    violations: List[ComplianceViolation] = field(default_factory=list)
    warnings: List[ComplianceViolation] = field(default_factory=list)
    passed: bool = True

    def add_violation(self, violation: ComplianceViolation):
        """Add a violation and categorize by severity"""
        if violation.severity == "error":
            self.violations.append(violation)
            self.passed = False
        else:
            self.warnings.append(violation)

    def format_report(self) -> str:
        """Format compliance report for display"""
        lines = []
        lines.append("=" * 70)
        lines.append("ARCHITECTURE COMPLIANCE REPORT")
        lines.append("=" * 70)
        lines.append(f"\nFiles Checked: {self.total_files_checked}")
        lines.append(f"Status: {'✅ PASSED' if self.passed else '❌ FAILED'}")
        lines.append(f"Errors: {len(self.violations)}")
        lines.append(f"Warnings: {len(self.warnings)}\n")

        if self.violations:
            lines.append("\n🔴 ERRORS:")
            for v in self.violations:
                lines.append(f"\n  {v.file}:{v.line or '?'}")
                lines.append(f"    Rule: {v.rule_type}")
                lines.append(f"    {v.message}")
                if v.suggestion:
                    lines.append(f"    💡 {v.suggestion}")

        if self.warnings:
            lines.append("\n⚠️  WARNINGS:")
            for w in self.warnings:
                lines.append(f"\n  {w.file}:{w.line or '?'}")
                lines.append(f"    Rule: {w.rule_type}")
                lines.append(f"    {w.message}")
                if w.suggestion:
                    lines.append(f"    💡 {w.suggestion}")

        return '\n'.join(lines)


class ArchitectureValidator:
    """Validates code against architecture.yml blueprint"""

    def __init__(self, repo_path: str = ".", arch_file: str = "architecture.yml"):
        self.repo_path = Path(repo_path).resolve()
        self.arch_file = self.repo_path / arch_file
        self.blueprint = None

    def load_blueprint(self) -> bool:
        """Load and parse architecture.yml"""
        try:
            with open(self.arch_file, 'r') as f:
                self.blueprint = yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"Error loading architecture.yml: {e}")
            return False

    def validate_all(self) -> ComplianceReport:
        """Run all compliance checks"""
        if not self.blueprint:
            if not self.load_blueprint():
                return ComplianceReport(total_files_checked=0, passed=False)

        report = ComplianceReport(total_files_checked=0)

        # Check each module defined in blueprint
        for module_spec in self.blueprint.get('modules', []):
            self._check_module(module_spec, report)
            report.total_files_checked += 1

        return report

    def _check_module(self, module_spec: Dict, report: ComplianceReport):
        """Check a single module for compliance"""
        file_path = self.repo_path / module_spec['path']

        if not file_path.exists():
            report.add_violation(ComplianceViolation(
                severity="warning",
                rule_type="missing_file",
                file=module_spec['path'],
                line=None,
                message=f"Module {module_spec['name']} not found"
            ))
            return

        # Check file size
        with open(file_path, 'r') as f:
            lines = f.readlines()
            line_count = len(lines)

        max_lines = module_spec.get('max_lines')
        if max_lines and line_count > max_lines:
            report.add_violation(ComplianceViolation(
                severity="error",
                rule_type="max_lines",
                file=module_spec['path'],
                line=None,
                message=f"File has {line_count} lines, exceeds limit of {max_lines}",
                suggestion=f"Run /refactor suggest-split {module_spec['path']}"
            ))

        # Check imports
        self._check_imports(file_path, module_spec, report)

        # Check concerns
        concerns = module_spec.get('concerns', [])
        for concern in concerns:
            report.add_violation(ComplianceViolation(
                severity="info",
                rule_type="concern",
                file=module_spec['path'],
                line=None,
                message=concern
            ))

    def _check_imports(self, file_path: Path, module_spec: Dict, report: ComplianceReport):
        """Check import compliance"""
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())

            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)

            # Check forbidden imports
            forbidden = module_spec.get('forbidden_imports', [])
            for forbidden_import in forbidden:
                # Match pattern (e.g., "modules.*" matches "modules.api_client")
                for actual_import in imports:
                    if self._match_import_pattern(forbidden_import, actual_import):
                        report.add_violation(ComplianceViolation(
                            severity="error",
                            rule_type="forbidden_import",
                            file=str(file_path.relative_to(self.repo_path)),
                            line=None,
                            message=f"Forbidden import: {actual_import}",
                            suggestion=f"Remove or refactor to eliminate {forbidden_import} dependency"
                        ))

            # Check allowed imports (if specified)
            allowed = module_spec.get('allowed_imports', [])
            if allowed:
                for actual_import in imports:
                    if actual_import.startswith('modules.'):
                        # Check if this module import is allowed
                        if not any(self._match_import_pattern(a, actual_import) for a in allowed):
                            report.add_violation(ComplianceViolation(
                                severity="warning",
                                rule_type="disallowed_import",
                                file=str(file_path.relative_to(self.repo_path)),
                                line=None,
                                message=f"Import not in allowed list: {actual_import}"
                            ))

        except Exception as e:
            report.add_violation(ComplianceViolation(
                severity="warning",
                rule_type="parse_error",
                file=str(file_path.relative_to(self.repo_path)),
                line=None,
                message=f"Could not parse file: {e}"
            ))

    def _match_import_pattern(self, pattern: str, actual: str) -> bool:
        """Match import pattern with wildcards"""
        if pattern == actual:
            return True
        if pattern.endswith('*'):
            prefix = pattern[:-1]
            return actual.startswith(prefix)
        return False

    def check_performance_budgets(self, profile_stats) -> List[ComplianceViolation]:
        """Check if performance budgets are met"""
        violations = []

        budgets = self.blueprint.get('performance_budgets', [])
        for budget in budgets:
            func_name = budget['function']
            max_time_ms = budget['max_time_ms']

            # Find this function in profile stats
            for prof_func, cumtime, ncalls in profile_stats.top_functions:
                if func_name in prof_func:
                    avg_ms = (cumtime * 1000) / ncalls if ncalls > 0 else 0

                    if avg_ms > max_time_ms:
                        violations.append(ComplianceViolation(
                            severity="error",
                            rule_type="performance_budget",
                            file=budget['location'],
                            line=None,
                            message=f"{func_name} took {avg_ms:.2f}ms (budget: {max_time_ms}ms)",
                            suggestion="Profile and optimize this function"
                        ))

        return violations

    def check_threading_compliance(self, thread_analysis) -> List[ComplianceViolation]:
        """Check if threading rules are followed"""
        violations = []

        threading_rules = self.blueprint.get('threading_rules', [])

        for rule in threading_rules:
            thread_name = rule.get('thread_name')
            thread_pattern = rule.get('thread_pattern')
            forbidden_ops = rule.get('forbidden_operations', [])

            # Find matching threads
            for thread in thread_analysis:
                if thread_name and thread.name == thread_name:
                    # Check for forbidden operations in stack trace
                    for forbidden_op in forbidden_ops:
                        if forbidden_op.lower() in thread.stack_trace.lower():
                            violations.append(ComplianceViolation(
                                severity="error",
                                rule_type="threading_violation",
                                file="runtime",
                                line=None,
                                message=f"{thread.name} performing forbidden operation: {forbidden_op}",
                                suggestion=f"Move {forbidden_op} to background thread"
                            ))

                elif thread_pattern and thread_pattern in thread.name:
                    # Check max blocking time
                    max_blocking_ms = rule.get('max_blocking_time_ms')
                    if max_blocking_ms and thread.blocked_time:
                        blocked_ms = thread.blocked_time * 1000
                        if blocked_ms > max_blocking_ms:
                            violations.append(ComplianceViolation(
                                severity="warning",
                                rule_type="thread_blocking",
                                file="runtime",
                                line=None,
                                message=f"{thread.name} blocked for {blocked_ms:.0f}ms (limit: {max_blocking_ms}ms)"
                            ))

        return violations


def validate_architecture(repo_path: str = ".") -> ComplianceReport:
    """Convenience function to validate architecture"""
    validator = ArchitectureValidator(repo_path)
    return validator.validate_all()
