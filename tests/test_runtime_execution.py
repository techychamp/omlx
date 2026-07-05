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

def test_parallel_execution_dispatcher():
    from omlx.runtime.execution.dispatcher import ParallelExecutionDispatcher
    from omlx.runtime.execution.context import ExecutionContext
    from omlx.runtime.execution.types import ExecutionStatus
    from omlx.runtime.scheduling.schedule import ExecutionSchedule
    from omlx.runtime.scheduling.group import ExecutionGroup

    dispatcher = ParallelExecutionDispatcher(max_workers=2)

    mock_op1 = MagicMock()
    mock_op2 = MagicMock()
    mock_op3 = MagicMock()

    graph = MockGraph(operations={"op1": mock_op1, "op2": mock_op2, "op3": mock_op3})

    import threading
    lock = threading.Lock()
    execution_record = []

    def mock_execute(op, context):
        import time
        time.sleep(0.01) # to simulate some work and ensure threads interleave
        with lock:
            execution_record.append(op)
        return "output"

    mock_adapter = MagicMock()
    mock_adapter.execute.side_effect = mock_execute

    context = ExecutionContext(request_context=Mock(), adapter=mock_adapter)

    # group1: op1 and op2 (parallel), group2: op3
    group1 = ExecutionGroup(group_id="g1", operations=["op1", "op2"])
    group2 = ExecutionGroup(group_id="g2", operations=["op3"])
    schedule = ExecutionSchedule(execution_groups=[group1, group2])

    result = dispatcher.dispatch(graph, context, schedule=schedule)

    assert result.status == ExecutionStatus.COMPLETED
    assert result.model_output["operations"] == 3
    assert result.model_output["last_output"] == "output"

    assert len(execution_record) == 3
    # op3 must run after op1 and op2 because it's in a later group
    assert execution_record[2] == mock_op3

def test_parallel_execution_dispatcher_failure():
    from omlx.runtime.execution.dispatcher import ParallelExecutionDispatcher
    from omlx.runtime.execution.context import ExecutionContext
    from omlx.runtime.execution.types import ExecutionStatus
    from omlx.runtime.scheduling.schedule import ExecutionSchedule
    from omlx.runtime.scheduling.group import ExecutionGroup

    dispatcher = ParallelExecutionDispatcher(max_workers=2)

    mock_op1 = MagicMock()
    graph = MockGraph(operations={"op1": mock_op1})

    def mock_execute_fail(op, context):
        raise ValueError("Simulated failure")

    mock_adapter = MagicMock()
    mock_adapter.execute.side_effect = mock_execute_fail

    context = ExecutionContext(request_context=Mock(), adapter=mock_adapter)
    group1 = ExecutionGroup(group_id="g1", operations=["op1"])
    schedule = ExecutionSchedule(execution_groups=[group1])

    result = dispatcher.dispatch(graph, context, schedule=schedule)

    assert result.status == ExecutionStatus.FAILED
    assert result.model_output is None

def test_group_barrier_synchronization():
    from omlx.runtime.execution.dispatcher import ParallelExecutionDispatcher
    from omlx.runtime.execution.context import ExecutionContext
    from omlx.runtime.execution.types import ExecutionStatus
    from omlx.runtime.scheduling.schedule import ExecutionSchedule
    from omlx.runtime.scheduling.group import ExecutionGroup
    import time
    import threading

    dispatcher = ParallelExecutionDispatcher(max_workers=4)

    mock_op1 = MagicMock(id="op1")
    mock_op2 = MagicMock(id="op2")
    mock_op3 = MagicMock(id="op3")
    mock_op4 = MagicMock(id="op4")

    graph = MockGraph(operations={
        "op1": mock_op1,
        "op2": mock_op2,
        "op3": mock_op3,
        "op4": mock_op4
    })

    # We want to prove that op3 and op4 (group 2) DO NOT start until op1 and op2 (group 1) are COMPLETELY finished.
    active_operations = set()
    lock = threading.Lock()
    barrier_violation = False

    # Store history of when ops started and ended
    events = []

    def mock_execute(op, context):
        nonlocal barrier_violation
        with lock:
            active_operations.add(op.id)
            events.append((op.id, "start"))

            # Check for barrier violations
            if op.id in ["op3", "op4"] and ("op1" in active_operations or "op2" in active_operations):
                barrier_violation = True

        # Simulate work
        time.sleep(0.05)

        with lock:
            active_operations.remove(op.id)
            events.append((op.id, "end"))

        return "output"

    mock_adapter = MagicMock()
    mock_adapter.execute.side_effect = mock_execute

    context = ExecutionContext(request_context=Mock(), adapter=mock_adapter)

    # group1: op1 and op2, group2: op3 and op4
    group1 = ExecutionGroup(group_id="g1", operations=["op1", "op2"])
    group2 = ExecutionGroup(group_id="g2", operations=["op3", "op4"])
    schedule = ExecutionSchedule(execution_groups=[group1, group2])

    result = dispatcher.dispatch(graph, context, schedule=schedule)

    assert result.status == ExecutionStatus.COMPLETED
    assert result.model_output["operations"] == 4
    assert not barrier_violation, "Barrier violation detected: group 2 started before group 1 finished"

    # Analyze events strictly
    # op1/op2 starts must happen before any op1/op2 ends (if fully parallel and enough workers)
    # op3/op4 starts must happen AFTER ALL op1/op2 ends

    group1_ends = [i for i, e in enumerate(events) if e[0] in ["op1", "op2"] and e[1] == "end"]
    group2_starts = [i for i, e in enumerate(events) if e[0] in ["op3", "op4"] and e[1] == "start"]

    assert max(group1_ends) < min(group2_starts), "Group 2 operations started before Group 1 operations ended!"


