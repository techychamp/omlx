# SPDX-License-Identifier: Apache-2.0
from typing import Any
from omlx.planner.compiler.passes import LogicalPass
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.domains.memory.artifacts import MemoryPlan
from .realizer import MemoryRealizer
from .validator import MemoryTransformationValidator

class MemoryRealizationPass(LogicalPass):
    """
    Logical compiler pass that realizes a MemoryPlan into the ExecutionIR.
    """
    def __init__(self, plan: MemoryPlan):
        self._plan = plan
        self._realizer = MemoryRealizer()
        self._validator = MemoryTransformationValidator()
        self._report = None

    @property
    def name(self) -> str:
        return "MemoryRealizationPass"

    def apply(self, ir: ExecutionIR) -> ExecutionIR:
        if not self._plan:
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
