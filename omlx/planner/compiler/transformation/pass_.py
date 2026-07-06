from typing import Any
from omlx.planner.compiler.passes import LogicalPass
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.domains.fusion.artifacts import FusionPlan
from .realizer import FusionRealizer
from .validator import TransformationValidator

class FusionRealizationPass(LogicalPass):
    """
    Logical compiler pass that realizes a FusionPlan into the ExecutionIR.
    """
    def __init__(self, plan: FusionPlan):
        self._plan = plan
        self._realizer = FusionRealizer()
        self._validator = TransformationValidator()
        self._report = None

    @property
    def name(self) -> str:
        return "FusionRealizationPass"

    def apply(self, ir: ExecutionIR) -> ExecutionIR:
        if not self._plan or not self._plan.groups:
            return ir

        transformed_ir, report = self._realizer.realize(ir, self._plan)

        # Ensure the transformed graph is valid
        validation_report = self._validator.validate(ir, transformed_ir)
        if not validation_report.is_valid:
            # If invalid, rollback and return the original graph
            # In a full implementation, we might raise a CompilerError or log a warning
            return ir

        self._report = report
        return transformed_ir

    @property
    def report(self) -> Any:
        return self._report
