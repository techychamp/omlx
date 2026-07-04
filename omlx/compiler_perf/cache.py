import threading
from typing import Dict, Optional, Any, Type
from omlx.compiler_perf.entries import CacheEntry
from omlx.compiler_perf.policies import EvictionPolicy, LRUPolicy
from omlx.compiler_perf.diagnostics import CacheDiagnostics

class CompilerCache:
    """Base class for generic thread-safe compiler caches."""
    def __init__(self,
                 name: str,
                 max_size: int = 1000,
                 policy: Optional[EvictionPolicy] = None,
                 diagnostics: Optional[CacheDiagnostics] = None):
        self.name = name
        self.max_size = max_size
        self.policy = policy or LRUPolicy()
        self.diagnostics = diagnostics

        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if entry:
                # Update hit count and policy
                updated_entry = entry.with_hit()
                self._cache[key] = updated_entry
                self.policy.on_get(key, updated_entry)

                if self.diagnostics:
                    self.diagnostics.record_hit(self.name)
                return updated_entry.compiled_object

            if self.diagnostics:
                self.diagnostics.record_miss(self.name)
            return None

    def put(self, key: str, obj: Any, metadata: Dict = None) -> None:
        with self._lock:
            # Create new entry
            from types import MappingProxyType
            meta = MappingProxyType(metadata or {})
            entry = CacheEntry(key=key, compiled_object=obj, cache_metadata=meta)

            # Handle capacity/eviction
            if key not in self._cache and len(self._cache) >= self.max_size:
                evict_key = self.policy.evict(self._cache)
                if evict_key:
                    self._remove_internal(evict_key)
                    if self.diagnostics:
                        self.diagnostics.record_eviction(self.name)

            self._cache[key] = entry
            self.policy.on_put(key, entry)

            if self.diagnostics:
                self.diagnostics.update_size(self.name, len(self._cache))

    def remove(self, key: str) -> None:
        with self._lock:
            self._remove_internal(key)

    def _remove_internal(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]
            self.policy.on_remove(key)
            if self.diagnostics:
                self.diagnostics.update_size(self.name, len(self._cache))

    def clear(self) -> None:
        with self._lock:
            keys = list(self._cache.keys())
            for k in keys:
                self._remove_internal(k)

class CapabilityCache(CompilerCache):
    def __init__(self, **kwargs):
        super().__init__(name="capability_cache", **kwargs)

class PlanCache(CompilerCache):
    def __init__(self, **kwargs):
        super().__init__(name="plan_cache", **kwargs)

class LogicalIRCache(CompilerCache):
    def __init__(self, **kwargs):
        super().__init__(name="logical_ir_cache", **kwargs)

class PhysicalIRCache(CompilerCache):
    def __init__(self, **kwargs):
        super().__init__(name="physical_ir_cache", **kwargs)

class BackendGraphCache(CompilerCache):
    def __init__(self, **kwargs):
        super().__init__(name="backend_graph_cache", **kwargs)
