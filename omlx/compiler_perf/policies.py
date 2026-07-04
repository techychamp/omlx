from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import time
from omlx.compiler_perf.entries import CacheEntry

class EvictionPolicy(ABC):
    """Base class for cache eviction policies."""
    @abstractmethod
    def on_put(self, key: str, entry: CacheEntry) -> None:
        pass

    @abstractmethod
    def on_get(self, key: str, entry: CacheEntry) -> None:
        pass

    @abstractmethod
    def on_remove(self, key: str) -> None:
        pass

    @abstractmethod
    def evict(self, current_entries: Dict[str, CacheEntry]) -> Optional[str]:
        """Returns the key of the entry to evict, or None if no eviction needed."""
        pass

class LRUPolicy(EvictionPolicy):
    """Least Recently Used eviction policy."""
    def on_put(self, key: str, entry: CacheEntry) -> None:
        pass

    def on_get(self, key: str, entry: CacheEntry) -> None:
        pass

    def on_remove(self, key: str) -> None:
        pass

    def evict(self, current_entries: Dict[str, CacheEntry]) -> Optional[str]:
        if not current_entries:
            return None
        return min(current_entries.items(), key=lambda x: x[1].last_access)[0]

class LFUPolicy(EvictionPolicy):
    """Least Frequently Used eviction policy."""
    def on_put(self, key: str, entry: CacheEntry) -> None:
        pass

    def on_get(self, key: str, entry: CacheEntry) -> None:
        pass

    def on_remove(self, key: str) -> None:
        pass

    def evict(self, current_entries: Dict[str, CacheEntry]) -> Optional[str]:
        if not current_entries:
            return None
        return min(current_entries.items(), key=lambda x: x[1].hit_count)[0]

class FIFOPolicy(EvictionPolicy):
    """First In First Out eviction policy."""
    def on_put(self, key: str, entry: CacheEntry) -> None:
        pass

    def on_get(self, key: str, entry: CacheEntry) -> None:
        pass

    def on_remove(self, key: str) -> None:
        pass

    def evict(self, current_entries: Dict[str, CacheEntry]) -> Optional[str]:
        if not current_entries:
            return None
        return min(current_entries.items(), key=lambda x: x[1].creation_timestamp)[0]

class TTLPolicy(EvictionPolicy):
    """Time-To-Live eviction policy (evicts based on age, doesn't force single item eviction)."""
    def __init__(self, ttl_seconds: float):
        self.ttl_seconds = ttl_seconds

    def on_put(self, key: str, entry: CacheEntry) -> None:
        pass

    def on_get(self, key: str, entry: CacheEntry) -> None:
        pass

    def on_remove(self, key: str) -> None:
        pass

    def evict(self, current_entries: Dict[str, CacheEntry]) -> Optional[str]:
        # Returns the oldest expired entry, or None
        now = time.time()
        expired = [k for k, v in current_entries.items() if now - v.creation_timestamp > self.ttl_seconds]
        if expired:
            return min(expired, key=lambda k: current_entries[k].creation_timestamp)
        return None
