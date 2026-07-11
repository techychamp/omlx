import pytest
from types import MappingProxyType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.domains.fusion.artifacts import FusionPlan, FusionGroup
from omlx.planner.compiler.transformation.pass_ import FusionRealizationPass

def test_fusion_realization_pass():
    node_c = IRNode(id="node_c", node_type=IRNodeType.FORWARD, dependencies=("node_b",))
    node_b = IRNode(id="node_b", node_type=IRNodeType.FORWARD, dependencies=("node_a",))
    node_a = IRNode(id="node_a", node_type=IRNodeType.FORWARD, dependencies=())

    nodes = {
        "node_a": node_a,
        "node_b": node_b,
        "node_c": node_c
    }

    ir = ExecutionIR(
        nodes=MappingProxyType(nodes),
        roots=("node_c",),
        metadata=MappingProxyType({})
    )

    plan = FusionPlan(
        groups=(
            FusionGroup(
                id="group_1",
                node_ids=("node_a", "node_b"),
                fusion_type="test_fusion"
            ),
        )
    )

    pass_ = FusionRealizationPass(plan)
    transformed_ir = pass_.apply(ir)

    assert len(transformed_ir.nodes) == 2
    assert pass_.report is not None
    assert pass_.report.validation_report.is_valid
