import pytest
from types import MappingProxyType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.domains.fusion.artifacts import FusionPlan, FusionGroup
from omlx.planner.compiler.transformation.realizer import FusionRealizer
from omlx.planner.compiler.transformation.validator import TransformationValidator

def test_fusion_realizer_basic():
    # Construct a simple IR graph
    # node_a -> node_b -> node_c
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

    # Create a FusionPlan to fuse a and b
    plan = FusionPlan(
        groups=(
            FusionGroup(
                id="group_1",
                node_ids=("node_a", "node_b"),
                fusion_type="test_fusion"
            ),
        )
    )

    realizer = FusionRealizer()
    transformed_ir, report = realizer.realize(ir, plan)

    assert report.validation_report.is_valid
    assert report.statistics.original_node_count == 3
    assert report.statistics.transformed_node_count == 2
    assert report.statistics.nodes_fused == 2
    assert report.statistics.groups_realized == 1

    assert len(transformed_ir.nodes) == 2
    assert "node_c" in transformed_ir.nodes
    assert "fused_group_1" in transformed_ir.nodes

    # Check dependencies are rewired
    assert "fused_group_1" in transformed_ir.nodes["node_c"].dependencies
    assert len(transformed_ir.nodes["fused_group_1"].dependencies) == 0

def test_fusion_validator_invalid_dependencies():
    node_b = IRNode(id="node_b", node_type=IRNodeType.FORWARD, dependencies=("missing_node",))
    node_a = IRNode(id="node_a", node_type=IRNodeType.FORWARD, dependencies=())

    nodes = {
        "node_a": node_a,
        "node_b": node_b
    }

    ir = ExecutionIR(
        nodes=MappingProxyType(nodes),
        roots=("node_b",),
        metadata=MappingProxyType({})
    )

    validator = TransformationValidator()
    report = validator.validate(ir, ir)

    assert not report.is_valid
    assert len(report.diagnostics) > 0
    assert any("missing dependency" in diag.message for diag in report.diagnostics)
