# SPDX-License-Identifier: Apache-2.0
"""
Dispatcher for OMLX Execution Engine.
"""

from typing import Any
import logging
import time

from .interfaces import ExecutionDispatcher
from .types import ExecutionResult, ExecutionStatus
from .context import ExecutionContext
from .artifacts import BackendOperationGraph

logger = logging.getLogger("omlx.execution.dispatcher")

class SequentialExecutionDispatcher(ExecutionDispatcher):
    """
    Dispatches graph operations sequentially without scheduling logic.
    Assumes operations are ordered by GraphExecutor.
    """
    def __init__(self, adapter_registry: Any = None):
        self.adapter_registry = adapter_registry

    def dispatch(self, graph: BackendOperationGraph, context: ExecutionContext, execution_order=None) -> ExecutionResult:
        logger.debug("ExecutionDispatcher dispatching graph operations")

        if not execution_order and hasattr(graph, 'operations'):
            execution_order = list(graph.operations.keys())

        if not execution_order:
             return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
             )

        adapter = getattr(context, 'adapter', None)
        if adapter is None and self.adapter_registry:
            adapter = self.adapter_registry.resolve(backend="mlx", hardware="any", execution_family="autoregressive", execution_mode="standard")

        ops_executed = 0
        last_output = None

        for op_id in execution_order:
            op = graph.operations[op_id]
            if adapter and hasattr(adapter, 'execute'):
                 # Formal BackendAdapter.execute boundary
                 last_output = adapter.execute(op, context)
            ops_executed += 1

        mock_output = {"status": "dispatched", "operations": ops_executed, "last_output": last_output}

        return ExecutionResult(
            status=ExecutionStatus.COMPLETED,
            model_output=mock_output,
        )