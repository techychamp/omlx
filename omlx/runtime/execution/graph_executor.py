# SPDX-License-Identifier: Apache-2.0
"""
Graph Executor for OMLX Execution Engine.
"""

from typing import Any, Union
import logging
import time

from .interfaces import GraphExecutor, ExecutionDispatcher
from .types import ExecutionResult, ExecutionStatus
from .context import ExecutionContext
from .artifacts import BackendOperationGraph
from .statistics import ExecutionStatistics

from omlx.runtime.scheduling.scheduler import GraphScheduler
from omlx.runtime.scheduling.artifacts import DependencyGraph

logger = logging.getLogger("omlx.execution.graph_executor")

class DeterministicGraphExecutor(GraphExecutor):
    """
    Validates and traverses dependency graphs, invoking ExecutionDispatcher.
    """
    def __init__(self, dispatcher: ExecutionDispatcher, scheduler: GraphScheduler = None):
        self.dispatcher = dispatcher
        self.scheduler = scheduler or GraphScheduler()

    def traverse_and_execute(self, graph: Union[BackendOperationGraph, DependencyGraph], context: ExecutionContext) -> ExecutionResult:
        logger.debug("GraphExecutor building schedule and traversing graph")

        start_time = time.time()

        if not graph:
            logger.error("No graph provided to GraphExecutor")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )

        # Basic validation
        if not hasattr(graph, 'operations'):
            logger.error("Invalid graph: missing operations")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )

        # Build schedule
        schedule = self.scheduler.build_schedule(graph)
        execution_order = schedule.ordered_operations

        operations = graph.operations
        if len(execution_order) != len(operations):
            logger.warning(f"Graph traversal incomplete: cycle detected or missing operations. Traversed {len(execution_order)}/{len(operations)}")

        # Pass ordered nodes to dispatcher
        dispatch_result = self.dispatcher.dispatch(graph, context, execution_order=execution_order, schedule=schedule)

        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000

        stats = ExecutionStatistics(
            executed_operations=len(execution_order),
            backend_invocations=len(execution_order),
            execution_duration_ms=duration_ms,
            graph_depth=schedule.statistics.graph_depth if schedule.statistics else 1,
            execution_groups=len(schedule.execution_groups) if schedule.execution_groups else 1,
            dispatcher_calls=len(execution_order),
            adapter_calls=len(execution_order),
            compiler_execution_count=1,
            legacy_fallback_count=0
        )

        return ExecutionResult(
            status=dispatch_result.status,
            model_output=dispatch_result.model_output,
            diagnostics=schedule.diagnostics, # Expose schedule diagnostics
            statistics=stats,
            execution_duration_ms=duration_ms
        )
