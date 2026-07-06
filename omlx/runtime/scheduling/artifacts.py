from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .diagnostics import SchedulingDiagnostics
from .statistics import SchedulingStatistics

@dataclass(frozen=True)
class SynchronizationPoint:
    name: str
    dependencies: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class DependencyBarrier:
    name: str
    dependencies: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class ExecutionPhase:
    name: str
    operations: List[str] = field(default_factory=list)
    barriers: List[DependencyBarrier] = field(default_factory=list)
    sync_points: List[SynchronizationPoint] = field(default_factory=list)

@dataclass(frozen=True)
class DependencyGraph:
    operations: Dict[str, Any] = field(default_factory=dict)
    phases: List[ExecutionPhase] = field(default_factory=list)
    barriers: List[DependencyBarrier] = field(default_factory=list)
    sync_points: List[SynchronizationPoint] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

# Aliases for Scheduler terminology
SchedulerDiagnostics = SchedulingDiagnostics
SchedulerStatistics = SchedulingStatistics
