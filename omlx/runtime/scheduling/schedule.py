# SPDX-License-Identifier: Apache-2.0
"""
ExecutionSchedule for OMLX Scheduling subsystem.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
from .group import ExecutionGroup
from .diagnostics import SchedulingDiagnostics
from .statistics import SchedulingStatistics

@dataclass(frozen=True)
class ExecutionSchedule:
    """Immutable canonical scheduling artifact."""
    ordered_operations: Tuple[str, ...] = field(default_factory=tuple)
    dependency_levels: Dict[str, int] = field(default_factory=dict)
    execution_groups: Tuple[ExecutionGroup, ...] = field(default_factory=tuple)
    critical_path: Tuple[str, ...] = field(default_factory=tuple)
    ready_queues: Dict[int, Tuple[str, ...]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    diagnostics: Optional[SchedulingDiagnostics] = None
    statistics: Optional[SchedulingStatistics] = None
