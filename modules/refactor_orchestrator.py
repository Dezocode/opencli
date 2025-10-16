"""
Refactoring Orchestrator - Master system for automated refactoring
Coordinates analysis, planning, execution, and validation
"""

import asyncio
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .code_analyzer import CodeAnalyzer
from .architecture_validator import ArchitectureValidator, ComplianceViolation
from .concurrency_analyzer import ConcurrencyAnalyzer, ConcurrencyIssue
from .refactor_executor import RefactoringExecutor, RefactoringPlan, RefactoringResult
from .profiler import RuntimeProfiler
from .auto_refactor import AutoRefactorManager


@dataclass
class RefactoringProposal:
    """A complete refactoring proposal with all analysis"""
    plan: RefactoringPlan
    compliance_violations: List[ComplianceViolation]
    concurrency_issues: List[ConcurrencyIssue]
    estimated_improvement: Dict[str, float]  # lines_reduced, performance_gain, etc.
    rationale: str
    priority: int  # 1-10, higher = more urgent


@dataclass
class RefactoringSession:
    """A refactoring session with full context"""
    proposal: RefactoringProposal
    result: Optional[RefactoringResult] = None
    approved: bool = False
    timestamp: str = ""


class RefactoringOrchestrator:
    """
    Master orchestrator for intelligent refactoring

    Workflow:
    1. Monitor files for violations (watchdog)
    2. Analyze violations (architecture + concurrency + performance)
    3. Generate refactoring proposals
    4. Execute in worktree sandbox
    5. Validate (tests + performance + architecture)
    6. Request permission
    7. Apply or reject

    Self-Healing:
    - Detects performance degradation
    - Automatically proposes fixes
    - Learns from approved/rejected refactorings
    """

    def __init__(self, repo_path: str = ".", permission_handler=None):
        self.repo_path = Path(repo_path).resolve()
        self.permission_handler = permission_handler

        # Components
        self.validator = ArchitectureValidator(repo_path)
        self.executor = RefactoringExecutor(repo_path)
        self.profiler = RuntimeProfiler()
        self.auto_refactor = AutoRefactorManager(repo_path, permission_handler)

        # Session tracking
        self.active_sessions: List[RefactoringSession] = []
        self.approved_patterns: List[str] = []  # Learn from approvals
        self.rejected_patterns: List[str] = []

        # Performance baseline
        self.performance_baseline: Dict[str, float] = {}

        # Monitoring
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None

    def start_monitoring(self, config=None) -> Dict:
        """Start continuous monitoring and self-healing"""
        if self._monitoring:
            return {"status": "already_running"}

        # Load architecture blueprint
        if not self.validator.load_blueprint():
            return {"status": "error", "message": "Failed to load architecture.yml"}

        # Start file watching
        self.auto_refactor.start(config)

        # Start performance monitoring
        self.profiler.start_profiling()

        # Start self-healing monitor
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._self_healing_loop, daemon=True)
        self._monitor_thread.start()

        return {
            "status": "started",
            "monitoring": ["architecture", "performance", "concurrency"],
            "self_healing": True
        }

    def stop_monitoring(self) -> Dict:
        """Stop monitoring"""
        self._monitoring = False
        self.auto_refactor.stop()

        if self.profiler.is_profiling:
            self.profiler.stop_profiling()

        return {"status": "stopped"}

    def _self_healing_loop(self):
        """Background loop that monitors and fixes degraded performance"""
        while self._monitoring:
            try:
                # Check performance every 60 seconds
                time.sleep(60)

                if not self.profiler.is_profiling:
                    continue

                # Get current performance
                stats = self.profiler.stop_profiling()
                self.profiler.start_profiling()

                # Check for degradation
                degraded_functions = self._detect_degradation(stats)

                if degraded_functions:
                    # Generate self-healing proposals
                    for func_name, current_time, baseline_time in degraded_functions:
                        self._propose_performance_fix(func_name, current_time, baseline_time)

            except Exception as e:
                print(f"Self-healing loop error: {e}")

    def _detect_degradation(self, stats) -> List[Tuple[str, float, float]]:
        """Detect functions that have degraded in performance"""
        degraded = []

        for func_name, cumtime, ncalls in stats.top_functions:
            avg_ms = (cumtime * 1000) / ncalls if ncalls > 0 else 0

            # Check against baseline
            if func_name in self.performance_baseline:
                baseline_ms = self.performance_baseline[func_name]
                degradation = (avg_ms - baseline_ms) / baseline_ms

                # More than 50% slower = degraded
                if degradation > 0.5:
                    degraded.append((func_name, avg_ms, baseline_ms))
            else:
                # Establish baseline
                self.performance_baseline[func_name] = avg_ms

        return degraded

    def _propose_performance_fix(self, func_name: str, current_ms: float, baseline_ms: float):
        """Propose a fix for degraded performance"""
        print(f"\n⚠️  PERFORMANCE DEGRADATION DETECTED:")
        print(f"   Function: {func_name}")
        print(f"   Current: {current_ms:.2f}ms")
        print(f"   Baseline: {baseline_ms:.2f}ms")
        print(f"   Degradation: {((current_ms - baseline_ms) / baseline_ms) * 100:.1f}%")
        print(f"\n   🔍 Analyzing for optimization opportunities...")

        # TODO: Implement automatic optimization detection and proposal

    def analyze_file(self, file_path: str) -> RefactoringProposal:
        """
        Comprehensive analysis of a file

        Returns a refactoring proposal with all issues and suggestions
        """
        file_path = Path(file_path)

        # 1. Architecture compliance
        compliance_report = self.validator.validate_all()
        file_violations = [
            v for v in compliance_report.violations + compliance_report.warnings
            if str(file_path) in v.file
        ]

        # 2. Concurrency analysis
        concurrency_analyzer = ConcurrencyAnalyzer(file_path)
        concurrency_report = concurrency_analyzer.analyze()

        # 3. Code structure analysis
        code_analyzer = CodeAnalyzer(file_path)
        code_analyzer.analyze()
        clusters = code_analyzer.identify_clusters()

        if not clusters:
            # No refactoring needed
            return None

        # Build refactoring plan from best cluster
        best_cluster = clusters[0]
        source_file = str(file_path.relative_to(self.repo_path))
        target_file = str(file_path.parent / f"{best_cluster.suggested_module_name}.py")

        plan = RefactoringPlan(
            action="extract_module",
            source_file=source_file,
            target_file=target_file,
            functions_to_move=best_cluster.functions,
            estimated_lines=best_cluster.total_lines,
            rationale=best_cluster.rationale
        )

        # Calculate estimated improvement
        estimated_improvement = {
            'lines_reduced': best_cluster.total_lines,
            'cohesion_gain': best_cluster.cohesion_score,
            'coupling_reduction': 1.0 - best_cluster.coupling_score,
            'concurrency_issues_fixed': len([
                i for i in concurrency_report.issues
                if i.function in best_cluster.functions and i.auto_fixable
            ])
        }

        # Calculate priority (1-10)
        priority = self._calculate_priority(
            file_violations,
            concurrency_report.issues,
            estimated_improvement
        )

        # Build rationale
        rationale_parts = [best_cluster.rationale]
        if file_violations:
            rationale_parts.append(f"Fixes {len(file_violations)} architecture violations")
        if concurrency_report.issues:
            critical = len([i for i in concurrency_report.issues if i.severity == "critical"])
            if critical:
                rationale_parts.append(f"Resolves {critical} critical concurrency issues")

        proposal = RefactoringProposal(
            plan=plan,
            compliance_violations=file_violations,
            concurrency_issues=[i for i in concurrency_report.issues if i.function in best_cluster.functions],
            estimated_improvement=estimated_improvement,
            rationale=". ".join(rationale_parts),
            priority=priority
        )

        return proposal

    def _calculate_priority(self, violations, concurrency_issues, improvements) -> int:
        """Calculate refactoring priority (1-10)"""
        priority = 5  # Base priority

        # Critical issues bump priority
        critical_concurrency = len([i for i in concurrency_issues if i.severity == "critical"])
        priority += critical_concurrency * 2

        # Architecture errors
        arch_errors = len([v for v in violations if v.severity == "error"])
        priority += arch_errors

        # Large improvements
        if improvements['lines_reduced'] > 500:
            priority += 2
        elif improvements['lines_reduced'] > 200:
            priority += 1

        return min(priority, 10)

    async def execute_proposal(self, proposal: RefactoringProposal) -> RefactoringSession:
        """
        Execute a refactoring proposal in sandbox

        Returns session with results for permission review
        """
        # Create session
        session = RefactoringSession(
            proposal=proposal,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

        # Execute in worktree
        result = self.executor.execute_extraction(proposal.plan)
        session.result = result

        if not result.success:
            return session

        # Run additional validation
        # TODO: Run architecture validation on refactored code
        # TODO: Run concurrency analysis on refactored code
        # TODO: Compare performance profiles

        return session

    async def request_approval(self, session: RefactoringSession) -> Tuple[bool, str]:
        """Request user approval for refactoring"""
        if not self.permission_handler:
            # No handler - auto-approve if tests pass
            if session.result and session.result.test_results:
                if "PASSED" in session.result.test_results or "0 failed" in session.result.test_results:
                    return True, "Tests passed - auto-approved"
            return False, "No permission handler - manual approval required"

        # Build approval request
        proposal_dict = {
            'source_file': session.proposal.plan.source_file,
            'target_file': session.proposal.plan.target_file,
            'functions_to_move': session.proposal.plan.functions_to_move,
            'rationale': session.proposal.rationale,
            'priority': session.proposal.priority,
            'estimated_improvement': session.proposal.estimated_improvement,
            'compliance_violations': len(session.proposal.compliance_violations),
            'concurrency_issues': len(session.proposal.concurrency_issues)
        }

        result_dict = {
            'test_results': session.result.test_results if session.result else None,
            'changes': session.result.changes if session.result else [],
            'diff': session.result.diff if session.result else ""
        }

        # Request permission
        try:
            approved, reason = await self.permission_handler.check_and_prompt(
                "Intelligent Refactoring",
                {"proposal": proposal_dict, "result": result_dict}
            )

            session.approved = approved

            # Learn from approval/rejection
            if approved:
                self.approved_patterns.append(session.proposal.plan.action)
            else:
                self.rejected_patterns.append(session.proposal.plan.action)

            return approved, reason

        except Exception as e:
            return False, f"Permission request failed: {e}"

    def apply_session(self, session: RefactoringSession) -> bool:
        """Apply approved refactoring"""
        if not session.approved or not session.result:
            return False

        return self.executor.apply_refactoring(session.result)

    def reject_session(self, session: RefactoringSession):
        """Reject and cleanup session"""
        if session.result:
            self.executor.reject_refactoring(session.result)

    def get_status(self) -> Dict:
        """Get current orchestrator status"""
        return {
            "monitoring": self._monitoring,
            "active_sessions": len(self.active_sessions),
            "approved_count": len(self.approved_patterns),
            "rejected_count": len(self.rejected_patterns),
            "performance_baseline_functions": len(self.performance_baseline),
            "auto_refactor_status": self.auto_refactor.status()
        }

    def cleanup(self):
        """Cleanup resources"""
        self.stop_monitoring()
        self.executor.cleanup()
        self.auto_refactor.cleanup()


# Global orchestrator instance
_orchestrator: Optional[RefactoringOrchestrator] = None


def get_orchestrator(permission_handler=None) -> RefactoringOrchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = RefactoringOrchestrator(permission_handler=permission_handler)
    return _orchestrator
