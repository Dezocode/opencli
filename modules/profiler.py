"""
Runtime Profiling and Thread Analysis for OpenCLI
Monitors performance, detects bottlenecks, and identifies threading issues
"""

import cProfile
import pstats
import io
import threading
import time
import traceback
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ThreadInfo:
    """Information about a running thread"""
    thread_id: int
    name: str
    daemon: bool
    alive: bool
    stack_trace: str
    blocked_time: Optional[float] = None


@dataclass
class ProfileStats:
    """Performance profile statistics"""
    total_calls: int
    total_time: float
    top_functions: List[Tuple[str, float, int]]  # (function, cumtime, ncalls)
    bottlenecks: List[Tuple[str, float]]  # Functions exceeding performance budget


class RuntimeProfiler:
    """Monitors runtime performance and threading compliance"""

    def __init__(self):
        self.profiler = None
        self.is_profiling = False
        self.thread_snapshots = []
        self.performance_budgets = {}  # function_name: max_time_ms

    def start_profiling(self) -> None:
        """Start performance profiling"""
        if self.is_profiling:
            return

        self.profiler = cProfile.Profile()
        self.profiler.enable()
        self.is_profiling = True

    def stop_profiling(self) -> ProfileStats:
        """Stop profiling and return statistics"""
        if not self.is_profiling:
            return None

        self.profiler.disable()
        self.is_profiling = False

        # Analyze statistics
        s = io.StringIO()
        stats = pstats.Stats(self.profiler, stream=s)
        stats.sort_stats('cumulative')

        # Get total stats
        total_calls = stats.total_calls
        total_time = stats.total_tt

        # Get top functions by cumulative time
        top_functions = []
        for func, (cc, nc, tt, ct, callers) in list(stats.stats.items())[:20]:
            func_name = f"{func[0]}:{func[1]}:{func[2]}"
            top_functions.append((func_name, ct, nc))

        # Identify bottlenecks (functions exceeding budgets)
        bottlenecks = []
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            func_name = f"{func[2]}"  # Just function name
            if func_name in self.performance_budgets:
                budget_ms = self.performance_budgets[func_name]
                actual_ms = (ct * 1000) / nc if nc > 0 else 0
                if actual_ms > budget_ms:
                    bottlenecks.append((func_name, actual_ms))

        return ProfileStats(
            total_calls=total_calls,
            total_time=total_time,
            top_functions=top_functions,
            bottlenecks=bottlenecks
        )

    def analyze_threads(self) -> List[ThreadInfo]:
        """Analyze all running threads and detect potential issues"""
        threads_info = []

        for thread in threading.enumerate():
            # Get stack trace
            stack_trace = "Not available"
            try:
                frame = threading._active.get(thread.ident)
                if frame:
                    stack_lines = traceback.format_stack(frame)
                    stack_trace = ''.join(stack_lines)
            except:
                pass

            thread_info = ThreadInfo(
                thread_id=thread.ident,
                name=thread.name,
                daemon=thread.daemon,
                alive=thread.is_alive(),
                stack_trace=stack_trace
            )

            threads_info.append(thread_info)

        return threads_info

    def detect_blocking_threads(self, snapshot_interval: float = 2.0) -> List[ThreadInfo]:
        """Detect threads that appear to be blocked or deadlocked"""
        # Take two snapshots of thread states
        snapshot1 = {t.thread_id: t.stack_trace for t in self.analyze_threads()}
        time.sleep(snapshot_interval)
        snapshot2 = {t.thread_id: t.stack_trace for t in self.analyze_threads()}

        # Find threads with identical stack traces (potentially blocked)
        blocked_threads = []

        for thread_id, stack1 in snapshot1.items():
            if thread_id in snapshot2:
                stack2 = snapshot2[thread_id]
                if stack1 == stack2 and "wait" in stack1.lower():
                    # Thread hasn't moved and is waiting - likely blocked
                    thread_info = next((t for t in self.analyze_threads() if t.thread_id == thread_id), None)
                    if thread_info:
                        thread_info.blocked_time = snapshot_interval
                        blocked_threads.append(thread_info)

        return blocked_threads

    def set_performance_budget(self, function_name: str, max_time_ms: float) -> None:
        """Set performance budget for a function"""
        self.performance_budgets[function_name] = max_time_ms

    def format_thread_report(self, threads: List[ThreadInfo]) -> str:
        """Format thread analysis into readable report"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"THREAD ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        lines.append(f"\nTotal Threads: {len(threads)}\n")

        for thread in threads:
            lines.append(f"Thread ID: {thread.thread_id}")
            lines.append(f"  Name: {thread.name}")
            lines.append(f"  Daemon: {thread.daemon}")
            lines.append(f"  Alive: {thread.alive}")
            if thread.blocked_time:
                lines.append(f"  ⚠️ BLOCKED for {thread.blocked_time}s")
            lines.append(f"  Stack Trace:")
            for line in thread.stack_trace.split('\n')[:5]:  # First 5 lines
                lines.append(f"    {line}")
            lines.append("")

        return '\n'.join(lines)

    def format_profile_report(self, stats: ProfileStats) -> str:
        """Format profile statistics into readable report"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"PERFORMANCE PROFILE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        lines.append(f"\nTotal Calls: {stats.total_calls}")
        lines.append(f"Total Time: {stats.total_time:.3f}s\n")

        if stats.bottlenecks:
            lines.append("⚠️ PERFORMANCE BUDGET VIOLATIONS:")
            for func_name, actual_ms in stats.bottlenecks:
                budget_ms = self.performance_budgets.get(func_name, 0)
                lines.append(f"  {func_name}: {actual_ms:.2f}ms (budget: {budget_ms:.2f}ms)")
            lines.append("")

        lines.append("TOP 20 FUNCTIONS BY CUMULATIVE TIME:")
        for func_name, cumtime, ncalls in stats.top_functions:
            avg_ms = (cumtime * 1000) / ncalls if ncalls > 0 else 0
            lines.append(f"  {func_name}")
            lines.append(f"    Cumulative: {cumtime:.3f}s | Calls: {ncalls} | Avg: {avg_ms:.2f}ms")

        return '\n'.join(lines)


# Global profiler instance
_profiler = RuntimeProfiler()


def get_profiler() -> RuntimeProfiler:
    """Get the global profiler instance"""
    return _profiler
