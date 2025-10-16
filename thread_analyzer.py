#!/usr/bin/env python3
"""
Runtime Thread Analyzer - Diagnose blocking and deadlocks

Usage:
    python3 thread_analyzer.py [PID]

If PID is provided, attaches to running process.
Otherwise, runs as import for live monitoring.
"""

import time
from typing import List, Dict, Any
from thread_analyzer_core import ThreadAnalysisEngine, ThreadCategorizer
from thread_analyzer_display import create_display_manager


class ThreadAnalyzer:
    """Real-time thread activity monitor with role-based blocking analysis"""

    def __init__(self):
        self.analysis_engine = ThreadAnalysisEngine()
        self.categorizer = ThreadCategorizer()
        self.display_manager = create_display_manager(self.categorizer)
        self.snapshots: List[Dict[str, Any]] = []

    def capture_snapshot(self) -> Dict[str, Any]:
        """Capture current state of all threads"""
        snapshot = self.analysis_engine.capture_snapshot()
        self.snapshots.append(snapshot)
        return snapshot

    def compare_snapshots(self, snap1: Dict[str, Any], snap2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compare two snapshots to find stuck threads"""
        return self.analysis_engine.compare_snapshots(snap1, snap2)

    def print_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Pretty print a snapshot"""
        self.display_manager.print_snapshot(snapshot)

    def print_stuck_threads(self, stuck_threads: List[Dict[str, Any]]) -> None:
        """Print report of stuck threads"""
        self.display_manager.print_stuck_threads(stuck_threads)

    def monitor_continuous(self, interval: float = 2.0, iterations: int = 5) -> None:
        """Monitor threads continuously"""
        print(f"\n🔍 Starting continuous monitoring...")
        print(f"   Interval: {interval}s")
        print(f"   Iterations: {iterations}")

        for i in range(iterations):
            print(f"\n📸 Snapshot {i+1}/{iterations}")
            snapshot = self.capture_snapshot()
            self.print_snapshot(snapshot)

            # Compare with previous
            if len(self.snapshots) >= 2:
                stuck = self.compare_snapshots(
                    self.snapshots[-2],
                    self.snapshots[-1]
                )
                self.print_stuck_threads(stuck)

            if i < iterations - 1:
                time.sleep(interval)

        print("\n✅ Monitoring complete")


def run_standalone() -> None:
    """Run as standalone monitoring tool"""
    print("="*80)
    print("OPENCLI RUNTIME THREAD ANALYZER")
    print("="*80)

    # Fix: Create ThreadAnalyzer instance properly
    analyzer = ThreadAnalyzer()

    try:
        analyzer.monitor_continuous(interval=2.0, iterations=5)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")

    # Final summary - use display manager
    analyzer.display_manager.print_analysis_summary(analyzer.snapshots, analyzer.analysis_engine)


def monitor_in_app(duration: int = 10, interval: float = 2) -> ThreadAnalyzer:
    """
    Import this function and call from within OpenCLI

    Usage in OpenCLI:
        from thread_analyzer import monitor_in_app
        monitor_in_app(duration=10, interval=2)
    """
    # Fix: Create ThreadAnalyzer instance properly
    analyzer = ThreadAnalyzer()
    iterations = int(duration / interval)

    print(f"\n🔍 Monitoring threads for {duration}s...")

    for i in range(iterations):
        snapshot = analyzer.capture_snapshot()

        if i > 0:
            stuck = analyzer.compare_snapshots(
                analyzer.snapshots[-2],
                analyzer.snapshots[-1]
            )
            if stuck:
                print(f"\n⚠️  Snapshot {i+1}: {len(stuck)} stuck threads")
                for st in stuck:
                    print(f"   - {st['thread']} blocked on {st['blocked_on']}")

        time.sleep(interval)

    return analyzer


if __name__ == '__main__':
    run_standalone()