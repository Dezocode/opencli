#!/usr/bin/env python3
"""
Thread Analyzer Core - Thread categorization and analysis
"""

import sys
import threading
import traceback
import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any


class ThreadCategorizer:
    """Handles thread role classification and blocking analysis"""

    # Thread role classification
    THREAD_ROLES = {
        'LEAD': ['MainThread', 'asyncio', 'Textual'],  # Critical - must never block
        'BACKGROUND': ['permission-buffer', 'SDK', 'worker'],  # Expected to block
        'USER': []  # Custom threads from user commands
    }

    # Blocking severity levels
    SEVERITY = {
        'CRITICAL': 3,   # Main thread blocked - app frozen
        'WARNING': 2,    # Worker blocked but not progressing - deadlock
        'HEALTHY': 1,    # Worker blocked waiting for input - expected
        'OPTIMAL': 0     # Non-blocking, fully async
    }

    def categorize_thread(self, thread_name: str) -> str:
        """Categorize thread by role: LEAD, BACKGROUND, or USER"""
        thread_lower = thread_name.lower()

        # Check LEAD patterns (critical threads)
        for pattern in self.THREAD_ROLES['LEAD']:
            if pattern.lower() in thread_lower:
                return 'LEAD'

        # Check BACKGROUND patterns (worker threads)
        for pattern in self.THREAD_ROLES['BACKGROUND']:
            if pattern.lower() in thread_lower:
                return 'BACKGROUND'

        # Everything else is USER
        return 'USER'

    def assess_blocking_severity(self, thread_info: Dict[str, Any], thread_role: str) -> Tuple[str, int, str]:
        """
        Assess blocking severity and return (severity_name, severity_level, description)
        """
        is_blocked = thread_info['is_blocked']
        blocked_on = thread_info['blocked_on']

        # LEAD thread should NEVER block
        if thread_role == 'LEAD' and is_blocked:
            return ('CRITICAL', self.SEVERITY['CRITICAL'],
                   f"Main thread blocked on {blocked_on} - APP FROZEN")

        # BACKGROUND threads - distinguish healthy vs problematic blocking
        if thread_role == 'BACKGROUND':
            if is_blocked:
                # Blocked on Event.wait() for user input = HEALTHY
                if blocked_on == 'threading.Event.wait()':
                    return ('HEALTHY', self.SEVERITY['HEALTHY'],
                           "Worker waiting for user response - expected")
                # Blocked on call_from_thread = WARNING (possible deadlock)
                elif blocked_on == 'Textual.call_from_thread()':
                    return ('WARNING', self.SEVERITY['WARNING'],
                           "Worker blocked on UI update - possible deadlock")
                # Other blocking = WARNING
                else:
                    return ('WARNING', self.SEVERITY['WARNING'],
                           f"Worker blocked on {blocked_on} - investigate")
            else:
                # Not blocked = OPTIMAL
                return ('OPTIMAL', self.SEVERITY['OPTIMAL'],
                       "Worker active, non-blocking")

        # USER threads - any blocking is just informational
        if is_blocked:
            return ('HEALTHY', self.SEVERITY['HEALTHY'],
                   f"User thread blocked on {blocked_on}")
        else:
            return ('OPTIMAL', self.SEVERITY['OPTIMAL'],
                   "User thread active")


