"""
Verbosity Manager - Multi-level logging and performance monitoring
Supports quiet, normal, verbose, debug, and trace modes
"""

import time
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import contextmanager


class VerbosityManager:
    """Multi-level logging system"""

    LEVELS = {
        'quiet': 0,      # Errors only
        'normal': 1,     # User-facing messages
        'verbose': 2,    # API timing, token counts
        'debug': 3,      # Message structures
        'trace': 4       # Full execution trace
    }

    def __init__(self, level: str = 'normal', app=None):
        """
        Args:
            level: Verbosity level (quiet, normal, verbose, debug, trace)
            app: Optional TUI app for output
        """
        self.level = self.LEVELS.get(level, 1)
        self.level_name = level
        self.app = app

    def set_level(self, level: str):
        """Change verbosity level"""
        self.level = self.LEVELS.get(level, 1)
        self.level_name = level

    def log(self, message: str, level: str = 'normal', end: str = '\n'):
        """
        Log message if current verbosity allows

        Args:
            message: Message to log
            level: Minimum level required to show message
            end: Line ending (default newline)
        """
        if self.LEVELS.get(level, 1) <= self.level:
            if self.app:
                self.app.write(message + end)
            else:
                print(message, end=end)

    def error(self, message: str):
        """Always show errors"""
        self.log(f"[red]❌ {message}[/red]", level='quiet')

    def info(self, message: str):
        """Show in normal mode and above"""
        self.log(message, level='normal')

    def verbose(self, message: str):
        """Show in verbose mode and above"""
        self.log(f"[dim]{message}[/dim]", level='verbose')

    def debug(self, message: str):
        """Show in debug mode and above"""
        self.log(f"[dim]🔍 DEBUG: {message}[/dim]", level='debug')

    def trace(self, message: str):
        """Show only in trace mode"""
        self.log(f"[dim]🔬 TRACE: {message}[/dim]", level='trace')

    def is_verbose(self) -> bool:
        """Check if verbose mode is enabled"""
        return self.level >= self.LEVELS['verbose']

    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.level >= self.LEVELS['debug']

    def is_trace(self) -> bool:
        """Check if trace mode is enabled"""
        return self.level >= self.LEVELS['trace']


class PerformanceMonitor:
    """Track API and tool execution performance"""

    def __init__(self, verbose_manager: Optional[VerbosityManager] = None):
        self.metrics: List[Dict] = []
        self.verbose = verbose_manager

    @contextmanager
    def measure(self, operation: str):
        """
        Context manager to measure operation duration

        Usage:
            with monitor.measure("API call"):
                result = await api_call()
        """
        start = time.time()
        start_time = datetime.now().isoformat()

        try:
            yield
        finally:
            duration = time.time() - start
            self.metrics.append({
                'operation': operation,
                'duration': duration,
                'timestamp': start_time
            })

            # Log if verbose mode
            if self.verbose and self.verbose.is_verbose():
                self.verbose.verbose(f"⏱️ {operation}: {duration:.2f}s")

    def get_stats(self) -> Dict:
        """Get performance statistics"""
        if not self.metrics:
            return {
                'total_operations': 0,
                'avg_duration': 0,
                'max_duration': 0,
                'min_duration': 0
            }

        durations = [m['duration'] for m in self.metrics]
        return {
            'total_operations': len(self.metrics),
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'recent_operations': self.metrics[-10:]  # Last 10
        }

    def get_operation_stats(self, operation: str) -> Dict:
        """Get stats for specific operation type"""
        op_metrics = [m for m in self.metrics if m['operation'] == operation]

        if not op_metrics:
            return {'count': 0}

        durations = [m['duration'] for m in op_metrics]
        return {
            'count': len(op_metrics),
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations)
        }

    def print_summary(self):
        """Print performance summary"""
        stats = self.get_stats()

        if stats['total_operations'] == 0:
            if self.verbose:
                self.verbose.info("No performance metrics collected")
            return

        if self.verbose:
            self.verbose.info("\n📊 Performance Summary:")
            self.verbose.info(f"  Total Operations: {stats['total_operations']}")
            self.verbose.info(f"  Average Duration: {stats['avg_duration']:.2f}s")
            self.verbose.info(f"  Max Duration: {stats['max_duration']:.2f}s")
            self.verbose.info(f"  Min Duration: {stats['min_duration']:.2f}s\n")

    def clear(self):
        """Clear all metrics"""
        self.metrics = []


class TokenCounter:
    """Track token usage across API calls"""

    def __init__(self, verbose_manager: Optional[VerbosityManager] = None):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
        self.verbose = verbose_manager

    def add_usage(self, prompt_tokens: int, completion_tokens: int, cost: float = 0.0):
        """Record token usage from API response"""
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_cost += cost

        if self.verbose and self.verbose.is_verbose():
            total = prompt_tokens + completion_tokens
            self.verbose.verbose(
                f"🎫 Tokens: {total:,} (prompt: {prompt_tokens:,}, completion: {completion_tokens:,})"
            )
            if cost > 0:
                self.verbose.verbose(f"💰 Cost: ${cost:.4f}")

    def get_summary(self) -> Dict:
        """Get token usage summary"""
        total = self.total_prompt_tokens + self.total_completion_tokens
        return {
            'total_tokens': total,
            'prompt_tokens': self.total_prompt_tokens,
            'completion_tokens': self.total_completion_tokens,
            'total_cost': self.total_cost
        }

    def print_summary(self):
        """Print token usage summary"""
        summary = self.get_summary()

        if self.verbose:
            self.verbose.info("\n🎫 Token Usage Summary:")
            self.verbose.info(f"  Total Tokens: {summary['total_tokens']:,}")
            self.verbose.info(f"  Prompt Tokens: {summary['prompt_tokens']:,}")
            self.verbose.info(f"  Completion Tokens: {summary['completion_tokens']:,}")
            if summary['total_cost'] > 0:
                self.verbose.info(f"  Total Cost: ${summary['total_cost']:.4f}\n")

    def clear(self):
        """Reset counters"""
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
