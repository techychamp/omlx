from abc import ABC, abstractmethod
from .artifacts import FusionOptimizationReport, FusionOptimizationDecision
from omlx.planner.domains.fusion.artifacts import FusionPlan

class FusionOptimizationPolicy(ABC):
    """
    Abstract base class for a policy that decides whether to accept a fusion plan
    based on its estimated cost.
    """
    @abstractmethod
    def evaluate(self, plan: FusionPlan, report: FusionOptimizationReport) -> FusionOptimizationDecision:
        pass

class DefaultFusionPolicy(FusionOptimizationPolicy):
    """
    Accepts any fusion plan that is deemed profitable by the cost model.
    """
    def evaluate(self, plan: FusionPlan, report: FusionOptimizationReport) -> FusionOptimizationDecision:
        return FusionOptimizationDecision(
            plan=plan,
            accepted=report.is_profitable,
            report=report
        )
