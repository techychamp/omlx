import pytest
from types import MappingProxyType
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.physical.operations import PhysicalOperationType
from omlx.planner.compiler.engine import CompilerEngine

def test_compiler_engine():
    nodes = {
        "prefill": IRNode(id="prefill", node_type=IRNodeType.PREFILL),
    }
    logical_ir = ExecutionIR(
        nodes=MappingProxyType(nodes),
        roots=("prefill",)
    )

    engine = CompilerEngine()
    physical_ir = engine.compile(logical_ir)

    assert "prefill" in physical_ir.operations
    assert physical_ir.operations["prefill"].operation_type == PhysicalOperationType.NOOP