def test_dispatcher_stress():
    from omlx.runtime.execution.dispatcher import ParallelExecutionDispatcher
    from omlx.runtime.execution.context import ExecutionContext
    from omlx.runtime.execution.types import ExecutionStatus
    from omlx.runtime.scheduling.schedule import ExecutionSchedule
    from omlx.runtime.scheduling.group import ExecutionGroup
    import concurrent.futures

    # Prepare context and graph
    mock_op1 = MagicMock(id="op1")
    graph = MockGraph(operations={"op1": mock_op1})

    mock_adapter = MagicMock()
    mock_adapter.execute.return_value = "stress_output"
    context = ExecutionContext(request_context=Mock(), adapter=mock_adapter)

    group1 = ExecutionGroup(group_id="g1", operations=["op1"])
    schedule = ExecutionSchedule(execution_groups=[group1])

    # 100 concurrent Runtime.generate() -> dispatcher invocations
    results = []

    def run_dispatcher():
        dispatcher = ParallelExecutionDispatcher(max_workers=2)
        return dispatcher.dispatch(graph, context, schedule=schedule)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as stress_executor:
        futures = [stress_executor.submit(run_dispatcher) for _ in range(100)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    assert len(results) == 100
    for r in results:
        assert r.status == ExecutionStatus.COMPLETED
        assert r.model_output["operations"] == 1
        assert r.model_output["last_output"] == "stress_output"

def test_dispatcher_determinism():
    from omlx.runtime.execution.dispatcher import ParallelExecutionDispatcher
    from omlx.runtime.execution.context import ExecutionContext
    from omlx.runtime.execution.types import ExecutionStatus
    from omlx.runtime.scheduling.schedule import ExecutionSchedule
    from omlx.runtime.scheduling.group import ExecutionGroup
    import threading

    # Simulate diamond graph:
    #   op1
    #  /   \
    # op2  op3
    #  \   /
    #   op4
    # Groups: g1:[op1], g2:[op2, op3], g3:[op4]

    dispatcher = ParallelExecutionDispatcher(max_workers=4)

    mock_ops = {f"op{i}": MagicMock(id=f"op{i}") for i in range(1, 5)}
    graph = MockGraph(operations=mock_ops)

    execution_orders = []
    lock = threading.Lock()

    def mock_execute(op, context):
        with lock:
            execution_orders[-1].append(op.id)
        return "output"

    mock_adapter = MagicMock()
    mock_adapter.execute.side_effect = mock_execute
    context = ExecutionContext(request_context=Mock(), adapter=mock_adapter)

    group1 = ExecutionGroup(group_id="g1", operations=["op1"])
    group2 = ExecutionGroup(group_id="g2", operations=["op2", "op3"])
    group3 = ExecutionGroup(group_id="g3", operations=["op4"])
    schedule = ExecutionSchedule(execution_groups=[group1, group2, group3])

    for _ in range(10):
        execution_orders.append([])
        result = dispatcher.dispatch(graph, context, schedule=schedule)
        assert result.status == ExecutionStatus.COMPLETED

    for order in execution_orders:
        # group 1 first
        assert order[0] == "op1"
        # group 2 ops can be in any order but must be indexes 1 and 2
        assert set(order[1:3]) == {"op2", "op3"}
        # group 3 last
        assert order[3] == "op4"
