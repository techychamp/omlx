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
from .dispatcher import SequentialExecutionDispatcher, ParallelExecutionDispatcher
from omlx.runtime.observability import get_observer

logger = logging.getLogger("omlx.execution.engine")

class ExecutionEngine:
    """
    Primary entry point for executing an intent using the Compiler artifacts.
    """
    def __init__(self, executor: ExecutionExecutor = None):
        if executor is None:
            # Construct default composition
            dispatcher = ParallelExecutionDispatcher()
            graph_executor = DeterministicGraphExecutor(dispatcher)
            self._executor = ImmutableExecutionExecutor(graph_executor)
        else:
            self._executor = executor

    def execute(self, session: Any) -> ExecutionResult:
        """
        Executes the compiled intent using the provided RuntimeSession.
        """
        context = session.execution_context

        logger.debug("ExecutionEngine starting execution")

        if not context.backend_operation_graph and not getattr(context, 'expert_execution_graph', None):
            logger.error("ExecutionContext missing execution graph (neither backend_operation_graph nor expert_execution_graph)")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )

        with get_observer().observe_phase("Execution", "Engine", "execute"):
            try:
                # The execution engine purely consumes the context.
                # If cache is required, it accesses session.cache_session without managing its lifecycle.
                if getattr(session, "cache_session", None):
                    logger.debug(f"ExecutionEngine utilizing cache session for plan: {session.cache_session.cache_plan.plan_id}")

                execution_graph = getattr(context, 'expert_execution_graph', None) or context.backend_operation_graph
                result = self._executor.execute(execution_graph, context)
                get_observer().track_artifact("ExecutionResult", result)
                return result
            except Exception as e:
                logger.error(f"ExecutionEngine encountered error: {e}", exc_info=True)
                result = ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    model_output=None
                )
                get_observer().track_artifact("ExecutionResult", result)
                return result
