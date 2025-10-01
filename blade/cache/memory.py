"""
Memory Cache
In-memory cache with file modification tracking
Fast but doesn't persist across restarts
"""

import os
import time
from typing import Optional, Dict, Any

from .base import BaseCacheInterface, CacheEntry


class MemoryCache(BaseCacheInterface):
    """
    In-memory cache with file modification tracking
    Fast but doesn't persist across restarts
    """

    def __init__(self, max_size: int = 1000, ttl: int = 3600, track_mtime: bool = True):
        """
        Args:
            max_size: Maximum number of cached templates
            ttl: Time-to-live in seconds (0 = infinite)
            track_mtime: Track file modification times for auto-invalidation
        """
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.ttl = ttl
        self.track_mtime = track_mtime
        self.hits = 0
        self.misses = 0

    def _get_file_mtime(self, template_path: str) -> float:
        """Get file modification time"""
        try:
            return os.path.getmtime(template_path)
        except OSError:
            return 0.0

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        if self.ttl == 0:
            return False
        return (time.time() - entry.access_time) > self.ttl

    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.cache:
            return

        # Find LRU entry
        lru_key = min(self.cache.keys(), key=lambda k: self.cache[k].access_time)
        del self.cache[lru_key]

    def get(self, template_path: str) -> Optional[str]:
        """
        Get cached raw template if valid

        Args:
            template_path: Full path to template file

        Returns:
            Cached raw template content or None
        """
        if template_path not in self.cache:
            self.misses += 1
            return None

        entry = self.cache[template_path]

        # Check expiration
        if self._is_expired(entry):
            del self.cache[template_path]
            self.misses += 1
            return None

        # Check file modification time
        if self.track_mtime:
            current_mtime = self._get_file_mtime(template_path)
            if current_mtime != entry.mtime:
                del self.cache[template_path]
                self.misses += 1
                return None

        # Update access stats
        entry.access_time = time.time()
        entry.access_count += 1
        self.hits += 1

        return entry.content

    def store(self, template_path: str, content: str):
        """
        Store raw template in cache

        Args:
            template_path: Full path to template file
            content: Raw template content
        """
        # Evict if at capacity
        if len(self.cache) >= self.max_size:
            self._evict_lru()

        # Get file mtime
        mtime = self._get_file_mtime(template_path) if self.track_mtime else 0

        # Store entry
        self.cache[template_path] = CacheEntry(content, mtime)

    def invalidate(self, template_path: str = None):
        """
        Invalidate cache entries

        Args:
            template_path: Specific template to invalidate (None = clear all)
        """
        if template_path is None:
            self.cache.clear()
        else:
            # Remove all entries for this template
            keys_to_remove = [k for k in self.cache.keys() if k.startswith(template_path)]
            for key in keys_to_remove:
                del self.cache[key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "total_requests": total_requests,
        }

    def is_cached(self, template_path: str) -> bool:
        """Check if template is cached and valid"""
        return self.get(template_path) is not None
