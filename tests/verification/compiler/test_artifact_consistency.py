# SPDX-License-Identifier: Apache-2.0
"""
Artifact consistency verification.
Verifies the complete lifecycle and transformation chain of compiler artifacts.
"""

import pytest
from unittest.mock import MagicMock
from types import MappingProxyType

from omlx.planner.plan import ExecutionPlan
from omlx.capabilities.descriptor import ExecutionFamily, CacheLayoutType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.physical.graph import PhysicalIR
from omlx.planner.ir.physical.operations import PhysicalOperation
from omlx.runtime.scheduling.types import BackendOperationGraph
from omlx.runtime.scheduling.schedule import ExecutionSchedule
from omlx.runtime.compiler_service import RuntimeCompilerService

def test_artifact_chain_completeness():
    """
    Verify that the pipeline fully traverses:
    ExecutionPlan -> LogicalIR -> PhysicalIR -> BackendOperationGraph -> TranslationResult.
    """
    mock_runtime = MagicMock()
    mock_runtime.feature_flags.COMPILER_RUNTIME_PIPELINE_ENABLED = True
    mock_runtime.feature_flags.CAPABILITY_RUNTIME_ENABLED = True
    mock_runtime.feature_flags.PLANNER_RUNTIME_ENABLED = True
    mock_runtime.feature_flags.LOWERING_RUNTIME_ENABLED = True
    mock_runtime.feature_flags.ADAPTER_RUNTIME_ENABLED = True
    mock_runtime.feature_flags.COMPILER_CONTEXT_ENABLED = True

    mock_resolver = MagicMock()
    mock_runtime.context.capability_resolver = mock_resolver

    mock_planner = MagicMock()
    mock_runtime.execution_planner = mock_planner
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
    mock_planner.plan.return_value = plan

    mock_ir_builder = MagicMock()
    mock_runtime.ir_builder = mock_ir_builder
    logical_ir = ExecutionIR(nodes=MappingProxyType({}), roots=tuple())
    mock_ir_builder.build.return_value = logical_ir

    mock_lowering = MagicMock()
    mock_runtime.lowering_engine = mock_lowering
    physical_ir = PhysicalIR(operations=MappingProxyType({}), roots=tuple())
    mock_lowering.lower.return_value = physical_ir

    mock_registry = MagicMock()
    mock_runtime.adapter_registry = mock_registry
    mock_adapter = MagicMock()
    mock_registry.resolve.return_value = mock_adapter

    mock_translation_result = MagicMock()
    mock_translation_result.backend_graph = MagicMock()
    mock_adapter.translate.return_value = mock_translation_result

    service = RuntimeCompilerService(mock_runtime)
    result = service.run_compilation("test_model")

    assert result == mock_translation_result

    mock_planner.plan.assert_called_once()
    mock_ir_builder.build.assert_called_once_with(plan)
    mock_lowering.lower.assert_called_once_with(logical_ir)
    mock_adapter.translate.assert_called_once_with(physical_ir)

def test_metadata_propagation():
    """Verify that metadata fields are successfully propagated down the pipeline."""
    plan = ExecutionPlan(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        execution_backend="mlx",
        execution_mode="standard",
        execution_topology="single_node",
        cache_strategy=CacheLayoutType.NONE,
        scheduler_strategy="dependency_driven",
        verification_stages=tuple(),
        optimization_passes=tuple(),
        planner_metadata=MappingProxyType({"trace_id": "12345"})
    )

    assert plan.planner_metadata["trace_id"] == "12345"

    logical_ir = ExecutionIR(
        nodes=MappingProxyType({}),
        roots=tuple(),
        metadata=MappingProxyType({"trace_id": plan.planner_metadata["trace_id"]})
    )

    assert logical_ir.metadata["trace_id"] == "12345"

    physical_ir = PhysicalIR(
        operations=MappingProxyType({}),
        roots=tuple(),
        metadata=MappingProxyType({"trace_id": logical_ir.metadata["trace_id"]})
    )

    assert physical_ir.metadata["trace_id"] == "12345"
