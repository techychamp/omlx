from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .policy import PlacementOptimization, AffinityOptimization, PlacementStrategy, UnifiedMemoryPolicy, ExecutionAffinityPreference

@dataclass(frozen=True)
class OptimizationDiagnostics:
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class OptimizationStatistics:
    total_placements_optimized: int = 0
    total_affinities_optimized: int = 0
    optimization_latency_ms: float = 0.0
    memory_savings_bytes: int = 0

@dataclass(frozen=True)
class AppleOptimizationReport:
    is_optimized: bool
    placements: List[PlacementOptimization] = field(default_factory=list)
    affinities: List[AffinityOptimization] = field(default_factory=list)
    placement_strategy: Optional[PlacementStrategy] = None
    memory_policy: Optional[UnifiedMemoryPolicy] = None
    affinity_preference: Optional[ExecutionAffinityPreference] = None
    diagnostics: OptimizationDiagnostics = field(default_factory=OptimizationDiagnostics)
    statistics: OptimizationStatistics = field(default_factory=OptimizationStatistics)
