"""
Cache Module
Template caching with memory and disk storage options
"""

from typing import Any

from .base import BaseCacheInterface, CacheEntry
from .memory import MemoryCache
from .disk import DiskCache
from ..constants import CACHE_STORAGE_MEMORY, CACHE_STORAGE_DISK


def create_cache(storage_type: str = CACHE_STORAGE_MEMORY, **kwargs: Any) -> BaseCacheInterface:
    """
    Factory function to create cache instance

    Args:
        storage_type: CACHE_STORAGE_MEMORY or CACHE_STORAGE_DISK
        **kwargs: Cache configuration options

    Returns:
        Cache instance

    Example:
        cache = create_cache(CACHE_STORAGE_MEMORY, max_size=1000, ttl=3600)
        cache = create_cache(CACHE_STORAGE_DISK, cache_dir='.cache/blade', max_size=500)
    """
    if storage_type == CACHE_STORAGE_DISK:
        return DiskCache(**kwargs)
    else:
        return MemoryCache(**kwargs)


# Backward compatibility alias
TemplateCache = MemoryCache

__all__ = [
    'BaseCacheInterface',
    'CacheEntry',
    'MemoryCache',
    'DiskCache',
    'TemplateCache',
    'create_cache',
]
