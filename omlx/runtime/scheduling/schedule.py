# SPDX-License-Identifier: Apache-2.0
"""
ExecutionSchedule for OMLX Scheduling subsystem.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .group import ExecutionGroup
from .diagnostics import SchedulingDiagnostics
from .statistics import SchedulingStatistics

@dataclass(frozen=True)
class ExecutionSchedule:
    """Immutable canonical scheduling artifact."""
    ordered_operations: List[str] = field(default_factory=list)
    dependency_levels: Dict[str, int] = field(default_factory=dict)
    execution_groups: List[ExecutionGroup] = field(default_factory=list)
    critical_path: List[str] = field(default_factory=list)
    ready_queues: Dict[int, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    diagnostics: Optional[SchedulingDiagnostics] = None
    statistics: Optional[SchedulingStatistics] = None
