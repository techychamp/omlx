# SPDX-License-Identifier: Apache-2.0

import json
from types import MappingProxyType
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.ir.graph import ExecutionIR

def test_execution_ir_creation():
    node1 = IRNode(id="n1", node_type=IRNodeType.PREFILL)
    node2 = IRNode(id="n2", node_type=IRNodeType.FORWARD, dependencies=("n1",))

    ir = ExecutionIR(
        nodes=MappingProxyType({"n1": node1, "n2": node2}),
        roots=("n2",),
        metadata=MappingProxyType({"version": "1.0"})
    )

    assert ir.get_node("n1") == node1
    assert ir.roots == ("n2",)
    assert ir.metadata["version"] == "1.0"

def test_execution_ir_serialization():
    node1 = IRNode(id="n1", node_type=IRNodeType.PREFILL)
    node2 = IRNode(id="n2", node_type=IRNodeType.FORWARD, dependencies=("n1",))

    ir = ExecutionIR(
        nodes=MappingProxyType({"n1": node1, "n2": node2}),
        roots=("n2",),
        metadata=MappingProxyType({"version": "1.0"})
    )

    json_str = ir.to_json()
    data = json.loads(json_str)

    assert "nodes" in data
    assert "n1" in data["nodes"]
    assert "roots" in data

    restored = ExecutionIR.from_json(json_str)
    assert restored.roots == ir.roots
    assert restored.metadata == ir.metadata
    assert restored.get_node("n1").id == "n1"
    assert restored.get_node("n2").dependencies == ("n1",)
