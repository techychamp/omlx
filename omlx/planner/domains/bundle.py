from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from .memory.artifacts import MemoryPlan
from omlx.framework.cache.plan import CachePlan
from .fusion.artifacts import FusionPlan
from .diffusion.artifacts import DiffusionPlan
from .moe.artifacts import MoEPlan
from .batch.artifacts import BatchPlan
from omlx.planner.plan import ExecutionPlan
class VerificationPlan:
    pass

from .speculation.artifacts import SpeculativeExecutionDescriptor, SpeculativeExecutionGraph

from omlx.planner.device.artifacts import DevicePlan

@dataclass
class PlanningBundle:
    """
    Immutable composition of all planning artifacts from different Planning Domains.
    Runtime consumes this bundle.
    """
    execution_plan: Optional['ExecutionPlan'] = None
    memory_plan: Optional[MemoryPlan] = None
    cache_plan: Optional[CachePlan] = None
    verification_plan: Optional['VerificationPlan'] = None
    fusion_plan: Optional[FusionPlan] = None
    diffusion_plan: Optional[DiffusionPlan] = None
    moe_plan: Optional[MoEPlan] = None
    batch_plan: Optional[BatchPlan] = None
    device_plan: Optional[DevicePlan] = None
    speculation_plan: Optional[SpeculativeExecutionDescriptor] = None
    speculative_graph: Optional[SpeculativeExecutionGraph] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_plan(self, domain: str) -> Optional[Any]:
        """Dynamically fetch a plan domain."""
        return getattr(self, f"{domain}_plan", None)
