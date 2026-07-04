# SPDX-License-Identifier: Apache-2.0

import pytest
from types import MappingProxyType
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.validation import validate_ir, IRValidationError

def test_valid_ir():
    node1 = IRNode(id="n1", node_type=IRNodeType.PREFILL)
    node2 = IRNode(id="n2", node_type=IRNodeType.FORWARD, dependencies=("n1",))

    ir = ExecutionIR(
        nodes=MappingProxyType({"n1": node1, "n2": node2}),
        roots=("n2",)
    )

    validate_ir(ir) # Should not raise

def test_missing_root():
    node1 = IRNode(id="n1", node_type=IRNodeType.PREFILL)

    ir = ExecutionIR(
        nodes=MappingProxyType({"n1": node1}),
        roots=()
    )

    with pytest.raises(IRValidationError, match="ExecutionIR has no roots"):
        validate_ir(ir)

def test_invalid_root():
    node1 = IRNode(id="n1", node_type=IRNodeType.PREFILL)

    ir = ExecutionIR(
        nodes=MappingProxyType({"n1": node1}),
        roots=("missing_node",)
    )

    with pytest.raises(IRValidationError, match="not in nodes"):
        validate_ir(ir)

def test_missing_dependency():
    node1 = IRNode(id="n1", node_type=IRNodeType.FORWARD, dependencies=("missing",))

    ir = ExecutionIR(
        nodes=MappingProxyType({"n1": node1}),
        roots=("n1",)
    )

    with pytest.raises(IRValidationError, match="missing node"):
        validate_ir(ir)

def test_cycle_detection():
    node1 = IRNode(id="n1", node_type=IRNodeType.FORWARD, dependencies=("n2",))
    node2 = IRNode(id="n2", node_type=IRNodeType.FORWARD, dependencies=("n1",))

    ir = ExecutionIR(
        nodes=MappingProxyType({"n1": node1, "n2": node2}),
        roots=("n1",)
    )

    with pytest.raises(IRValidationError, match="Cycle detected"):
        validate_ir(ir)

def test_unreachable_node():
    node1 = IRNode(id="n1", node_type=IRNodeType.PREFILL)
    node2 = IRNode(id="n2", node_type=IRNodeType.FORWARD) # Not connected to root

    ir = ExecutionIR(
        nodes=MappingProxyType({"n1": node1, "n2": node2}),
        roots=("n1",)
    )

    with pytest.raises(IRValidationError, match="Unreachable nodes"):
        validate_ir(ir)
