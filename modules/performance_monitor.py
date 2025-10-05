"""
Performance Monitor - Live CPU and bottleneck tracking
Displays real-time performance metrics beneath prompt
"""

import psutil
import threading
import time
import sys
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
        self.tokens_per_sec = 0.0

        # Token tracking for streaming performance
        self.token_timestamps = deque(maxlen=100)  # Last 100 tokens
        self.last_token_time = None

        # CPU history for trend detection
        self.cpu_history = deque(maxlen=60)  # Last 60 seconds

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
        """Background thread that updates metrics every second"""
        while not self.stop_flag.is_set():
            try:
                # Update CPU (1 second interval for accuracy)
                self.cpu_percent = self.process.cpu_percent(interval=1)
                self.cpu_history.append(self.cpu_percent)

                # Update memory
                mem_info = self.process.memory_info()
                self.memory_mb = mem_info.rss / 1024 / 1024

                # Update thread count
                self.thread_count = self.process.num_threads()

                # Calculate tokens/sec from recent history
                self._calculate_token_rate()

                # Detect hotspot (simplified - checks thread names)
                self._detect_hotspot()

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
        """Detect which component is using most CPU (simplified)"""
        # This is a simplified version - in production would use profiling
        try:
            threads = self.process.threads()
            if len(threads) > 1:
                # Multiple threads - likely async operations
                if self.cpu_percent > 50:
                    self.hotspot_function = "async_write"  # Common bottleneck
                elif self.cpu_percent > 30:
                    self.hotspot_function = "markdown_render"
                elif self.tokens_per_sec < 10 and self.tokens_per_sec > 0:
                    self.hotspot_function = "slow_streaming"
                else:
                    self.hotspot_function = "normal"
            else:
                self.hotspot_function = "idle"
        except:
            self.hotspot_function = "unknown"

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

        # Color based on CPU usage
        if self.cpu_percent > 80:
            cpu_color = "red"
            indicator = "🔴"
        elif self.cpu_percent > 50:
            cpu_color = "yellow"
            indicator = "🟡"
        else:
            cpu_color = "green"
            indicator = "🟢"

        # Trend arrow
        trend = self.get_cpu_trend()
        if trend == "rising":
            trend_arrow = "↗️"
        elif trend == "falling":
            trend_arrow = "↘️"
        else:
            trend_arrow = "→"

        # Token rate color
        if self.tokens_per_sec < 5 and self.tokens_per_sec > 0:
            token_color = "red"
        elif self.tokens_per_sec < 15:
            token_color = "yellow"
        else:
            token_color = "green"

        # Build status line
        parts = [
            f"{indicator}",
            f"CPU: [{cpu_color}]{self.cpu_percent:.1f}%[/{cpu_color}] {trend_arrow}",
            f"MEM: {self.memory_mb:.0f}MB",
            f"Threads: {self.thread_count}",
        ]

        # Add token rate if streaming
        if self.tokens_per_sec > 0:
            parts.append(f"Speed: [{token_color}]{self.tokens_per_sec:.1f} tok/s[/{token_color}]")

        # Add hotspot if significant
        if self.hotspot_function not in ["idle", "normal", "unknown"]:
            parts.append(f"Bottleneck: [red]{self.hotspot_function}[/red]")

        return " | ".join(parts)

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

        if self.cpu_percent < 30 and self.tokens_per_sec > 20:
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
