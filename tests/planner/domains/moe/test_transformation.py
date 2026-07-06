import pytest
from types import MappingProxyType

from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.domains.moe.artifacts import MoEPlan, ExpertGroup, ExpertDescriptor
from omlx.planner.domains.moe.transformation.realizer import MoERealizer
from omlx.planner.domains.moe.transformation.validator import MoETransformationValidator
from omlx.planner.domains.moe.transformation.pass_ import MoERealizationPass

def _create_basic_ir() -> ExecutionIR:
    node1 = IRNode("node_1", IRNodeType.FORWARD)
    return ExecutionIR(
        nodes=MappingProxyType({"node_1": node1}),
        roots=("node_1",)
    )

def _create_moe_plan() -> MoEPlan:
    expert1 = ExpertDescriptor(id="e1")
    expert2 = ExpertDescriptor(id="e2")
    group = ExpertGroup(id="g1", experts=(expert1, expert2))
    return MoEPlan(
        experts=(expert1, expert2),
        groups=(group,)
    )

def test_moe_realizer_transformation():
    ir = _create_basic_ir()
    plan = _create_moe_plan()

    realizer = MoERealizer()
    transformed_ir, report = realizer.realize(ir, plan)

    assert report.validation_report.is_valid
    assert len(transformed_ir.nodes) == 1 + 3 # original 1 + routing 1 + experts 2
    assert report.statistics.experts_realized == 2
    assert report.statistics.groups_realized == 1

    # Check routing node
    assert "moe_routing_g1" in transformed_ir.nodes
    routing_node = transformed_ir.nodes["moe_routing_g1"]
    assert routing_node.node_type == IRNodeType.ROUTING

    # Check expert node dependencies
    expert1_node = transformed_ir.nodes["moe_expert_g1_e1"]
    assert expert1_node.node_type == IRNodeType.FORWARD
    assert "moe_routing_g1" in expert1_node.dependencies

    expert2_node = transformed_ir.nodes["moe_expert_g1_e2"]
    assert expert2_node.node_type == IRNodeType.FORWARD
    assert "moe_routing_g1" in expert2_node.dependencies

def test_moe_validator_logic():
    ir = _create_basic_ir()
    plan = _create_moe_plan()

    realizer = MoERealizer()
    transformed_ir, report = realizer.realize(ir, plan)

    validator = MoETransformationValidator()
    validation_report = validator.validate(ir, transformed_ir)

    assert validation_report.is_valid
    assert len(validation_report.diagnostics) == 0

def test_moe_realization_pass():
    ir = _create_basic_ir()
    plan = _create_moe_plan()

    moe_pass = MoERealizationPass(plan)
    assert moe_pass.name == "MoERealizationPass"

    transformed_ir = moe_pass.apply(ir)

    assert len(transformed_ir.nodes) == 4
    assert "moe_routing_g1" in transformed_ir.nodes

    assert moe_pass.report is not None
    assert moe_pass.report.statistics.experts_realized == 2
