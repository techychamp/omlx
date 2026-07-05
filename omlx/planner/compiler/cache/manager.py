# SPDX-License-Identifier: Apache-2.0
"""
Compiler Cache Manager.
"""

import threading
from collections import OrderedDict
from typing import Any, Optional, Dict

from .interface import CompilerCacheInterface, CacheEntry
from ..dependency_tracker import DependencyTracker
from .metrics import CompilerMetrics
from .invalidation import CacheInvalidationPolicy

class CompilerCacheManager(CompilerCacheInterface):
    """Thread-safe LRU Cache for compiler artifacts."""
    def __init__(self, max_memory_bytes: int = 1024 * 1024 * 100, compiler_version: str = "v1", dependency_tracker: Optional['DependencyTracker'] = None, metrics: Optional['CompilerMetrics'] = None):
        self.max_memory_bytes = max_memory_bytes
        self.dependency_tracker = dependency_tracker
        self.metrics = metrics
        self.current_memory_bytes = 0

        # OrderedDict for LRU: items added to the end are most recently used
        self._cache: OrderedDict[str, CacheEntry[Any]] = OrderedDict()
        self._lock = threading.Lock()

        self.invalidation_policy = CacheInvalidationPolicy(compiler_version)
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[CacheEntry[Any]]:
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if self.invalidation_policy.should_invalidate(entry.version):
                    self._remove(key)
                    self.misses += 1
                    return None

                # Move to end to mark as recently used
                self._cache.move_to_end(key)
                self.hits += 1
                if self.metrics:
                    self.metrics.record_hit("cache_get")
                return entry
            self.misses += 1
            if self.metrics:
                self.metrics.record_miss("cache_get")
            return None

    def put(self, key: str, value: Any, size_bytes: int, version: str) -> None:
        with self._lock:
            if key in self._cache:
                self._remove(key)

            entry = CacheEntry(key=key, value=value, size_bytes=size_bytes, version=version)

            # If a single item is larger than the entire cache, don't cache it
            if size_bytes > self.max_memory_bytes:
                return

            # Evict if necessary
            while self._cache and self.current_memory_bytes + size_bytes > self.max_memory_bytes:
                self._evict_lru()

            self._cache[key] = entry
            self.current_memory_bytes += size_bytes

    def invalidate(self, key: str) -> None:
        keys_to_invalidate = {key}

        if self.dependency_tracker:
            keys_to_invalidate.update(self.dependency_tracker.get_downstream_dependencies(key))

        with self._lock:
            for k in keys_to_invalidate:
                if k in self._cache:
                    self._remove(k)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self.current_memory_bytes = 0

    def get_memory_usage(self) -> int:
        with self._lock:
            return self.current_memory_bytes

    def _remove(self, key: str) -> None:
        """Internal method to remove an item, assuming lock is held."""
        if key in self._cache:
            entry = self._cache.pop(key)
            self.current_memory_bytes -= entry.size_bytes

    def _evict_lru(self) -> None:
        """Internal method to evict least recently used item, assuming lock is held."""
        if self._cache:
            key, entry = self._cache.popitem(last=False) # pop from beginning (least recently used)
            self.current_memory_bytes -= entry.size_bytes
