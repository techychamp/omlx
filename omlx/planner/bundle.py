from dataclasses import dataclass
from typing import Optional

from omlx.planner.plan import ExecutionPlan
from omlx.planner.device.artifacts import DevicePlan
from omlx.planner.domains.batch.artifacts import BatchPlan

@dataclass(frozen=True)
class CachePlan:
    pass

@dataclass(frozen=True)
class MemoryPlan:
    pass

@dataclass(frozen=True)
class VerificationPlan:
    pass

@dataclass(frozen=True)
class PlanningBundle:
    execution_plan: ExecutionPlan
    device_plan: Optional[DevicePlan] = None
    cache_plan: Optional[CachePlan] = None
    memory_plan: Optional[MemoryPlan] = None
    verification_plan: Optional[VerificationPlan] = None
    batch_plan: Optional[BatchPlan] = None
