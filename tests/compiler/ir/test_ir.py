from omlx.compiler.ir.core import Node, Edge

def test_node_serialization():
    node = Node(id="n1", type="Linear", inputs=["x"], outputs=["y"])

    data = node.to_dict()
    assert data["id"] == "n1"
    assert data["type"] == "Linear"
    assert data["inputs"] == ["x"]
    assert data["outputs"] == ["y"]

    node2 = Node.from_dict(data)
    assert node2.id == "n1"
    assert node2.type == "Linear"

def test_edge_serialization():
    edge = Edge(source_node="n1", target_node="n2", tensor_name="h")
    data = edge.to_dict()
    assert data["source_node"] == "n1"
    assert data["target_node"] == "n2"
    assert data["tensor_name"] == "h"

    edge2 = Edge.from_dict(data)
    assert edge2.source_node == "n1"
    assert edge2.target_node == "n2"
