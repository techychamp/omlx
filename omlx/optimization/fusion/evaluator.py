from .artifacts import FusionOptimizationDecision, FusionOptimizationStatistics, FusionOptimizationDiagnostic
from .cost_model import FusionCostModel, DefaultFusionCostModel
from .policy import FusionOptimizationPolicy, DefaultFusionPolicy
from omlx.planner.domains.fusion.artifacts import FusionPlan
from omlx.framework.graph.artifacts import GraphAnalysisReport
from omlx.framework.graph.descriptor import GraphDescriptor
from typing import Tuple

class FusionEvaluator:
    """
    Coordinates cost estimation and policy evaluation to decide which
    FusionPlans should be realized.
    """
    def __init__(self, cost_model: FusionCostModel = None, policy: FusionOptimizationPolicy = None):
        self.cost_model = cost_model or DefaultFusionCostModel()
        self.policy = policy or DefaultFusionPolicy()

    def evaluate_plan(self, plan: FusionPlan, graph: GraphDescriptor, analysis: GraphAnalysisReport) -> FusionOptimizationDecision:
        """
        Evaluates a single FusionPlan.
        """
        report = self.cost_model.estimate_cost(plan, graph, analysis)
        decision = self.policy.evaluate(plan, report)
        return decision

    def evaluate_plans(self, plans: Tuple[FusionPlan, ...], graph: GraphDescriptor, analysis: GraphAnalysisReport) -> Tuple[Tuple[FusionOptimizationDecision, ...], FusionOptimizationStatistics]:
        """
        Evaluates multiple FusionPlans and aggregates statistics.
        """
        decisions = []
        accepted = 0
        rejected = 0
        total_latency_saved = 0.0
        total_memory_saved = 0

        for plan in plans:
            decision = self.evaluate_plan(plan, graph, analysis)
            decisions.append(decision)

            if decision.accepted:
                accepted += 1
                total_latency_saved += decision.report.estimated_latency_reduction_ms
                total_memory_saved += decision.report.estimated_memory_reduction_bytes
            else:
                rejected += 1

        stats = FusionOptimizationStatistics(
            total_plans_evaluated=len(plans),
            plans_accepted=accepted,
            plans_rejected=rejected,
            total_estimated_latency_saved_ms=total_latency_saved,
            total_estimated_memory_saved_bytes=total_memory_saved
        )

        return tuple(decisions), stats
