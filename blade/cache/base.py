"""
Cache Base Classes
Abstract base class and cache entry for template caching
"""

import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseCacheInterface(ABC):
    """Abstract base class for template cache implementations"""

    @abstractmethod
    def get(self, template_path: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Get cached template if valid"""
        pass

    @abstractmethod
    def store(self, template_path: str, context: Dict[str, Any], content: str):
        """Store rendered template in cache"""
        pass

    @abstractmethod
    def invalidate(self, template_path: str = None):
        """Invalidate cache entries"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        pass

    @abstractmethod
    def is_cached(self, template_path: str, context: Dict[str, Any] = None) -> bool:
        """Check if template is cached and valid"""
        pass


class CacheEntry:
    """Represents a cached template"""

    def __init__(self, content: str, mtime: float, context_hash: str):
        self.content = content
        self.mtime = mtime
        self.context_hash = context_hash
        self.access_time = time.time()
        self.access_count = 0
