from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class PlacementOptimization:
    original_device: str
    optimized_device: str
    strategy: str
    reason: str

@dataclass(frozen=True)
class AffinityOptimization:
    original_affinity: str
    optimized_affinity: str
    priority_adjustment: int
    reason: str

@dataclass(frozen=True)
class AppleOptimizationPolicy:
    enable_unified_memory: bool = True
    enable_ane_offload: bool = False
    enable_amx_offload: bool = True
    target_architecture: str = "apple_silicon"
    placement_rules: Dict[str, Any] = field(default_factory=dict)
    affinity_rules: Dict[str, Any] = field(default_factory=dict)
