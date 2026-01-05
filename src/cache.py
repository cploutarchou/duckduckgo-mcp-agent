"""
In-memory caching implementation for search results.

This module provides a simple but effective LRU (Least Recently Used) cache
that stores search results to improve performance and reduce API calls to
DuckDuckGo. The cache includes TTL (time-to-live) support and size limits.
"""
import hashlib
import time
from typing import Any, Dict, Optional

from config import get_settings


class SearchCache:
    """
    In-memory cache for DuckDuckGo search results.

    This cache stores search results with a configurable TTL. When the TTL
    expires, cached entries are automatically considered invalid. The cache
    has a maximum size limit and will evict the oldest entry when full.

    Attributes:
        _enabled: Whether caching is enabled.
        _ttl: Time-to-live for cache entries in seconds.
        _max_size: Maximum number of entries to store.
        _cache: Dictionary storing cached search results.
    """

    def __init__(self) -> None:
        """Initialize the cache with settings from configuration."""
        self.settings = get_settings()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._enabled = self.settings.cache_enabled
        self._ttl = self.settings.cache_ttl
        self._max_size = self.settings.cache_max_size

    def _generate_key(self, query: str, max_results: int) -> str:
        """
        Generate a unique cache key for a search query.

        Args:
            query: The search query string.
            max_results: The maximum number of results requested.

        Returns:
            A MD5 hash of the query and max_results as the cache key.
        """
        content = f"{query}:{max_results}"
        return hashlib.md5(content.encode()).hexdigest()

    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """
        Check whether a cache entry has exceeded its TTL.

        Args:
            entry: The cache entry to check.

        Returns:
            True if the entry's TTL has expired, False otherwise.
        """
        return time.time() - entry["timestamp"] > self._ttl

    def _evict_oldest(self) -> None:
        """Remove the oldest cache entry when the cache is at maximum capacity."""
        if len(self._cache) >= self._max_size:
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k]["timestamp"]
            )
            del self._cache[oldest_key]

    def get(self, query: str, max_results: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached search results if available and not expired.

        Args:
            query: The search query string.
            max_results: The maximum number of results.

        Returns:
            The cached result data if found and valid, None otherwise.
        """
        if not self._enabled:
            return None

        key = self._generate_key(query, max_results)
        entry = self._cache.get(key)

        if entry is None:
            return None

        if self._is_expired(entry):
            del self._cache[key]
            return None

        return entry["data"]

    def set(self, query: str, max_results: int, data: Dict[str, Any]) -> None:
        """
        Store search results in the cache.

        Args:
            query: The search query string.
            max_results: The maximum number of results.
            data: The search result data to cache.
        """
        if not self._enabled:
            return

        self._evict_oldest()

        key = self._generate_key(query, max_results)
        self._cache[key] = {
            "data": data,
            "timestamp": time.time()
        }

    def clear(self) -> None:
        """Remove all cached entries."""
        self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics and configuration.

        Returns:
            A dictionary with cache status, size, and settings.
        """
        return {
            "enabled": self._enabled,
            "size": len(self._cache),
            "max_size": self._max_size,
            "ttl": self._ttl,
        }


# Create the global cache instance
cache = SearchCache()
