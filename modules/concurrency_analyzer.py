"""
Concurrency Analyzer - Detects threading issues and suggests async/threading improvements
Analyzes code for blocking I/O, deadlocks, and missing concurrency
"""

import ast
import re
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ConcurrencyIssue:
    """A concurrency-related issue"""
    issue_type: str  # "blocking_io", "missing_async", "deadlock_risk", "race_condition"
    severity: str  # "critical", "high", "medium", "low"
    file: str
    function: str
    line: int
    code_snippet: str
    explanation: str
    suggested_fix: str
    auto_fixable: bool = False


@dataclass
class ConcurrencyReport:
    """Report of concurrency analysis"""
    issues: List[ConcurrencyIssue] = field(default_factory=list)
    blocking_functions: Set[str] = field(default_factory=set)
    async_candidates: List[str] = field(default_factory=list)
    threading_candidates: List[str] = field(default_factory=list)

    def format_report(self) -> str:
        """Format concurrency report"""
        lines = []
        lines.append("=" * 70)
        lines.append("CONCURRENCY ANALYSIS REPORT")
        lines.append("=" * 70)
        lines.append(f"\nTotal Issues: {len(self.issues)}")
        lines.append(f"Blocking Functions: {len(self.blocking_functions)}")
        lines.append(f"Async Candidates: {len(self.async_candidates)}")
        lines.append(f"Threading Candidates: {len(self.threading_candidates)}\n")

        # Group by severity
        critical = [i for i in self.issues if i.severity == "critical"]
        high = [i for i in self.issues if i.severity == "high"]
        medium = [i for i in self.issues if i.severity == "medium"]

        if critical:
            lines.append("\n🔴 CRITICAL ISSUES:")
            for issue in critical:
                lines.append(f"\n  {issue.file}:{issue.line} in {issue.function}")
                lines.append(f"    Type: {issue.issue_type}")
                lines.append(f"    {issue.explanation}")
                lines.append(f"    Fix: {issue.suggested_fix}")
                if issue.auto_fixable:
                    lines.append(f"    ✨ Auto-fixable")

        if high:
            lines.append("\n⚠️  HIGH PRIORITY:")
            for issue in high:
                lines.append(f"\n  {issue.file}:{issue.line} in {issue.function}")
                lines.append(f"    {issue.explanation}")
                lines.append(f"    💡 {issue.suggested_fix}")

        if medium:
            lines.append(f"\n📋 MEDIUM PRIORITY: ({len(medium)} issues)")
            for issue in medium[:5]:  # Show first 5
                lines.append(f"  • {issue.file}:{issue.line} - {issue.issue_type}")

        return '\n'.join(lines)


