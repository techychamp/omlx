import pytest
from omlx.planner.domains.fusion.analyzer import FusionAnalyzer
from omlx.framework.graph.artifacts import GraphAnalysisReport
from omlx.framework.graph.descriptor import GraphDescriptor
from omlx.runtime.scheduling.artifacts import DependencyGraph
from types import MappingProxyType

def test_fusion_analyzer_initialization():
    analyzer = FusionAnalyzer()
    assert analyzer is not None

def test_fusion_analyzer_empty_graph():
    analyzer = FusionAnalyzer()
    desc = GraphDescriptor(id='test', nodes=MappingProxyType({}), edges=())
    dep_graph = DependencyGraph(operations={})
    report = GraphAnalysisReport()
    opportunities = analyzer.analyze_opportunities(desc, dep_graph, report)
    assert len(opportunities) == 0

def test_fusion_analyzer_finds_opportunity():
    from omlx.framework.graph.artifacts import GraphAnalysisReport
    from omlx.framework.graph.descriptor import GraphDescriptor
    from omlx.runtime.scheduling.artifacts import DependencyGraph
    from omlx.planner.domains.fusion.analyzer import FusionAnalyzer
    from types import MappingProxyType

    desc = GraphDescriptor(id='test', nodes=MappingProxyType({}), edges=())
    dep_graph = DependencyGraph(operations={})
    report = GraphAnalysisReport(node_properties=MappingProxyType({
        "node_1": {"fusion_candidate": True, "fusion_target": "node_2", "fusion_type": "QKV"}
    }))

    analyzer = FusionAnalyzer()
    opps = analyzer.analyze_opportunities(desc, dep_graph, report)
    assert len(opps) == 1
    assert opps[0].potential_group_type == "QKV"
    assert opps[0].target_nodes == ("node_1", "node_2")
