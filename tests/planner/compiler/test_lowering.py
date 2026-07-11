import pytest
from types import MappingProxyType
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.physical.operations import PhysicalOperationType
from omlx.planner.compiler.lowering import LoweringEngine, DefaultLoweringPass

def test_default_lowering():
    # Setup Logical IR
    nodes = {
        "prefill": IRNode(id="prefill", node_type=IRNodeType.PREFILL),
        "forward": IRNode(id="forward", node_type=IRNodeType.FORWARD, dependencies=("prefill",)),
        "sample": IRNode(id="sample", node_type=IRNodeType.SAMPLE, dependencies=("forward",))
    }
    logical_ir = ExecutionIR(
        nodes=MappingProxyType(nodes),
        roots=("sample",)
    )

    # Lower
    engine = LoweringEngine()
    physical_ir = engine.lower(logical_ir)

    # Verify
    assert "prefill" in physical_ir.operations
    assert physical_ir.operations["prefill"].operation_type == PhysicalOperationType.NOOP

    assert "forward" in physical_ir.operations
    assert physical_ir.operations["forward"].operation_type == PhysicalOperationType.FORWARD

    assert "sample" in physical_ir.operations
    assert physical_ir.operations["sample"].operation_type == PhysicalOperationType.SAMPLING

    assert physical_ir.roots == ("sample",)
