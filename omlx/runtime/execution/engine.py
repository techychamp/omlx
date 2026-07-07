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


    def _execute_subgraph(self, original_graph: Any, node_ids: tuple[str, ...], context: ExecutionContext) -> ExecutionResult:
        from omlx.planner.compiler.backend.operations import BackendOperationGraph
        from types import MappingProxyType

        subset_ops = {nid: original_graph.operations[nid] for nid in node_ids if nid in original_graph.operations}
        subgraph = BackendOperationGraph(
            backend_id=original_graph.backend_id,
            operations=MappingProxyType(subset_ops),
            roots=tuple(nid for nid in node_ids if nid in original_graph.roots),
            barriers=original_graph.barriers,
            synchronization_points=original_graph.synchronization_points,
            metadata=original_graph.metadata
        )
        return self._executor.execute(subgraph, context)

    def execute(self, session: Any) -> ExecutionResult:
        """
        Executes the compiled intent using the provided RuntimeSession.
        """
        from omlx.runtime.session import SessionState
        session.transition(SessionState.EXECUTING)

        context = session.execution_context

        logger.debug("ExecutionEngine starting execution")

        if not context.backend_operation_graph and not getattr(context, 'expert_execution_graph', None):
            logger.error("ExecutionContext missing execution graph (neither backend_operation_graph nor expert_execution_graph)")
        if not context.backend_operation_graph and not context.execution_graphs:
            logger.error("ExecutionContext missing backend_operation_graph or execution_graphs")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )

        with get_observer().observe_phase("Execution", "Engine", "execute"):
            try:
                if getattr(session, "cache_session", None):
                    logger.debug(f"ExecutionEngine utilizing cache session for plan: {session.cache_session.cache_plan.plan_id}")

                if context.diffusion_execution_graph is not None:
                    # Diffusion specific execution
                    total_latency = 0.0

                    latent_nodes = tuple(node.id for node in context.diffusion_execution_graph.latent_graph.nodes)
                    latent_res = self._execute_subgraph(context.backend_operation_graph, latent_nodes, context)
                    total_latency += latent_res.execution_duration_ms

                    cond_nodes = tuple(node.id for node in context.diffusion_execution_graph.conditioning_graph.nodes)
                    cond_res = self._execute_subgraph(context.backend_operation_graph, cond_nodes, context)
                    total_latency += cond_res.execution_duration_ms

                    last_res = cond_res
                    for ts in context.diffusion_execution_graph.timesteps:
                        ts_nodes = tuple(node.id for node in ts.nodes)
                        ts_res = self._execute_subgraph(context.backend_operation_graph, ts_nodes, context)
                        total_latency += ts_res.execution_duration_ms
                        last_res = ts_res

                    from .diagnostics import DiffusionExecutionReport
                    report = DiffusionExecutionReport(
                        execution_latency_ms=total_latency,
                        total_timesteps_executed=len(context.diffusion_execution_graph.timesteps)
                    )
                    get_observer().artifact_tracker.track("DiffusionExecutionReport", report)

                    import dataclasses
                    if dataclasses.is_dataclass(last_res):
                        result = dataclasses.replace(last_res, execution_duration_ms=total_latency)
                    else:
                        result = ExecutionResult(status=ExecutionStatus.COMPLETED, model_output=getattr(last_res, "model_output", None), execution_duration_ms=total_latency)
                else:
                    # Standard canonical graph execution
                    result = self._executor.execute(context.backend_operation_graph, context)

                execution_graph = getattr(context, 'expert_execution_graph', None) or context.backend_operation_graph
                result = self._executor.execute(execution_graph, context)
                if context.execution_graphs:
                    last_result = None
                    for graph in context.execution_graphs:
                        last_result = self._executor.execute(graph, context)
                        if last_result.status != ExecutionStatus.COMPLETED:
                            break
                    result = last_result
                else:
                    result = self._executor.execute(context.backend_operation_graph, context)

                get_observer().track_artifact("ExecutionResult", result)

                if result.status == ExecutionStatus.COMPLETED:
                     session.transition(SessionState.COMPLETED)
                else:
                     session.transition(SessionState.FAILED)

                return result
            except Exception as e:
                logger.error(f"ExecutionEngine encountered error: {e}", exc_info=True)
                result = ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    model_output=None
                )
                session.transition(SessionState.FAILED)
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
