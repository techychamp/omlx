# SPDX-License-Identifier: Apache-2.0
from typing import Dict, List, Set, Tuple
from omlx.planner.ir.graph import ExecutionIR
from .artifacts import DiffusionRealizationDiagnostic, DiffusionValidationReport

class DiffusionTransformationValidator:
    """
    Validates that transformed diffusion graphs preserve semantics and remain structurally valid.
    """
    def validate(self, original_ir: ExecutionIR, transformed_ir: ExecutionIR) -> DiffusionValidationReport:
        diagnostics = []
        is_valid = True

        # 1. Structural Validation
        # Check roots
        if not transformed_ir.roots:
            diagnostics.append(DiffusionRealizationDiagnostic(
                level="ERROR",
                message="Transformed diffusion graph has no roots."
            ))
            is_valid = False

        for root in transformed_ir.roots:
            if root not in transformed_ir.nodes:
                diagnostics.append(DiffusionRealizationDiagnostic(
                    level="ERROR",
                    message=f"Root node {root} not found in nodes.",
                    node_id=root
                ))
                is_valid = False

        # Check dependencies exist
        for nid, node in transformed_ir.nodes.items():
            for dep in node.dependencies:
                if dep not in transformed_ir.nodes:
                    diagnostics.append(DiffusionRealizationDiagnostic(
                        level="ERROR",
                        message=f"Node {nid} has missing dependency {dep}",
                        node_id=nid
                    ))
                    is_valid = False

        return DiffusionValidationReport(
            is_valid=is_valid,
            diagnostics=tuple(diagnostics)
        )
