from typing import List, Optional
import time

from omlx.planner.domains.batch.artifacts import BatchPlan
from omlx.planner.compiler.batch.artifacts import (
    BatchExecutionGraph,
    BatchRealizationReport,
    BatchRealizationDiagnostic,
    BatchRealizationStatistics,
    BatchGroupingGraph,
    BatchSynchronizationGraph
)

class BatchRealizer:
    def realize(self, plan: BatchPlan) -> BatchRealizationReport:
        start_time = time.time()

        # Realize grouping
        grouping_graph = self._realize_grouping(plan)

        # Realize synchronization
        sync_graph = self._realize_synchronization(plan)

        # Realize dependency (mocked here, might need full graph logic)

        # Generate execution graph
        execution_graph = BatchExecutionGraph(
            batch_id=plan.batch_descriptor.batch_id,
            grouping_graph=grouping_graph,
            synchronization_graph=sync_graph,
            nodes=[{"id": "node_1", "type": "batch_op"}],
            edges=[]
        )

        latency = (time.time() - start_time) * 1000
        stats = BatchRealizationStatistics(
            realization_latency_ms=latency,
            batch_size=len(plan.batch_descriptor.request_ids),
            synchronization_count=len(sync_graph.nodes),
            dependency_count=0
        )

        return BatchRealizationReport(
            success=True,
            batch_execution_graph=execution_graph,
            diagnostics=[],
            statistics=stats
        )

    def _realize_grouping(self, plan: BatchPlan) -> BatchGroupingGraph:
        return BatchGroupingGraph(
            batch_id=plan.batch_descriptor.batch_id,
            nodes=[{"id": f"group_{req_id}"} for req_id in plan.batch_descriptor.request_ids],
            edges=[]
        )

    def _realize_synchronization(self, plan: BatchPlan) -> BatchSynchronizationGraph:
        return BatchSynchronizationGraph(
            batch_id=plan.batch_descriptor.batch_id,
            nodes=[{"id": "sync_point_1"}],
            edges=[]
        )
