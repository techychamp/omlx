import pytest
from omlx.planner.domains.fusion.planner import FusionPlanner
from omlx.planner.domains.fusion.analyzer import FusionAnalyzer
from omlx.framework.graph.artifacts import GraphAnalysisReport, GraphDescriptor
from omlx.runtime.scheduling.artifacts import DependencyGraph
from types import MappingProxyType

def test_fusion_planner_initialization():
    analyzer = FusionAnalyzer()
    planner = FusionPlanner(analyzer=analyzer)
    assert planner is not None

def test_fusion_planner_plan_empty():
    analyzer = FusionAnalyzer()
    planner = FusionPlanner(analyzer=analyzer)
    desc = GraphDescriptor(id='test')
    dep_graph = DependencyGraph(operations={})
    report = GraphAnalysisReport()
    plan = planner.plan(desc, dep_graph, report)
    assert plan.statistics.total_opportunities_found == 0
    assert plan.statistics.total_groups_formed == 0
    assert len(plan.groups) == 0

def test_fusion_planner_forms_groups():
    from omlx.framework.graph.artifacts import GraphAnalysisReport, GraphDescriptor
    from omlx.runtime.scheduling.artifacts import DependencyGraph
    from omlx.planner.domains.fusion.planner import FusionPlanner
    from omlx.planner.domains.fusion.analyzer import FusionAnalyzer
    from types import MappingProxyType

    desc = GraphDescriptor(id='test')
    dep_graph = DependencyGraph(operations={})
    report = GraphAnalysisReport(node_properties=MappingProxyType({
        "node_1": {"fusion_candidate": True, "fusion_target": "node_2", "fusion_type": "QKV"}
    }))

    planner = FusionPlanner(FusionAnalyzer())
    plan = planner.plan(desc, dep_graph, report)
    assert len(plan.groups) == 1
    assert plan.statistics.nodes_fused == 2
