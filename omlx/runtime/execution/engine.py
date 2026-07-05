# SPDX-License-Identifier: Apache-2.0
"""
Execution Engine for OMLX runtime.
"""

import time
import logging
from typing import Any

from .types import ExecutionResult, ExecutionStatus
from .context import ExecutionContext
from .interfaces import ExecutionExecutor, GraphExecutor, ExecutionDispatcher
from .executor import ImmutableExecutionExecutor
from .graph_executor import DeterministicGraphExecutor
from .dispatcher import SequentialExecutionDispatcher

logger = logging.getLogger("omlx.execution.engine")

class ExecutionEngine:
    """
    Primary entry point for executing an intent using the Compiler artifacts.
    """
    def __init__(self, executor: ExecutionExecutor = None):
        if executor is None:
            # Construct default composition
            dispatcher = SequentialExecutionDispatcher()
            graph_executor = DeterministicGraphExecutor(dispatcher)
            self._executor = ImmutableExecutionExecutor(graph_executor)
        else:
            self._executor = executor

    def execute(self, context: ExecutionContext) -> ExecutionResult:
        """
        Executes the compiled intent using the provided context.
        """
        logger.debug("ExecutionEngine starting execution")

        if not context.backend_operation_graph:
            logger.error("ExecutionContext missing backend_operation_graph")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )

        try:
            return self._executor.execute(context.backend_operation_graph, context)
        except Exception as e:
            logger.error(f"ExecutionEngine encountered error: {e}", exc_info=True)
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )
