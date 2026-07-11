import pytest
from types import MappingProxyType
from omlx.framework.graph import (
    GraphNode,
    GraphEdge,
    GraphMetadata,
    GraphDescriptor
)
from omlx.framework.graph.transformation import (
    GraphRewriter,
    TransformationStatistics,
    TransformationPass,
    TransformationDescriptor,
    TransformationContext,
    TransformationPipeline,
    TransformationValidator,
    TransformationValidationReport,
    TransformationDiagnostic
)

def create_simple_graph():
    n1 = GraphNode(id="n1")
    n2 = GraphNode(id="n2")
    n3 = GraphNode(id="n3")
    e12 = GraphEdge(source_id="n1", target_id="n2")
    e23 = GraphEdge(source_id="n2", target_id="n3")

    return GraphDescriptor(
        id="test_graph",
        nodes=MappingProxyType({"n1": n1, "n2": n2, "n3": n3}),
        edges=(e12, e23)
    )

def test_insert_node():
    graph = create_simple_graph()
    n4 = GraphNode(id="n4")

    new_graph, stats = GraphRewriter.insert_node(graph, n4)

    assert "n4" in new_graph.nodes
    assert len(new_graph.nodes) == 4
    assert stats.nodes_added == 1
    assert stats.nodes_removed == 0

def test_remove_node():
    graph = create_simple_graph()

    new_graph, stats = GraphRewriter.remove_node(graph, "n2")

    assert "n2" not in new_graph.nodes
    assert len(new_graph.nodes) == 2
    assert len(new_graph.edges) == 0  # Both edges should be removed as they connect to n2
    assert stats.nodes_removed == 1
    assert stats.edges_removed == 2

def test_replace_node():
    graph = create_simple_graph()
    n2_new = GraphNode(id="n2_new")

    new_graph, stats = GraphRewriter.replace_node(graph, "n2", n2_new)

    assert "n2" not in new_graph.nodes
    assert "n2_new" in new_graph.nodes
    assert len(new_graph.edges) == 2

    # Check if edges are correctly rewired
    edge_sources = [e.source_id for e in new_graph.edges]
    edge_targets = [e.target_id for e in new_graph.edges]

    assert "n2_new" in edge_sources
    assert "n2_new" in edge_targets
    assert "n2" not in edge_sources
    assert "n2" not in edge_targets

    assert stats.nodes_replaced == 1

def test_rewire_edge():
    graph = create_simple_graph()
    old_edge = graph.edges[0]  # n1 -> n2
    new_edge = GraphEdge(source_id="n1", target_id="n3")

    new_graph, stats = GraphRewriter.rewire_edge(graph, old_edge, new_edge)

    assert len(new_graph.edges) == 2
    assert old_edge not in new_graph.edges
    assert new_edge in new_graph.edges
    assert stats.edges_added == 1
    assert stats.edges_removed == 1

def test_clone_graph():
    graph = create_simple_graph()

    new_graph = GraphRewriter.clone_graph(graph, "cloned_graph")

    assert new_graph.id == "cloned_graph"
    assert new_graph.nodes == graph.nodes
    assert new_graph.edges == graph.edges

def test_normalize_graph():
    n1 = GraphNode(id="n1")
    n2 = GraphNode(id="n2")
    e12 = GraphEdge(source_id="n1", target_id="n2")
    e21 = GraphEdge(source_id="n2", target_id="n1")

    graph = GraphDescriptor(
        id="test_graph",
        nodes=MappingProxyType({"n1": n1, "n2": n2}),
        edges=(e21, e12)  # Unsorted
    )

    new_graph, stats = GraphRewriter.normalize_graph(graph)

    assert new_graph.edges == (e12, e21)  # Should be sorted
    assert new_graph.nodes == graph.nodes

class DummyPass(TransformationPass):
    @property
    def descriptor(self) -> TransformationDescriptor:
        return TransformationDescriptor(id="dummy_pass", description="Dummy pass")

    def apply(self, graph: GraphDescriptor, context: TransformationContext) -> tuple[GraphDescriptor, TransformationStatistics]:
        n_dummy = GraphNode(id="dummy")
        return GraphRewriter.insert_node(graph, n_dummy)

class DummyValidator(TransformationValidator):
    def validate(self, original_graph: GraphDescriptor, transformed_graph: GraphDescriptor) -> TransformationValidationReport:
        if "dummy" in transformed_graph.nodes:
            return TransformationValidationReport(is_valid=True)
        return TransformationValidationReport(
            is_valid=False,
            diagnostics=(TransformationDiagnostic(level="error", message="Dummy node missing"),)
        )

def test_transformation_pipeline():
    graph = create_simple_graph()
    context = TransformationContext()

    pipeline = TransformationPipeline(
        passes=(DummyPass(),),
        validators=(DummyValidator(),)
    )

    new_graph, stats, report = pipeline.execute(graph, context)

    assert "dummy" in new_graph.nodes
    assert stats.nodes_added == 1
    assert report.is_valid

def test_transformation_pipeline_validation_failure():
    graph = create_simple_graph()
    context = TransformationContext()

    # Empty pipeline, dummy node won't be added
    pipeline = TransformationPipeline(
        passes=(),
        validators=(DummyValidator(),)
    )

    new_graph, stats, report = pipeline.execute(graph, context)

    assert "dummy" not in new_graph.nodes
    assert not report.is_valid
    assert len(report.diagnostics) == 1
    assert report.diagnostics[0].message == "Dummy node missing"