class ThreadAnalysisEngine:
    """Core thread analysis functionality"""

    def __init__(self):
        self.categorizer = ThreadCategorizer()

    def is_thread_blocked(self, frame: Any, stack: List[Any]) -> bool:
        """Check if thread appears blocked"""
        if not stack:
            return False

        blocking_patterns = [
            'wait', 'join', 'acquire', 'get', 'recv', 'accept', 'select', 'poll'
        ]

        for frame_info in stack:
            for pattern in blocking_patterns:
                if pattern in frame_info.name.lower():
                    return True

        return False

    def identify_blocking_call(self, frame: Any, stack: List[Any]) -> Optional[str]:
        """Identify what the thread is blocked on"""
        if not stack:
            return None

        # Check last few frames for blocking calls
        for frame_info in reversed(stack[-5:]):
            name = frame_info.name.lower()

            if 'event.wait' in name or 'done_event.wait' in name:
                return 'threading.Event.wait()'
            elif 'queue.get' in name:
                return 'Queue.get()'
            elif 'lock.acquire' in name:
                return 'Lock.acquire()'
            elif 'future.result' in name or 'wait_for' in name:
                return 'asyncio.Future/wait_for()'
            elif 'call_from_thread' in name:
                return 'Textual.call_from_thread()'
            elif 'sleep' in name:
                return 'sleep()'

        return None

    def format_stack(self, stack: List[Any]) -> List[Dict[str, Any]]:
        """Format stack trace for display"""
        formatted_stack = []
        for s in stack[-10:]:  # Last 10 frames
            frame_data = {
                'file': s.filename.split('/')[-1],  # Just filename
                'line': s.lineno,
                'function': s.name,
                'code': s.line if s.line else ''
            }
            formatted_stack.append(frame_data)
        return formatted_stack

    def analyze_execution_health(self, threads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze overall parallel execution health
        """
        critical_count = sum(1 for t in threads if t['severity_name'] == 'CRITICAL')
        warning_count = sum(1 for t in threads if t['severity_name'] == 'WARNING')
        healthy_count = sum(1 for t in threads if t['severity_name'] == 'HEALTHY')
        optimal_count = sum(1 for t in threads if t['severity_name'] == 'OPTIMAL')

        # Determine overall status
        if critical_count > 0:
            status = 'CRITICAL'
            max_severity = self.categorizer.SEVERITY['CRITICAL']
            description = f"⛔ {critical_count} CRITICAL: Main thread(s) blocked - app frozen!"
        elif warning_count > 0:
            status = 'WARNING'
            max_severity = self.categorizer.SEVERITY['WARNING']
            description = f"⚠️  {warning_count} WARNING: Worker thread(s) possibly deadlocked"
        elif healthy_count > 0:
            status = 'HEALTHY'
            max_severity = self.categorizer.SEVERITY['HEALTHY']
            description = f"✓ {healthy_count} threads waiting (expected), {optimal_count} active"
        else:
            status = 'OPTIMAL'
            max_severity = self.categorizer.SEVERITY['OPTIMAL']
            description = f"✅ All {optimal_count} threads active, fully async, non-blocking"

        return {
            'status': status,
            'max_severity': max_severity,
            'critical_count': critical_count,
            'warning_count': warning_count,
            'healthy_count': healthy_count,
            'optimal_count': optimal_count,
            'description': description
        }

    def capture_snapshot(self) -> Dict[str, Any]:
        """Capture current state of all threads"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'threads': []
        }

        # Get all threads
        for thread_id, frame in sys._current_frames().items():
            thread_name = None
            thread_obj = None

            # Find thread object
            for thread in threading.enumerate():
                if thread.ident == thread_id:
                    thread_name = thread.name
                    thread_obj = thread
                    break

            # Get stack trace
            stack = traceback.extract_stack(frame)

            # Analyze what it's doing
            current_function = stack[-1].name if stack else "unknown"
            current_file = stack[-1].filename if stack else "unknown"
            current_line = stack[-1].lineno if stack else 0

            # Check if blocked
            is_blocked = self.is_thread_blocked(frame, stack)
            blocked_on = self.identify_blocking_call(frame, stack)

            thread_info = {
                'id': thread_id,
                'name': thread_name or f"Thread-{thread_id}",
                'daemon': thread_obj.daemon if thread_obj else False,
                'alive': thread_obj.is_alive() if thread_obj else False,
                'current_function': current_function,
                'current_file': current_file,
                'current_line': current_line,
                'is_blocked': is_blocked,
                'blocked_on': blocked_on,
                'stack_trace': self.format_stack(stack)
            }

            # Add role categorization and severity assessment
            thread_role = self.categorizer.categorize_thread(thread_info['name'])
            severity_name, severity_level, severity_desc = self.categorizer.assess_blocking_severity(
                thread_info, thread_role
            )

            thread_info['role'] = thread_role
            thread_info['severity_name'] = severity_name
            thread_info['severity_level'] = severity_level
            thread_info['severity_desc'] = severity_desc

            snapshot['threads'].append(thread_info)

        # Check for asyncio event loop
        try:
            loop = asyncio.get_running_loop()
            snapshot['asyncio'] = {
                'running': True,
                'is_closed': loop.is_closed(),
                'tasks_count': len(asyncio.all_tasks(loop))
            }
        except RuntimeError:
            snapshot['asyncio'] = {'running': False}

        # Analyze parallel execution health
        snapshot['health'] = self.analyze_execution_health(snapshot['threads'])

        return snapshot

    def compare_snapshots(self, snap1: Dict[str, Any], snap2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compare two snapshots to find stuck threads"""
        stuck_threads = []

        # Build lookup for snap2
        snap2_threads = {t['id']: t for t in snap2['threads']}

        for t1 in snap1['threads']:
            t2 = snap2_threads.get(t1['id'])
            if not t2:
                continue

            # Check if thread is stuck in same location
            if (t1['is_blocked'] and t2['is_blocked'] and
                t1['current_function'] == t2['current_function'] and
                t1['current_line'] == t2['current_line']):

                stuck_threads.append({
                    'thread': t1['name'],
                    'location': f"{t1['current_file']}:{t1['current_line']} in {t1['current_function']}",
                    'blocked_on': t1['blocked_on'],
                    'duration': 'stuck between snapshots'
                })

        return stuck_threads