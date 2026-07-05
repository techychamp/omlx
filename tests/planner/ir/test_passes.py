# SPDX-License-Identifier: Apache-2.0

from types import MappingProxyType
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.passes import IROptimizationPass, IRPassRegistry

class DummyPass(IROptimizationPass):
    @property
    def name(self) -> str:
        return "dummy_pass"

    def apply(self, ir: ExecutionIR) -> ExecutionIR:
        # Just returns a new IR with a different root for testing
        node = ir.get_node(ir.roots[0])
        new_node = IRNode(
            id=node.id,
            node_type=node.node_type,
            dependencies=node.dependencies,
            metadata=MappingProxyType({"modified": True})
        )

        nodes = dict(ir.nodes)
        nodes[new_node.id] = new_node

        return ExecutionIR(
            nodes=MappingProxyType(nodes),
            roots=ir.roots,
            metadata=ir.metadata
        )

def test_pass_registry():
    registry = IRPassRegistry()
    registry.register(DummyPass())

    passes = registry.get_passes()
    assert len(passes) == 1
    assert passes[0].name == "dummy_pass"

def test_apply_pass():
    node1 = IRNode(id="n1", node_type=IRNodeType.PREFILL)
    ir = ExecutionIR(
        nodes=MappingProxyType({"n1": node1}),
        roots=("n1",)
    )

    opt_pass = DummyPass()
    new_ir = opt_pass.apply(ir)

    assert new_ir.get_node("n1").metadata.get("modified") is True
    assert ir.get_node("n1").metadata.get("modified") is None # original should be untouched