class ConcurrencyAnalyzer:
    """Analyzes code for concurrency issues and opportunities"""

    # Blocking I/O patterns
    BLOCKING_PATTERNS = {
        'file_io': ['open(', 'read(', 'write(', 'close('],
        'network': ['requests.', 'urllib.', 'socket.', 'http.client'],
        'subprocess': ['subprocess.run', 'subprocess.call', 'subprocess.check_output'],
        'sleep': ['time.sleep', 'threading.Event.wait'],
        'locks': ['Lock.acquire', 'RLock.acquire', 'Semaphore.acquire']
    }

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.source = None
        self.tree = None
        self.issues: List[ConcurrencyIssue] = []

    def analyze(self) -> ConcurrencyReport:
        """Perform complete concurrency analysis"""
        try:
            with open(self.file_path, 'r') as f:
                self.source = f.read()

            self.tree = ast.parse(self.source, filename=str(self.file_path))

            # Run analysis passes
            self._detect_blocking_io()
            self._detect_missing_async()
            self._detect_ui_thread_violations()
            self._detect_race_conditions()

            # Build report
            report = ConcurrencyReport(issues=self.issues)
            self._categorize_functions(report)

            return report

        except Exception as e:
            print(f"Error analyzing {self.file_path}: {e}")
            return ConcurrencyReport()

    def _detect_blocking_io(self):
        """Detect blocking I/O operations"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                is_async = isinstance(node, ast.AsyncFunctionDef)

                # Get function body as text
                lines = self.source.split('\n')
                func_source = '\n'.join(lines[node.lineno - 1:node.end_lineno])

                # Check for blocking patterns
                for pattern_type, patterns in self.BLOCKING_PATTERNS.items():
                    for pattern in patterns:
                        if pattern in func_source:
                            # Found blocking operation
                            issue = ConcurrencyIssue(
                                issue_type="blocking_io",
                                severity="high" if pattern_type in ['network', 'sleep'] else "medium",
                                file=str(self.file_path.relative_to(Path.cwd())),
                                function=func_name,
                                line=node.lineno,
                                code_snippet=func_source[:100],
                                explanation=f"Blocking {pattern_type} operation: {pattern}",
                                suggested_fix=f"Use asyncio.to_thread() or async equivalent" if is_async else f"Move to background thread or use async",
                                auto_fixable=True
                            )
                            self.issues.append(issue)
                            break  # One issue per function

    def _detect_missing_async(self):
        """Detect functions that should be async"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and not isinstance(node, ast.AsyncFunctionDef):
                # Check if function calls async functions
                has_async_calls = False
                has_await = False

                for child in ast.walk(node):
                    if isinstance(child, ast.Await):
                        has_await = True
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            if child.func.id.startswith('async_'):
                                has_async_calls = True

                if has_async_calls or has_await:
                    self.issues.append(ConcurrencyIssue(
                        issue_type="missing_async",
                        severity="critical",
                        file=str(self.file_path.relative_to(Path.cwd())),
                        function=node.name,
                        line=node.lineno,
                        code_snippet=f"def {node.name}(...)",
                        explanation="Function calls async code but is not async",
                        suggested_fix=f"Change to: async def {node.name}(...)",
                        auto_fixable=True
                    ))

    def _detect_ui_thread_violations(self):
        """Detect operations that shouldn't run on UI thread"""
        ui_thread_patterns = [
            'app.write',
            'content.update',
            'widget.update',
            '_rebuild_display',
            'refresh'
        ]

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                func_source = self.source.split('\n')[node.lineno - 1:node.end_lineno]
                func_text = '\n'.join(func_source)

                # Check if this looks like a UI function
                is_ui_function = any(pattern in func_text for pattern in ui_thread_patterns)

                if is_ui_function:
                    # Check for blocking operations in UI function
                    for pattern_type, patterns in self.BLOCKING_PATTERNS.items():
                        if pattern_type in ['file_io', 'network', 'subprocess']:
                            for pattern in patterns:
                                if pattern in func_text and 'asyncio.to_thread' not in func_text:
                                    self.issues.append(ConcurrencyIssue(
                                        issue_type="ui_thread_violation",
                                        severity="critical",
                                        file=str(self.file_path.relative_to(Path.cwd())),
                                        function=func_name,
                                        line=node.lineno,
                                        code_snippet=f"UI function with {pattern}",
                                        explanation=f"Blocking {pattern_type} on UI thread: {pattern}",
                                        suggested_fix="Wrap in asyncio.to_thread() or move to background",
                                        auto_fixable=True
                                    ))

    def _detect_race_conditions(self):
        """Detect potential race conditions"""
        shared_state_patterns = [
            r'self\.\w+\s*=',  # Instance variable assignment
            r'global\s+\w+',   # Global variable declaration
            r'\w+\[\w+\]\s*=', # Dict/list mutation
        ]

        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_source = self.source.split('\n')[node.lineno - 1:node.end_lineno]
                func_text = '\n'.join(func_source)

                # Count state mutations
                mutation_count = sum(
                    len(re.findall(pattern, func_text))
                    for pattern in shared_state_patterns
                )

                # Check if function is async or in threaded context
                is_concurrent = isinstance(node, ast.AsyncFunctionDef) or \
                              'thread' in node.name.lower()

                if is_concurrent and mutation_count > 0:
                    # Check for lock usage
                    has_lock = 'Lock' in func_text or 'lock.acquire' in func_text

                    if not has_lock:
                        self.issues.append(ConcurrencyIssue(
                            issue_type="race_condition",
                            severity="high",
                            file=str(self.file_path.relative_to(Path.cwd())),
                            function=node.name,
                            line=node.lineno,
                            code_snippet=f"{mutation_count} state mutations",
                            explanation=f"Concurrent function modifies shared state without locking",
                            suggested_fix="Add threading.Lock or use asyncio.Lock",
                            auto_fixable=False
                        ))

    def _categorize_functions(self, report: ConcurrencyReport):
        """Categorize functions as async or threading candidates"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                func_source = self.source.split('\n')[node.lineno - 1:node.end_lineno]
                func_text = '\n'.join(func_source)

                # Check for I/O operations
                has_io = any(
                    pattern in func_text
                    for patterns in self.BLOCKING_PATTERNS.values()
                    for pattern in patterns
                )

                if has_io:
                    report.blocking_functions.add(func_name)

                    # Async candidates: functions with network/file I/O
                    if any(p in func_text for p in self.BLOCKING_PATTERNS['network'] + self.BLOCKING_PATTERNS['file_io']):
                        if not isinstance(node, ast.AsyncFunctionDef):
                            report.async_candidates.append(func_name)

                    # Threading candidates: CPU-heavy or subprocess operations
                    if any(p in func_text for p in self.BLOCKING_PATTERNS['subprocess']):
                        report.threading_candidates.append(func_name)


def analyze_concurrency(file_path: str) -> ConcurrencyReport:
    """Convenience function to analyze a file for concurrency issues"""
    analyzer = ConcurrencyAnalyzer(file_path)
    return analyzer.analyze()
