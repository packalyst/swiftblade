"""
Memory Cache
In-memory cache with file modification tracking
Fast but doesn't persist across restarts
"""

import os
import time
import hashlib
import json
from typing import Optional, Dict, Any
from functools import lru_cache

from .base import BaseCacheInterface, CacheEntry
from ..constants import CACHE_KEY_SEPARATOR


# Cached helper functions (module-level for LRU cache)
@lru_cache(maxsize=2000)
def _compute_context_hash(context_str: str) -> str:
    """
    Compute hash for context string (cached)

    Uses LRU cache to avoid recomputing hashes for identical contexts.
    Particularly useful when the same context is used repeatedly.
    """
    return hashlib.sha256(context_str.encode()).hexdigest()


@lru_cache(maxsize=500)
def _get_file_mtime_cached(template_path: str) -> float:
    """
    Get file modification time (cached)

    Caches mtime checks to reduce filesystem calls.
    Cache is smaller since file mtimes change less frequently.
    """
    try:
        return os.path.getmtime(template_path)
    except OSError:
        return 0.0


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

    def _get_context_hash(self, context: Dict[str, Any]) -> str:
        """
        Generate hash from context keys AND values for cache key

        Uses cached hash computation for performance.
        """
        if not context:
            return _compute_context_hash('')

        # Sort items to ensure consistent hashing
        # Use JSON for consistent serialization of complex values
        try:
            context_str = json.dumps(context, sort_keys=True, default=str)
        except (TypeError, ValueError):
            # Fallback: convert to string representation
            items = sorted(context.items())
            context_str = str(items)

        return _compute_context_hash(context_str)

    def _get_file_mtime(self, template_path: str) -> float:
        """
        Get file modification time (uses cached function)

        Cached to reduce filesystem I/O when checking the same file repeatedly.
        """
        return _get_file_mtime_cached(template_path)

    def _make_cache_key(self, template_path: str, context: Dict[str, Any]) -> str:
        """Create unique cache key"""
        context_hash = self._get_context_hash(context)
        return f"{template_path}{CACHE_KEY_SEPARATOR}{context_hash}"

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

    def get(self, template_path: str, context: Dict[str, Any] = None) -> Optional[str]:
        """
        Get cached template if valid

        Args:
            template_path: Full path to template file
            context: Template context (for cache key)

        Returns:
            Cached content or None
        """
        context = context or {}
        cache_key = self._make_cache_key(template_path, context)

        if cache_key not in self.cache:
            self.misses += 1
            return None

        entry = self.cache[cache_key]

        # Check expiration
        if self._is_expired(entry):
            del self.cache[cache_key]
            self.misses += 1
            return None

        # Check file modification time
        if self.track_mtime:
            current_mtime = self._get_file_mtime(template_path)
            if current_mtime != entry.mtime:
                del self.cache[cache_key]
                self.misses += 1
                return None

        # Update access stats
        entry.access_time = time.time()
        entry.access_count += 1
        self.hits += 1

        return entry.content

    def store(self, template_path: str, context: Dict[str, Any], content: str):
        """
        Store rendered template in cache

        Args:
            template_path: Full path to template file
            context: Template context
            content: Rendered content
        """
        context = context or {}
        cache_key = self._make_cache_key(template_path, context)

        # Evict if at capacity
        if len(self.cache) >= self.max_size:
            self._evict_lru()

        # Get file mtime
        mtime = self._get_file_mtime(template_path) if self.track_mtime else 0

        # Store entry
        context_hash = self._get_context_hash(context)
        self.cache[cache_key] = CacheEntry(content, mtime, context_hash)

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

    def is_cached(self, template_path: str, context: Dict[str, Any] = None) -> bool:
        """Check if template is cached and valid"""
        return self.get(template_path, context) is not None
