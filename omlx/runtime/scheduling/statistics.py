# SPDX-License-Identifier: Apache-2.0
"""
SchedulingStatistics for OMLX Scheduling subsystem.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class SchedulingStatistics:
    """Immutable snapshot of scheduling statistics."""
    graph_depth: int = 0
    graph_width: int = 0
    critical_path_length: int = 0
    dependency_fan_in: float = 0.0
    dependency_fan_out: float = 0.0
    parallel_groups: int = 0
    execution_levels: int = 0
    estimated_parallelism: float = 0.0
    schedule_generation_time_ms: float = 0.0
