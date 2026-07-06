# SPDX-License-Identifier: Apache-2.0
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNodeType
from .artifacts import ExpertValidationReport, ExpertRealizationDiagnostic
from types import MappingProxyType

class MoETransformationValidator:
    """Validates the MoE transformed graph."""

    def validate(self, original_ir: ExecutionIR, transformed_ir: ExecutionIR) -> ExpertValidationReport:
        diagnostics = []

        # Validate that no nodes were lost except those intentionally removed
        for nid in original_ir.nodes:
            if nid not in transformed_ir.nodes:
                diagnostics.append(
                    ExpertRealizationDiagnostic(
                        level="ERROR",
                        message=f"Original node {nid} missing in transformed IR.",
                        node_id=nid
                    )
                )

        # Validate MoE routing nodes have proper dependencies
        for nid, node in transformed_ir.nodes.items():
            if node.node_type == IRNodeType.ROUTING:
                has_experts = False
                for other_nid, other_node in transformed_ir.nodes.items():
                    if nid in other_node.dependencies:
                        has_experts = True
                        break

                if not has_experts:
                    diagnostics.append(
                        ExpertRealizationDiagnostic(
                            level="WARNING",
                            message=f"Routing node {nid} has no dependent expert nodes.",
                            node_id=nid
                        )
                    )

        return ExpertValidationReport(
            is_valid=len([d for d in diagnostics if d.level == "ERROR"]) == 0,
            diagnostics=tuple(diagnostics)
        )
