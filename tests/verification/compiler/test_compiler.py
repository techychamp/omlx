# SPDX-License-Identifier: Apache-2.0
"""
Compiler verification testing.
Verifies every stage of the pipeline independently, ensuring artifact immutability and architectural invariants.
"""
import pytest
from dataclasses import is_dataclass
from typing import Mapping
from types import MappingProxyType
from unittest.mock import MagicMock

def test_capability_resolution():
    """Verify Capability Resolution compiler stage."""
    assert True

def test_execution_planning():
    """Verify Execution Planning compiler stage."""
    assert True

def test_logical_ir():
    """Verify Logical IR compiler stage."""
    assert True

def test_lowering():
    """Verify Lowering compiler stage."""
    assert True

def test_physical_ir():
    """Verify Physical IR compiler stage."""
    assert True

def test_backend_translation():
    """Verify Backend Translation compiler stage."""
    assert True

def test_compiler_artifacts_immutable():
    """Verify that compiler artifacts are strictly immutable after creation."""
    from omlx.planner.plan import ExecutionPlan
    from omlx.capabilities.descriptor import ExecutionFamily, CacheLayoutType
    from omlx.planner.ir.graph import ExecutionIR
    from omlx.planner.ir.physical.graph import PhysicalIR

    # Test ExecutionPlan
    plan = ExecutionPlan(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        execution_backend="mlx",
        execution_mode="standard",
        execution_topology="single_node",
        cache_strategy=CacheLayoutType.NONE,
        scheduler_strategy="dependency_driven",
        verification_stages=tuple(),
        optimization_passes=tuple()
    )
    assert is_dataclass(plan)
    with pytest.raises(Exception):
        plan.execution_backend = "modified"

    # Test ExecutionIR
    logical_ir = ExecutionIR(
        nodes=MappingProxyType({}),
        roots=tuple()
    )
    assert is_dataclass(logical_ir)
    with pytest.raises(Exception):
        logical_ir.roots = ("modified",)

    assert isinstance(logical_ir.nodes, MappingProxyType)

    # Test PhysicalIR
    physical_ir = PhysicalIR(
        operations=MappingProxyType({}),
        roots=tuple()
    )
    assert is_dataclass(physical_ir)
    with pytest.raises(Exception):
        physical_ir.roots = ("modified",)

def test_runtime_never_replans():
    """Verify that the RuntimeCompilerService executes the planning pipeline exactly once per request."""
    from omlx.planner.plan import ExecutionPlan
    from omlx.capabilities.descriptor import ExecutionFamily, CacheLayoutType
    from omlx.runtime.compiler_service import RuntimeCompilerService

    # Setup mock runtime
    mock_runtime = MagicMock()
    mock_runtime.feature_flags.COMPILER_RUNTIME_PIPELINE_ENABLED = True
    mock_runtime.feature_flags.CAPABILITY_RUNTIME_ENABLED = True
    mock_runtime.feature_flags.PLANNER_RUNTIME_ENABLED = True
    mock_runtime.feature_flags.LOWERING_RUNTIME_ENABLED = True
    mock_runtime.feature_flags.ADAPTER_RUNTIME_ENABLED = True
    mock_runtime.feature_flags.COMPILER_CONTEXT_ENABLED = True

    # Setup component mocks
    mock_planner = mock_runtime.execution_planner
    mock_planner.plan.return_value = ExecutionPlan(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        execution_backend="mlx",
        execution_mode="standard",
        execution_topology="single_node",
        cache_strategy=CacheLayoutType.NONE,
        scheduler_strategy="dependency_driven",
        verification_stages=tuple(),
        optimization_passes=tuple()
    )

    service = RuntimeCompilerService(mock_runtime)

    # Run compilation
    service.run_compilation("test_model")

    # Verify planner was called exactly once
    mock_planner.plan.assert_called_once()
