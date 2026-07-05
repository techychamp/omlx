# SPDX-License-Identifier: Apache-2.0
"""
Execution invariants verification testing.
Verifies ExecutionEngine and Dispatcher adhere to their execution boundaries.
"""

import pytest
from unittest.mock import MagicMock
from collections import namedtuple

from omlx.runtime.execution.dispatcher import SequentialExecutionDispatcher
from omlx.runtime.execution.context import ExecutionContext
from omlx.runtime.execution.types import ExecutionStatus

# Mock structures
MockGraph = namedtuple("MockGraph", ["operations"])

def test_execution_engine_consumes_schedule_only():
    """Verify that ExecutionDispatcher works strictly off a schedule (execution_order)."""
    dispatcher = SequentialExecutionDispatcher()

    mock_op_A = MagicMock()
    mock_op_B = MagicMock()

    graph = MockGraph(operations={
        "A": mock_op_A,
        "B": mock_op_B
    })

    context = ExecutionContext()

    # Force execution order
    execution_order = ["B", "A"]

    result = dispatcher.dispatch(graph, context, execution_order=execution_order)
    assert result.status == ExecutionStatus.COMPLETED
    assert result.model_output["operations"] == 2

def test_dispatcher_execution_order_adherence():
    """Verify that the dispatcher faithfully follows the exact order provided."""
    mock_adapter = MagicMock()
    mock_adapter.execute.side_effect = lambda op, ctx: op

    class MockRegistry:
        def resolve(self, **kwargs):
            return mock_adapter

    dispatcher = SequentialExecutionDispatcher(adapter_registry=MockRegistry())

    graph = MockGraph(operations={
        "X": "OperationX",
        "Y": "OperationY",
        "Z": "OperationZ"
    })

    context = ExecutionContext()
    execution_order = ["Y", "Z", "X"]

    result = dispatcher.dispatch(graph, context, execution_order=execution_order)

    assert result.status == ExecutionStatus.COMPLETED
    assert result.model_output["operations"] == 3
    # Verify adapter was called for all items
    assert mock_adapter.execute.call_count == 3

    # Check calling order
    calls = mock_adapter.execute.call_args_list
    assert calls[0][0][0] == "OperationY"
    assert calls[1][0][0] == "OperationZ"
    assert calls[2][0][0] == "OperationX"
