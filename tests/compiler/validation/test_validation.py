from omlx.compiler.graph.builder import Graph
from omlx.compiler.ir.core import Node, Edge
from omlx.compiler.cmr.models import CanonicalModelRepresentation
from omlx.compiler.validation.validator import GraphValidator

def test_graph_validation_cycle():
    graph = Graph()

    node1 = Node(id="n1", type="Attention", inputs=["x"], outputs=["y"])
    node2 = Node(id="n2", type="Attention", inputs=["y"], outputs=["x"])

    graph.add_node(node1)
    graph.add_node(node2)

    graph.add_edge(Edge(source_node="n1", target_node="n2", tensor_name="y"))
    graph.add_edge(Edge(source_node="n2", target_node="n1", tensor_name="x"))

    cmr = CanonicalModelRepresentation(architecture="llama")
    validator = GraphValidator()

    errors = validator.validate(graph, cmr)
    assert len(errors) == 1
    assert "Graph contains a cycle" in errors[0]
