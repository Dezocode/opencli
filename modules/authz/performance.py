"""
Performance Monitoring for Authorization System - Phase 3

Tracks and reports on authorization decision performance:
- P50, P95, P99 latency
- Decision volume over time
- Cache hit rates
- Risk level distribution
"""

import time
from typing import List, Dict, Any
from dataclasses import dataclass
from collections import deque
import threading


@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    timestamp: float
    latency_ms: float
    decision_result: str
    risk_level: str
    cache_hit: bool = False


class PerformanceMonitor:
    """Monitor authorization system performance"""
    
    def __init__(self, window_size: int = 1000):
        self._window_size = window_size
        self._metrics: deque = deque(maxlen=window_size)
        self._lock = threading.Lock()
        
        # SLO targets (from Phase 3 requirements)
        self.slo_p95_cache = 3.0  # ms
        self.slo_p95_no_cache = 25.0  # ms
        self.slo_p99 = 25.0  # ms
    
    def record_decision(
        self,
        latency_ms: float,
        decision_result: str,
        risk_level: str,
        cache_hit: bool = False
    ):
        """Record a decision performance metric"""
        with self._lock:
            metric = PerformanceMetric(
                timestamp=time.time(),
                latency_ms=latency_ms,
                decision_result=decision_result,
                risk_level=risk_level,
                cache_hit=cache_hit
            )
            self._metrics.append(metric)
    
    def get_latency_percentiles(self) -> Dict[str, float]:
        """Calculate latency percentiles"""
        with self._lock:
            if not self._metrics:
                return {
                    'p50': 0.0,
                    'p95': 0.0,
                    'p99': 0.0,
                    'count': 0
                }
            
            latencies = sorted([m.latency_ms for m in self._metrics])
            count = len(latencies)
            
            return {
                'p50': latencies[int(count * 0.50)] if count > 0 else 0.0,
                'p95': latencies[int(count * 0.95)] if count > 0 else 0.0,
                'p99': latencies[int(count * 0.99)] if count > 0 else 0.0,
                'count': count
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache hit/miss statistics"""
        with self._lock:
            if not self._metrics:
                return {
                    'total': 0,
                    'hits': 0,
                    'misses': 0,
                    'hit_rate': 0.0
                }
            
            total = len(self._metrics)
            hits = sum(1 for m in self._metrics if m.cache_hit)
            misses = total - hits
            
            return {
                'total': total,
                'hits': hits,
                'misses': misses,
                'hit_rate': hits / total if total > 0 else 0.0
            }
    
    def get_risk_distribution(self) -> Dict[str, int]:
        """Get distribution of decisions by risk level"""
        with self._lock:
            distribution = {}
            for metric in self._metrics:
                risk = metric.risk_level
                distribution[risk] = distribution.get(risk, 0) + 1
            return distribution
    
    def check_slo_compliance(self) -> Dict[str, Any]:
        """Check if performance meets SLO targets"""
        percentiles = self.get_latency_percentiles()
        cache_stats = self.get_cache_stats()
        
        # Check P95 latency
        p95_meets_slo = percentiles['p95'] < self.slo_p95_no_cache
        
        # For cached requests, check stricter SLO
        cached_latencies = [m.latency_ms for m in self._metrics if m.cache_hit]
        if cached_latencies:
            p95_cached = sorted(cached_latencies)[int(len(cached_latencies) * 0.95)]
            p95_cache_meets_slo = p95_cached < self.slo_p95_cache
        else:
            p95_cache_meets_slo = True
        
        # Check P99
        p99_meets_slo = percentiles['p99'] < self.slo_p99
        
        return {
            'slo_compliant': p95_meets_slo and p99_meets_slo and p95_cache_meets_slo,
            'p95_latency': percentiles['p95'],
            'p95_slo': self.slo_p95_no_cache,
            'p95_meets_slo': p95_meets_slo,
            'p99_latency': percentiles['p99'],
            'p99_slo': self.slo_p99,
            'p99_meets_slo': p99_meets_slo,
            'cache_hit_rate': cache_stats['hit_rate']
        }
    
    def get_performance_report(self) -> str:
        """Generate human-readable performance report"""
        percentiles = self.get_latency_percentiles()
        cache_stats = self.get_cache_stats()
        risk_dist = self.get_risk_distribution()
        slo_status = self.check_slo_compliance()
        
        report = []
        report.append("\n" + "="*70)
        report.append("📊 Authorization System Performance Report")
        report.append("="*70)
        report.append("")
        
        # Latency percentiles
        report.append("⏱️  Latency Percentiles:")
        report.append(f"   P50: {percentiles['p50']:.2f}ms")
        report.append(f"   P95: {percentiles['p95']:.2f}ms (SLO: < {self.slo_p95_no_cache}ms)")
        report.append(f"   P99: {percentiles['p99']:.2f}ms (SLO: < {self.slo_p99}ms)")
        report.append(f"   Total decisions: {percentiles['count']}")
        report.append("")
        
        # Cache stats
        report.append("💾 Cache Performance:")
        report.append(f"   Hit rate: {cache_stats['hit_rate']:.1%}")
        report.append(f"   Hits: {cache_stats['hits']}")
        report.append(f"   Misses: {cache_stats['misses']}")
        report.append("")
        
        # Risk distribution
        report.append("⚠️  Risk Level Distribution:")
        for risk, count in sorted(risk_dist.items()):
            percentage = (count / percentiles['count'] * 100) if percentiles['count'] > 0 else 0
            report.append(f"   {risk}: {count} ({percentage:.1f}%)")
        report.append("")
        
        # SLO compliance
        report.append("✅ SLO Compliance:")
        status_icon = "✅" if slo_status['slo_compliant'] else "❌"
        report.append(f"   {status_icon} Overall: {'COMPLIANT' if slo_status['slo_compliant'] else 'NON-COMPLIANT'}")
        report.append(f"   {'✅' if slo_status['p95_meets_slo'] else '❌'} P95: {slo_status['p95_latency']:.2f}ms < {slo_status['p95_slo']}ms")
        report.append(f"   {'✅' if slo_status['p99_meets_slo'] else '❌'} P99: {slo_status['p99_latency']:.2f}ms < {slo_status['p99_slo']}ms")
        report.append("")
        report.append("="*70)
        report.append("")
        
        return "\n".join(report)


# Global performance monitor instance
_performance_monitor: PerformanceMonitor = None
_monitor_lock = threading.Lock()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    
    if _performance_monitor is None:
        with _monitor_lock:
            if _performance_monitor is None:
                _performance_monitor = PerformanceMonitor()
    
    return _performance_monitor


def record_authorization_decision(
    latency_ms: float,
    decision_result: str,
    risk_level: str,
    cache_hit: bool = False
):
    """Convenience function to record authorization decision performance"""
    monitor = get_performance_monitor()
    monitor.record_decision(latency_ms, decision_result, risk_level, cache_hit)


if __name__ == "__main__":
    # Example usage
    import random
    
    monitor = get_performance_monitor()
    
    # Simulate some decisions
    for i in range(100):
        latency = random.gauss(2.0, 0.5) if random.random() > 0.2 else random.gauss(15.0, 3.0)
        result = random.choice(['allow', 'deny', 'prompt'])
        risk = random.choice(['safe', 'low', 'medium', 'high'])
        cache_hit = random.random() > 0.3
        
        monitor.record_decision(latency, result, risk, cache_hit)
    
    # Print report
    print(monitor.get_performance_report())
