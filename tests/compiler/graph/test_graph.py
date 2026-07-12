from omlx.compiler.graph.builder import Graph
from omlx.compiler.ir.core import Node, Edge

def test_graph_building_and_sorting():
    graph = Graph()

    node1 = Node(id="n1", type="Attention", inputs=["x"], outputs=["h1"])
    node2 = Node(id="", type="Linear", inputs=["h1"], outputs=["y"])

    graph.add_node(node1)
    graph.add_node(node2)

    assert node2.id == "Linear_001"

    edge = Edge(source_node="n1", target_node="Linear_001", tensor_name="h1")
    graph.add_edge(edge)

    sorted_nodes = graph.topological_sort()
    assert len(sorted_nodes) == 2
    assert sorted_nodes[0].id == "n1"
    assert sorted_nodes[1].id == "Linear_001"

    data = graph.to_dict()
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1
    assert data["version"] == 1
    assert data["graph_version"] == 1
