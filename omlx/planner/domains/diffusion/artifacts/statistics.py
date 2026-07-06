from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(frozen=True)
class DiffusionStatistics:
    """Execution statistics for diffusion."""
    planning_latency_ms: float = 0.0
    iteration_statistics: Dict[str, Any] = field(default_factory=dict)
    timestep_statistics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
