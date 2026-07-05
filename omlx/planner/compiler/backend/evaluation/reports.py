from dataclasses import dataclass, field
from typing import Mapping, Sequence

@dataclass(frozen=True)
class BackendCostReport:
    """Estimated costs for backend execution."""
    estimated_latency_ms: float
    estimated_peak_memory_mb: float
    estimated_startup_time_ms: float
    cache_efficiency_score: float
    graph_complexity_score: float
    estimated_throughput_tokens_per_sec: float
    hardware_utilization_score: float

@dataclass(frozen=True)
class BackendCapabilityReport:
    """Discovered capabilities for a backend."""
    supported_execution_families: tuple[str, ...]
    supported_optimization_phases: tuple[str, ...]
    supported_cache_layouts: tuple[str, ...]
    supported_synchronization_primitives: tuple[str, ...]
    supported_quantization_methods: tuple[str, ...]
    supported_model_families: tuple[str, ...]
    supports_graph_execution: bool

@dataclass(frozen=True)
class BackendEvaluationReport:
    """Comprehensive evaluation of a backend."""
    backend_id: str
    suitability_score: float
    compatibility_score: float
    hardware_fit_score: float
    optimization_support_score: float
    cost_report: BackendCostReport
    capability_report: BackendCapabilityReport
    is_suitable: bool
    rejection_reasons: tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class BackendRecommendationReport:
    """Recommendation for a backend."""
    backend_id: str
    recommendation_score: float
    reasons: tuple[str, ...]

@dataclass(frozen=True)
class BackendSelectionReport:
    """Report generated during backend selection."""
    selected_backend_id: str
    policy_applied: str
    evaluations: Mapping[str, BackendEvaluationReport]
    recommendations: Sequence[BackendRecommendationReport]
    fallback_plan: tuple[str, ...]
