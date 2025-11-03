#!/usr/bin/env python3
"""
Production Monitoring Dashboard - Phase 4

Real-time monitoring of authorization system in production:
- Decision volume and trends
- Performance metrics (P95, P99)
- Policy version distribution
- Error rates and anomalies
- Security alerts

Run: python scripts/monitor_authz_production.py
"""

import time
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_dashboard():
    """Print real-time dashboard"""
    from modules.authz import get_authz_manager
    from modules.authz.performance import get_performance_monitor
    from modules.authz.policy_versioning import get_policy_manager
    
    # Get managers
    authz = get_authz_manager()
    perf = get_performance_monitor()
    policy = get_policy_manager()
    
    # Clear screen
    print("\033[2J\033[H")
    
    print("="*80)
    print("🔒 AUTHORIZATION SYSTEM - PRODUCTION MONITORING")
    print("="*80)
    print()
    
    # Authorization metrics
    metrics = authz.get_metrics()
    print("📊 AUTHORIZATION DECISIONS")
    print("-"*80)
    print(f"  Total decisions:    {metrics.get('total_decisions', 0):,}")
    print(f"  Allowed:            {metrics.get('allowed', 0):,}")
    print(f"  Denied:             {metrics.get('denied', 0):,}")
    print(f"  Allow rate:         {metrics.get('allow_rate', 0):.1%}")
    print()
    
    if metrics.get('by_risk_level'):
        print("  By Risk Level:")
        for risk, count in sorted(metrics['by_risk_level'].items()):
            percentage = (count / metrics['total_decisions'] * 100) if metrics['total_decisions'] > 0 else 0
            print(f"    {risk:12s}: {count:5,} ({percentage:5.1f}%)")
        print()
    
    # Performance metrics
    percentiles = perf.get_latency_percentiles()
    slo_status = perf.check_slo_compliance()
    
    print("⏱️  PERFORMANCE METRICS")
    print("-"*80)
    
    # Latency
    p50_status = "✅" if percentiles['p50'] < 10 else "⚠️ "
    p95_status = "✅" if slo_status['p95_meets_slo'] else "❌"
    p99_status = "✅" if slo_status['p99_meets_slo'] else "❌"
    
    print(f"  {p50_status} P50 latency:    {percentiles['p50']:6.2f}ms")
    print(f"  {p95_status} P95 latency:    {percentiles['p95']:6.2f}ms  (SLO: < {slo_status['p95_slo']:.0f}ms)")
    print(f"  {p99_status} P99 latency:    {percentiles['p99']:6.2f}ms  (SLO: < {slo_status['p99_slo']:.0f}ms)")
    print()
    
    # Cache performance
    cache_stats = perf.get_cache_stats()
    cache_status = "✅" if cache_stats['hit_rate'] > 0.5 else "⚠️ "
    print(f"  {cache_status} Cache hit rate: {cache_stats['hit_rate']:.1%}")
    print(f"     Cache hits:     {cache_stats['hits']:,}")
    print(f"     Cache misses:   {cache_stats['misses']:,}")
    print()
    
    # SLO compliance
    slo_icon = "✅" if slo_status['slo_compliant'] else "❌"
    print(f"  {slo_icon} SLO Compliance: {'PASS' if slo_status['slo_compliant'] else 'FAIL'}")
    print()
    
    # Policy versions
    print("📋 POLICY VERSIONS")
    print("-"*80)
    current_version = policy.get_current_version()
    versions = policy.list_versions()
    
    for version, info in sorted(versions.items()):
        status_icon = "🟢" if info.active else "⚪"
        canary_info = f" (Canary: {info.canary_percentage:.0f}%)" if info.canary_percentage > 0 else ""
        current_marker = " ← CURRENT" if version == current_version else ""
        
        print(f"  {status_icon} {version}: {info.description[:50]}{canary_info}{current_marker}")
    print()
    
    # Recent decisions
    print("📝 RECENT DECISIONS (Last 5)")
    print("-"*80)
    decisions = authz.get_decision_log(limit=5)
    
    for i, decision in enumerate(decisions, 1):
        result_icon = "✅" if decision.allowed else "❌"
        risk_icon = {"safe": "🟢", "low": "🟡", "medium": "🟠", "high": "🔴", "critical": "💀"}.get(
            decision.risk_level.value, "⚪"
        )
        
        print(f"  {i}. {result_icon} {risk_icon} {decision.context.action[:30]:30s}")
        print(f"     Subject: {decision.context.subject.id[:20]:20s}  Risk: {decision.risk_level.value:8s}")
        print(f"     Resource: {decision.context.resource[:50]}")
        print()
    
    # System health
    print("🏥 SYSTEM HEALTH")
    print("-"*80)
    
    health_status = []
    
    # Check decision volume (should be > 0 in production)
    if metrics.get('total_decisions', 0) == 0:
        health_status.append("⚠️  No authorization decisions recorded")
    else:
        health_status.append("✅ Decision logging active")
    
    # Check performance SLO
    if slo_status['slo_compliant']:
        health_status.append("✅ Performance SLO met")
    else:
        health_status.append("❌ Performance SLO violated")
    
    # Check for anomalies (e.g., sudden deny spike)
    if metrics.get('total_decisions', 0) > 0:
        deny_rate = 1 - metrics.get('allow_rate', 1.0)
        if deny_rate > 0.5:
            health_status.append("⚠️  High deny rate detected")
        else:
            health_status.append("✅ Deny rate normal")
    
    for status in health_status:
        print(f"  {status}")
    
    print()
    print("="*80)
    print(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Press Ctrl+C to exit")
    print()


def main():
    """Run monitoring dashboard"""
    print("Starting production monitoring...")
    print("Dashboard will refresh every 5 seconds")
    print()
    
    try:
        while True:
            print_dashboard()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
