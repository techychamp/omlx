# SPDX-License-Identifier: Apache-2.0
"""
Tests for OMLX Execution Engine implementation.
"""

import pytest
from dataclasses import dataclass
from unittest.mock import Mock, MagicMock

from omlx.runtime.execution import (
    ExecutionEngine, ExecutionContext, ExecutionStatus,
    SequentialExecutionDispatcher, DeterministicGraphExecutor,
    ImmutableExecutionExecutor
)
from omlx.runtime.builder import RuntimeBuilder, FeatureFlags

@dataclass
class MockGraph:
    operations: dict
    roots: tuple = ()

def test_execution_engine_initialization():
    engine = ExecutionEngine()
    assert isinstance(engine._executor, ImmutableExecutionExecutor)

def test_execution_engine_missing_graph():
    engine = ExecutionEngine()
    context = ExecutionContext(request_context=Mock())
    result = engine.execute(context)
    assert result.status == ExecutionStatus.FAILED

def test_execution_engine_valid_graph():
    engine = ExecutionEngine()

    mock_op = MagicMock()
    mock_op.dependencies = []
    graph = MockGraph(operations={"op1": mock_op}, roots=("op1",))

    mock_adapter = MagicMock()
    mock_adapter.execute.return_value = "node_output"

    context = ExecutionContext(request_context=Mock(), backend_operation_graph=graph, adapter=mock_adapter)

    result = engine.execute(context)
    assert result.status == ExecutionStatus.COMPLETED
    assert result.model_output["operations"] == 1
    assert result.statistics is not None
    assert result.statistics.executed_operations == 1

def test_dispatcher_mock():
    dispatcher = SequentialExecutionDispatcher()

    mock_op1 = MagicMock()
    mock_op1.dependencies = []
    mock_op2 = MagicMock()
    mock_op2.dependencies = ["op1"]
    graph = MockGraph(operations={"op1": mock_op1, "op2": mock_op2}, roots=("op1",))

    mock_adapter = MagicMock()
    mock_adapter.execute.return_value = "node_output"

    context = ExecutionContext(request_context=Mock(), backend_operation_graph=graph, adapter=mock_adapter)

    result = dispatcher.dispatch(graph, context, execution_order=['op1', 'op2'])
    assert result.status == ExecutionStatus.COMPLETED
    assert result.model_output["operations"] == 2
    assert mock_adapter.execute.call_count == 2

def test_runtime_builder_integration():
    builder = RuntimeBuilder()
    flags = FeatureFlags(COMPILER_RUNTIME_ENABLED=True)
    builder.with_feature_flags(flags)
    runtime = builder.build()

    assert hasattr(runtime, 'execution_engine')
    assert runtime.execution_engine is not None

def test_runtime_execute_request_integration():
    """
    Integration test proving:
    Runtime.execute_request() -> RuntimeCompilerService -> BackendOperationGraph -> ExecutionEngine -> Dispatcher -> Backend Adapter
    """
    builder = RuntimeBuilder()
    flags = FeatureFlags(COMPILER_RUNTIME_ENABLED=True)
    builder.with_feature_flags(flags)
    runtime = builder.build()

    # Mock compiler service
    runtime.compiler_service = MagicMock()
    mock_translation_result = MagicMock()

    mock_op = MagicMock()
    mock_op.dependencies = []
    mock_translation_result.backend_graph = MockGraph(operations={"op1": mock_op}, roots=("op1",))
    runtime.compiler_service.run_compilation.return_value = mock_translation_result

    # Mock adapter registry
    mock_adapter = MagicMock()
    mock_adapter.execute.return_value = "executed_by_adapter"
    runtime.adapter_registry = MagicMock()
    runtime.adapter_registry.resolve.return_value = mock_adapter

    request = MagicMock()
    request.model = "test_model"

    result = runtime.execute_request(request)
    assert result is not None
    assert result.status == ExecutionStatus.COMPLETED
    assert result.model_output["last_output"] == "executed_by_adapter"
    assert mock_adapter.execute.call_count == 1

def test_legacy_fallback():
    builder = RuntimeBuilder()
    flags = FeatureFlags(COMPILER_RUNTIME_ENABLED=False, LEGACY_RUNTIME_ENABLED=True)
    builder.with_feature_flags(flags)
    runtime = builder.build()

    request = MagicMock()
    request.model = "test_model"

    with pytest.raises(NotImplementedError):
        runtime.execute_request(request)
