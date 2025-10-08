"""
Architecture Compliance Checker
Validates codebase against architecture.yml blueprint
"""

import ast
import os
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Violation:
    """A violation of the architecture blueprint"""
    severity: str  # "error", "warning", "info"
    category: str  # "forbidden_import", "max_lines", "performance_budget", etc.
    file: str
    line: Optional[int]
    message: str
    rule: str


@dataclass
class ComplianceReport:
    """Architecture compliance report"""
    timestamp: str
    violations: List[Violation] = field(default_factory=list)
    warnings: List[Violation] = field(default_factory=list)
    info: List[Violation] = field(default_factory=list)
    metrics: Dict[str, any] = field(default_factory=dict)

    def add_violation(self, violation: Violation):
        """Add a violation to the appropriate list"""
        if violation.severity == "error":
            self.violations.append(violation)
        elif violation.severity == "warning":
            self.warnings.append(violation)
        else:
            self.info.append(violation)

    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.violations) > 0


class ArchitectureChecker:
    """Check codebase compliance against architecture blueprint"""

    def __init__(self, blueprint_path: str = "architecture.yml"):
        self.blueprint_path = blueprint_path
        self.blueprint = None
        self.project_root = Path(blueprint_path).parent

    def load_blueprint(self) -> bool:
        """Load the architecture blueprint"""
        try:
            with open(self.blueprint_path, 'r') as f:
                self.blueprint = yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"Error loading blueprint: {e}")
            return False

    def check_all(self) -> ComplianceReport:
        """Run all compliance checks"""
        if not self.blueprint:
            if not self.load_blueprint():
                report = ComplianceReport(timestamp=datetime.now().isoformat())
                report.add_violation(Violation(
                    severity="error",
                    category="blueprint",
                    file=self.blueprint_path,
                    line=None,
                    message="Failed to load architecture blueprint",
                    rule="blueprint_exists"
                ))
                return report

        report = ComplianceReport(timestamp=datetime.now().isoformat())

        # Run all checks
        self._check_module_dependencies(report)
        self._check_file_sizes(report)
        self._check_forbidden_imports(report)
        self._calculate_metrics(report)

        return report

    def _check_module_dependencies(self, report: ComplianceReport):
        """Check that modules only import allowed dependencies"""
        if 'modules' not in self.blueprint:
            return

        for module_spec in self.blueprint['modules']:
            module_path = self.project_root / module_spec['path']

            if not module_path.exists():
                report.add_violation(Violation(
                    severity="warning",
                    category="missing_file",
                    file=module_spec['path'],
                    line=None,
                    message=f"Module file not found: {module_spec['path']}",
                    rule="file_exists"
                ))
                continue

            # Parse the file and check imports
            try:
                with open(module_path, 'r') as f:
                    tree = ast.parse(f.read(), filename=str(module_path))

                imports = self._extract_imports(tree)
                allowed = set(module_spec.get('allowed_imports', []))
                forbidden = set(module_spec.get('forbidden_imports', []))

                # Check forbidden imports
                for imp in imports:
                    if any(imp.startswith(f) for f in forbidden):
                        report.add_violation(Violation(
                            severity="error",
                            category="forbidden_import",
                            file=module_spec['path'],
                            line=None,
                            message=f"Forbidden import '{imp}' in {module_spec['name']}",
                            rule="forbidden_imports"
                        ))

                    # Check if import is allowed (if allowlist is specified)
                    if allowed and not any(imp.startswith(a) for a in allowed):
                        # Ignore standard library imports
                        if not self._is_stdlib_import(imp):
                            report.add_violation(Violation(
                                severity="warning",
                                category="unallowed_import",
                                file=module_spec['path'],
                                line=None,
                                message=f"Import '{imp}' not in allowed list for {module_spec['name']}",
                                rule="allowed_imports"
                            ))

            except Exception as e:
                report.add_violation(Violation(
                    severity="warning",
                    category="parse_error",
                    file=module_spec['path'],
                    line=None,
                    message=f"Failed to parse file: {e}",
                    rule="parseable"
                ))

    def _check_file_sizes(self, report: ComplianceReport):
        """Check that files don't exceed max_lines"""
        if 'modules' not in self.blueprint:
            return

        for module_spec in self.blueprint['modules']:
            if 'max_lines' not in module_spec:
                continue

            module_path = self.project_root / module_spec['path']
            if not module_path.exists():
                continue

            try:
                with open(module_path, 'r') as f:
                    line_count = sum(1 for _ in f)

                max_lines = module_spec['max_lines']
                if line_count > max_lines:
                    report.add_violation(Violation(
                        severity="warning",
                        category="max_lines",
                        file=module_spec['path'],
                        line=None,
                        message=f"File has {line_count} lines (max: {max_lines})",
                        rule="max_file_size"
                    ))

            except Exception:
                pass

    def _check_forbidden_imports(self, report: ComplianceReport):
        """Check forbidden import patterns across all files"""
        if 'patterns' not in self.blueprint:
            return

        for pattern_spec in self.blueprint['patterns']:
            if pattern_spec.get('pattern') == 'ui_business_separation':
                if 'check' in pattern_spec:
                    for check in pattern_spec['check']:
                        self._check_ui_business_separation(report, check)

    def _check_ui_business_separation(self, report: ComplianceReport, rule: str):
        """Check UI/business separation rule"""
        # Parse rule like "modules/simple_tui.py should not import modules/api_client"
        parts = rule.split(' should not import ')
        if len(parts) != 2:
            return

        file_pattern, forbidden_import = parts
        file_path = self.project_root / file_pattern

        if not file_path.exists():
            return

        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read(), filename=str(file_path))

            imports = self._extract_imports(tree)

            for imp in imports:
                if forbidden_import in imp:
                    report.add_violation(Violation(
                        severity="error",
                        category="ui_business_separation",
                        file=file_pattern,
                        line=None,
                        message=f"UI/Business separation violation: {rule}",
                        rule="separation_of_concerns"
                    ))

        except Exception:
            pass

    def _calculate_metrics(self, report: ComplianceReport):
        """Calculate codebase metrics"""
        total_lines = 0
        file_count = 0
        function_lengths = []

        # Walk through modules directory
        modules_dir = self.project_root / "modules"
        if modules_dir.exists():
            for py_file in modules_dir.glob("*.py"):
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                        lines = len(content.splitlines())
                        total_lines += lines
                        file_count += 1

                        # Parse for function lengths
                        tree = ast.parse(content, filename=str(py_file))
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                func_lines = node.end_lineno - node.lineno + 1
                                function_lengths.append(func_lines)

                except Exception:
                    pass

        report.metrics['total_lines_of_code'] = total_lines
        report.metrics['module_count'] = file_count
        report.metrics['average_function_length'] = (
            sum(function_lengths) / len(function_lengths) if function_lengths else 0
        )

        # Check against targets
        if 'metrics' in self.blueprint and 'track' in self.blueprint['metrics']:
            for metric_spec in self.blueprint['metrics']['track']:
                metric_name = metric_spec['metric']
                target = metric_spec['target']
                actual = report.metrics.get(metric_name)

                if actual is not None:
                    # Parse target (e.g., "< 15000", "> 70%")
                    self._check_metric_target(report, metric_name, actual, target)

    def _check_metric_target(self, report: ComplianceReport, metric: str, actual: float, target: str):
        """Check if metric meets target"""
        # Parse target string
        if target.startswith('<'):
            target_value = float(target[1:].strip())
            if actual >= target_value:
                report.add_violation(Violation(
                    severity="info",
                    category="metric",
                    file="",
                    line=None,
                    message=f"Metric '{metric}': {actual:.1f} (target: {target})",
                    rule="metrics"
                ))
        elif target.startswith('>'):
            target_value = float(target[1:].strip().rstrip('%'))
            if actual <= target_value:
                report.add_violation(Violation(
                    severity="info",
                    category="metric",
                    file="",
                    line=None,
                    message=f"Metric '{metric}': {actual:.1f} (target: {target})",
                    rule="metrics"
                ))

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all import statements from AST"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports

    def _is_stdlib_import(self, import_name: str) -> bool:
        """Check if import is from standard library"""
        stdlib_modules = {
            'os', 'sys', 'ast', 'json', 'yaml', 'time', 'datetime',
            'pathlib', 'typing', 'dataclasses', 'threading', 'asyncio',
            'io', 'traceback', 'inspect', 'functools', 'itertools',
            'collections', 're', 'subprocess', 'shutil', 'tempfile',
            'cProfile', 'pstats'
        }

        first_part = import_name.split('.')[0]
        return first_part in stdlib_modules

    def format_report(self, report: ComplianceReport) -> str:
        """Format compliance report as readable text"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"ARCHITECTURE COMPLIANCE REPORT - {report.timestamp}")
        lines.append("=" * 70)
        lines.append("")

        # Metrics
        if report.metrics:
            lines.append("📊 METRICS:")
            for metric, value in report.metrics.items():
                lines.append(f"  • {metric}: {value:.1f}")
            lines.append("")

        # Errors
        if report.violations:
            lines.append(f"❌ ERRORS ({len(report.violations)}):")
            for v in report.violations:
                lines.append(f"  [{v.category}] {v.file}")
                lines.append(f"    {v.message}")
                lines.append(f"    Rule: {v.rule}")
                lines.append("")

        # Warnings
        if report.warnings:
            lines.append(f"⚠️  WARNINGS ({len(report.warnings)}):")
            for v in report.warnings:
                lines.append(f"  [{v.category}] {v.file}")
                lines.append(f"    {v.message}")
                lines.append("")

        # Info
        if report.info:
            lines.append(f"ℹ️  INFO ({len(report.info)}):")
            for v in report.info:
                lines.append(f"  {v.message}")

        lines.append("")

        # Summary
        if not report.has_errors():
            lines.append("✅ No critical violations found")
        else:
            lines.append(f"❌ {len(report.violations)} critical violations need attention")

        lines.append("=" * 70)

        return '\n'.join(lines)


def check_architecture(blueprint_path: str = "architecture.yml") -> ComplianceReport:
    """Convenience function to check architecture"""
    checker = ArchitectureChecker(blueprint_path)
    return checker.check_all()
