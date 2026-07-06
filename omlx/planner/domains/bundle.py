from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from .memory.artifacts import MemoryPlan
from .fusion.artifacts import FusionPlan
from .moe.artifacts import MoEPlan

@dataclass(frozen=True)
class PlanningBundle:
    """
    Immutable composition of all planning artifacts from different Planning Domains.
    Runtime consumes this bundle.
    """
    execution_plan: Optional[Any] = None # Will be properly typed when ExecutionPlan is moved
    memory_plan: Optional[MemoryPlan] = None
    cache_plan: Optional[Any] = None # Placeholder for future CachePlan
    verification_plan: Optional[Any] = None # Placeholder for future VerificationPlan
    fusion_plan: Optional[FusionPlan] = None
    moe_plan: Optional[MoEPlan] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
