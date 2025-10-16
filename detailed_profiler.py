#!/usr/bin/env python3
"""
Detailed Runtime Profiler - Maximum Detail Timeline Analysis

Generates comprehensive multi-page PDF with:
- Every thread on separate row
- Every function call labeled
- Blocking status color-coded
- Handoff arrows between functions
- State transitions marked
- Full stack context

Usage:
    python3 detailed_profiler.py --interval 0.5 --duration 120
"""

import sys
import threading
import time
import traceback
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json
import re

# Try to import keyboard listener (optional)
HAS_KEYBOARD_LISTENER = False
try:
    from pynput import keyboard
    HAS_KEYBOARD_LISTENER = True
except ImportError:
    # Will fallback to analyzing system logs
    pass

# Auto-install matplotlib if needed
HAS_MATPLOTLIB = False
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    import matplotlib.lines as mlines
    HAS_MATPLOTLIB = True
except ImportError:
    print("📦 matplotlib not found - attempting auto-install...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'matplotlib', '--quiet'])
        print("✅ matplotlib installed successfully")
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
        import matplotlib.lines as mlines
        HAS_MATPLOTLIB = True
    except Exception as e:
        print(f"⚠️  Failed to auto-install matplotlib: {e}")
        HAS_MATPLOTLIB = False


class DetailedProfiler:
    """
    Comprehensive profiler with maximum detail visualization
    VERSION: UPGRADED - 8 PAGES WITH USER INPUT TRACKING
    """

    # Thread role classification
    THREAD_ROLES = {
        'LEAD': ['MainThread', 'asyncio', 'Textual'],
        'BACKGROUND': ['permission-buffer', 'SDK', 'worker'],
        'USER': []
    }

    # Colors for states
    STATE_COLORS = {
        'active': '#2ECC71',      # Green - actively executing
        'blocked': '#E74C3C',     # Red - blocked/waiting
        'waiting': '#F39C12',     # Orange - waiting on I/O
        'idle': '#95A5A6'         # Gray - idle
    }

    # Colors for roles
    ROLE_COLORS = {
        'LEAD': '#E74C3C',
        'BACKGROUND': '#3498DB',
        'USER': '#2ECC71'
    }

    def __init__(self, sample_interval: float = 0.5, duration: int = 120):
        # DEBUG: Print which version is loaded
        import sys
        profiler_file = sys.modules[self.__class__.__module__].__file__
        print(f"🔍 DEBUG: DetailedProfiler loaded from: {profiler_file}")
        print(f"🔍 DEBUG: MAXIMUM DETAIL MODE - Dynamic page generation enabled")

        self.sample_interval = sample_interval
        self.duration = duration
        self.samples: List[Dict] = []
        self.threads_seen: Dict[str, Dict] = {}  # Track all threads
        self.function_changes: List[Dict] = []  # Track function transitions
        self.handoffs: List[Dict] = []  # Track function handoffs
        self.user_events: List[Dict] = []  # Track ALL user input events
        self.event_propagation: List[Dict] = []  # Track event flow
        self.function_hierarchy: Dict = defaultdict(list)  # Track call hierarchies
        self.blocking_hierarchy: Dict = defaultdict(list)  # Hierarchical blocking
        self.all_functions: Dict = defaultdict(int)  # ALL function calls seen
        self.call_chains: Dict = defaultdict(int)  # Track unique call chains

        # NEW: Message and response tracking
        self.user_messages: List[Dict] = []  # Track ALL chat messages sent
        self.message_responses: Dict = defaultdict(list)  # Map message -> responding functions
        self.permission_prompts: List[Dict] = []  # Track ALL permission prompts
        self.prompt_responses: Dict = defaultdict(list)  # Map prompt -> responding functions

        # NEW: Line-level tracking
        self.function_line_executions: Dict = defaultdict(int)  # Track function:line executions

        # NEW: State hierarchy tracking (running/blocking/async)
        self.state_hierarchy: List[Dict] = []  # Timestamped state snapshots

        self.start_time = None
        self.keyboard_hook_active = False
        self.keyboard_listener = None

    def _categorize_thread(self, thread_name: str) -> str:
        """Categorize thread by role"""
        thread_lower = thread_name.lower()
        for pattern in self.THREAD_ROLES['LEAD']:
            if pattern.lower() in thread_lower:
                return 'LEAD'
        for pattern in self.THREAD_ROLES['BACKGROUND']:
            if pattern.lower() in thread_lower:
                return 'BACKGROUND'
        return 'USER'

    def _detect_blocking_state(self, stack) -> str:
        """Detect if thread is blocked and what type"""
        if not stack:
            return 'idle'

        blocking_keywords = {
            'wait': 'blocked',
            'join': 'blocked',
            'acquire': 'blocked',
            'lock': 'blocked',
            'event': 'blocked',
            'queue.get': 'waiting',
            'recv': 'waiting',
            'accept': 'waiting',
            'select': 'waiting',
            'poll': 'waiting',
            'sleep': 'waiting'
        }

        for frame in reversed(stack[-5:]):
            name = frame.name.lower()
            for keyword, state in blocking_keywords.items():
                if keyword in name:
                    return state

        return 'active'

    def _on_key_press(self, key):
        """Callback for keyboard events"""
        if not self.start_time:
            return

        timestamp = time.time() - self.start_time
        try:
            key_str = key.char if hasattr(key, 'char') and key.char else str(key)
        except AttributeError:
            key_str = str(key)

        self.user_events.append({
            'timestamp': timestamp,
            'event_type': 'keypress',
            'key': key_str,
            'datetime': datetime.now().isoformat()
        })

        # Also track which thread handles this key
        # (we'll detect this in capture_sample by checking for on_key functions)

    def _start_keyboard_monitoring(self):
        """Start keyboard event monitoring"""
        if not HAS_KEYBOARD_LISTENER:
            print("⚠️  Keyboard listener not available (pynput not installed)")
            return

        try:
            self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
            self.keyboard_listener.start()
            self.keyboard_hook_active = True
            print("✅ Keyboard monitoring started")
        except Exception as e:
            print(f"⚠️  Could not start keyboard monitoring: {e}")
            self.keyboard_hook_active = False

    def _stop_keyboard_monitoring(self):
        """Stop keyboard event monitoring"""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_hook_active = False

    def capture_sample(self) -> Dict:
        """Capture detailed sample of all thread states"""
        timestamp = time.time() - self.start_time
        sample = {
            'timestamp': timestamp,
            'datetime': datetime.now().isoformat(),
            'threads': []
        }

        for thread_id, frame in sys._current_frames().items():
            thread_name = None
            for thread in threading.enumerate():
                if thread.ident == thread_id:
                    thread_name = thread.name
                    break

            if not thread_name:
                thread_name = f"Thread-{thread_id}"

            stack = traceback.extract_stack(frame)
            if not stack:
                continue

            current_frame = stack[-1]
            current_function = current_frame.name
            current_file = current_frame.filename.split('/')[-1]
            current_line = current_frame.lineno

            # Detect state
            state = self._detect_blocking_state(stack)

            # Caller info
            caller_function = stack[-2].name if len(stack) > 1 else None
            caller_file = stack[-2].filename.split('/')[-1] if len(stack) > 1 else None

            role = self._categorize_thread(thread_name)

            thread_info = {
                'thread_id': thread_id,
                'thread_name': thread_name,
                'role': role,
                'function': current_function,
                'file': current_file,
                'line': current_line,
                'state': state,
                'caller_function': caller_function,
                'caller_file': caller_file,
                'stack_depth': len(stack),
                'full_stack': [
                    f"{s.filename.split('/')[-1]}:{s.lineno}::{s.name}"
                    for s in stack  # FULL STACK, not just last 10!
                ]
            }

            # Track ALL functions seen + LINE-LEVEL tracking
            for s in stack:
                func_key = f"{s.filename.split('/')[-1]}::{s.name}"
                self.all_functions[func_key] += 1

                # NEW: Track line-level executions
                line_key = f"{s.filename.split('/')[-1]}:{s.lineno}::{s.name}"
                self.function_line_executions[line_key] += 1

            # Track function hierarchy (call chain)
            if len(stack) > 1:
                for i in range(len(stack) - 1):
                    parent = f"{stack[i].filename.split('/')[-1]}::{stack[i].name}"
                    child = f"{stack[i+1].filename.split('/')[-1]}::{stack[i+1].name}"
                    self.function_hierarchy[parent].append({
                        'child': child,
                        'timestamp': timestamp,
                        'thread': thread_name,
                        'state': state
                    })

            # Track blocking hierarchy
            if state == 'blocked':
                # Full call chain leading to block
                block_chain = [f"{s.filename.split('/')[-1]}::{s.name}" for s in stack]
                self.blocking_hierarchy[thread_name].append({
                    'timestamp': timestamp,
                    'chain': block_chain,
                    'blocked_at': current_function
                })

            # Track event propagation (detect event handlers)
            event_handler_patterns = ['on_key', 'on_', 'handle_', '_handle', 'process_key', 'key_press']
            for pattern in event_handler_patterns:
                if pattern in current_function.lower():
                    # This might be handling a user event
                    # Check if there's a recent user event
                    recent_events = [e for e in self.user_events if timestamp - e['timestamp'] < 0.5]
                    if recent_events or any(pattern in f.name.lower() for f in stack[-5:]):
                        self.event_propagation.append({
                            'timestamp': timestamp,
                            'thread_name': thread_name,
                            'handler_function': current_function,
                            'handler_file': current_file,
                            'full_call_chain': [f"{s.filename.split('/')[-1]}::{s.name}" for s in stack],
                            'state': state
                        })
                    break

            # Track unique call chains
            call_chain_key = ' -> '.join([f"{s.name}" for s in stack[-5:]])
            self.call_chains[call_chain_key] += 1

            # NEW: Detect user messages being sent (REAL OpenCLI function names from actual traces!)
            # CHECK ENTIRE STACK, not just top function!
            message_patterns = ['_handle_user_message', 'action_submit', 'post_message', 'Submitted']
            message_files = ['simple_tui.py', 'multiline_input.py']
            message_detected = False
            for frame in stack:
                frame_func = frame.name
                frame_file = frame.filename.split('/')[-1]
                # Match if pattern in function name AND in relevant file
                for pattern in message_patterns:
                    if pattern in frame_func and any(f in frame_file for f in message_files):
                        # Message send detected in stack!
                        message_info = {
                            'timestamp': timestamp,
                            'thread': thread_name,
                            'function': frame_func,  # Use the frame where pattern was found
                            'file': frame_file,
                            'line': frame.lineno,
                            'full_stack': [f"{s.filename.split('/')[-1]}:{s.lineno}::{s.name}" for s in stack],
                            'state': state
                        }
                        # Check if this is a new message (relax deduplication to 0.05s)
                        if not self.user_messages or abs(self.user_messages[-1]['timestamp'] - timestamp) > 0.05:
                            self.user_messages.append(message_info)
                            print(f"📨 DEBUG: User message detected at {timestamp:.2f}s in stack frame: {frame_func} (file:{frame_file})")
                        message_detected = True
                        break
                if message_detected:
                    break

            # NEW: Detect permission prompts (REAL OpenCLI functions from actual traces!)
            # CHECK ENTIRE STACK, not just top function!
            permission_patterns = ['_show', '_run', 'prompt', 'show_transient', 'update',
                                  'resolve', '_resolve_current', '_clear',
                                  'watch_permission_prompt_data', '_render_permission_prompt',
                                  'check_and_prompt', 'PermissionResponse', 'PermissionCancelled']
            permission_files = ['permission_buffer_manager.py', 'async_permissions.py',
                               'tool_permissions.py', 'multiline_input.py', 'permission_prompt.py']
            permission_detected = False
            for frame in stack:
                frame_func = frame.name
                frame_file = frame.filename.split('/')[-1]
                # Match if pattern in function name AND in permission-related file
                for pattern in permission_patterns:
                    if pattern in frame_func and any(f in frame_file for f in permission_files):
                        # Permission prompt detected in stack!
                        prompt_info = {
                            'timestamp': timestamp,
                            'thread': thread_name,
                            'function': frame_func,  # Use the frame where pattern was found
                            'file': frame_file,
                            'line': frame.lineno,
                            'full_stack': [f"{s.filename.split('/')[-1]}:{s.lineno}::{s.name}" for s in stack],
                            'state': state
                        }
                        # Check if this is a new prompt (relax deduplication to 0.05s)
                        if not self.permission_prompts or abs(self.permission_prompts[-1]['timestamp'] - timestamp) > 0.05:
                            self.permission_prompts.append(prompt_info)
                            print(f"🔐 DEBUG: Permission prompt detected at {timestamp:.2f}s in stack frame: {frame_func} (file:{frame_file})")
                        permission_detected = True
                        break
                if permission_detected:
                    break

            sample['threads'].append(thread_info)

            # Track thread first appearance
            if thread_name not in self.threads_seen:
                self.threads_seen[thread_name] = {
                    'first_seen': timestamp,
                    'role': role,
                    'thread_id': thread_id
                }

            # Detect function changes (transitions)
            if self.samples:
                prev_sample = self.samples[-1]
                prev_thread = next(
                    (t for t in prev_sample['threads'] if t['thread_name'] == thread_name),
                    None
                )
                if prev_thread and prev_thread['function'] != current_function:
                    self.function_changes.append({
                        'timestamp': timestamp,
                        'thread_name': thread_name,
                        'from_function': prev_thread['function'],
                        'to_function': current_function,
                        'from_state': prev_thread['state'],
                        'to_state': state
                    })

            # Detect handoffs (caller changed)
            if caller_function and self.samples:
                prev_sample = self.samples[-1]
                prev_thread = next(
                    (t for t in prev_sample['threads'] if t['thread_name'] == thread_name),
                    None
                )
                if prev_thread and prev_thread.get('caller_function') != caller_function:
                    self.handoffs.append({
                        'timestamp': timestamp,
                        'thread_name': thread_name,
                        'from_caller': prev_thread.get('caller_function', 'None'),
                        'to_caller': caller_function,
                        'function': current_function
                    })

        # NEW: Build state hierarchy snapshot for this timestamp
        state_snapshot = {
            'timestamp': timestamp,
            'threads_running': [],
            'threads_blocked': [],
            'threads_waiting': [],
            'threads_async': [],
            'total_threads': len(sample['threads'])
        }

        for thread_data in sample['threads']:
            thread_summary = {
                'name': thread_data['thread_name'],
                'function': thread_data['function'],
                'file': thread_data['file'],
                'line': thread_data['line'],
                'role': thread_data['role']
            }

            if thread_data['state'] == 'active':
                state_snapshot['threads_running'].append(thread_summary)
            elif thread_data['state'] == 'blocked':
                state_snapshot['threads_blocked'].append(thread_summary)
            elif thread_data['state'] == 'waiting':
                state_snapshot['threads_waiting'].append(thread_summary)

        self.state_hierarchy.append(state_snapshot)

        return sample

    def profile(self):
        """Run profiling"""
        self.start_time = time.time()
        print("="*80)
        print("🔬 DETAILED PROFILER - Maximum Detail Timeline Analysis")
        print("="*80)
        print(f"\n⏱️  Sampling interval: {self.sample_interval}s")
        print(f"⏱️  Duration: {self.duration}s")
        print(f"📊 Total samples: {int(self.duration / self.sample_interval)}")
        print("\nProfiling started...\n")

        # Start keyboard monitoring
        self._start_keyboard_monitoring()

        end_time = self.start_time + self.duration
        sample_count = 0

        try:
            while time.time() < end_time:
                sample = self.capture_sample()
                self.samples.append(sample)
                sample_count += 1

                if sample_count % 10 == 0:
                    elapsed = time.time() - self.start_time
                    progress = (elapsed / self.duration) * 100
                    print(f"📸 Sample {sample_count} | {progress:.1f}% | {elapsed:.1f}s | Keys: {len(self.user_events)}")

                time.sleep(self.sample_interval)
        finally:
            # Stop keyboard monitoring
            self._stop_keyboard_monitoring()

        print(f"\n✅ Profiling complete! {len(self.samples)} samples captured")
        print(f"   Threads tracked: {len(self.threads_seen)}")
        print(f"   Function transitions: {len(self.function_changes)}")
        print(f"   Handoffs detected: {len(self.handoffs)}")
        print(f"   User events captured: {len(self.user_events)}")
        print(f"   Event propagations: {len(self.event_propagation)}")
        print(f"   Total functions: {len(self.all_functions)}")
        print(f"   Unique call chains: {len(self.call_chains)}")
        print(f"   User messages detected: {len(self.user_messages)}")
        print(f"   Permission prompts detected: {len(self.permission_prompts)}")

    def _analyze_discovery_window(self, event_timestamp: float, window_size: float = 10.0) -> Dict:
        """
        Analyze ±window_size seconds around an event timestamp
        Returns detailed analysis of what was running/blocking/responding
        """
        start_time = max(0, event_timestamp - window_size)
        end_time = min(self.duration, event_timestamp + window_size)

        # Get all samples in the window
        window_samples = [s for s in self.samples if start_time <= s['timestamp'] <= end_time]

        analysis = {
            'event_timestamp': event_timestamp,
            'window_start': start_time,
            'window_end': end_time,
            'total_samples': len(window_samples),
            'functions_before_event': defaultdict(int),
            'functions_after_event': defaultdict(int),
            'functions_at_event': [],
            'blocking_before': [],
            'blocking_after': [],
            'state_transitions': [],
            'response_candidates': []  # Functions that might be responding
        }

        for sample in window_samples:
            is_before = sample['timestamp'] < event_timestamp
            is_at_event = abs(sample['timestamp'] - event_timestamp) < self.sample_interval

            for thread_data in sample['threads']:
                func_line = f"{thread_data['file']}:{thread_data['line']}::{thread_data['function']}"

                # Track functions before/after
                if is_before:
                    analysis['functions_before_event'][func_line] += 1
                else:
                    analysis['functions_after_event'][func_line] += 1

                # Track functions right at event time
                if is_at_event:
                    analysis['functions_at_event'].append({
                        'thread': thread_data['thread_name'],
                        'function': thread_data['function'],
                        'file': thread_data['file'],
                        'line': thread_data['line'],
                        'state': thread_data['state'],
                        'role': thread_data['role']
                    })

                # Track blocking
                if thread_data['state'] in ['blocked', 'waiting']:
                    blocking_info = {
                        'timestamp': sample['timestamp'],
                        'thread': thread_data['thread_name'],
                        'function': func_line,
                        'state': thread_data['state']
                    }
                    if is_before:
                        analysis['blocking_before'].append(blocking_info)
                    else:
                        analysis['blocking_after'].append(blocking_info)

        # Identify response candidates (functions that appear more after the event)
        for func, after_count in analysis['functions_after_event'].items():
            before_count = analysis['functions_before_event'].get(func, 0)
            if after_count > before_count:
                analysis['response_candidates'].append({
                    'function': func,
                    'before_count': before_count,
                    'after_count': after_count,
                    'increase': after_count - before_count
                })

        # Sort response candidates by increase
        analysis['response_candidates'].sort(key=lambda x: x['increase'], reverse=True)

        return analysis

    def generate_detailed_pdf(self, output_path: str = "/tmp/opencli_detailed_timeline.pdf"):
        """Generate comprehensive DYNAMIC multi-page PDF with maximum detail"""
        if not HAS_MATPLOTLIB:
            print("\n⚠️  Cannot generate PDF - matplotlib not installed")
            return

        # Calculate total pages dynamically
        base_pages = 8
        message_pages = len(self.user_messages)
        permission_pages = len(self.permission_prompts)
        total_pages = base_pages + message_pages + permission_pages

        print(f"\n📄 Generating DYNAMIC detailed PDF: {output_path}")
        print(f"   Base pages: {base_pages}")
        print(f"   User message discovery pages: {message_pages}")
        print(f"   Permission prompt discovery pages: {permission_pages}")
        print(f"   TOTAL PAGES: {total_pages}")

        with PdfPages(output_path) as pdf:
            # BASE PAGES (8 pages)
            print("  📊 Generating base timeline pages...")
            self._generate_thread_timeline_page(pdf)
            self._generate_function_timeline_page(pdf)
            self._generate_blocking_analysis_page(pdf)
            self._generate_handoff_analysis_page(pdf)
            self._generate_state_distribution_page(pdf)
            self._generate_function_hierarchy_page(pdf)
            self._generate_all_functions_coverage_page(pdf)
            self._generate_event_propagation_page(pdf)

            # DYNAMIC PAGES: One per user message (±10s discovery)
            for idx, message in enumerate(self.user_messages, 1):
                print(f"  📨 Generating message #{idx} discovery page (±10s window)...")
                self._generate_message_discovery_page(pdf, message, idx)

            # DYNAMIC PAGES: One per permission prompt (±10s discovery)
            for idx, prompt in enumerate(self.permission_prompts, 1):
                print(f"  🔐 Generating permission #{idx} discovery page (±10s window)...")
                self._generate_permission_discovery_page(pdf, prompt, idx)

        print(f"\n✅ Detailed PDF saved: {output_path}")
        print(f"   TOTAL PAGES: {total_pages}")
        print(f"   - Base pages: 8")
        print(f"   - Message discovery pages: {message_pages}")
        print(f"   - Permission discovery pages: {permission_pages}")
        print(f"   User events tracked: {len(self.user_events)}")
        print(f"   All functions: {len(self.all_functions)}")

    def _add_user_input_markers(self, ax):
        """Add vertical lines showing user input events"""
        if not self.user_events:
            return

        for event in self.user_events:
            timestamp = event['timestamp']
            key = event.get('key', '?')

            # Draw vertical line
            ax.axvline(x=timestamp, color='cyan', alpha=0.4, linewidth=1, linestyle='--')

            # Add small label at top
            ax.text(
                timestamp,
                ax.get_ylim()[1] * 0.98,
                f"⌨️{key[:3]}",
                rotation=90,
                fontsize=5,
                color='cyan',
                va='top',
                ha='right',
                alpha=0.7
            )

    def _generate_thread_timeline_page(self, pdf):
        """Page 1: Detailed thread activity timeline with labeled functions + USER INPUT MARKERS"""
        fig, ax = plt.subplots(figsize=(20, 12))

        # Sort threads by role and name
        thread_names = sorted(
            self.threads_seen.keys(),
            key=lambda t: (
                0 if self.threads_seen[t]['role'] == 'LEAD' else
                1 if self.threads_seen[t]['role'] == 'BACKGROUND' else 2,
                t
            )
        )

        y_pos = 0
        y_labels = []
        y_ticks = []

        for thread_name in thread_names:
            thread_info = self.threads_seen[thread_name]
            role = thread_info['role']

            # Track current function and state
            current_func = None
            current_state = None
            block_start = None

            for i, sample in enumerate(self.samples):
                thread_data = next(
                    (t for t in sample['threads'] if t['thread_name'] == thread_name),
                    None
                )

                if not thread_data:
                    continue

                timestamp = sample['timestamp']
                func = thread_data['function']
                state = thread_data['state']
                file = thread_data['file']

                # Detect function/state change
                if func != current_func or state != current_state or i == len(self.samples) - 1:
                    # Draw previous block
                    if current_func and block_start is not None:
                        width = timestamp - block_start
                        color = self.STATE_COLORS.get(current_state, '#95A5A6')

                        # Draw block
                        rect = FancyBboxPatch(
                            (block_start, y_pos - 0.4),
                            width,
                            0.8,
                            boxstyle="round,pad=0.02",
                            facecolor=color,
                            edgecolor='black',
                            linewidth=1,
                            alpha=0.7
                        )
                        ax.add_patch(rect)

                        # Add function name label if block is wide enough
                        if width > 2:
                            label = f"{current_func[:15]}"
                            ax.text(
                                block_start + width/2,
                                y_pos,
                                label,
                                ha='center',
                                va='center',
                                fontsize=6,
                                fontweight='bold',
                                color='white',
                                bbox=dict(boxstyle='round', facecolor='black', alpha=0.3, pad=0.2)
                            )

                    # Start new block
                    current_func = func
                    current_state = state
                    block_start = timestamp

            # Thread label with role indicator
            role_emoji = '🎯' if role == 'LEAD' else '⚙️' if role == 'BACKGROUND' else '👤'
            y_labels.append(f"{role_emoji} {thread_name}")
            y_ticks.append(y_pos)
            y_pos += 1

        ax.set_xlim(0, self.duration)
        ax.set_ylim(-1, y_pos)
        ax.set_xlabel('Time (seconds)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Threads', fontsize=14, fontweight='bold')
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels, fontsize=9)
        ax.set_title(
            f'Detailed Thread Activity Timeline\n'
            f'Every function labeled | State color-coded | {len(self.samples)} samples @ {int(self.sample_interval*1000)}ms',
            fontsize=16,
            fontweight='bold',
            pad=20
        )
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        # Legend
        legend_elements = [
            mpatches.Patch(color=self.STATE_COLORS['active'], label='Active (executing)'),
            mpatches.Patch(color=self.STATE_COLORS['blocked'], label='Blocked (wait/lock)'),
            mpatches.Patch(color=self.STATE_COLORS['waiting'], label='Waiting (I/O)'),
            mpatches.Patch(color=self.STATE_COLORS['idle'], label='Idle'),
            mlines.Line2D([], [], color='cyan', linestyle='--', alpha=0.7, label=f'User Input ({len(self.user_events)} events)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10, framealpha=0.9)

        # Add user input markers
        self._add_user_input_markers(ax)

        plt.tight_layout()
        pdf.savefig(fig, dpi=200)
        plt.close()

    def _generate_function_timeline_page(self, pdf):
        """Page 2: Function transition timeline with arrows + USER INPUT MARKERS"""
        fig, ax = plt.subplots(figsize=(20, 12))

        # Plot function changes as timeline with annotations
        thread_names = sorted(self.threads_seen.keys())
        y_pos_map = {name: i for i, name in enumerate(thread_names)}

        # Draw transitions
        for change in self.function_changes[:200]:  # Limit to avoid clutter
            thread_name = change['thread_name']
            timestamp = change['timestamp']
            y_pos = y_pos_map.get(thread_name, 0)

            # Draw transition marker
            color = self.STATE_COLORS.get(change['to_state'], 'gray')
            ax.plot(timestamp, y_pos, 'o', color=color, markersize=4, alpha=0.6)

            # Add label for significant transitions
            if change['from_state'] != change['to_state']:
                ax.annotate(
                    f"{change['to_function'][:10]}",
                    xy=(timestamp, y_pos),
                    xytext=(5, 5),
                    textcoords='offset points',
                    fontsize=6,
                    alpha=0.7
                )

        ax.set_xlim(0, self.duration)
        ax.set_ylim(-1, len(thread_names))
        ax.set_xlabel('Time (seconds)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Threads', fontsize=14, fontweight='bold')
        ax.set_yticks(range(len(thread_names)))
        ax.set_yticklabels(thread_names, fontsize=9)
        ax.set_title(
            f'Function Transition Timeline (with User Input)\n'
            f'{len(self.function_changes)} function changes | State transitions marked',
            fontsize=16,
            fontweight='bold',
            pad=20
        )
        ax.grid(alpha=0.3)

        # Add user input markers
        self._add_user_input_markers(ax)

        plt.tight_layout()
        pdf.savefig(fig, dpi=200)
        plt.close()

    def _generate_blocking_analysis_page(self, pdf):
        """Page 3: Blocking analysis - when and where blocking occurs + USER INPUT MARKERS"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 12))

        # Top: Blocking timeline (show when each thread is blocked)
        thread_names = sorted(self.threads_seen.keys())
        y_pos_map = {name: i for i, name in enumerate(thread_names)}

        for sample in self.samples:
            timestamp = sample['timestamp']
            for thread_data in sample['threads']:
                if thread_data['state'] == 'blocked':
                    y_pos = y_pos_map.get(thread_data['thread_name'], 0)
                    ax1.plot(timestamp, y_pos, 's', color='red', markersize=3, alpha=0.5)

        ax1.set_xlim(0, self.duration)
        ax1.set_ylim(-1, len(thread_names))
        ax1.set_yticks(range(len(thread_names)))
        ax1.set_yticklabels(thread_names, fontsize=9)
        ax1.set_title('Blocking Timeline (Red = Blocked, Cyan = User Input)', fontsize=14, fontweight='bold')
        ax1.grid(alpha=0.3)

        # Add user input markers to top graph
        self._add_user_input_markers(ax1)

        # Bottom: Blocking duration histogram
        blocking_durations = defaultdict(list)
        for thread_name in thread_names:
            block_start = None
            for sample in self.samples:
                thread_data = next(
                    (t for t in sample['threads'] if t['thread_name'] == thread_name),
                    None
                )
                if thread_data:
                    if thread_data['state'] == 'blocked':
                        if block_start is None:
                            block_start = sample['timestamp']
                    else:
                        if block_start is not None:
                            duration = sample['timestamp'] - block_start
                            blocking_durations[thread_name].append(duration)
                            block_start = None

        # Plot histogram
        all_durations = []
        for durations in blocking_durations.values():
            all_durations.extend(durations)

        if all_durations:
            ax2.hist(all_durations, bins=50, color='red', alpha=0.7, edgecolor='black')
            ax2.set_xlabel('Blocking Duration (seconds)', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Frequency', fontsize=12, fontweight='bold')
            ax2.set_title(f'Blocking Duration Distribution ({len(all_durations)} blocks)', fontsize=14, fontweight='bold')
            ax2.grid(alpha=0.3)

        plt.tight_layout()
        pdf.savefig(fig, dpi=200)
        plt.close()

    def _generate_handoff_analysis_page(self, pdf):
        """Page 4: Function handoff analysis"""
        fig, ax = plt.subplots(figsize=(20, 12))

        # Count handoffs
        handoff_counts = defaultdict(int)
        for handoff in self.handoffs:
            key = (handoff['from_caller'], handoff['to_caller'], handoff['thread_name'])
            handoff_counts[key] += 1

        # Plot top handoffs as bar chart
        top_handoffs = sorted(handoff_counts.items(), key=lambda x: x[1], reverse=True)[:30]

        y_labels = []
        counts = []
        for (from_c, to_c, thread), count in top_handoffs:
            label = f"{thread}\n{from_c[:15]} → {to_c[:15]}"
            y_labels.append(label)
            counts.append(count)

        y_pos = range(len(y_labels))
        ax.barh(y_pos, counts, color='steelblue', edgecolor='black', alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(y_labels, fontsize=8)
        ax.set_xlabel('Handoff Count', fontsize=14, fontweight='bold')
        ax.set_title(
            f'Top 30 Function Handoffs\n'
            f'Total handoffs: {len(self.handoffs)} | Unique patterns: {len(handoff_counts)}',
            fontsize=16,
            fontweight='bold',
            pad=20
        )
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        pdf.savefig(fig, dpi=200)
        plt.close()

    def _generate_state_distribution_page(self, pdf):
        """Page 5: State distribution analysis"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 12))

        # Overall state distribution
        state_counts = defaultdict(int)
        for sample in self.samples:
            for thread_data in sample['threads']:
                state_counts[thread_data['state']] += 1

        ax1.pie(
            state_counts.values(),
            labels=state_counts.keys(),
            autopct='%1.1f%%',
            colors=[self.STATE_COLORS.get(s, 'gray') for s in state_counts.keys()],
            startangle=90
        )
        ax1.set_title('Overall State Distribution', fontsize=14, fontweight='bold')

        # State over time
        timestamps = [s['timestamp'] for s in self.samples]
        state_timeline = {state: [] for state in self.STATE_COLORS.keys()}

        for sample in self.samples:
            counts = defaultdict(int)
            for thread_data in sample['threads']:
                counts[thread_data['state']] += 1
            for state in state_timeline.keys():
                state_timeline[state].append(counts.get(state, 0))

        for state, counts in state_timeline.items():
            if any(counts):
                ax2.plot(timestamps, counts, label=state, color=self.STATE_COLORS[state], linewidth=2)

        ax2.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Thread Count', fontsize=12, fontweight='bold')
        ax2.set_title('State Distribution Over Time', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(alpha=0.3)

        # Per-thread state summary
        thread_states = defaultdict(lambda: defaultdict(int))
        for sample in self.samples:
            for thread_data in sample['threads']:
                thread_states[thread_data['thread_name']][thread_data['state']] += 1

        # Top threads by blocking
        thread_blocking = []
        for thread_name, states in thread_states.items():
            blocked_count = states.get('blocked', 0)
            total = sum(states.values())
            if total > 0:
                blocked_pct = (blocked_count / total) * 100
                thread_blocking.append((thread_name, blocked_pct, blocked_count))

        thread_blocking.sort(key=lambda x: x[1], reverse=True)
        top_threads = thread_blocking[:15]

        if top_threads:
            thread_names = [t[0] for t in top_threads]
            blocked_pcts = [t[1] for t in top_threads]

            y_pos = range(len(thread_names))
            ax3.barh(y_pos, blocked_pcts, color='red', alpha=0.7, edgecolor='black')
            ax3.set_yticks(y_pos)
            ax3.set_yticklabels(thread_names, fontsize=9)
            ax3.set_xlabel('% Time Blocked', fontsize=12, fontweight='bold')
            ax3.set_title('Top 15 Threads by Blocking %', fontsize=14, fontweight='bold')
            ax3.grid(axis='x', alpha=0.3)

        # Stack depth distribution
        stack_depths = []
        for sample in self.samples:
            for thread_data in sample['threads']:
                stack_depths.append(thread_data['stack_depth'])

        if stack_depths:
            ax4.hist(stack_depths, bins=30, color='purple', alpha=0.7, edgecolor='black')
            ax4.set_xlabel('Stack Depth', fontsize=12, fontweight='bold')
            ax4.set_ylabel('Frequency', fontsize=12, fontweight='bold')
            ax4.set_title('Stack Depth Distribution', fontsize=14, fontweight='bold')
            ax4.grid(alpha=0.3)

        plt.tight_layout()
        pdf.savefig(fig, dpi=200)
        plt.close()

    def _generate_function_hierarchy_page(self, pdf):
        """Page 6: Hierarchical Function Call Graph"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 12))

        # Top: Most frequent parent-child relationships
        parent_child_counts = defaultdict(int)
        for parent, children in self.function_hierarchy.items():
            for child_data in children:
                key = f"{parent[:20]} → {child_data['child'][:20]}"
                parent_child_counts[key] += 1

        # Get top 40 relationships
        top_relationships = sorted(parent_child_counts.items(), key=lambda x: x[1], reverse=True)[:40]

        if top_relationships:
            labels = [rel[0] for rel in top_relationships]
            counts = [rel[1] for rel in top_relationships]

            y_pos = range(len(labels))
            ax1.barh(y_pos, counts, color='forestgreen', edgecolor='black', alpha=0.7)
            ax1.set_yticks(y_pos)
            ax1.set_yticklabels(labels, fontsize=7)
            ax1.set_xlabel('Call Count', fontsize=12, fontweight='bold')
            ax1.set_title(
                f'Top 40 Function Call Relationships (Hierarchy)\n'
                f'Parent → Child calls | Total unique relationships: {len(parent_child_counts)}',
                fontsize=14,
                fontweight='bold'
            )
            ax1.grid(axis='x', alpha=0.3)

        # Bottom: Call chain depth analysis
        unique_chains = list(self.call_chains.items())
        unique_chains.sort(key=lambda x: x[1], reverse=True)
        top_chains = unique_chains[:30]

        if top_chains:
            chain_labels = [chain[0][:60] + '...' if len(chain[0]) > 60 else chain[0] for chain, _ in top_chains]
            chain_counts = [count for _, count in top_chains]

            y_pos = range(len(chain_labels))
            ax2.barh(y_pos, chain_counts, color='darkorange', edgecolor='black', alpha=0.7)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(chain_labels, fontsize=6)
            ax2.set_xlabel('Occurrence Count', fontsize=12, fontweight='bold')
            ax2.set_title(
                f'Top 30 Call Chains (Execution Paths)\n'
                f'Total unique call chains: {len(self.call_chains)}',
                fontsize=14,
                fontweight='bold'
            )
            ax2.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        pdf.savefig(fig, dpi=200)
        plt.close()

    def _generate_all_functions_coverage_page(self, pdf):
        """Page 7: All Functions Coverage - Stock-Like Graph"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 12))

        # Top: All functions ranked by execution count (stock-like bar chart)
        sorted_functions = sorted(self.all_functions.items(), key=lambda x: x[1], reverse=True)
        top_functions = sorted_functions[:50]  # Top 50 most called

        if top_functions:
            func_names = [f[:40] for f, _ in top_functions]
            func_counts = [count for _, count in top_functions]

            y_pos = range(len(func_names))
            ax1.barh(y_pos, func_counts, color='steelblue', edgecolor='black', alpha=0.7)
            ax1.set_yticks(y_pos)
            ax1.set_yticklabels(func_names, fontsize=7)
            ax1.set_xlabel('Total Executions', fontsize=12, fontweight='bold')
            ax1.set_title(
                f'Top 50 Functions by Execution Count (Coverage Analysis)\n'
                f'Total unique functions tracked: {len(self.all_functions)}',
                fontsize=14,
                fontweight='bold'
            )
            ax1.grid(axis='x', alpha=0.3)

        # Bottom: Function execution timeline (stock-like line graph)
        # Track top 10 functions over time
        top_10_funcs = [f for f, _ in sorted_functions[:10]]
        timestamps = [s['timestamp'] for s in self.samples]
        func_timeline = {func: [0] * len(self.samples) for func in top_10_funcs}

        for sample_idx, sample in enumerate(self.samples):
            for thread_data in sample['threads']:
                full_stack = thread_data.get('full_stack', [])
                for stack_entry in full_stack:
                    # Extract function name from stack entry
                    parts = stack_entry.split('::')
                    if len(parts) == 2:
                        func_key = f"{parts[0].split(':')[0]}::{parts[1]}"
                        if func_key in func_timeline:
                            func_timeline[func_key][sample_idx] += 1

        for func, counts in func_timeline.items():
            if any(counts):
                ax2.plot(timestamps, counts, label=func[:30], linewidth=2, alpha=0.7)

        ax2.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Active Instances', fontsize=12, fontweight='bold')
        ax2.set_title(
            'Top 10 Functions Over Time (Stock-Like Timeline)',
            fontsize=14,
            fontweight='bold'
        )
        ax2.legend(fontsize=7, loc='best')
        ax2.grid(alpha=0.3)

        plt.tight_layout()
        pdf.savefig(fig, dpi=200)
        plt.close()

    def _generate_event_propagation_page(self, pdf):
        """Page 8: Event Propagation Analysis"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 12))

        # Top: Event propagation timeline
        if self.event_propagation:
            thread_names = sorted(set(ep['thread_name'] for ep in self.event_propagation))
            y_pos_map = {name: i for i, name in enumerate(thread_names)}

            for ep in self.event_propagation:
                timestamp = ep['timestamp']
                thread_name = ep['thread_name']
                handler = ep['handler_function']
                state = ep['state']

                y_pos = y_pos_map.get(thread_name, 0)
                color = self.STATE_COLORS.get(state, 'gray')

                ax1.plot(timestamp, y_pos, 'o', color=color, markersize=5, alpha=0.7)
                ax1.annotate(
                    handler[:10],
                    xy=(timestamp, y_pos),
                    xytext=(5, 5),
                    textcoords='offset points',
                    fontsize=5,
                    alpha=0.6
                )

            ax1.set_xlim(0, self.duration)
            ax1.set_ylim(-1, len(thread_names))
            ax1.set_yticks(range(len(thread_names)))
            ax1.set_yticklabels(thread_names, fontsize=9)
            ax1.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
            ax1.set_title(
                f'Event Propagation Timeline\n'
                f'{len(self.event_propagation)} event handlers detected',
                fontsize=14,
                fontweight='bold'
            )
            ax1.grid(alpha=0.3)

            # Add user input markers
            self._add_user_input_markers(ax1)

        # Bottom: Most common event handlers
        handler_counts = defaultdict(int)
        for ep in self.event_propagation:
            handler_counts[ep['handler_function']] += 1

        if handler_counts:
            top_handlers = sorted(handler_counts.items(), key=lambda x: x[1], reverse=True)[:25]
            handler_names = [h[:30] for h, _ in top_handlers]
            counts = [count for _, count in top_handlers]

            y_pos = range(len(handler_names))
            ax2.barh(y_pos, counts, color='purple', edgecolor='black', alpha=0.7)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(handler_names, fontsize=8)
            ax2.set_xlabel('Call Count', fontsize=12, fontweight='bold')
            ax2.set_title(
                f'Top 25 Event Handlers\n'
                f'Total unique handlers: {len(handler_counts)}',
                fontsize=14,
                fontweight='bold'
            )
            ax2.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        pdf.savefig(fig, dpi=200)
        plt.close()

    def _generate_message_discovery_page(self, pdf, message, idx):
        """DYNAMIC PAGE: User Message #{idx} Discovery (±10s Analysis)"""
        fig = plt.figure(figsize=(20, 16))
        gs = fig.add_gridspec(4, 2, hspace=0.3, wspace=0.3)

        # Analyze ±10s window
        analysis = self._analyze_discovery_window(message['timestamp'], window_size=10.0)

        # Title
        fig.suptitle(
            f"📨 USER MESSAGE #{idx} DISCOVERY - ±10s WINDOW\n"
            f"Timestamp: {message['timestamp']:.2f}s | Function: {message['function']} | Line: {message['line']}",
            fontsize=16, fontweight='bold'
        )

        # Top Left: Timeline showing ±10s window
        ax1 = fig.add_subplot(gs[0, :])
        window_start = analysis['window_start']
        window_end = analysis['window_end']
        event_time = analysis['event_timestamp']

        # Draw window samples
        window_samples = [s for s in self.samples if window_start <= s['timestamp'] <= window_end]
        thread_names = sorted(set(t['thread_name'] for s in window_samples for t in s['threads']))
        y_pos_map = {name: i for i, name in enumerate(thread_names)}

        for sample in window_samples:
            for thread_data in sample['threads']:
                y = y_pos_map.get(thread_data['thread_name'], 0)
                color = self.STATE_COLORS.get(thread_data['state'], 'gray')
                ax1.plot(sample['timestamp'], y, 'o', color=color, markersize=3, alpha=0.6)

        # Mark the event
        ax1.axvline(x=event_time, color='red', linewidth=3, linestyle='--', label='MESSAGE SENT', alpha=0.8)
        ax1.set_xlim(window_start, window_end)
        ax1.set_ylim(-1, len(thread_names))
        ax1.set_yticks(range(len(thread_names)))
        ax1.set_yticklabels(thread_names, fontsize=8)
        ax1.set_xlabel('Time (seconds)', fontsize=10, fontweight='bold')
        ax1.set_title(f'±10s Timeline (Event at {event_time:.2f}s)', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(alpha=0.3)

        # Top Right: Functions at event time
        ax2 = fig.add_subplot(gs[0, 1])
        if analysis['functions_at_event']:
            func_labels = [f"{f['thread'][:15]}\n{f['function'][:20]}" for f in analysis['functions_at_event'][:10]]
            func_colors = [self.STATE_COLORS.get(f['state'], 'gray') for f in analysis['functions_at_event'][:10]]
            y_pos = range(len(func_labels))
            ax2.barh(y_pos, [1]*len(func_labels), color=func_colors, edgecolor='black', alpha=0.7)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(func_labels, fontsize=7)
            ax2.set_title(f'Functions AT Event Time ({len(analysis["functions_at_event"])} total)', fontsize=10, fontweight='bold')
            ax2.set_xlim(0, 1.2)
            ax2.set_xticks([])

        # Middle Left: Response candidates (functions appearing MORE after event)
        ax3 = fig.add_subplot(gs[1, :])
        if analysis['response_candidates']:
            top_responders = analysis['response_candidates'][:20]
            resp_labels = [r['function'][:50] for r in top_responders]
            resp_increases = [r['increase'] for r in top_responders]
            y_pos = range(len(resp_labels))
            ax3.barh(y_pos, resp_increases, color='green', edgecolor='black', alpha=0.7)
            ax3.set_yticks(y_pos)
            ax3.set_yticklabels(resp_labels, fontsize=7)
            ax3.set_xlabel('Increase in Execution Count (After - Before)', fontsize=10, fontweight='bold')
            ax3.set_title(
                f'TOP 20 RESPONSE CANDIDATES (Functions appearing MORE after message)\n'
                f'These are likely responding to the message!',
                fontsize=11, fontweight='bold'
            )
            ax3.grid(axis='x', alpha=0.3)

        # Bottom Left: Blocking BEFORE event
        ax4 = fig.add_subplot(gs[2, 0])
        if analysis['blocking_before']:
            block_counts = defaultdict(int)
            for b in analysis['blocking_before']:
                block_counts[b['thread']] += 1
            threads = list(block_counts.keys())[:15]
            counts = [block_counts[t] for t in threads]
            y_pos = range(len(threads))
            ax4.barh(y_pos, counts, color='orange', edgecolor='black', alpha=0.7)
            ax4.set_yticks(y_pos)
            ax4.set_yticklabels(threads, fontsize=7)
            ax4.set_xlabel('Block Count', fontsize=9)
            ax4.set_title(f'Blocking BEFORE Event ({len(analysis["blocking_before"])} blocks)', fontsize=10, fontweight='bold')
            ax4.grid(axis='x', alpha=0.3)

        # Bottom Right: Blocking AFTER event
        ax5 = fig.add_subplot(gs[2, 1])
        if analysis['blocking_after']:
            block_counts = defaultdict(int)
            for b in analysis['blocking_after']:
                block_counts[b['thread']] += 1
            threads = list(block_counts.keys())[:15]
            counts = [block_counts[t] for t in threads]
            y_pos = range(len(threads))
            ax5.barh(y_pos, counts, color='red', edgecolor='black', alpha=0.7)
            ax5.set_yticks(y_pos)
            ax5.set_yticklabels(threads, fontsize=7)
            ax5.set_xlabel('Block Count', fontsize=9)
            ax5.set_title(f'Blocking AFTER Event ({len(analysis["blocking_after"])} blocks)', fontsize=10, fontweight='bold')
            ax5.grid(axis='x', alpha=0.3)

        # Bottom: State hierarchy at event
        ax6 = fig.add_subplot(gs[3, :])
        # Find state snapshot closest to event
        closest_snapshot = min(self.state_hierarchy, key=lambda s: abs(s['timestamp'] - event_time))
        state_data = {
            'Running': len(closest_snapshot['threads_running']),
            'Blocked': len(closest_snapshot['threads_blocked']),
            'Waiting': len(closest_snapshot['threads_waiting'])
        }
        colors_pie = ['#2ECC71', '#E74C3C', '#F39C12']
        ax6.pie(state_data.values(), labels=state_data.keys(), autopct='%1.1f%%', colors=colors_pie, startangle=90)
        ax6.set_title(f'Thread State Distribution AT Event Time', fontsize=11, fontweight='bold')

        plt.tight_layout()
        pdf.savefig(fig, dpi=150)
        plt.close()

    def _generate_permission_discovery_page(self, pdf, prompt, idx):
        """DYNAMIC PAGE: Permission Prompt #{idx} Discovery (±10s Analysis)"""
        fig = plt.figure(figsize=(20, 16))
        gs = fig.add_gridspec(4, 2, hspace=0.3, wspace=0.3)

        # Analyze ±10s window
        analysis = self._analyze_discovery_window(prompt['timestamp'], window_size=10.0)

        # Title
        fig.suptitle(
            f"🔐 PERMISSION PROMPT #{idx} DISCOVERY - ±10s WINDOW\n"
            f"Timestamp: {prompt['timestamp']:.2f}s | Function: {prompt['function']} | Line: {prompt['line']}",
            fontsize=16, fontweight='bold'
        )

        # Top Left: Timeline showing ±10s window
        ax1 = fig.add_subplot(gs[0, :])
        window_start = analysis['window_start']
        window_end = analysis['window_end']
        event_time = analysis['event_timestamp']

        # Draw window samples
        window_samples = [s for s in self.samples if window_start <= s['timestamp'] <= window_end]
        thread_names = sorted(set(t['thread_name'] for s in window_samples for t in s['threads']))
        y_pos_map = {name: i for i, name in enumerate(thread_names)}

        for sample in window_samples:
            for thread_data in sample['threads']:
                y = y_pos_map.get(thread_data['thread_name'], 0)
                color = self.STATE_COLORS.get(thread_data['state'], 'gray')
                ax1.plot(sample['timestamp'], y, 'o', color=color, markersize=3, alpha=0.6)

        # Mark the event
        ax1.axvline(x=event_time, color='purple', linewidth=3, linestyle='--', label='PERMISSION PROMPT', alpha=0.8)
        ax1.set_xlim(window_start, window_end)
        ax1.set_ylim(-1, len(thread_names))
        ax1.set_yticks(range(len(thread_names)))
        ax1.set_yticklabels(thread_names, fontsize=8)
        ax1.set_xlabel('Time (seconds)', fontsize=10, fontweight='bold')
        ax1.set_title(f'±10s Timeline (Prompt at {event_time:.2f}s)', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(alpha=0.3)

        # Top Right: Functions at prompt time
        ax2 = fig.add_subplot(gs[0, 1])
        if analysis['functions_at_event']:
            func_labels = [f"{f['thread'][:15]}\n{f['function'][:20]}" for f in analysis['functions_at_event'][:10]]
            func_colors = [self.STATE_COLORS.get(f['state'], 'gray') for f in analysis['functions_at_event'][:10]]
            y_pos = range(len(func_labels))
            ax2.barh(y_pos, [1]*len(func_labels), color=func_colors, edgecolor='black', alpha=0.7)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(func_labels, fontsize=7)
            ax2.set_title(f'Functions AT Prompt Time ({len(analysis["functions_at_event"])} total)', fontsize=10, fontweight='bold')
            ax2.set_xlim(0, 1.2)
            ax2.set_xticks([])

        # Middle: Response handlers (functions appearing MORE after prompt)
        ax3 = fig.add_subplot(gs[1, :])
        if analysis['response_candidates']:
            top_responders = analysis['response_candidates'][:20]
            resp_labels = [r['function'][:50] for r in top_responders]
            resp_increases = [r['increase'] for r in top_responders]
            y_pos = range(len(resp_labels))
            ax3.barh(y_pos, resp_increases, color='purple', edgecolor='black', alpha=0.7)
            ax3.set_yticks(y_pos)
            ax3.set_yticklabels(resp_labels, fontsize=7)
            ax3.set_xlabel('Increase in Execution Count (After - Before)', fontsize=10, fontweight='bold')
            ax3.set_title(
                f'TOP 20 PERMISSION HANDLERS (Functions appearing MORE after prompt)\n'
                f'These are handling the permission request/response!',
                fontsize=11, fontweight='bold'
            )
            ax3.grid(axis='x', alpha=0.3)

        # Bottom Left: Blocking BEFORE prompt
        ax4 = fig.add_subplot(gs[2, 0])
        if analysis['blocking_before']:
            block_counts = defaultdict(int)
            for b in analysis['blocking_before']:
                block_counts[b['thread']] += 1
            threads = list(block_counts.keys())[:15]
            counts = [block_counts[t] for t in threads]
            y_pos = range(len(threads))
            ax4.barh(y_pos, counts, color='orange', edgecolor='black', alpha=0.7)
            ax4.set_yticks(y_pos)
            ax4.set_yticklabels(threads, fontsize=7)
            ax4.set_xlabel('Block Count', fontsize=9)
            ax4.set_title(f'Blocking BEFORE Prompt ({len(analysis["blocking_before"])} blocks)', fontsize=10, fontweight='bold')
            ax4.grid(axis='x', alpha=0.3)

        # Bottom Right: Blocking AFTER prompt
        ax5 = fig.add_subplot(gs[2, 1])
        if analysis['blocking_after']:
            block_counts = defaultdict(int)
            for b in analysis['blocking_after']:
                block_counts[b['thread']] += 1
            threads = list(block_counts.keys())[:15]
            counts = [block_counts[t] for t in threads]
            y_pos = range(len(threads))
            ax5.barh(y_pos, counts, color='red', edgecolor='black', alpha=0.7)
            ax5.set_yticks(y_pos)
            ax5.set_yticklabels(threads, fontsize=7)
            ax5.set_xlabel('Block Count', fontsize=9)
            ax5.set_title(f'Blocking AFTER Prompt ({len(analysis["blocking_after"])} blocks)', fontsize=10, fontweight='bold')
            ax5.grid(axis='x', alpha=0.3)

        # Bottom: State hierarchy at prompt time
        ax6 = fig.add_subplot(gs[3, :])
        # Find state snapshot closest to prompt
        closest_snapshot = min(self.state_hierarchy, key=lambda s: abs(s['timestamp'] - event_time))
        state_data = {
            'Running': len(closest_snapshot['threads_running']),
            'Blocked': len(closest_snapshot['threads_blocked']),
            'Waiting': len(closest_snapshot['threads_waiting'])
        }
        colors_pie = ['#2ECC71', '#E74C3C', '#F39C12']
        ax6.pie(state_data.values(), labels=state_data.keys(), autopct='%1.1f%%', colors=colors_pie, startangle=90)
        ax6.set_title(f'Thread State Distribution AT Prompt Time', fontsize=11, fontweight='bold')

        plt.tight_layout()
        pdf.savefig(fig, dpi=150)
        plt.close()

    def save_detailed_json(self, output_path: str = "/tmp/opencli_detailed_data.json"):
        """Save comprehensive raw data with ALL new structures"""

        # Convert defaultdicts to regular dicts for JSON serialization
        function_hierarchy_serializable = {
            parent: children for parent, children in self.function_hierarchy.items()
        }
        blocking_hierarchy_serializable = {
            thread: blocks for thread, blocks in self.blocking_hierarchy.items()
        }
        all_functions_serializable = dict(self.all_functions)
        call_chains_serializable = dict(self.call_chains)
        function_line_executions_serializable = dict(self.function_line_executions)
        message_responses_serializable = {
            k: v for k, v in self.message_responses.items()
        }
        prompt_responses_serializable = {
            k: v for k, v in self.prompt_responses.items()
        }

        data = {
            'config': {
                'sample_interval': self.sample_interval,
                'duration': self.duration,
                'total_samples': len(self.samples),
                'keyboard_monitoring': self.keyboard_hook_active
            },
            'samples': self.samples,
            'threads_tracked': self.threads_seen,
            'function_changes': self.function_changes,
            'handoffs': self.handoffs,
            # NEW: Maximum detail data structures
            'user_events': self.user_events,
            'event_propagation': self.event_propagation,
            'function_hierarchy': function_hierarchy_serializable,
            'blocking_hierarchy': blocking_hierarchy_serializable,
            'all_functions': all_functions_serializable,
            'call_chains': call_chains_serializable,
            # NEW: Message and response tracking
            'user_messages': self.user_messages,
            'permission_prompts': self.permission_prompts,
            'function_line_executions': function_line_executions_serializable,
            'state_hierarchy': self.state_hierarchy,
            'message_responses': message_responses_serializable,
            'prompt_responses': prompt_responses_serializable,
            # Summary stats
            'summary': {
                'total_threads': len(self.threads_seen),
                'total_functions': len(self.all_functions),
                'total_call_chains': len(self.call_chains),
                'total_user_events': len(self.user_events),
                'total_event_propagations': len(self.event_propagation),
                'total_function_transitions': len(self.function_changes),
                'total_handoffs': len(self.handoffs),
                'total_user_messages': len(self.user_messages),
                'total_permission_prompts': len(self.permission_prompts),
                'total_line_level_executions': len(self.function_line_executions),
                'total_state_snapshots': len(self.state_hierarchy),
                'unique_function_relationships': len(set(
                    f"{parent} → {child['child']}"
                    for parent, children in self.function_hierarchy.items()
                    for child in children
                ))
            }
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"💾 Detailed data saved: {output_path}")
        print(f"   Total data structures exported: {len(data.keys())}")
        print(f"   User events (keypresses): {len(self.user_events)}")
        print(f"   User messages detected: {len(self.user_messages)}")
        print(f"   Permission prompts detected: {len(self.permission_prompts)}")
        print(f"   Line-level executions tracked: {len(self.function_line_executions)}")
        print(f"   State snapshots: {len(self.state_hierarchy)}")
        print(f"   All functions: {len(self.all_functions)}")
        print(f"   Call chains: {len(self.call_chains)}")
        print(f"   Event propagations: {len(self.event_propagation)}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Detailed OpenCLI Runtime Profiler')
    parser.add_argument('--interval', type=float, default=0.5, help='Sample interval (seconds)')
    parser.add_argument('--duration', type=int, default=120, help='Duration (seconds)')
    parser.add_argument('--output', type=str, default='/tmp/opencli_detailed_timeline.pdf', help='Output PDF')
    args = parser.parse_args()

    profiler = DetailedProfiler(sample_interval=args.interval, duration=args.duration)

    try:
        profiler.profile()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")

    profiler.generate_detailed_pdf(args.output)
    profiler.save_detailed_json()

    print("\n" + "="*80)
    print("✅ DETAILED PROFILING COMPLETE - MAXIMUM DETAIL MODE")
    print("="*80)
    print(f"\n📄 PDF: {args.output} (DYNAMIC PAGE COUNT)")
    print("   BASE PAGES (8):")
    print("   - Page 1: Thread timeline (every function labeled + user input markers)")
    print("   - Page 2: Function transitions (with user input)")
    print("   - Page 3: Blocking analysis (with user input)")
    print("   - Page 4: Handoff patterns")
    print("   - Page 5: State distribution")
    print("   - Page 6: Function hierarchy (parent→child relationships)")
    print("   - Page 7: All functions coverage (stock-like graph)")
    print("   - Page 8: Event propagation (user input flow)")
    print("   DYNAMIC PAGES:")
    print("   - One page per user message detected (±10s discovery window)")
    print("   - One page per permission prompt detected (±10s discovery window)")
    print(f"\n💾 Data: /tmp/opencli_detailed_data.json")
    print("   Includes: user_events, user_messages, permission_prompts,")
    print("             function_line_executions, state_hierarchy,")
    print("             event_propagation, function_hierarchy,")
    print("             blocking_hierarchy, all_functions, call_chains")
    print("\nOpen PDF: open", args.output)


if __name__ == '__main__':
    main()
