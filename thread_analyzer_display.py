#!/usr/bin/env python3
"""
Thread Analyzer Display - Pretty printing and reporting functionality
"""

from typing import Dict, List, Any


class ThreadDisplayManager:
    """Handles thread snapshot display and reporting"""

    def __init__(self, categorizer):
        """Initialize with categorizer for severity levels"""
        self.categorizer = categorizer

    def print_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Pretty print a snapshot with role categorization and severity ranking"""
        print("\n" + "="*80)
        print(f"THREAD SNAPSHOT - {snapshot['timestamp']}")
        print("="*80)

        # Show parallel execution health
        health = snapshot['health']
        print(f"\n📊 PARALLEL EXECUTION HEALTH: {health['description']}")
        print(f"   Status: {health['status']} (Severity: {health['max_severity']})")

        print(f"\n🔄 Asyncio Event Loop: {snapshot['asyncio']}")

        print(f"\n📋 Total Threads: {len(snapshot['threads'])}")
        print("-"*80)

        # Group threads by role for better readability
        lead_threads = [t for t in snapshot['threads'] if t['role'] == 'LEAD']
        bg_threads = [t for t in snapshot['threads'] if t['role'] == 'BACKGROUND']
        user_threads = [t for t in snapshot['threads'] if t['role'] == 'USER']

        # Sort each group by severity (highest first)
        lead_threads.sort(key=lambda t: t['severity_level'], reverse=True)
        bg_threads.sort(key=lambda t: t['severity_level'], reverse=True)
        user_threads.sort(key=lambda t: t['severity_level'], reverse=True)

        # Print LEAD threads first (most critical)
        if lead_threads:
            print("\n🎯 LEAD THREADS (Main/Event Loop - MUST NOT BLOCK):")
            print("-"*80)
            for t in lead_threads:
                self.print_thread(t)

        # Print BACKGROUND threads
        if bg_threads:
            print("\n⚙️  BACKGROUND THREADS (Workers - Expected to Block):")
            print("-"*80)
            for t in bg_threads:
                self.print_thread(t)

        # Print USER threads
        if user_threads:
            print("\n👤 USER THREADS (Custom/Command Threads):")
            print("-"*80)
            for t in user_threads:
                self.print_thread(t)

    def print_thread(self, t: Dict[str, Any]) -> None:
        """Print individual thread with severity indicators"""
        # Severity emoji
        severity_emoji = {
            'CRITICAL': '🔴',
            'WARNING': '🟠',
            'HEALTHY': '🟢',
            'OPTIMAL': '⚪'
        }
        emoji = severity_emoji.get(t['severity_name'], '⚫')

        # Status
        status = "BLOCKED" if t['is_blocked'] else "ACTIVE"

        print(f"\n{emoji} [{t['severity_name']}] {t['name']} ({status})")
        print(f"   ID: {t['id']} | Daemon: {t['daemon']} | Role: {t['role']}")
        print(f"   Location: {t['current_file']}:{t['current_line']} in {t['current_function']}()")
        print(f"   Severity: {t['severity_desc']}")

        if t['blocked_on']:
            print(f"   ⚠️  BLOCKED ON: {t['blocked_on']}")

        # Show last 3 stack frames for problematic threads
        if t['severity_level'] >= self.categorizer.SEVERITY['WARNING']:
            print(f"   Stack (last 3):")
            for frame in t['stack_trace'][-3:]:
                print(f"     {frame['file']}:{frame['line']} {frame['function']}()")
                if frame['code']:
                    # Fix: Safely handle frame code that might be None
                    code_text = frame['code']
                    if code_text is not None:
                        print(f"       → {code_text.strip()}")

    def print_stuck_threads(self, stuck_threads: List[Dict[str, Any]]) -> None:
        """Print report of stuck threads"""
        if not stuck_threads:
            print("\n✅ No stuck threads detected")
            return

        print("\n" + "="*80)
        print("⚠️  STUCK THREADS DETECTED")
        print("="*80)

        for st in stuck_threads:
            print(f"\n🔴 {st['thread']}")
            print(f"   Location: {st['location']}")
            print(f"   Blocked on: {st['blocked_on']}")
            print(f"   Duration: {st['duration']}")

    def print_analysis_summary(self, snapshots: List[Dict[str, Any]], analysis_engine) -> None:
        """Print final analysis summary"""
        print("\n" + "="*80)
        print("ANALYSIS SUMMARY")
        print("="*80)

        if len(snapshots) >= 2:
            all_stuck = []
            for i in range(1, len(snapshots)):
                stuck = analysis_engine.compare_snapshots(
                    snapshots[i-1],
                    snapshots[i]
                )
                # Fix: Use extend method properly
                all_stuck.extend(stuck)

            # Deduplicate
            seen = set()
            unique_stuck = []
            for st in all_stuck:
                key = (st['thread'], st['location'])
                if key not in seen:
                    # Fix: Use add method properly
                    seen.add(key)
                    # Fix: Use append method properly
                    unique_stuck.append(st)

            if unique_stuck:
                print("\n🚨 PERSISTENT BLOCKING DETECTED:")
                for st in unique_stuck:
                    print(f"\n   Thread: {st['thread']}")
                    print(f"   Location: {st['location']}")
                    print(f"   Blocked on: {st['blocked_on']}")
            else:
                print("\n✅ No persistent blocking detected")


def create_display_manager(categorizer):
    """Factory function to create display manager"""
    return ThreadDisplayManager(categorizer)