import threading
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class CacheStatistics:
    """Tracks basic statistics for a specific cache layer."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0

    @property
    def total_requests(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    @property
    def miss_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.misses / self.total_requests

class CacheDiagnostics:
    """Thread-safe diagnostics tracker for all compiler caches."""
    def __init__(self):
        self._lock = threading.Lock()
        self._stats: Dict[str, CacheStatistics] = {}

        # Latency tracking
        self._latencies: Dict[str, float] = {
            "planner_time_ms": 0.0,
            "lowering_time_ms": 0.0,
            "translation_time_ms": 0.0,
            "graph_creation_time_ms": 0.0
        }

    def _get_stats(self, layer: str) -> CacheStatistics:
        if layer not in self._stats:
            self._stats[layer] = CacheStatistics()
        return self._stats[layer]

    def record_hit(self, layer: str) -> None:
        with self._lock:
            self._get_stats(layer).hits += 1

    def record_miss(self, layer: str) -> None:
        with self._lock:
            self._get_stats(layer).misses += 1

    def record_eviction(self, layer: str) -> None:
        with self._lock:
            self._get_stats(layer).evictions += 1

    def update_size(self, layer: str, size: int) -> None:
        with self._lock:
            self._get_stats(layer).size = size

    def record_latency(self, metric: str, duration_ms: float) -> None:
        """Record the latest latency for a compiler stage."""
        with self._lock:
            if metric in self._latencies:
                # Could implement rolling average here, keeping simple for now
                self._latencies[metric] = duration_ms

    def get_snapshot(self) -> Dict[str, Dict]:
        """Returns a snapshot of all statistics and latencies."""
        with self._lock:
            snapshot = {
                layer: {
                    "hits": stat.hits,
                    "misses": stat.misses,
                    "evictions": stat.evictions,
                    "size": stat.size,
                    "hit_rate": stat.hit_rate,
                    "miss_rate": stat.miss_rate
                } for layer, stat in self._stats.items()
            }
            snapshot["latencies"] = self._latencies.copy()
            return snapshot
