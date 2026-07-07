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

def _get_operation_from_graph(graph: Any, op_id: str) -> Any:
    if hasattr(graph, 'operations') and op_id in graph.operations:
        return graph.operations[op_id]
    elif type(graph).__name__ == 'ExpertExecutionGraph' and hasattr(graph, 'routing_graph'):
        if graph.routing_graph.routing_node.id == op_id:
            return graph.routing_graph.routing_node
        for expert in graph.routing_graph.expert_graphs:
            for node in expert.expert_nodes:
                if node.id == op_id:
                    return node
    return None


class SequentialExecutionDispatcher(ExecutionDispatcher):
    """
    Dispatches graph operations sequentially without scheduling logic.
    Assumes operations are ordered by GraphExecutor.
    """
    def __init__(self):
        pass

    def dispatch(self, graph: Any, context: ExecutionContext, execution_order=None, schedule=None) -> ExecutionResult:
        logger.debug("SequentialExecutionDispatcher dispatching graph operations")

        if not execution_order:
            if hasattr(graph, 'operations'):
                execution_order = list(graph.operations.keys())
            elif type(graph).__name__ == 'ExpertExecutionGraph':
                execution_order = [graph.routing_graph.routing_node.id]
                for e in graph.routing_graph.expert_graphs:
                    for n in e.expert_nodes:
                        execution_order.append(n.id)

        if not execution_order:
             return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
             )

        adapter = getattr(context, 'adapter', None)
        if adapter is None:
            logger.error("No BackendAdapter found in ExecutionContext")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )

        ops_executed = 0
        last_output = None

        for op_id in execution_order:
            op = _get_operation_from_graph(graph, op_id)
            if not op:
                continue
            if hasattr(adapter, 'execute'):
                 # Formal BackendAdapter.execute boundary
                 out = adapter.execute(op, context)
                 if out and isinstance(out, dict) and out.get("result") is not None:
                     res = out.get("result")
                     if isinstance(res, dict) and ("logits" in res or "logits_shape" in res):
                         last_output = out
            ops_executed += 1

        mock_output = {"status": "dispatched", "operations": ops_executed, "last_output": last_output}

        return ExecutionResult(
            status=ExecutionStatus.COMPLETED,
            model_output=mock_output,
        )

class ParallelExecutionDispatcher(ExecutionDispatcher):
    """
    Dispatches graph operations concurrently based on ExecutionGroups provided in the schedule.
    Operations within the same group are executed in parallel.
    """
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers
        import concurrent.futures
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)

    def dispatch(self, graph: Any, context: ExecutionContext, execution_order=None, schedule=None) -> ExecutionResult:
        logger.debug("ParallelExecutionDispatcher dispatching graph operations")

        if not schedule or not hasattr(schedule, 'execution_groups') or not schedule.execution_groups:
            logger.error("ParallelExecutionDispatcher requires a valid ExecutionSchedule with execution_groups")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )

        adapter = getattr(context, 'adapter', None)
        if adapter is None:
            logger.error("No BackendAdapter found in ExecutionContext")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )

        ops_executed = 0
        last_output = None
        has_failure = False

        from omlx.runtime.observability import get_observer
        import threading
        import concurrent.futures

        has_adapter_execute = hasattr(adapter, 'execute')

        for group in schedule.execution_groups:
            if has_failure:
                break

            with get_observer().observe_phase("Execution", "Group", f"group_{group.group_id}") as group_phase:
                futures = []
                for op_id in group.operations:
                    op = _get_operation_from_graph(graph, op_id)
                    if not op:
                        logger.error(f"Operation {op_id} from schedule not found in graph")
                        has_failure = True
                        break

                    if has_adapter_execute:
                        def exec_with_obs(inner_op, inner_context):
                            thread_id = threading.get_ident()
                            with get_observer().observe_phase("Execution", "Worker", f"op_{inner_op.id if hasattr(inner_op, 'id') else op_id}_thread_{thread_id}"):
                                return adapter.execute(inner_op, inner_context)
                        futures.append(self._executor.submit(exec_with_obs, op, context))
                    else:
                        ops_executed += 1

                if has_failure:
                    break

                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        if result is not None and isinstance(result, dict) and result.get("result") is not None:
                            res = result.get("result")
                            if isinstance(res, dict) and ("logits" in res or "logits_shape" in res):
                                last_output = result
                        ops_executed += 1
                    except Exception as e:
                        logger.error(f"Execution failed during parallel dispatch: {e}", exc_info=True)
                        has_failure = True
                        break # Stop processing this group, wait for others to finish before raising

        if has_failure:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )

        mock_output = {"status": "dispatched", "operations": ops_executed, "last_output": last_output}
        return ExecutionResult(
            status=ExecutionStatus.COMPLETED,
            model_output=mock_output,
        )
