import pytest
from types import MappingProxyType
from omlx.framework.graph import (
    GraphNode,
    GraphEdge,
    GraphMetadata,
    GraphStatistics,
    GraphDiagnostic,
    GraphValidationReport,
    GraphDescriptor
)

def test_graph_node_immutable():
    node = GraphNode(id="n1", metadata=MappingProxyType({"type": "compute"}))
    assert node.id == "n1"
    with pytest.raises(Exception):
        node.id = "n2"

def test_graph_edge_immutable():
    edge = GraphEdge(source_id="n1", target_id="n2")
    assert edge.source_id == "n1"
    assert edge.target_id == "n2"
    with pytest.raises(Exception):
        edge.source_id = "n3"

def test_graph_metadata_immutable():
    meta = GraphMetadata(attributes=MappingProxyType({"a": 1}))
    assert meta.attributes["a"] == 1
    with pytest.raises(Exception):
        meta.attributes = MappingProxyType({"b": 2})

def test_graph_statistics_immutable():
    stats = GraphStatistics(node_count=10, edge_count=15)
    assert stats.node_count == 10
    assert stats.edge_count == 15
    with pytest.raises(Exception):
        stats.node_count = 20

def test_graph_diagnostic_immutable():
    diag = GraphDiagnostic(level="error", message="test")
    assert diag.level == "error"
    with pytest.raises(Exception):
        diag.level = "warning"

def test_graph_validation_report_immutable():
    diag = GraphDiagnostic(level="error", message="test")
    report = GraphValidationReport(is_valid=False, diagnostics=(diag,))
    assert not report.is_valid
    assert len(report.diagnostics) == 1
    with pytest.raises(Exception):
        report.is_valid = True

def test_graph_descriptor_immutable():
    n1 = GraphNode(id="n1")
    n2 = GraphNode(id="n2")
    e1 = GraphEdge(source_id="n1", target_id="n2")

    desc = GraphDescriptor(
        id="test_graph",
        nodes=MappingProxyType({"n1": n1, "n2": n2}),
        edges=(e1,)
    )
    assert desc.id == "test_graph"
    assert len(desc.nodes) == 2
    assert len(desc.edges) == 1
    with pytest.raises(Exception):
        desc.id = "new_id"
