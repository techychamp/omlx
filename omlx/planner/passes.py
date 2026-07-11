from typing import Protocol
from omlx.planner.plan import ExecutionPlan
from omlx.capabilities.descriptor import CapabilityDescriptor

class PlanningPass(Protocol):
    """Protocol for an execution planning pass."""

    @property
    def name(self) -> str:
        ...

    def apply(self, plan: dict, capability_descriptor: CapabilityDescriptor) -> None:
        """Modifies the mutable plan dictionary based on capability_descriptor."""
        ...

class PassRegistry:
    """Registry for planning optimization passes."""

    def __init__(self):
        self._passes: list[PlanningPass] = []

    def register(self, planning_pass: PlanningPass) -> None:
        self._passes.append(planning_pass)

    def get_passes(self) -> list[PlanningPass]:
        return self._passes.copy()
