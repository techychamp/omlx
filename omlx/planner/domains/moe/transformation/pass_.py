# SPDX-License-Identifier: Apache-2.0
from typing import Any
from omlx.planner.compiler.passes import LogicalPass
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.domains.moe.artifacts import MoEPlan
from .realizer import MoERealizer
from .validator import MoETransformationValidator

class MoERealizationPass(LogicalPass):
    """
    Logical compiler pass that realizes a MoEPlan into the ExecutionIR.
    """
    def __init__(self, plan: MoEPlan):
        self._plan = plan
        self._realizer = MoERealizer()
        self._validator = MoETransformationValidator()
        self._report = None

    @property
    def name(self) -> str:
        return "MoERealizationPass"

    def apply(self, ir: ExecutionIR) -> ExecutionIR:
        if not self._plan or not self._plan.groups:
            return ir

        transformed_ir, report = self._realizer.realize(ir, self._plan)

        validation_report = self._validator.validate(ir, transformed_ir)
        if not validation_report.is_valid:
            # If invalid, rollback and return the original graph
            return ir

        self._report = report
        return transformed_ir

    @property
    def report(self) -> Any:
        return self._report
