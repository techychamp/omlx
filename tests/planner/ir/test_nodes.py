# SPDX-License-Identifier: Apache-2.0

from types import MappingProxyType
from omlx.planner.ir.nodes import IRNode, IRNodeType

def test_ir_node_creation():
    node = IRNode(
        id="test_node",
        node_type=IRNodeType.FORWARD,
        dependencies=("dep1", "dep2"),
        metadata=MappingProxyType({"key": "value"})
    )

    assert node.id == "test_node"
    assert node.node_type == IRNodeType.FORWARD
    assert node.dependencies == ("dep1", "dep2")
    assert node.metadata["key"] == "value"

def test_ir_node_serialization():
    node = IRNode(
        id="test_node",
        node_type=IRNodeType.FORWARD,
        dependencies=("dep1", "dep2"),
        metadata=MappingProxyType({"key": "value"})
    )

    data = node.to_dict()
    assert data["id"] == "test_node"
    assert data["node_type"] == "forward"
    assert data["dependencies"] == ["dep1", "dep2"]
    assert data["metadata"] == {"key": "value"}

    restored = IRNode.from_dict(data)
    assert restored.id == node.id
    assert restored.node_type == node.node_type
    assert restored.dependencies == node.dependencies
    assert restored.metadata == node.metadata
