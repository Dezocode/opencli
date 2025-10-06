"""
Performance Monitor - Live CPU and bottleneck tracking
Displays real-time performance metrics beneath prompt
"""

import psutil
import threading
import time
import sys
import traceback
from collections import deque
from datetime import datetime


class PerformanceMonitor:
    """Real-time performance monitoring with live statusline display"""

    def __init__(self):
        self.enabled = False
        self.process = psutil.Process()
        self.monitor_thread = None
        self.stop_flag = threading.Event()

        # Performance metrics
        self.cpu_percent = 0.0
        self.memory_mb = 0.0
        self.thread_count = 0
        self.hotspot_function = "idle"
        self.hotspot_location = ""  # file:line of hotspot
        self.tokens_per_sec = 0.0

        # Token tracking for streaming performance
        self.token_timestamps = deque(maxlen=100)  # Last 100 tokens
        self.last_token_time = None

        # CPU history for trend detection
        self.cpu_history = deque(maxlen=60)  # Last 60 seconds

        # CPU spike logging
        self.cpu_spikes = deque(maxlen=100)  # Last 100 spikes

    def start(self):
        """Start background monitoring thread"""
        if self.enabled:
            return  # Already running

        self.enabled = True
        self.stop_flag.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        """Stop background monitoring"""
        self.enabled = False
        self.stop_flag.set()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

    def _monitor_loop(self):
        """Background thread - LIGHTWEIGHT metrics only"""
        while not self.stop_flag.is_set():
            try:
                # Update CPU (2 second interval to reduce overhead)
                self.cpu_percent = self.process.cpu_percent(interval=2)
                self.cpu_history.append(self.cpu_percent)

                # Log CPU spikes (>11%)
                if self.cpu_percent > 11:
                    spike_info = {
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'cpu': self.cpu_percent,
                        'location': ""  # Don't profile - too expensive
                    }
                    self.cpu_spikes.append(spike_info)

                # Update memory
                mem_info = self.process.memory_info()
                self.memory_mb = mem_info.rss / 1024 / 1024

                # Update thread count
                self.thread_count = self.process.num_threads()

                # Calculate tokens/sec from recent history
                self._calculate_token_rate()

                # NO PROFILING - it's too expensive and causes the problem!
                # Just show generic status
                if self.cpu_percent > 50:
                    self.hotspot_function = "high_load"
                    self.hotspot_location = ""
                elif self.cpu_percent > 11:
                    self.hotspot_function = "elevated"
                    self.hotspot_location = ""
                else:
                    self.hotspot_function = "idle"
                    self.hotspot_location = ""

            except Exception as e:
                # Don't crash monitor on errors
                pass

    def _calculate_token_rate(self):
        """Calculate tokens per second from recent timestamps"""
        if len(self.token_timestamps) < 2:
            self.tokens_per_sec = 0.0
            return

        # Calculate rate over last 5 seconds
        now = time.time()
        recent_tokens = [t for t in self.token_timestamps if now - t <= 5.0]

        if len(recent_tokens) >= 2:
            time_span = recent_tokens[-1] - recent_tokens[0]
            if time_span > 0:
                self.tokens_per_sec = len(recent_tokens) / time_span
            else:
                self.tokens_per_sec = 0.0
        else:
            self.tokens_per_sec = 0.0

    def _detect_hotspot(self):
        """AGGRESSIVE thread profiling - ALL threads, FULL stacks, ALL files"""
        try:
            # Get ALL thread frames
            frames = sys._current_frames()

            # Profile EVERY thread with FULL stack traces
            candidates = []

            for thread_id, frame in frames.items():
                try:
                    # FULL stack trace - NO LIMIT
                    # We need to see EVERYTHING to fix the performance issue
                    stack = traceback.extract_stack(frame)
                except:
                    continue

                # Check ALL frames in stack
                for s in stack:
                    filename = s.filename.split('/')[-1]
                    location = f"{filename}:{s.lineno}"
                    function = s.name

                    # Priority 1: OpenCLI code
                    if '/opencli/' in s.filename or '/.opencli/' in s.filename:
                        candidates.append((1, function, location, s.filename))
                    # Priority 2: Python stdlib
                    elif '/lib/python' in s.filename or 'site-packages' in s.filename:
                        candidates.append((2, function, location, s.filename))
                    # Priority 3: Everything else
                    elif s.filename != '<string>':
                        candidates.append((3, function, location, s.filename))

            # Pick highest priority candidate (lowest number = most relevant)
            if candidates:
                candidates.sort(key=lambda x: x[0])
                _, function, location, full_path = candidates[0]
                self.hotspot_function = function
                self.hotspot_location = location
                return

            # Fallback: no frames found
            self.hotspot_function = f"no_code_found"
            self.hotspot_location = f"threads:{len(frames)}"

        except Exception as e:
            self.hotspot_function = f"profiler_error"
            self.hotspot_location = f"{str(e)[:25]}"

    def record_token(self):
        """Call this when a token is received/displayed"""
        now = time.time()
        self.token_timestamps.append(now)
        self.last_token_time = now

    def get_cpu_trend(self):
        """Get CPU trend: rising, falling, stable"""
        if len(self.cpu_history) < 10:
            return "warming_up"

        recent_avg = sum(list(self.cpu_history)[-10:]) / 10
        older_avg = sum(list(self.cpu_history)[:10]) / 10

        diff = recent_avg - older_avg

        if diff > 10:
            return "rising"
        elif diff < -10:
            return "falling"
        else:
            return "stable"

    def get_status_line(self):
        """Generate statusline string for display"""
        if not self.enabled:
            return ""

        # Frontier colors (subtle like top statusline)
        # Color based on CPU usage - using frontier palette
        if self.cpu_percent > 50:
            cpu_color = "#E27878"  # Frontier red (subtle)
            indicator = "⏺"
        elif self.cpu_percent > 11:
            cpu_color = "#E2A478"  # Frontier orange (subtle)
            indicator = "⏺"
        else:
            cpu_color = "#6B9E78"  # Frontier green (subtle)
            indicator = "⏺"

        # Trend arrow
        trend = self.get_cpu_trend()
        if trend == "rising":
            trend_arrow = "↗"
        elif trend == "falling":
            trend_arrow = "↘"
        else:
            trend_arrow = "→"

        # Token rate color (frontier palette)
        if self.tokens_per_sec < 5 and self.tokens_per_sec > 0:
            token_color = "#E27878"  # Frontier red
        elif self.tokens_per_sec < 15:
            token_color = "#E2A478"  # Frontier orange
        else:
            token_color = "#6B9E78"  # Frontier green

        # Build status line with dim style like top bar
        dim_color = "#5C6773"  # Frontier gray (dim)
        parts = [
            f"[{dim_color}]{indicator}[/{dim_color}]",
            f"[{dim_color}]CPU:[/{dim_color}] [{cpu_color}]{self.cpu_percent:.1f}%[/{cpu_color}] [{dim_color}]{trend_arrow}[/{dim_color}]",
            f"[{dim_color}]MEM:[/{dim_color}] [{cpu_color}]{self.memory_mb:.0f}MB[/{cpu_color}]",
            f"[{dim_color}]Threads:[/{dim_color}] [{cpu_color}]{self.thread_count}[/{cpu_color}]",
        ]

        # Add token rate if streaming
        if self.tokens_per_sec > 0:
            parts.append(f"[{dim_color}]Speed:[/{dim_color}] [{token_color}]{self.tokens_per_sec:.1f} tok/s[/{token_color}]")

        # ALWAYS show hotspot if available (even at low CPU for transparency)
        if self.hotspot_location:
            parts.append(f"[{dim_color}]Hotspot:[/{dim_color}] [#E27878]{self.hotspot_location}[/#E27878]")
        elif self.cpu_percent > 11:
            # Show function even if no location
            parts.append(f"[{dim_color}]Running:[/{dim_color}] [{cpu_color}]{self.hotspot_function}[/{cpu_color}]")

        return f" [{dim_color}]│[/{dim_color}] ".join(parts)

    def get_detailed_report(self):
        """Generate detailed performance report"""
        lines = [
            "\n📊 Performance Report",
            "=" * 60,
            "",
            f"CPU Usage: {self.cpu_percent:.1f}% ({self.get_cpu_trend()})",
            f"Memory: {self.memory_mb:.1f} MB",
            f"Threads: {self.thread_count}",
            f"Token Rate: {self.tokens_per_sec:.1f} tokens/sec",
            "",
            "CPU History (last 60s):",
        ]

        # Simple ASCII graph of CPU usage
        if self.cpu_history:
            max_cpu = max(self.cpu_history)
            for i, cpu in enumerate(list(self.cpu_history)[-30:]):  # Last 30 seconds
                bar_length = int((cpu / 100) * 40)
                bar = "█" * bar_length
                lines.append(f"  {i+1:2d}s: {bar} {cpu:.1f}%")

        lines.extend([
            "",
            f"Current Bottleneck: {self.hotspot_function}",
        ])

        if self.hotspot_location:
            lines.append(f"Hotspot Location: {self.hotspot_location}")

        # CPU Spike Log
        lines.extend([
            "",
            "🔥 CPU Spikes (>11%):",
        ])

        if self.cpu_spikes:
            # Show last 20 spikes
            for spike in list(self.cpu_spikes)[-20:]:
                location_str = f" at {spike['location']}" if spike['location'] else ""
                lines.append(f"  {spike['timestamp']} - {spike['cpu']:.1f}%{location_str}")
        else:
            lines.append("  No spikes detected")

        lines.extend([
            "",
            "💡 Optimization Tips:",
        ])

        # Add specific tips based on metrics
        if self.cpu_percent > 70:
            lines.append("  • High CPU usage detected - consider reducing write frequency")
        if self.tokens_per_sec < 10 and self.tokens_per_sec > 0:
            lines.append("  • Slow token streaming - check markdown rendering overhead")
        if self.thread_count > 50:
            lines.append("  • High thread count - check for thread leaks")
        if self.memory_mb > 500:
            lines.append("  • High memory usage - check for large result caching")

        if self.cpu_percent < 11 and self.tokens_per_sec > 20:
            lines.append("  • ✅ Performance is optimal!")

        lines.append("")
        return "\n".join(lines)


# Global instance
_monitor = None

def get_monitor():
    """Get or create global performance monitor"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor
