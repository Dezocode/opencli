"""
Analytics and metrics tracking for permission system
Performance monitoring, response time tracking, usage statistics
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from .enums import DEFAULT_MAX_RESPONSE_TIMES


class AnalyticsManager:
    """Tracks analytics and metrics for permission prompts (Constitution compliant)"""
    
    def __init__(self, enabled: bool = True, max_response_times: int = DEFAULT_MAX_RESPONSE_TIMES):
        self._enabled = enabled
        self._max_response_times = max_response_times
        self._metrics = self._initialize_metrics()
        self._response_times: List[float] = []
    
    def _initialize_metrics(self) -> Dict[str, Any]:
        """Initialize metrics tracking (Constitution compliant)"""
        return {
            'total_prompts': 0,
            'resolved_prompts': 0,
            'cancelled_prompts': 0,
            'auto_dismissed_prompts': 0,
            'escalated_prompts': 0,
            'cached_responses_used': 0,
            'average_response_time': 0.0,
            'min_response_time': float('inf'),
            'max_response_time': 0.0,
            'total_response_time': 0.0,
            'concurrent_prompt_peaks': 0,
            'queue_overflow_events': 0,
            'validation_failures': 0,
            'i18n_translations_used': 0,
            'accessibility_features_used': 0,
            'memory_cleanup_events': 0,
            'priority_escalations': 0,
            'timeout_events': 0,
            'started_at': datetime.now().isoformat()
        }
    
    def update_analytics(self, event_type: str, task=None, details: Dict[str, Any] = None) -> None:
        """Update analytics tracking (Constitution compliant)"""
        if not self._enabled:
            return
        
        current_time = time.time()
        
        # Update basic counters
        if event_type == 'prompt_created':
            self._metrics['total_prompts'] += 1
            
        elif event_type == 'prompt_resolved':
            self._metrics['resolved_prompts'] += 1
            if task and hasattr(task, 'created_at'):
                response_time = current_time - task.created_at
                self._add_response_time(response_time)
                
        elif event_type == 'prompt_cancelled':
            self._metrics['cancelled_prompts'] += 1
            
        elif event_type == 'prompt_auto_dismissed':
            self._metrics['auto_dismissed_prompts'] += 1
            
        elif event_type == 'prompt_escalated':
            self._metrics['escalated_prompts'] += 1
            self._metrics['priority_escalations'] += 1
            
        elif event_type == 'cached_response_used':
            self._metrics['cached_responses_used'] += 1
            
        elif event_type == 'concurrent_peak':
            if details and 'count' in details:
                self._metrics['concurrent_prompt_peaks'] = max(
                    self._metrics['concurrent_prompt_peaks'],
                    details['count']
                )
                
        elif event_type == 'queue_overflow':
            self._metrics['queue_overflow_events'] += 1
            
        elif event_type == 'validation_failure':
            self._metrics['validation_failures'] += 1
            
        elif event_type == 'i18n_translation':
            self._metrics['i18n_translations_used'] += 1
            
        elif event_type == 'accessibility_used':
            self._metrics['accessibility_features_used'] += 1
            
        elif event_type == 'memory_cleanup':
            self._metrics['memory_cleanup_events'] += 1
            
        elif event_type == 'timeout_event':
            self._metrics['timeout_events'] += 1
        
        # Update response time statistics
        self._update_response_time_stats()
    
    def _add_response_time(self, response_time: float) -> None:
        """Add response time to tracking"""
        self._response_times.append(response_time)
        
        # Keep only the last N response times
        if len(self._response_times) > self._max_response_times:
            self._response_times = self._response_times[-self._max_response_times:]
        
        # Update total response time
        self._metrics['total_response_time'] += response_time
        
        # Update min/max
        self._metrics['min_response_time'] = min(self._metrics['min_response_time'], response_time)
        self._metrics['max_response_time'] = max(self._metrics['max_response_time'], response_time)
    
    def _update_response_time_stats(self) -> None:
        """Update response time statistics"""
        if not self._response_times:
            return
        
        # Calculate average from recent response times
        self._metrics['average_response_time'] = sum(self._response_times) / len(self._response_times)
    
    def get_analytics_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report (Constitution compliant)"""
        if not self._enabled:
            return {'analytics_disabled': True}
        
        report = self._metrics.copy()
        
        # Calculate additional statistics
        total_prompts = self._metrics['total_prompts']
        if total_prompts > 0:
            report['resolution_rate'] = self._metrics['resolved_prompts'] / total_prompts
            report['cancellation_rate'] = self._metrics['cancelled_prompts'] / total_prompts
            report['auto_dismiss_rate'] = self._metrics['auto_dismissed_prompts'] / total_prompts
            report['escalation_rate'] = self._metrics['escalated_prompts'] / total_prompts
            
            if self._metrics['cached_responses_used'] > 0:
                report['cache_hit_rate'] = self._metrics['cached_responses_used'] / total_prompts
            else:
                report['cache_hit_rate'] = 0.0
        else:
            report.update({
                'resolution_rate': 0.0,
                'cancellation_rate': 0.0,
                'auto_dismiss_rate': 0.0,
                'escalation_rate': 0.0,
                'cache_hit_rate': 0.0
            })
        
        # Response time percentiles (if we have data)
        if self._response_times:
            sorted_times = sorted(self._response_times)
            count = len(sorted_times)
            
            report['response_time_percentiles'] = {
                'p50': sorted_times[int(count * 0.5)],
                'p75': sorted_times[int(count * 0.75)],
                'p90': sorted_times[int(count * 0.9)],
                'p95': sorted_times[int(count * 0.95)],
                'p99': sorted_times[int(count * 0.99)] if count >= 100 else sorted_times[-1]
            }
            
            # Calculate standard deviation
            mean = report['average_response_time']
            variance = sum((t - mean) ** 2 for t in self._response_times) / count
            report['response_time_std_dev'] = variance ** 0.5
        
        # System performance metrics
        report['performance_score'] = self._calculate_performance_score()
        report['system_health'] = self._assess_system_health()
        
        # Uptime calculation
        started_at = datetime.fromisoformat(self._metrics['started_at'])
        uptime_seconds = (datetime.now() - started_at).total_seconds()
        report['uptime_seconds'] = uptime_seconds
        report['uptime_formatted'] = self._format_uptime(uptime_seconds)
        
        return report
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        if self._metrics['total_prompts'] == 0:
            return 100.0
        
        # Factors that contribute to performance score
        resolution_rate = self._metrics['resolved_prompts'] / self._metrics['total_prompts']
        cancellation_penalty = min(0.3, self._metrics['cancelled_prompts'] / self._metrics['total_prompts'])
        timeout_penalty = min(0.2, self._metrics['timeout_events'] / max(1, self._metrics['total_prompts']))
        overflow_penalty = min(0.2, self._metrics['queue_overflow_events'] / 10)
        validation_penalty = min(0.1, self._metrics['validation_failures'] / max(1, self._metrics['total_prompts']))
        
        # Response time factor (faster is better)
        response_time_factor = 1.0
        if self._metrics['average_response_time'] > 0:
            # Optimal response time is around 1 second
            optimal_time = 1.0
            actual_time = self._metrics['average_response_time']
            response_time_factor = max(0.5, min(1.0, optimal_time / actual_time))
        
        # Calculate score
        base_score = resolution_rate * 100
        penalties = (cancellation_penalty + timeout_penalty + overflow_penalty + validation_penalty) * 100
        response_bonus = (response_time_factor - 0.5) * 20  # Up to 10 point bonus for fast response
        
        score = max(0, min(100, base_score - penalties + response_bonus))
        return round(score, 2)
    
    def _assess_system_health(self) -> str:
        """Assess overall system health"""
        score = self._calculate_performance_score()
        
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good" 
        elif score >= 60:
            return "fair"
        elif score >= 40:
            return "poor"
        else:
            return "critical"
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human readable format"""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
        else:
            days = seconds / 86400
            return f"{days:.1f} days"
    
    def export_analytics(self, format: str = 'json') -> str:
        """Export analytics data in specified format (Constitution compliant)"""
        if not self._enabled:
            return '{"error": "Analytics disabled"}'
        
        data = self.get_analytics_report()
        
        if format.lower() == 'json':
            return json.dumps(data, indent=2, default=str)
        elif format.lower() == 'csv':
            return self._export_as_csv(data)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_as_csv(self, data: Dict[str, Any]) -> str:
        """Export analytics as CSV format"""
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Metric', 'Value'])
        
        # Write metrics
        for key, value in data.items():
            if isinstance(value, dict):
                # Handle nested dictionaries (like percentiles)
                for sub_key, sub_value in value.items():
                    writer.writerow([f"{key}.{sub_key}", sub_value])
            else:
                writer.writerow([key, value])
        
        return output.getvalue()
    
    def reset_analytics(self) -> None:
        """Reset all analytics data (Constitution compliant)"""
        self._metrics = self._initialize_metrics()
        self._response_times.clear()
    
    def get_recent_response_times(self, limit: int = 10) -> List[float]:
        """Get recent response times"""
        return self._response_times[-limit:] if self._response_times else []
    
    @property
    def enabled(self) -> bool:
        """Check if analytics is enabled"""
        return self._enabled
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable analytics"""
        self._enabled = enabled