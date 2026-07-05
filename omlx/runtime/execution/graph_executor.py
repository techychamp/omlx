# SPDX-License-Identifier: Apache-2.0
"""
Graph Executor for OMLX Execution Engine.
"""

from typing import Any
import logging
import time

from .interfaces import GraphExecutor, ExecutionDispatcher
from .types import ExecutionResult, ExecutionStatus
from .context import ExecutionContext
from .artifacts import BackendOperationGraph
from .statistics import ExecutionStatistics

logger = logging.getLogger("omlx.execution.graph_executor")

class DeterministicGraphExecutor(GraphExecutor):
    """
    Validates and traverses BackendOperationGraph, invoking ExecutionDispatcher.
    """
    def __init__(self, dispatcher: ExecutionDispatcher):
        self.dispatcher = dispatcher

    def traverse_and_execute(self, graph: BackendOperationGraph, context: ExecutionContext) -> ExecutionResult:
        logger.debug("GraphExecutor validating and traversing graph")

        start_time = time.time()

        if not graph:
            logger.error("No BackendOperationGraph provided to GraphExecutor")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )

        # Basic validation (must have operations)
        if not hasattr(graph, 'operations'):
            logger.error("Invalid BackendOperationGraph: missing operations")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )

        # Let dispatcher handle the sequential execution of the graph
        dispatch_result = self.dispatcher.dispatch(graph, context)

        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000

        # Build statistics
        op_count = len(graph.operations)
        stats = ExecutionStatistics(
            executed_operations=op_count,
            backend_invocations=1,
            execution_duration_ms=duration_ms,
            graph_depth=1,  # Simplified
            execution_groups=1,
            dispatcher_calls=1,
            adapter_calls=0,
            compiler_execution_count=1,
            legacy_fallback_count=0
        )

        return ExecutionResult(
            status=dispatch_result.status,
            model_output=dispatch_result.model_output,
            diagnostics=dispatch_result.diagnostics,
            statistics=stats,
            execution_duration_ms=duration_ms
        )
