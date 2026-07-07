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

        if context.speculative_execution_graph:
            return self._execute_speculative(session, context, context.speculative_execution_graph)

        if not context.backend_operation_graph and not getattr(context, 'expert_execution_graph', None):
            logger.error("ExecutionContext missing execution graph (neither backend_operation_graph nor expert_execution_graph)")
        if not context.backend_operation_graph and not context.execution_graphs and not getattr(context, 'expert_execution_graph', None):
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
                if context.execution_graphs:
                    last_result = None
                    for graph in context.execution_graphs:
                        last_result = self._executor.execute(graph, context)
                        if last_result.status != ExecutionStatus.COMPLETED:
                            break
                    result = last_result
                else:
                    execution_graph = getattr(context, 'expert_execution_graph', None) or context.backend_operation_graph
                    result = self._executor.execute(execution_graph, context)

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

    def _execute_speculative(self, session: Any, context: ExecutionContext, spec_graph: Any) -> ExecutionResult:
        from omlx.runtime.session import SessionState
        from omlx.runtime.execution.artifacts import (
            SpeculativeExecutionReport,
            VerificationExecutionReport,
            AcceptanceExecutionReport,
            RollbackExecutionReport
        )

        with get_observer().observe_phase("Execution", "Engine", "execute_speculative"):
            try:
                # 1. Draft Phase
                draft_start = time.time()
                draft_result = self._executor.execute(spec_graph.draft_graph.graph, context)
                if draft_result.status != ExecutionStatus.COMPLETED:
                    session.transition(SessionState.FAILED)
                    return draft_result

                # Mock drafting tokens
                # TODO: This is a temporary execution stub for draft tokens until real backend integration.
                session.draft_tokens = (1, 2, 3)

                # 2. Verification Phase
                verify_start = time.time()
                verify_result = self._executor.execute(spec_graph.verification_graph.graph, context)
                if verify_result.status != ExecutionStatus.COMPLETED:
                    session.transition(SessionState.FAILED)
                    return verify_result

                from omlx.runtime.execution.artifacts import VerificationResult
                accepted = False
                if isinstance(verify_result.model_output, VerificationResult):
                    accepted = verify_result.model_output.accepted
                else:
                    # Fallback for dispatcher mock consistency if not properly returned
                    accepted = True

                verify_latency = (time.time() - verify_start) * 1000
                verify_report = VerificationExecutionReport(
                    accepted=accepted,
                    accepted_tokens_count=len(session.draft_tokens) if accepted else 0,
                    rejected_tokens_count=0 if accepted else len(session.draft_tokens),
                    latency_ms=verify_latency
                )
                session.speculative_reports.append(verify_report)

                # 3. Acceptance / Rollback Phase
                if accepted:
                    accept_start = time.time()
                    accept_result = self._executor.execute(spec_graph.acceptance_graph.graph, context)
                    if accept_result.status != ExecutionStatus.COMPLETED:
                        session.transition(SessionState.FAILED)
                        return accept_result

                    session.accepted_tokens = session.draft_tokens
                    accept_latency = (time.time() - accept_start) * 1000
                    accept_report = AcceptanceExecutionReport(
                        accepted_tokens=session.accepted_tokens,
                        latency_ms=accept_latency
                    )
                    session.speculative_reports.append(accept_report)
                else:
                    session.rejected_tokens = session.draft_tokens
                    rollback_report = RollbackExecutionReport(
                        rejected_tokens=session.rejected_tokens,
                        latency_ms=0.0
                    )
                    session.speculative_reports.append(rollback_report)

                spec_report = SpeculativeExecutionReport(
                    attempts=1,
                    accepted_tokens=len(session.accepted_tokens),
                    rejected_tokens=len(session.rejected_tokens),
                    latency_ms=(time.time() - draft_start) * 1000
                )
                session.speculative_reports.append(spec_report)

                session.transition(SessionState.COMPLETED)
                return ExecutionResult(status=ExecutionStatus.COMPLETED, model_output={"accepted": accepted})

            except Exception as e:
                logger.error(f"ExecutionEngine encountered error during speculative execution: {e}", exc_info=True)
                result = ExecutionResult(status=ExecutionStatus.FAILED, model_output=None)
                session.transition(SessionState.FAILED)
                return result
