# SPDX-License-Identifier: Apache-2.0
"""
Planner for the fusion domain. Creates a FusionPlan based on analysis.
"""

from .artifacts import FusionPlan, FusionGroup, FusionStatistics
from .analyzer import FusionAnalyzer
from omlx.framework.graph.artifacts import GraphAnalysisReport
from omlx.framework.graph.descriptor import GraphDescriptor
from omlx.runtime.scheduling.artifacts import DependencyGraph

class FusionPlanner:
    """
    Coordinates fusion analysis and group formation to produce a FusionPlan.
    """
    def __init__(self, analyzer: FusionAnalyzer):
        self._analyzer = analyzer

    def plan(self, graph_descriptor: GraphDescriptor, dependency_graph: DependencyGraph, analysis_report: GraphAnalysisReport) -> FusionPlan:
        """
        Generates an immutable FusionPlan based on Graph Analysis reports.
        """
        opportunities = self._analyzer.analyze_opportunities(graph_descriptor, dependency_graph, analysis_report)
        groups = []
        nodes_fused = 0

        for idx, opp in enumerate(opportunities):
            report = self._analyzer.check_compatibility(opp, dependency_graph)
            if report.is_compatible:
                group = FusionGroup(
                    id=f"group_{idx}",
                    node_ids=opp.target_nodes,
                    fusion_type=opp.potential_group_type
                )
                groups.append(group)
                nodes_fused += len(opp.target_nodes)

        stats = FusionStatistics(
            total_opportunities_found=len(opportunities),
            total_groups_formed=len(groups),
            nodes_fused=nodes_fused
        )

        return FusionPlan(
            groups=tuple(groups),
            statistics=stats
        )
