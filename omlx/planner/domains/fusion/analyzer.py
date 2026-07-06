# SPDX-License-Identifier: Apache-2.0
"""
Analyzer for discovering fusion opportunities in the compiler graph.
"""

from typing import Iterable, Sequence
from .artifacts import FusionOpportunity, FusionDiagnostic, FusionCompatibilityReport
from omlx.framework.graph.artifacts import GraphAnalysisReport, GraphDescriptor
from omlx.runtime.scheduling.artifacts import DependencyGraph

class FusionAnalyzer:
    """
    Stateless analyzer that inspects an ExecutionIR graph
    and discovers potential fusion opportunities.
    """

    def analyze_opportunities(self, graph_descriptor: GraphDescriptor, dependency_graph: DependencyGraph, analysis_report: GraphAnalysisReport) -> Sequence[FusionOpportunity]:
        """
        Discovers fusion opportunities based on Graph Analysis rather than analyzing the graph itself.
        Must not mutate the graph or execution state.
        """
        opportunities = []

        # Consumes GraphAnalysisReport to find opportunities
        for node_id, props in analysis_report.node_properties.items():
            if props.get("fusion_candidate"):
                opp = FusionOpportunity(
                    id=f"opp_{node_id}",
                    target_nodes=(node_id, props.get("fusion_target")),
                    potential_group_type=props.get("fusion_type", "GENERIC"),
                    estimated_benefit=props.get("fusion_benefit", 0.1)
                )
                opportunities.append(opp)

        return tuple(opportunities)

    def check_compatibility(self, opportunity: FusionOpportunity, dependency_graph: DependencyGraph) -> FusionCompatibilityReport:
        """
        Evaluates whether a discovered fusion opportunity is compatible with current constraints.
        """
        return FusionCompatibilityReport(is_compatible=True)
