# SPDX-License-Identifier: Apache-2.0
"""Test Backend Validation and Translation verification."""

import pytest
from types import MappingProxyType
from omlx.planner.compiler.backend.adapter import MLXAdapter
from omlx.planner.ir.physical.graph import PhysicalIR
from omlx.planner.ir.physical.operations import PhysicalOperation, PhysicalOperationType

def test_mlx_backend_translation_valid():
    """Verify MLXAdapter translates a valid physical IR graph correctly."""
    adapter = MLXAdapter()

    op_forward = PhysicalOperation(
        id="op_1",
        operation_type=PhysicalOperationType.FORWARD.value,
        inputs=tuple(),
        outputs=tuple(),
        dependencies=tuple(),
        execution_family="autoregressive",
        metadata=MappingProxyType({})
    )

    physical_ir = PhysicalIR(
        operations=MappingProxyType({"op_1": op_forward}),
        roots=("op_1",),
        metadata=MappingProxyType({})
    )

    result = adapter.translate(physical_ir)

    assert result.backend_graph is not None
    assert "op_1" in result.backend_graph.operations
    assert result.backend_descriptor == adapter.descriptor
    assert len(result.translation_warnings) == 0

def test_mlx_backend_translation_invalid():
    """Verify MLXAdapter validation catches unsupported operations."""
    adapter = MLXAdapter()

    # Try to pass an unknown op type
    op_invalid = PhysicalOperation(
        id="op_invalid",
        operation_type="UNKNOWN_OP",
        inputs=tuple(),
        outputs=tuple(),
        dependencies=tuple(),
        execution_family="autoregressive",
        metadata=MappingProxyType({})
    )

    physical_ir = PhysicalIR(
        operations=MappingProxyType({"op_invalid": op_invalid}),
        roots=("op_invalid",),
        metadata=MappingProxyType({})
    )

    with pytest.raises(ValueError, match="Physical IR validation failed"):
        adapter.translate(physical_ir)
