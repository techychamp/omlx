import time
from typing import Optional, TYPE_CHECKING, Any
from types import MappingProxyType
from omlx.capabilities.descriptor import CapabilityDescriptor, ExecutionFamily
from omlx.planner.plan import ExecutionPlan
from omlx.planner.passes import PassRegistry
from omlx.planner.validation import validate_plan
from omlx.planner.compiler.cache.utils import compute_cache_key
from omlx.planner.domains.bundle import PlanningBundle
from omlx.planner.domains.memory.planner import MemoryPlanner
if TYPE_CHECKING:
    from omlx.planner.compiler.dependency_tracker import DependencyTracker
if TYPE_CHECKING:
    from omlx.planner.compiler.cache.manager import CompilerCacheManager

class CompilerPlanner:
    """
    Composes multiple Planning Domains into a single PlanningBundle.
    """
    def __init__(self, memory_planner: Optional[MemoryPlanner] = None):
        self.memory_planner = memory_planner or MemoryPlanner()

    def compose_bundle(self, descriptor: CapabilityDescriptor, execution_plan: ExecutionPlan, strategy_intent: Any = None) -> PlanningBundle:
        """
        Coordinates all planning domains to produce a PlanningBundle.
        """
        memory_plan = self.memory_planner.plan(descriptor, strategy_intent)

        return PlanningBundle(
            execution_plan=execution_plan,
            memory_plan=memory_plan
        )
