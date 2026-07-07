from typing import Optional
from omlx.planner.domains.batch.artifacts import BatchPlan
from omlx.planner.compiler.batch.artifacts import BatchExecutionGraph, BatchRealizationReport
from omlx.planner.compiler.batch.realizer import BatchRealizer

class Compiler:
    def __init__(self):
        self.batch_realizer = BatchRealizer()

    def realize_batch(self, plan: BatchPlan) -> BatchRealizationReport:
        """
        Compiler is the sole owner of batch realization.
        It converts a BatchPlan into a BatchExecutionGraph.
        """
        return self.batch_realizer.realize(plan)
