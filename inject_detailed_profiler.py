#!/usr/bin/env python3
"""
Inject Detailed Profiler into Running OpenCLI

This script injects the detailed profiler as a background thread into
the current Python process (OpenCLI).

Usage:
    From within OpenCLI, execute:
    >>> exec(open('inject_detailed_profiler.py').read())

    Or run from command line (will inject into current process):
    python3 inject_detailed_profiler.py
"""

import sys
import os
import threading

# Add path (handle both __file__ and exec() contexts)
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Running via exec(), use home directory
    script_dir = os.path.expanduser('~/opencli')

sys.path.insert(0, script_dir)

from detailed_profiler import DetailedProfiler


def inject_profiler(interval: float = 0.1, duration: int = 120):
    """
    Inject detailed profiler into current process as background thread

    Args:
        interval: Sample interval in seconds (default 100ms for better event capture)
        duration: Profiling duration in seconds (default 2 minutes)
    """
    print("="*80)
    print("🔬 DETAILED PROFILER INJECTED")
    print("="*80)
    print(f"\n⏱️  Sampling every {int(interval * 1000)}ms for {duration}s")
    print(f"📊 Will capture {int(duration / interval)} samples")
    print("\n🎯 PROFILER RUNNING IN BACKGROUND")
    print("   You can continue using OpenCLI normally!")
    print("")
    print("To reproduce the bug:")
    print("  1. Type: /local")
    print("  2. When permission prompt appears, try arrow keys")
    print("  3. Notice it freezes (this is what we're capturing)")
    print("  4. Wait for profiler to finish (2 minutes)")
    print(f"  5. PDF will be saved to: /tmp/opencli_detailed_timeline.pdf")
    print("")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ Profiler started - continue using OpenCLI!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")

    profiler = DetailedProfiler(sample_interval=interval, duration=duration)

    def profile_thread():
        try:
            profiler.profile()

            print("\n" + "="*80)
            print("📊 Profiling complete - Generating PDF...")
            print("="*80)

            profiler.generate_detailed_pdf('/tmp/opencli_detailed_timeline.pdf')
            profiler.save_detailed_json('/tmp/opencli_detailed_data.json')

            print("\n" + "="*80)
            print("✅ DETAILED PROFILING COMPLETE - MAXIMUM DETAIL")
            print("="*80)
            print("\n📄 PDF Report (8 PAGES):")
            print("   /tmp/opencli_detailed_timeline.pdf")
            print("\n   - Page 1: Thread timeline (every function + user input markers)")
            print("   - Page 2: Function transitions (with user input)")
            print("   - Page 3: Blocking analysis (with user input)")
            print("   - Page 4: Handoff patterns")
            print("   - Page 5: State distribution")
            print("   - Page 6: Function hierarchy (parent→child relationships)")
            print("   - Page 7: All functions coverage (stock-like graph)")
            print("   - Page 8: Event propagation (user input flow)")
            print("\n💾 Raw Data:")
            print("   /tmp/opencli_detailed_data.json")
            print("   Includes: user_events, event_propagation, function_hierarchy,")
            print("             blocking_hierarchy, all_functions, call_chains")
            print("\nOpen PDF:")
            print("   open /tmp/opencli_detailed_timeline.pdf")
            print("")

            # Try to open PDF automatically
            try:
                import subprocess
                subprocess.run(['open', '/tmp/opencli_detailed_timeline.pdf'], check=False)
                print("✅ PDF opened automatically")
            except:
                pass

        except Exception as e:
            print(f"\n❌ Profiler error: {e}")
            import traceback
            traceback.print_exc()

    # Start profiler thread
    thread = threading.Thread(
        target=profile_thread,
        daemon=True,
        name="DetailedProfiler"
    )
    thread.start()

    print(f"✅ Profiler thread started (ID: {thread.ident})")
    print(f"   Monitoring will run for {duration} seconds")
    print("")


# Auto-run
if __name__ == '__main__':
    inject_profiler()
else:
    # When imported/executed, auto-start
    inject_profiler()
