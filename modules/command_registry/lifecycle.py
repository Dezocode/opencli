"""
Command Lifecycle Management
Handles command usage tracking, statistics, and lifecycle monitoring
"""

import json
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


class CommandLifecycleManager:
    """Manages command lifecycle including usage tracking and analytics"""
    
    def __init__(self, usage_file: Path, available_commands: Dict):
        """Initialize lifecycle manager.
        
        Args:
            usage_file: Path to usage statistics storage file
            available_commands: Dictionary of available command definitions
        """
        self.usage_file = usage_file
        self.available_commands = available_commands
        self._session_stats = defaultdict(int)
        self._session_start = time.time()
        
    def record_usage(self, command: str) -> None:
        """Increment usage counter for a command.

        Args:
            command: Command name (e.g., "/model" or "model")
        """
        # Normalize command
        if not command.startswith('/'):
            command = f'/{command}'

        # Only track known commands
        if command not in self.available_commands:
            return

        # Track session stats
        self._session_stats[command] += 1

        # Load current stats
        stats = self.get_usage_stats()

        # Increment counter
        stats[command] = stats.get(command, 0) + 1

        # Save updated stats
        self._save_usage_stats(stats)

    def get_usage_stats(self) -> Dict[str, int]:
        """Load command usage statistics from file.

        Returns:
            Dict mapping command names to usage counts
        """
        if not self.usage_file.exists():
            return {}

        try:
            with open(self.usage_file) as f:
                return json.load(f)
        except Exception:
            return {}

    def get_most_used_commands(self, limit: int = 10) -> List[Dict]:
        """Get most frequently used commands.

        Args:
            limit: Maximum number of commands to return

        Returns:
            List of dicts with command info sorted by usage
        """
        usage_stats = self.get_usage_stats()

        # Build list with metadata
        commands = []
        for cmd, count in usage_stats.items():
            if cmd in self.available_commands:
                info = self.available_commands[cmd]
                commands.append({
                    'name': cmd,
                    'description': info['description'],
                    'category': info['category'],
                    'usage_count': count
                })

        # Sort by usage (descending)
        commands.sort(key=lambda x: x['usage_count'], reverse=True)

        return commands[:limit]

    def get_session_stats(self) -> Dict[str, any]:
        """Get current session statistics.
        
        Returns:
            Dictionary with session statistics
        """
        session_duration = time.time() - self._session_start
        total_commands = sum(self._session_stats.values())
        
        return {
            'duration_seconds': int(session_duration),
            'total_commands': total_commands,
            'unique_commands': len(self._session_stats),
            'commands_used': dict(self._session_stats),
            'commands_per_minute': round(total_commands / (session_duration / 60), 2) if session_duration > 0 else 0
        }

    def get_command_frequency_by_category(self) -> Dict[str, Dict]:
        """Get usage frequency grouped by command category.
        
        Returns:
            Dictionary mapping categories to usage statistics
        """
        usage_stats = self.get_usage_stats()
        category_stats = defaultdict(lambda: {'total_usage': 0, 'commands': {}})
        
        for cmd, count in usage_stats.items():
            if cmd in self.available_commands:
                category = self.available_commands[cmd].get('category', 'other')
                category_stats[category]['total_usage'] += count
                category_stats[category]['commands'][cmd] = count
                
        return dict(category_stats)

    def get_rarely_used_commands(self, threshold: int = 5) -> List[Dict]:
        """Get commands that are rarely used.
        
        Args:
            threshold: Usage count threshold below which commands are considered rarely used
            
        Returns:
            List of rarely used command information
        """
        usage_stats = self.get_usage_stats()
        rarely_used = []
        
        for cmd, info in self.available_commands.items():
            usage_count = usage_stats.get(cmd, 0)
            if usage_count < threshold:
                rarely_used.append({
                    'name': cmd,
                    'description': info['description'],
                    'category': info['category'],
                    'usage_count': usage_count
                })
                
        return sorted(rarely_used, key=lambda x: x['usage_count'])

    def get_unused_commands(self) -> List[Dict]:
        """Get commands that have never been used.
        
        Returns:
            List of unused command information
        """
        return self.get_rarely_used_commands(threshold=1)

    def get_command_usage_trend(self, days: int = 30) -> Dict[str, List]:
        """Get command usage trend over time (requires extended tracking).
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with trend data (placeholder for future implementation)
        """
        # Placeholder for future implementation with time-based tracking
        return {
            'note': 'Time-based usage tracking not yet implemented',
            'current_stats': self.get_usage_stats(),
            'session_stats': self.get_session_stats()
        }

    def export_usage_report(self) -> Dict[str, any]:
        """Export comprehensive usage report.
        
        Returns:
            Complete usage analytics report
        """
        usage_stats = self.get_usage_stats()
        session_stats = self.get_session_stats()
        category_stats = self.get_command_frequency_by_category()
        most_used = self.get_most_used_commands(limit=10)
        rarely_used = self.get_rarely_used_commands(threshold=3)
        unused = self.get_unused_commands()
        
        return {
            'report_generated': datetime.now().isoformat(),
            'summary': {
                'total_commands': len(self.available_commands),
                'commands_with_usage': len([c for c in usage_stats.values() if c > 0]),
                'total_executions': sum(usage_stats.values()),
                'session_executions': session_stats['total_commands']
            },
            'session_stats': session_stats,
            'category_breakdown': category_stats,
            'top_commands': most_used,
            'rarely_used_commands': rarely_used,
            'unused_commands': unused,
            'usage_distribution': self._calculate_usage_distribution(usage_stats)
        }

    def reset_usage_stats(self) -> None:
        """Reset all usage statistics."""
        try:
            if self.usage_file.exists():
                self.usage_file.unlink()
            self._session_stats.clear()
            self._session_start = time.time()
        except Exception as e:
            print(f"⚠️  Could not reset usage stats: {e}")

    def backup_usage_stats(self, backup_path: Optional[Path] = None) -> Path:
        """Create backup of usage statistics.
        
        Args:
            backup_path: Optional custom backup path
            
        Returns:
            Path to backup file
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.usage_file.parent / f"command_usage_backup_{timestamp}.json"
            
        try:
            if self.usage_file.exists():
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(self.usage_file, backup_path)
            return backup_path
        except Exception as e:
            print(f"⚠️  Could not backup usage stats: {e}")
            return backup_path

    def restore_usage_stats(self, backup_path: Path) -> bool:
        """Restore usage statistics from backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if restoration successful, False otherwise
        """
        try:
            if backup_path.exists():
                import shutil
                shutil.copy2(backup_path, self.usage_file)
                return True
            return False
        except Exception as e:
            print(f"⚠️  Could not restore usage stats: {e}")
            return False

    def merge_usage_stats(self, other_stats: Dict[str, int]) -> None:
        """Merge external usage statistics.
        
        Args:
            other_stats: Dictionary of usage statistics to merge
        """
        current_stats = self.get_usage_stats()
        
        for cmd, count in other_stats.items():
            if cmd in self.available_commands:
                current_stats[cmd] = current_stats.get(cmd, 0) + count
                
        self._save_usage_stats(current_stats)

    def get_command_performance_metrics(self) -> Dict[str, any]:
        """Get performance metrics for command usage.
        
        Returns:
            Dictionary with performance analytics
        """
        usage_stats = self.get_usage_stats()
        session_stats = self.get_session_stats()
        
        total_usage = sum(usage_stats.values())
        total_commands = len(self.available_commands)
        commands_used = len([c for c in usage_stats.values() if c > 0])
        
        return {
            'adoption_rate': round((commands_used / total_commands) * 100, 2) if total_commands > 0 else 0,
            'average_usage_per_command': round(total_usage / commands_used, 2) if commands_used > 0 else 0,
            'session_efficiency': round(session_stats['commands_per_minute'], 2),
            'command_diversity': round((commands_used / total_commands) * 100, 2) if total_commands > 0 else 0,
            'power_user_commands': len([c for c in usage_stats.values() if c > 10]),
            'discovery_potential': total_commands - commands_used
        }

    def get_recommendations(self) -> List[Dict]:
        """Get command usage recommendations.
        
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        usage_stats = self.get_usage_stats()
        unused = self.get_unused_commands()
        session_stats = self.get_session_stats()
        
        # Recommend unused commands based on user's current usage patterns
        user_categories = set()
        for cmd in session_stats['commands_used'].keys():
            if cmd in self.available_commands:
                user_categories.add(self.available_commands[cmd].get('category'))
        
        for cmd_info in unused[:5]:  # Top 5 unused commands
            if cmd_info['category'] in user_categories:
                recommendations.append({
                    'type': 'discover',
                    'command': cmd_info['name'],
                    'reason': f"Unused {cmd_info['category']} command that might be useful",
                    'description': cmd_info['description']
                })
        
        # Recommend efficiency improvements
        if session_stats['commands_per_minute'] < 1:
            recommendations.append({
                'type': 'efficiency',
                'command': None,
                'reason': 'Consider using command shortcuts and autocomplete',
                'description': 'Your command usage rate is low - explore faster input methods'
            })
            
        return recommendations

    def _save_usage_stats(self, stats: Dict[str, int]) -> None:
        """Save usage statistics to file.
        
        Args:
            stats: Usage statistics dictionary
        """
        try:
            self.usage_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.usage_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            # Silent failure - usage tracking is not critical
            pass

    def _calculate_usage_distribution(self, usage_stats: Dict[str, int]) -> Dict[str, int]:
        """Calculate usage distribution statistics.
        
        Args:
            usage_stats: Raw usage statistics
            
        Returns:
            Usage distribution buckets
        """
        distribution = {
            'heavy_use_10plus': 0,
            'moderate_use_3to9': 0,
            'light_use_1to2': 0,
            'unused': 0
        }
        
        all_commands = set(self.available_commands.keys())
        used_commands = set(usage_stats.keys())
        
        for cmd in all_commands:
            count = usage_stats.get(cmd, 0)
            if count >= 10:
                distribution['heavy_use_10plus'] += 1
            elif count >= 3:
                distribution['moderate_use_3to9'] += 1
            elif count >= 1:
                distribution['light_use_1to2'] += 1
            else:
                distribution['unused'] += 1
                
        return distribution


