# SPDX-License-Identifier: Apache-2.0
"""
Backend Evaluation.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

@dataclass(frozen=True)
class BackendEvaluationReport:
    backend_id: str
    is_compatible: bool
    estimated_latency_ms: float
    estimated_memory_mb: float
    estimated_throughput_tps: float
    estimated_startup_cost_ms: float
    cache_compatibility_score: float
    hardware_utilization_score: float
    diagnostics: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    selection_constraints: tuple[str, ...] = tuple()

    @property
    def score(self) -> float:
        # Provide a basic weighted score if requested, but policies should interpret fields directly.
        if not self.is_compatible:
            return 0.0

        score = 0.0
        # High throughput is good
        score += self.estimated_throughput_tps * 10
        # Low latency is good
        if self.estimated_latency_ms > 0:
            score += (1000 / self.estimated_latency_ms)
        # High scores are good
        score += self.cache_compatibility_score * 100
        score += self.hardware_utilization_score * 100

        return score
