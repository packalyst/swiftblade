"""
Disk Cache
Disk-based cache with file modification tracking
Slower than memory but persists across restarts
"""

import os
import time
import hashlib
import json
from typing import Optional, Dict, Any
from pathlib import Path
from functools import lru_cache

from .base import BaseCacheInterface


@lru_cache(maxsize=500)
def _get_file_mtime_cached_disk(template_path: str) -> float:
    """
    Get file modification time (cached)

    Caches mtime checks to reduce filesystem calls.
    """
    try:
        return os.path.getmtime(template_path)
    except OSError:
        return 0.0


class DiskCache(BaseCacheInterface):
    """
    Disk-based cache with file modification tracking
    Slower than memory but persists across restarts
    """

    def __init__(self, cache_dir: str = ".cache/blade", max_size: int = 1000, ttl: int = 3600, track_mtime: bool = True):
        """
        Args:
            cache_dir: Directory to store cache files
            max_size: Maximum number of cached templates
            ttl: Time-to-live in seconds (0 = infinite)
            track_mtime: Track file modification times for auto-invalidation
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size = max_size
        self.ttl = ttl
        self.track_mtime = track_mtime
        self.hits = 0
        self.misses = 0
        self._index_file = self.cache_dir / "index.json"
        self._load_index()

    def _load_index(self):
        """Load cache index from disk"""
        if self._index_file.exists():
            try:
                with open(self._index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.hits = data.get('hits', 0)
                    self.misses = data.get('misses', 0)
            except Exception:
                pass

    def _save_index(self):
        """Save cache index to disk"""
        try:
            with open(self._index_file, 'w', encoding='utf-8') as f:
                json.dump({'hits': self.hits, 'misses': self.misses}, f)
        except Exception:
            pass

    def _get_file_mtime(self, template_path: str) -> float:
        """
        Get file modification time (uses cached function)

        Cached to reduce filesystem I/O when checking the same file repeatedly.
        """
        return _get_file_mtime_cached_disk(template_path)

    def _make_cache_key(self, template_path: str) -> str:
        """Create unique cache key from template path"""
        return hashlib.sha256(template_path.encode()).hexdigest()

    def _get_cache_file(self, cache_key: str) -> Path:
        """Get path to cache file"""
        return self.cache_dir / f"{cache_key}.json"

    def _is_expired(self, cache_file: Path) -> bool:
        """Check if cache file is expired"""
        if self.ttl == 0:
            return False
        try:
            age = time.time() - cache_file.stat().st_mtime
            return age > self.ttl
        except OSError:
            return True

    def _evict_lru(self):
        """Evict least recently accessed cache file"""
        cache_files = list(self.cache_dir.glob("*.json"))
        if len(cache_files) <= 1:  # Keep index file
            return

        # Sort by access time
        cache_files = [f for f in cache_files if f != self._index_file]
        if cache_files:
            oldest = min(cache_files, key=lambda f: f.stat().st_atime)
            oldest.unlink()

    def get(self, template_path: str) -> Optional[str]:
        """
        Get cached raw template if valid

        Args:
            template_path: Full path to template file

        Returns:
            Cached raw template content or None
        """
        cache_key = self._make_cache_key(template_path)
        cache_file = self._get_cache_file(cache_key)

        if not cache_file.exists():
            self.misses += 1
            return None

        # Check expiration
        if self._is_expired(cache_file):
            cache_file.unlink()
            self.misses += 1
            return None

        # Load cache entry
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                entry = json.load(f)

            # Check file modification time
            if self.track_mtime:
                current_mtime = self._get_file_mtime(template_path)
                if current_mtime != entry.get('mtime', 0):
                    cache_file.unlink()
                    self.misses += 1
                    return None

            # Update access time
            cache_file.touch()
            self.hits += 1

            return entry.get('content')

        except Exception:
            self.misses += 1
            return None

    def store(self, template_path: str, content: str):
        """
        Store raw template in cache

        Args:
            template_path: Full path to template file
            content: Raw template content
        """
        cache_key = self._make_cache_key(template_path)
        cache_file = self._get_cache_file(cache_key)

        # Evict if at capacity
        cache_files = list(self.cache_dir.glob("*.json"))
        if len(cache_files) >= self.max_size + 1:  # +1 for index file
            self._evict_lru()

        # Get file mtime
        mtime = self._get_file_mtime(template_path) if self.track_mtime else 0

        # Store entry
        entry = {
            'content': content,
            'mtime': mtime,
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(entry, f)
        except Exception:
            pass

    def invalidate(self, template_path: str = None):
        """
        Invalidate cache entries

        Args:
            template_path: Specific template to invalidate (None = clear all)
        """
        if template_path is None:
            # Clear all cache files except index
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file != self._index_file:
                    cache_file.unlink()
        else:
            # Remove all entries for this template (needs scanning all files)
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file == self._index_file:
                    continue
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        entry = json.load(f)
                    # This is imperfect - we can't easily map back to template path
                    # So we'll just clear all if any template is invalidated
                    cache_file.unlink()
                except Exception:
                    pass

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        cache_files = list(self.cache_dir.glob("*.json"))
        size = len([f for f in cache_files if f != self._index_file])

        return {
            "size": size,
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "total_requests": total_requests,
            "cache_dir": str(self.cache_dir),
        }

    def is_cached(self, template_path: str) -> bool:
        """Check if template is cached and valid"""
        return self.get(template_path) is not None
