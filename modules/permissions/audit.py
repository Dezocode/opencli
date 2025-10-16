"""
Audit logging for permission system
Security event logging, compliance tracking, audit trail management
"""

import json
import time
import threading
from typing import Dict, List, Optional, Any
from .enums import DEFAULT_MAX_AUDIT_ENTRIES


class AuditManager:
    """Manages audit logging for permission prompts (Constitution compliant security)"""
    
    def __init__(self, enabled: bool = True, max_entries: int = DEFAULT_MAX_AUDIT_ENTRIES):
        self._enabled = enabled
        self._max_entries = max_entries
        self._audit_log: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    def log_event(self, event_type: str, task_id: str, details: Dict[str, Any] = None) -> None:
        """Add audit log entry (Constitution compliant security logging)"""
        if not self._enabled:
            return
        
        audit_entry = {
            'timestamp': time.time(),
            'event_type': event_type,  # CREATED, DISPLAYED, RESOLVED, CANCELLED, TIMEOUT, etc.
            'task_id': task_id,
            'thread_id': threading.get_ident(),
            'details': details or {}
        }
        
        with self._lock:
            self._audit_log.append(audit_entry)
            
            # Limit memory usage - remove old entries
            if len(self._audit_log) > self._max_entries:
                removed_count = len(self._audit_log) - self._max_entries
                self._audit_log = self._audit_log[-self._max_entries:]
                import sys
                sys.stderr.write(f"[PermissionManager] Audit log trimmed - removed {removed_count} old entries\n")
                sys.stderr.flush()

    def get_audit_log(self, event_type: Optional[str] = None, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit log entries with optional filtering (Constitution compliant)"""
        with self._lock:
            if not event_type and not task_id:
                return self._audit_log.copy()
            
            filtered_log = []
            for entry in self._audit_log:
                if event_type and entry['event_type'] != event_type:
                    continue
                if task_id and entry['task_id'] != task_id:
                    continue
                filtered_log.append(entry)
            
            return filtered_log

    def export_audit_log(self, format: str = 'json') -> str:
        """Export audit log for security analysis (Constitution compliant)"""
        with self._lock:
            if format.lower() == 'json':
                return json.dumps(self._audit_log, indent=2)
            elif format.lower() == 'csv':
                # Simple CSV format
                lines = ['timestamp,event_type,task_id,thread_id,details']
                for entry in self._audit_log:
                    details_str = json.dumps(entry['details']).replace(',', ';')  # Escape commas
                    line = f"{entry['timestamp']},{entry['event_type']},{entry['task_id']},{entry['thread_id']},{details_str}"
                    lines.append(line)
                return '\n'.join(lines)
            else:
                raise ValueError(f"Unsupported export format: {format}")
    
    def get_audit_stats(self) -> Dict[str, Any]:
        """Get audit logging statistics"""
        with self._lock:
            total_entries = len(self._audit_log)
            
            # Count by event type
            event_counts = {}
            thread_counts = {}
            
            if self._audit_log:
                oldest_timestamp = min(entry['timestamp'] for entry in self._audit_log)
                newest_timestamp = max(entry['timestamp'] for entry in self._audit_log)
                timespan = newest_timestamp - oldest_timestamp
                
                for entry in self._audit_log:
                    event_type = entry['event_type']
                    thread_id = entry['thread_id']
                    
                    event_counts[event_type] = event_counts.get(event_type, 0) + 1
                    thread_counts[thread_id] = thread_counts.get(thread_id, 0) + 1
            else:
                timespan = 0
            
            return {
                'total_entries': total_entries,
                'enabled': self._enabled,
                'max_entries': self._max_entries,
                'event_type_counts': event_counts,
                'thread_counts': thread_counts,
                'timespan_seconds': timespan,
                'entries_per_second': total_entries / max(1, timespan)
            }
    
    def clear_audit_log(self) -> int:
        """Clear all audit log entries"""
        with self._lock:
            cleared_count = len(self._audit_log)
            self._audit_log.clear()
            return cleared_count
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable audit logging"""
        self._enabled = enabled
    
    @property
    def enabled(self) -> bool:
        """Check if audit logging is enabled"""
        return self._enabled
    
    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent audit events"""
        with self._lock:
            return self._audit_log[-limit:] if self._audit_log else []
    
    def search_events(self, **criteria) -> List[Dict[str, Any]]:
        """Search audit events by criteria"""
        with self._lock:
            results = []
            
            for entry in self._audit_log:
                match = True
                
                for key, value in criteria.items():
                    if key not in entry:
                        match = False
                        break
                    
                    if isinstance(value, str) and value.startswith('*'):
                        # Wildcard search
                        pattern = value[1:]
                        if pattern not in str(entry[key]):
                            match = False
                            break
                    elif entry[key] != value:
                        match = False
                        break
                
                if match:
                    results.append(entry)
            
            return results