#!/usr/bin/env python3
"""
Inject Advanced Profiler into running OpenCLI process

This runs the advanced profiler in a background thread within the current process.

Usage:
    1. Start OpenCLI normally
    2. In the OpenCLI prompt, run:
       >>> exec(open('inject_advanced_profiler.py').read())
    3. The profiler will run for 2 minutes while you trigger bugs
    4. A PDF timeline graph will be generated automatically
"""

import sys
import os
import threading

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from advanced_profiler import AdvancedProfiler


def inject_and_profile(interval: float = 0.5, duration: int = 120):
    """
    Run profiler in background thread within the current process

    Args:
        interval: Sample interval in seconds (default 500ms)
        duration: Profiling duration in seconds (default 2 minutes)
    """
    print("="*80)
    print("🔬 INJECTED ADVANCED PROFILER")
    print("="*80)
    print(f"\n⏱️  Sampling every {int(interval * 1000)}ms for {duration}s")
    print(f"📊 Will capture {int(duration / interval)} samples")
    print("\n🚀 Profiler running in background...")
    print("   Continue using OpenCLI and trigger the bug")
    print(f"   Analysis will complete in {duration}s\n")

    profiler = AdvancedProfiler(sample_interval=interval, duration=duration)

    # Run profiler in background thread
    def profile_thread():
        try:
            profiler.profile()
            profiler.analyze()
            profiler.generate_pdf_timeline()
            profiler.save_raw_data()

            print("\n" + "="*80)
            print("✅ PROFILING COMPLETE - Results saved:")
            print("   📄 PDF: /tmp/opencli_profiler_timeline.pdf")
            print("   💾 Data: /tmp/opencli_profiler_data.json")
            print("="*80)
            print("\nOpen PDF with: open /tmp/opencli_profiler_timeline.pdf\n")
        except Exception as e:
            print(f"\n❌ Profiler error: {e}")
            import traceback
            traceback.print_exc()

    thread = threading.Thread(target=profile_thread, daemon=True, name="AdvancedProfiler")
    thread.start()

    print(f"✅ Profiler thread started (ID: {thread.ident})")
    print("   It will run for 2 minutes, then auto-generate PDF\n")


# Auto-run if imported/executed
if __name__ == '__main__':
    inject_and_profile()
else:
    # When imported, auto-start profiling
    inject_and_profile()
