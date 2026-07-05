# SPDX-License-Identifier: Apache-2.0
"""Test golden assets alignment checks."""

import pytest
import os
from types import MappingProxyType
from omlx.planner.plan import ExecutionPlan
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from verification.scripts.utils import GoldenLoader, GoldenComparator, ArtifactSerializer

# Define test assets directory
GOLDEN_DIR = "tests/golden"

def _get_dummy_execution_plan() -> ExecutionPlan:
    return ExecutionPlan(
        execution_family="autoregressive",
        execution_backend="autoregressive",
        execution_mode="standard",
        execution_topology="single_node",
        cache_strategy="paged",
        scheduler_strategy="static_batching",
        verification_stages=tuple(),
        optimization_passes=tuple(),
        execution_hints=MappingProxyType({"precision": "fp16"}),
        hardware_requirements=tuple(),
        planner_metadata=MappingProxyType({"planning_time_ms": 10.0})
    )

def _get_dummy_execution_ir() -> ExecutionIR:
    node = IRNode(
        id="node_prefill",
        node_type=IRNodeType.PREFILL,
        metadata=MappingProxyType({})
    )
    return ExecutionIR(
        nodes=MappingProxyType({node.id: node}),
        roots=("node_prefill",),
        metadata=MappingProxyType({"execution_mode": "standard"})
    )

def test_execution_plan_golden_alignment():
    """Verify that execution plan matches its golden asset."""
    plan = _get_dummy_execution_plan()
    golden_path = os.path.join(GOLDEN_DIR, "execution_plan", "dummy_plan.json")
    
    if not os.path.exists(golden_path):
        GoldenLoader.save(ArtifactSerializer.serialize(plan), golden_path)
        pytest.skip(f"Golden asset created at {golden_path}. Run again to verify.")

    golden_plan = GoldenLoader.load(golden_path)
    # Exclude metadata like planning_time_ms which might vary
    actual_dict = ArtifactSerializer.serialize(plan)
    actual_dict.pop("planner_metadata", None)
    expected_dict = dict(golden_plan)
    expected_dict.pop("planner_metadata", None)
    
    diff = GoldenComparator.compare(actual_dict, expected_dict)
    
    assert not diff.has_differences(), f"ExecutionPlan drifted from golden baseline. Diff: {diff.to_dict()}"

def test_execution_ir_golden_alignment():
    """Verify that execution IR matches its golden asset."""
    ir = _get_dummy_execution_ir()
    golden_path = os.path.join(GOLDEN_DIR, "logical_ir", "dummy_ir.json")
    
    if not os.path.exists(golden_path):
        GoldenLoader.save(ArtifactSerializer.serialize(ir), golden_path)
        pytest.skip(f"Golden asset created at {golden_path}. Run again to verify.")

    golden_ir = GoldenLoader.load(golden_path)
    
    diff = GoldenComparator.compare(ir, golden_ir)

    assert not diff.has_differences(), f"ExecutionIR drifted from golden baseline. Diff: {diff.to_dict()}"
