#!/usr/bin/env python3
"""
Run OpenCLI with Detailed Profiler Injected

This script starts OpenCLI with the detailed profiler running
as a background thread. The profiler won't block the UI.

Usage:
    python3 run_with_profiler.py
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.expanduser('~/opencli'))
sys.path.insert(0, os.path.expanduser('~/.opencli'))

print("="*80)
print("🔬 DETAILED PROFILER - MAXIMUM DETAIL - OpenCLI with Background Monitoring")
print("="*80)
print()
print("Starting UPGRADED detailed profiler as background thread...")
print("You can use OpenCLI normally - profiler runs silently!")
print()
print("📊 Profiler will:")
print("  • Sample every 500ms for 2 minutes")
print("  • Track ALL threads, functions, AND USER INPUT (keypresses)")
print("  • Auto-generate 8-PAGE PDF with MAXIMUM DETAIL when done")
print("  • Show exact blocking patterns WITH user input correlation")
print()
print("🎯 To reproduce the bug:")
print("  1. Type: /local")
print("  2. When permission prompt appears, try arrow keys")
print("  3. Notice it freezes (profiler captures this)")
print("  4. Continue using OpenCLI normally")
print("  5. After 2 min, 8-page PDF opens automatically")
print()
print("📄 Output: /tmp/opencli_detailed_timeline.pdf (8 PAGES)")
print("   - Pages 1-3: Timeline graphs with cyan USER INPUT MARKERS")
print("   - Page 6: Function hierarchy (parent→child relationships)")
print("   - Page 7: All functions coverage (stock-like graph)")
print("   - Page 8: Event propagation (where your keys went)")
print()
print("━"*80)
print("Starting OpenCLI with UPGRADED profiler injected...")
print("━"*80)
print()

# Import and start profiler
from inject_detailed_profiler import inject_profiler
inject_profiler(interval=0.5, duration=120)

# Now run OpenCLI
print()
print("Loading OpenCLI...")
print()

# Import OpenCLI and run it
os.chdir(os.path.expanduser('~/.opencli'))

# Read and execute opencli.py
with open(os.path.expanduser('~/.opencli/opencli.py'), 'r') as f:
    opencli_code = f.read()

exec(opencli_code, {'__name__': '__main__', '__file__': '~/.opencli/opencli.py'})