class CommandAnalytics:
    """Advanced analytics for command usage patterns"""
    
    def __init__(self, lifecycle_manager: CommandLifecycleManager):
        """Initialize analytics with lifecycle manager.
        
        Args:
            lifecycle_manager: CommandLifecycleManager instance
        """
        self.lifecycle = lifecycle_manager
        
    def analyze_usage_patterns(self) -> Dict[str, any]:
        """Analyze command usage patterns.
        
        Returns:
            Dictionary with usage pattern analysis
        """
        usage_stats = self.lifecycle.get_usage_stats()
        category_stats = self.lifecycle.get_command_frequency_by_category()
        
        # Find most and least used categories
        sorted_categories = sorted(
            category_stats.items(), 
            key=lambda x: x[1]['total_usage'], 
            reverse=True
        )
        
        return {
            'most_used_category': sorted_categories[0][0] if sorted_categories else None,
            'least_used_category': sorted_categories[-1][0] if sorted_categories else None,
            'category_diversity': len(category_stats),
            'power_user_threshold': self._calculate_power_user_threshold(usage_stats),
            'usage_concentration': self._calculate_usage_concentration(usage_stats)
        }
        
    def _calculate_power_user_threshold(self, usage_stats: Dict[str, int]) -> int:
        """Calculate threshold for power user commands."""
        if not usage_stats:
            return 0
        usage_values = list(usage_stats.values())
        return int(sum(usage_values) / len(usage_values)) if usage_values else 0
        
    def _calculate_usage_concentration(self, usage_stats: Dict[str, int]) -> float:
        """Calculate how concentrated usage is (Gini coefficient style)."""
        if not usage_stats:
            return 0.0
        values = sorted(usage_stats.values())
        n = len(values)
        total = sum(values)
        if total == 0:
            return 0.0
        cumulative = 0
        gini_sum = 0
        for i, value in enumerate(values):
            cumulative += value
            gini_sum += (2 * (i + 1) - n - 1) * value
        return gini_sum / (n * total) if total > 0 else 0.0