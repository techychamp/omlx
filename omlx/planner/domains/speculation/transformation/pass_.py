# SPDX-License-Identifier: Apache-2.0
"""
Speculative Realization Pass.
"""

from omlx.planner.compiler.passes import LogicalPass

from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.domains.speculation.artifacts import SpeculativeExecutionDescriptor, SpeculativeRealizationReport
from omlx.planner.domains.speculation.realizer import SpeculativeRealizer

class SpeculationRealizationPass(LogicalPass):
    """
    Transforms the ExecutionIR based on the SpeculativeExecutionDescriptor.
    """

    def __init__(self, plan: SpeculativeExecutionDescriptor):
        self.plan = plan
        self.realizer = SpeculativeRealizer()
        self.report: SpeculativeRealizationReport | None = None

    @property
    def name(self) -> str:
        return "SpeculationRealizationPass"

    def apply(self, ir: ExecutionIR) -> ExecutionIR:
        """Executes the pass, utilizing the realizer."""
        self.report = self.realizer.realize(self.plan)

        # Currently, this is a mock realization pass that does not significantly mutate
        # the ExecutionIR but proves the architecture connects planning to the realization
        # step inside the compiler engine. In a production system, this would modify
        # the IR graph based on the output of the realizer.
        return ir
