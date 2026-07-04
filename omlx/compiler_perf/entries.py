import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from types import MappingProxyType

@dataclass(frozen=True)
class CacheEntry:
    """
    Immutable cache entry containing the compiled object and metadata.
    """
    key: str
    compiled_object: Any
    creation_timestamp: float = field(default_factory=time.time)
    last_access: float = field(default_factory=time.time)
    hit_count: int = 0
    miss_count: int = 0
    compiler_version: str = "unknown"
    cache_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    diagnostics: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def with_hit(self) -> "CacheEntry":
        """Returns a new CacheEntry with updated hit count and access time."""
        return CacheEntry(
            key=self.key,
            compiled_object=self.compiled_object,
            creation_timestamp=self.creation_timestamp,
            last_access=time.time(),
            hit_count=self.hit_count + 1,
            miss_count=self.miss_count,
            compiler_version=self.compiler_version,
            cache_metadata=self.cache_metadata,
            diagnostics=self.diagnostics
        )
