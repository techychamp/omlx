import pytest
from types import MappingProxyType
from omlx.framework.graph import GraphDescriptor, GraphNode, GraphEdge
from omlx.framework.graph.transformation import TransformationContext
from omlx.planner.domains.fusion.artifacts import FusionPlan, FusionGroup
from omlx.planner.domains.fusion.transformation import FusionRealizationPass

def test_fusion_realization_pass():
    n1 = GraphNode(id="n1")
    n2 = GraphNode(id="n2")
    n3 = GraphNode(id="n3")
    n4 = GraphNode(id="n4")

    e12 = GraphEdge(source_id="n1", target_id="n2")
    e23 = GraphEdge(source_id="n2", target_id="n3")
    e34 = GraphEdge(source_id="n3", target_id="n4")

    graph = GraphDescriptor(
        id="test_graph",
        nodes=MappingProxyType({"n1": n1, "n2": n2, "n3": n3, "n4": n4}),
        edges=(e12, e23, e34)
    )

    # Fuse n2 and n3
    group = FusionGroup(id="g1", node_ids=("n2", "n3"), fusion_type="TEST")
    plan = FusionPlan(groups=(group,))

    fusion_pass = FusionRealizationPass(plan)
    new_graph, stats = fusion_pass.apply(graph, TransformationContext())

    assert "n2" not in new_graph.nodes
    assert "n3" not in new_graph.nodes
    assert "fused_n2_n3" in new_graph.nodes

    edge_targets = [e.target_id for e in new_graph.edges]
    edge_sources = [e.source_id for e in new_graph.edges]

    assert "fused_n2_n3" in edge_targets  # from n1
    assert "fused_n2_n3" in edge_sources  # to n4

    assert stats.nodes_added == 1
    assert stats.nodes_removed == 2
