from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Tuple

from omlx.planner.domains.fusion.artifacts import FusionPlan

@dataclass(frozen=True)
class FusionOptimizationReport:
    """An immutable report outlining the profitability of a fusion plan."""
    plan_id: str
    estimated_latency_reduction_ms: float
    estimated_memory_reduction_bytes: int
    is_profitable: bool
    reason: str
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class FusionOptimizationStatistics:
    """Immutable statistics from a fusion optimization pass."""
    total_plans_evaluated: int = 0
    plans_accepted: int = 0
    plans_rejected: int = 0
    total_estimated_latency_saved_ms: float = 0.0
    total_estimated_memory_saved_bytes: int = 0
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class FusionOptimizationDiagnostic:
    """An immutable diagnostic message from the optimization pass."""
    severity: str # "INFO", "WARNING", "ERROR"
    message: str
    plan_id: str

@dataclass(frozen=True)
class FusionOptimizationDecision:
    """The immutable decision emitted by the optimization evaluator."""
    plan: FusionPlan
    accepted: bool
    report: FusionOptimizationReport
    diagnostics: Tuple[FusionOptimizationDiagnostic, ...] = field(default_factory=tuple)
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
