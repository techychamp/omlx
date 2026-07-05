# SPDX-License-Identifier: Apache-2.0
"""
Executor for OMLX Execution Engine.
"""

from typing import Any
import time
import logging

from .interfaces import ExecutionExecutor, GraphExecutor
from .types import ExecutionResult, ExecutionStatus
from .context import ExecutionContext
from .artifacts import BackendOperationGraph

logger = logging.getLogger("omlx.execution.executor")

class ImmutableExecutionExecutor(ExecutionExecutor):
    """
    Executes BackendOperationGraph and collects metadata.
    """
    def __init__(self, graph_executor: GraphExecutor):
        self._graph_executor = graph_executor

    def execute(self, graph: BackendOperationGraph, context: ExecutionContext) -> ExecutionResult:
        logger.debug("ExecutionExecutor starting graph execution")
        start_time = time.time()

        try:
            result = self._graph_executor.traverse_and_execute(graph, context)

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            # Create a new result to add duration if the graph executor didn't already
            if result.execution_duration_ms == 0.0:
                 return ExecutionResult(
                     status=result.status,
                     model_output=result.model_output,
                     diagnostics=result.diagnostics,
                     statistics=result.statistics,
                     execution_duration_ms=duration_ms
                 )
            return result
        except Exception as e:
            logger.error(f"ExecutionExecutor failed: {e}", exc_info=True)
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None,
                execution_duration_ms=(time.time() - start_time) * 1000
            )
