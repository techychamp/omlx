# SPDX-License-Identifier: Apache-2.0
"""
Compiler Optimization Framework - Statistics
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class PassExecutionStats:
    name: str
    duration_ms: float
    success: bool
    nodes_removed: int = 0
    nodes_added: int = 0
    metadata_changes: int = 0

class StatisticsCollector:
    def record_cache_hit(self): self.cache_hits += 1
    def record_cache_miss(self): self.cache_misses += 1
    def record_parallel_execution(self): self.parallel_executions += 1

    def __init__(self):
        self._executions: List[PassExecutionStats] = []
        self._total_duration_ms: float = 0.0
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.parallel_executions: int = 0

    def record_pass_execution(
        self,
        name: str,
        duration_ms: float,
        success: bool,
        nodes_removed: int = 0,
        nodes_added: int = 0,
        metadata_changes: int = 0
    ):
        stats = PassExecutionStats(
            name=name,
            duration_ms=duration_ms,
            success=success,
            nodes_removed=nodes_removed,
            nodes_added=nodes_added,
            metadata_changes=metadata_changes
        )
        self._executions.append(stats)
        self._total_duration_ms += duration_ms

    def get_summary(self) -> Dict[str, Any]:
        successful_passes = sum(1 for e in self._executions if e.success)
        failed_passes = len(self._executions) - successful_passes
        total_nodes_removed = sum(e.nodes_removed for e in self._executions)

        cache_hit_rate = 0.0
        total_cache = self.cache_hits + self.cache_misses
        if total_cache > 0:
            cache_hit_rate = self.cache_hits / total_cache

        return {
            "total_passes_run": len(self._executions),
            "successful_passes": successful_passes,
            "failed_passes": failed_passes,
            "total_execution_time_ms": self._total_duration_ms,
            "total_nodes_removed": total_nodes_removed,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "parallel_executions": self.parallel_executions
        }

    def get_all_executions(self) -> List[PassExecutionStats]:
        return list(self._executions)
