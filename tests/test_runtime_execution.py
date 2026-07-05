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
    graph = MockGraph(operations={"op1": "val1"})
    context = ExecutionContext(request_context=Mock(), backend_operation_graph=graph)
    result = engine.execute(context)
    assert result.status == ExecutionStatus.COMPLETED
    assert result.model_output["operations"] == 1
    assert result.statistics is not None
    assert result.statistics.executed_operations == 1

def test_dispatcher_mock():
    dispatcher = SequentialExecutionDispatcher()
    graph = MockGraph(operations={"op1": "val1", "op2": "val2"})
    context = ExecutionContext(request_context=Mock(), backend_operation_graph=graph)
    result = dispatcher.dispatch(graph, context)
    assert result.status == ExecutionStatus.COMPLETED
    assert result.model_output["operations"] == 2

def test_runtime_builder_integration():
    builder = RuntimeBuilder()
    flags = FeatureFlags(COMPILER_RUNTIME_ENABLED=True)
    builder.with_feature_flags(flags)
    runtime = builder.build()

    assert hasattr(runtime, 'execution_engine')
    assert runtime.execution_engine is not None

def test_runtime_execute_request():
    builder = RuntimeBuilder()
    flags = FeatureFlags(COMPILER_RUNTIME_ENABLED=True)
    builder.with_feature_flags(flags)
    runtime = builder.build()

    # Mock compiler service
    runtime.compiler_service = MagicMock()
    mock_translation_result = MagicMock()
    mock_translation_result.backend_graph = MockGraph(operations={"op1": "val1"})
    runtime.compiler_service.run_compilation.return_value = mock_translation_result

    request = MagicMock()
    request.model = "test_model"

    result = runtime.execute_request(request)
    assert result is not None
    assert result.status == ExecutionStatus.COMPLETED

def test_legacy_fallback():
    builder = RuntimeBuilder()
    flags = FeatureFlags(COMPILER_RUNTIME_ENABLED=False, LEGACY_RUNTIME_ENABLED=True)
    builder.with_feature_flags(flags)
    runtime = builder.build()

    request = MagicMock()
    request.model = "test_model"

    result = runtime.execute_request(request)
    assert result is None
