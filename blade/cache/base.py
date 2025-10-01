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
    def get(self, template_path: str) -> Optional[str]:
        """Get cached raw template content if valid"""
        pass

    @abstractmethod
    def store(self, template_path: str, content: str):
        """Store raw template content in cache"""
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
    def is_cached(self, template_path: str) -> bool:
        """Check if template is cached and valid"""
        pass


class CacheEntry:
    """Represents a cached raw template"""

    def __init__(self, content: str, mtime: float):
        self.content = content  # Raw template content
        self.mtime = mtime  # File modification time
        self.access_time = time.time()
        self.access_count = 0
