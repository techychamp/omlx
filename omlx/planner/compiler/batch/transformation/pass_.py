from typing import Optional
from omlx.planner.compiler.passes import LogicalPass
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.domains.batch.artifacts import BatchPlan
from omlx.planner.compiler.batch.realizer import BatchRealizer
from omlx.planner.compiler.batch.artifacts import BatchRealizationReport

class BatchRealizationPass(LogicalPass):
    """
    Transforms ExecutionIR by applying Batching constraints.
    Integrates the BatchRealization domain into the canonical compilation pipeline.
    """
    def __init__(self, plan: BatchPlan):
        super().__init__(name="BatchRealizationPass")
        self.plan = plan
        self.realizer = BatchRealizer()
        self.report: Optional[BatchRealizationReport] = None

    def apply(self, ir: ExecutionIR) -> ExecutionIR:
        # Generate the realization report and execution graph
        self.report = self.realizer.realize(self.plan)

        # In a fully realized system, this pass would traverse `ir.nodes`
        # and wrap or annotate them with batching constraints derived from
        # `self.report.batch_execution_graph`.

        # For BATCH-002, we execute the realizer to generate the immutable artifacts
        # and attach the report so the CompilerEngine can observe it.
        # The IR structure itself is preserved pending BATCH-003.

        return ir
