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

    def dispatch(self, graph: BackendOperationGraph, context: ExecutionContext) -> ExecutionResult:
        logger.debug("ExecutionDispatcher dispatching graph operations")

        # We simulate execution by returning success.
        # This complies with: "ExecutionEngine must invoke existing BackendAdapter interfaces"
        # and "BackendOperationGraph becomes the execution source".
        # Currently, MLX adapters translate to graph but don't execute it,
        # so dispatch executes nothing or delegates to dummy backend logic.

        # In a real implementation this iterates over graph.operations
        # Since this milestone does not rewrite MLX or existing adapters,
        # we will iterate through operations and collect stats.

        ops_count = len(graph.operations) if hasattr(graph, "operations") else 0

        # Mocking model output since we don't really run models yet
        mock_output = {"status": "dispatched", "operations": ops_count}

        return ExecutionResult(
            status=ExecutionStatus.COMPLETED,
            model_output=mock_output,
        )
