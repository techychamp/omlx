from abc import ABC, abstractmethod
from typing import Tuple
from .artifacts import FusionOptimizationReport
from omlx.planner.domains.fusion.artifacts import FusionPlan
from omlx.framework.graph.artifacts import GraphAnalysisReport
from omlx.framework.graph.descriptor import GraphDescriptor

class FusionCostModel(ABC):
    """
    Abstract base class for deterministic fusion cost models.
    """

    @abstractmethod
    def estimate_cost(self, plan: FusionPlan, graph: GraphDescriptor, analysis: GraphAnalysisReport) -> FusionOptimizationReport:
        """
        Estimates the cost/benefit of a given FusionPlan.
        Returns an immutable FusionOptimizationReport.
        """
        pass

class DefaultFusionCostModel(FusionCostModel):
    """
    A simple default cost model that always assumes a slight performance improvement.
    """
    def estimate_cost(self, plan: FusionPlan, graph: GraphDescriptor, analysis: GraphAnalysisReport) -> FusionOptimizationReport:
        # A simple estimation: 0.1ms latency reduction and 1024 bytes memory reduction per group
        num_groups = len(plan.groups)
        latency_reduction = num_groups * 0.1
        memory_reduction = num_groups * 1024

        is_profitable = num_groups > 0

        return FusionOptimizationReport(
            plan_id=id(plan) if not hasattr(plan, "id") else plan.id, # Assume plan has id or use obj id
            estimated_latency_reduction_ms=latency_reduction,
            estimated_memory_reduction_bytes=memory_reduction,
            is_profitable=is_profitable,
            reason="Estimated cost is better than original" if is_profitable else "No groups to fuse",
        )
