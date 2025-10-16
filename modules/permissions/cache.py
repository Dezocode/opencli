"""
Caching system for permission prompts
Response caching, TTL management, LRU eviction
"""

import json
import time
import hashlib
import threading
from typing import Dict, Optional, Any
from .enums import DEFAULT_CACHE_TTL_SECONDS, DEFAULT_MAX_CACHE_ENTRIES


class CacheManager:
    """Manages caching for permission responses (Constitution compliant)"""
    
    def __init__(self, enabled: bool = True, ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS, 
                 max_entries: int = DEFAULT_MAX_CACHE_ENTRIES):
        self._enabled = enabled
        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def generate_cache_key(self, prompt_data: Dict[str, Any]) -> str:
        """Generate cache key for permission prompt (Constitution compliant)"""
        # Create stable cache key from prompt data (excluding timestamps, etc.)
        cache_data = {
            'title': prompt_data.get('title', ''),
            'message': prompt_data.get('message', ''),
            'options': prompt_data.get('options', []),
            'type': prompt_data.get('type', 'default')
        }
        
        # Generate hash of stable data
        cache_json = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_json.encode()).hexdigest()

    def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if still valid (Constitution compliant)"""
        if not self._enabled:
            return None
            
        current_time = time.time()
        
        with self._lock:
            if cache_key not in self._cache:
                return None
            
            cached_entry = self._cache[cache_key]
            cache_time = cached_entry.get('cached_at', 0)
            
            # Check if cache is still valid
            if current_time - cache_time > self._ttl_seconds:
                # Cache expired - remove it
                del self._cache[cache_key]
                return None
            
            # Update access time for LRU behavior
            cached_entry['last_accessed'] = current_time
            return cached_entry.get('response')

    def cache_response(self, cache_key: str, response: Dict[str, Any]) -> None:
        """Cache permission response (Constitution compliant)"""
        if not self._enabled:
            return
            
        current_time = time.time()
        
        with self._lock:
            # Clean up expired entries first
            self._cleanup_expired()
            
            # Check cache size limit
            if len(self._cache) >= self._max_entries:
                # Remove oldest entry (LRU)
                self._evict_lru()
            
            # Add new cache entry
            self._cache[cache_key] = {
                'response': response,
                'cached_at': current_time,
                'last_accessed': current_time
            }
    
    def _cleanup_expired(self) -> None:
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if current_time - entry.get('cached_at', 0) > self._ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self._cache:
            return
        
        oldest_key = min(self._cache.keys(), 
                        key=lambda k: self._cache[k].get('last_accessed', 0))
        del self._cache[oldest_key]

    def clear_cache(self) -> int:
        """Clear all cached permission responses (Constitution compliant)"""
        with self._lock:
            cleared_count = len(self._cache)
            self._cache.clear()
            return cleared_count

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics (Constitution compliant)"""
        current_time = time.time()
        
        with self._lock:
            total_entries = len(self._cache)
            expired_count = 0
            oldest_access = current_time
            newest_access = 0
            
            for entry in self._cache.values():
                if current_time - entry.get('cached_at', 0) > self._ttl_seconds:
                    expired_count += 1
                
                last_accessed = entry.get('last_accessed', 0)
                oldest_access = min(oldest_access, last_accessed)
                newest_access = max(newest_access, last_accessed)
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_count,
                'valid_entries': total_entries - expired_count,
                'cache_enabled': self._enabled,
                'ttl_seconds': self._ttl_seconds,
                'max_entries': self._max_entries,
                'hit_ratio': self._calculate_hit_ratio(),
                'oldest_access_age': current_time - oldest_access if total_entries > 0 else 0,
                'newest_access_age': current_time - newest_access if total_entries > 0 else 0
            }
    
    def _calculate_hit_ratio(self) -> float:
        """Calculate cache hit ratio (requires tracking hits/misses)"""
        # This would require additional tracking in real implementation
        # For now, return 0.0 as placeholder
        return 0.0
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable caching"""
        self._enabled = enabled
        if not enabled:
            self.clear_cache()
    
    def set_ttl(self, ttl_seconds: int) -> None:
        """Set cache TTL in seconds"""
        self._ttl_seconds = max(1, ttl_seconds)
    
    def set_max_entries(self, max_entries: int) -> None:
        """Set maximum cache entries"""
        with self._lock:
            self._max_entries = max(1, max_entries)
            
            # Evict entries if we're over the new limit
            while len(self._cache) > self._max_entries:
                self._evict_lru()
    
    @property
    def enabled(self) -> bool:
        """Check if caching is enabled"""
        return self._enabled
    
    @property
    def size(self) -> int:
        """Get current cache size"""
        with self._lock:
            return len(self._cache)
    
    def get_cache_keys(self) -> list:
        """Get all cache keys"""
        with self._lock:
            return list(self._cache.keys())
    
    def remove_by_key(self, cache_key: str) -> bool:
        """Remove specific cache entry by key"""
        with self._lock:
            if cache_key in self._cache:
                del self._cache[cache_key]
                return True
            return False
    
    def get_cache_entry_info(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific cache entry"""
        with self._lock:
            if cache_key not in self._cache:
                return None
            
            entry = self._cache[cache_key]
            current_time = time.time()
            
            return {
                'cached_at': entry.get('cached_at'),
                'last_accessed': entry.get('last_accessed'),
                'age_seconds': current_time - entry.get('cached_at', 0),
                'access_age_seconds': current_time - entry.get('last_accessed', 0),
                'is_expired': current_time - entry.get('cached_at', 0) > self._ttl_seconds
            }