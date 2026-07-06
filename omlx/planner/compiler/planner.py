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
from omlx.planner.domains.fusion.planner import FusionPlanner
from omlx.planner.domains.fusion.analyzer import FusionAnalyzer
from omlx.framework.graph.artifacts import GraphAnalysisReport
from omlx.framework.graph.descriptor import GraphDescriptor
from omlx.runtime.scheduling.artifacts import DependencyGraph
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
        self.fusion_planner = FusionPlanner(FusionAnalyzer())

    def compose_bundle(self, descriptor: CapabilityDescriptor, execution_plan: ExecutionPlan, strategy_intent: Any = None) -> PlanningBundle:
        """
        Coordinates all planning domains to produce a PlanningBundle.
        """
        memory_plan = self.memory_planner.plan(descriptor, strategy_intent)

        # In the integrated pipeline, GraphDescriptor, DependencyGraph, and GraphAnalysisReport
        # should be provided via the strategy_intent or a broader PlanningContext.
        # This fallback ensures backwards compatibility with tests that don't pass them.
        graph_descriptor = getattr(strategy_intent, 'graph_descriptor', GraphDescriptor(id="planning_graph", nodes=(), edges=()))
        dependency_graph = getattr(strategy_intent, 'dependency_graph', DependencyGraph(operations={}))
        analysis_report = getattr(strategy_intent, 'analysis_report', GraphAnalysisReport())

        fusion_plan = self.fusion_planner.plan(graph_descriptor, dependency_graph, analysis_report)

        return PlanningBundle(
            execution_plan=execution_plan,
            memory_plan=memory_plan,
            fusion_plan=fusion_plan
        )
