# SPDX-License-Identifier: Apache-2.0
"""
Compiler Metrics tracking.
"""

import threading
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class StageMetrics:
    hits: int = 0
    misses: int = 0
    total_time_ms: float = 0.0
    invocations: int = 0

class CompilerMetrics:
    """Thread-safe metrics collector for the compiler pipeline."""

    def __init__(self):
        self._lock = threading.Lock()
        self._stage_metrics: Dict[str, StageMetrics] = {}

    def record_hit(self, stage: str):
        with self._lock:
            if stage not in self._stage_metrics:
                self._stage_metrics[stage] = StageMetrics()
            self._stage_metrics[stage].hits += 1

    def record_miss(self, stage: str):
        with self._lock:
            if stage not in self._stage_metrics:
                self._stage_metrics[stage] = StageMetrics()
            self._stage_metrics[stage].misses += 1

    def record_latency(self, stage: str, latency_ms: float):
        with self._lock:
            if stage not in self._stage_metrics:
                self._stage_metrics[stage] = StageMetrics()
            self._stage_metrics[stage].total_time_ms += latency_ms
            self._stage_metrics[stage].invocations += 1

    def get_metrics_snapshot(self) -> Dict[str, Dict[str, float]]:
        with self._lock:
            snapshot = {}
            for stage, metrics in self._stage_metrics.items():
                hit_rate = 0.0
                total_lookups = metrics.hits + metrics.misses
                if total_lookups > 0:
                    hit_rate = metrics.hits / total_lookups

                avg_latency = 0.0
                if metrics.invocations > 0:
                    avg_latency = metrics.total_time_ms / metrics.invocations

                snapshot[stage] = {
                    "hits": metrics.hits,
                    "misses": metrics.misses,
                    "hit_rate": hit_rate,
                    "avg_latency_ms": avg_latency,
                    "total_latency_ms": metrics.total_time_ms,
                    "invocations": metrics.invocations
                }
            return snapshot
