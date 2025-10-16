#!/usr/bin/env python3
"""
Advanced Runtime Profiler - Function Call Flow & Timeline Analysis

Tracks:
- Function call handoffs between threads
- 500ms interval sampling over 2 minutes
- Generates PDF timeline graph with hierarchical activity view

Usage:
    python3 advanced_profiler.py

    Then run OpenCLI in another terminal and trigger the bug.
    After 2 minutes, a PDF report will be generated.
"""

import sys
import threading
import time
import traceback
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json

# For PDF generation - auto-install if needed
HAS_MATPLOTLIB = False
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-GUI backend
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.patches as mpatches
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
        HAS_MATPLOTLIB = True
    except Exception as e:
        print(f"⚠️  Failed to auto-install matplotlib: {e}")
        print("   PDF generation will be disabled")
        HAS_MATPLOTLIB = False


class AdvancedProfiler:
    """
    Comprehensive profiler that tracks function calls, handoffs, and generates timeline graphs
    """

    # Thread role classification (same as ThreadAnalyzer)
    THREAD_ROLES = {
        'LEAD': ['MainThread', 'asyncio', 'Textual'],
        'BACKGROUND': ['permission-buffer', 'SDK', 'worker'],
        'USER': []
    }

    # Colors for each category
    ROLE_COLORS = {
        'LEAD': '#E74C3C',      # Red - critical
        'BACKGROUND': '#3498DB', # Blue - workers
        'USER': '#2ECC71'        # Green - user threads
    }

    def __init__(self, sample_interval: float = 0.5, duration: int = 120):
        """
        Args:
            sample_interval: Sampling interval in seconds (default 500ms)
            duration: Total profiling duration in seconds (default 2 minutes)
        """
        self.sample_interval = sample_interval
        self.duration = duration
        self.samples: List[Dict] = []
        self.call_graph: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)
        self.function_timeline: Dict[str, List[Tuple[float, str, str]]] = defaultdict(list)
        self.start_time = None
        self.profiling = False

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

    def capture_sample(self) -> Dict:
        """Capture a single sample of all thread states"""
        timestamp = time.time() - self.start_time
        sample = {
            'timestamp': timestamp,
            'datetime': datetime.now().isoformat(),
            'threads': []
        }

        # Get all threads and their current state
        for thread_id, frame in sys._current_frames().items():
            thread_name = None

            # Find thread object
            for thread in threading.enumerate():
                if thread.ident == thread_id:
                    thread_name = thread.name
                    break

            if not thread_name:
                thread_name = f"Thread-{thread_id}"

            # Get stack trace
            stack = traceback.extract_stack(frame)

            if not stack:
                continue

            # Current function
            current_frame = stack[-1]
            current_function = current_frame.name
            current_file = current_frame.filename.split('/')[-1]

            # Caller (function that called this one)
            caller_function = stack[-2].name if len(stack) > 1 else None
            caller_file = stack[-2].filename.split('/')[-1] if len(stack) > 1 else None

            # Categorize
            role = self._categorize_thread(thread_name)

            # Full function identifier
            func_id = f"{thread_name}::{current_file}::{current_function}"
            caller_id = f"{thread_name}::{caller_file}::{caller_function}" if caller_function else None

            thread_info = {
                'thread_id': thread_id,
                'thread_name': thread_name,
                'role': role,
                'function': current_function,
                'file': current_file,
                'func_id': func_id,
                'caller_id': caller_id,
                'stack_depth': len(stack)
            }

            sample['threads'].append(thread_info)

            # Track function timeline
            self.function_timeline[func_id].append((timestamp, thread_name, role))

            # Track call graph (handoff)
            if caller_id and caller_id != func_id:
                self.call_graph[caller_id].append((func_id, thread_name, timestamp))

        return sample

    def profile(self):
        """Run profiling for specified duration with interval sampling"""
        self.start_time = time.time()
        self.profiling = True

        print("="*80)
        print("🔬 ADVANCED PROFILER - Function Call Flow & Timeline Analysis")
        print("="*80)
        print(f"\n⏱️  Sampling interval: {self.sample_interval}s ({int(self.sample_interval * 1000)}ms)")
        print(f"⏱️  Total duration: {self.duration}s ({self.duration // 60} minutes)")
        print(f"📊 Total samples: {int(self.duration / self.sample_interval)}")
        print("\nProfiling started. Trigger the bug in OpenCLI now...\n")

        samples_count = 0
        end_time = self.start_time + self.duration

        while time.time() < end_time:
            sample = self.capture_sample()
            self.samples.append(sample)
            samples_count += 1

            # Progress indicator
            elapsed = time.time() - self.start_time
            progress = (elapsed / self.duration) * 100
            if samples_count % 10 == 0:
                print(f"📸 Sample {samples_count} | {progress:.1f}% | {elapsed:.1f}s elapsed")

            time.sleep(self.sample_interval)

        self.profiling = False
        print(f"\n✅ Profiling complete! Captured {len(self.samples)} samples")

    def analyze(self):
        """Analyze captured data"""
        print("\n" + "="*80)
        print("📊 ANALYSIS RESULTS")
        print("="*80)

        # Function call counts
        function_calls = defaultdict(int)
        thread_activity = defaultdict(int)
        role_activity = defaultdict(int)

        for sample in self.samples:
            for thread in sample['threads']:
                function_calls[thread['func_id']] += 1
                thread_activity[thread['thread_name']] += 1
                role_activity[thread['role']] += 1

        # Top functions by call count
        print("\n🔥 TOP 10 MOST ACTIVE FUNCTIONS:")
        print("-"*80)
        sorted_funcs = sorted(function_calls.items(), key=lambda x: x[1], reverse=True)
        for func_id, count in sorted_funcs[:10]:
            print(f"   {count:4d} calls | {func_id}")

        # Thread activity
        print("\n🔄 THREAD ACTIVITY:")
        print("-"*80)
        for thread_name, count in sorted(thread_activity.items(), key=lambda x: x[1], reverse=True):
            role = self._categorize_thread(thread_name)
            print(f"   {count:4d} samples | [{role:10s}] {thread_name}")

        # Call graph summary
        print(f"\n🔗 CALL GRAPH - Function Handoffs:")
        print("-"*80)
        print(f"   Total unique callers: {len(self.call_graph)}")
        print(f"   Total handoff interactions: {sum(len(v) for v in self.call_graph.values())}")

        # Most frequent handoffs
        print("\n   Top 10 Most Frequent Handoffs:")
        handoffs = []
        for caller, callees in self.call_graph.items():
            for callee, thread, ts in callees:
                handoffs.append((caller, callee, thread))

        from collections import Counter
        handoff_counts = Counter(handoffs)
        for (caller, callee, thread), count in handoff_counts.most_common(10):
            print(f"     {count:3d}x | {caller} → {callee}")

    def generate_pdf_timeline(self, output_path: str = "/tmp/opencli_profiler_timeline.pdf"):
        """Generate PDF timeline graph showing function activity hierarchy"""
        if not HAS_MATPLOTLIB:
            print("\n⚠️  Cannot generate PDF - matplotlib not installed")
            print("   Install with: pip3 install matplotlib")
            return

        print(f"\n📄 Generating PDF timeline graph: {output_path}")

        # Prepare data for plotting
        # Group functions by role
        functions_by_role = defaultdict(list)
        for func_id in self.function_timeline.keys():
            # Determine role from first sample
            if self.function_timeline[func_id]:
                role = self.function_timeline[func_id][0][2]
                functions_by_role[role].append(func_id)

        # Create figure
        fig, ax = plt.subplots(figsize=(16, 10))

        # Y-axis: Functions grouped by role
        y_pos = 0
        y_labels = []
        y_ticks = []
        role_boundaries = []

        for role in ['LEAD', 'BACKGROUND', 'USER']:
            if role not in functions_by_role:
                continue

            role_start = y_pos
            color = self.ROLE_COLORS[role]

            for func_id in sorted(functions_by_role[role]):
                timeline = self.function_timeline[func_id]

                # Plot activity blocks for this function
                for timestamp, thread_name, _ in timeline:
                    # Draw activity bar (500ms wide)
                    rect = mpatches.Rectangle(
                        (timestamp, y_pos - 0.4),
                        self.sample_interval,
                        0.8,
                        facecolor=color,
                        alpha=0.6,
                        edgecolor='black',
                        linewidth=0.5
                    )
                    ax.add_patch(rect)

                y_labels.append(func_id.split('::')[-1][:30])  # Just function name, truncated
                y_ticks.append(y_pos)
                y_pos += 1

            role_boundaries.append((role_start, y_pos, role))

        # Draw role section separators
        for start, end, role in role_boundaries:
            ax.axhline(y=end - 0.5, color='gray', linestyle='--', linewidth=1, alpha=0.5)
            # Role label on right
            ax.text(self.duration + 1, (start + end) / 2, role,
                   rotation=0, va='center', fontsize=12, fontweight='bold',
                   color=self.ROLE_COLORS[role])

        # Formatting
        ax.set_xlim(0, self.duration)
        ax.set_ylim(-1, y_pos)
        ax.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Functions (grouped by role)', fontsize=12, fontweight='bold')
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels, fontsize=8)
        ax.set_title(
            f'OpenCLI Function Activity Timeline\n'
            f'Sampled every {int(self.sample_interval * 1000)}ms over {self.duration}s '
            f'({len(self.samples)} samples)',
            fontsize=14, fontweight='bold', pad=20
        )
        ax.grid(axis='x', alpha=0.3)

        # Legend
        legend_elements = [
            mpatches.Patch(color=self.ROLE_COLORS['LEAD'], alpha=0.6, label='LEAD (Main/Event Loop)'),
            mpatches.Patch(color=self.ROLE_COLORS['BACKGROUND'], alpha=0.6, label='BACKGROUND (Workers)'),
            mpatches.Patch(color=self.ROLE_COLORS['USER'], alpha=0.6, label='USER (Custom Threads)')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

        # Save to PDF
        plt.tight_layout()
        with PdfPages(output_path) as pdf:
            pdf.savefig(fig, dpi=150)
            plt.close()

        print(f"✅ PDF timeline graph saved: {output_path}")
        print(f"   Open with: open {output_path}")

    def save_raw_data(self, output_path: str = "/tmp/opencli_profiler_data.json"):
        """Save raw profiling data as JSON for further analysis"""
        data = {
            'config': {
                'sample_interval': self.sample_interval,
                'duration': self.duration,
                'total_samples': len(self.samples)
            },
            'samples': self.samples,
            'call_graph': {k: list(v) for k, v in self.call_graph.items()},
            'function_timeline': {k: list(v) for k, v in self.function_timeline.items()}
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"💾 Raw profiling data saved: {output_path}")


def main():
    """Main entry point"""
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Advanced OpenCLI Runtime Profiler')
    parser.add_argument('--interval', type=float, default=0.5,
                       help='Sample interval in seconds (default: 0.5 = 500ms)')
    parser.add_argument('--duration', type=int, default=120,
                       help='Profiling duration in seconds (default: 120 = 2 minutes)')
    parser.add_argument('--output', type=str, default='/tmp/opencli_profiler_timeline.pdf',
                       help='Output PDF path')
    args = parser.parse_args()

    # Create profiler
    profiler = AdvancedProfiler(
        sample_interval=args.interval,
        duration=args.duration
    )

    # Run profiling
    try:
        profiler.profile()
    except KeyboardInterrupt:
        print("\n\n⚠️  Profiling interrupted by user")

    # Analyze results
    profiler.analyze()

    # Generate PDF timeline
    profiler.generate_pdf_timeline(args.output)

    # Save raw data
    profiler.save_raw_data()

    print("\n" + "="*80)
    print("✅ PROFILING COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
