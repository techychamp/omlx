# SPDX-License-Identifier: Apache-2.0
from typing import Any
from omlx.planner.compiler.passes import LogicalPass
from omlx.planner.ir.graph import ExecutionIR
from omlx.framework.cache.plan import CachePlan
from .realizer import CacheRealizer
from .validator import CacheTransformationValidator
from omlx.planner.domains.cache.artifacts import CacheRealizationReport

class CacheRealizationPass(LogicalPass):
    """
    Logical compiler pass that realizes a CachePlan into the ExecutionIR.
    """
    def __init__(self, plan: CachePlan):
        self._plan = plan
        self._realizer = CacheRealizer()
        self._validator = CacheTransformationValidator()
        self._report = None

    @property
    def name(self) -> str:
        return "CacheRealizationPass"

    def apply(self, ir: ExecutionIR) -> ExecutionIR:
        if not self._plan:
            return ir

        transformed_ir, report = self._realizer.realize(ir, self._plan)

        validation_report = self._validator.validate(ir, transformed_ir)
        if not validation_report.is_valid:
            # If invalid, rollback and return the original graph, but surface diagnostics
            self._report = CacheRealizationReport(
                is_successful=False,
                statistics=report.statistics,
                diagnostics=validation_report.diagnostics,
                execution_graph=report.execution_graph
            )
            return ir

        self._report = report
        return transformed_ir

    @property
    def report(self) -> Any:
        return self._report
