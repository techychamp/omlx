# SPDX-License-Identifier: Apache-2.0
from omlx.planner.ir.graph import ExecutionIR
from .artifacts import MemoryValidationReport, MemoryRealizationDiagnostic

class MemoryTransformationValidator:
    def __init__(self):
        pass

    def validate(self, original_ir: ExecutionIR, transformed_ir: ExecutionIR) -> MemoryValidationReport:
        diagnostics = []

        # Validate that the transformed IR is not None
        if transformed_ir is None:
            diagnostics.append(MemoryRealizationDiagnostic(
                severity="ERROR",
                message="Transformed IR is None."
            ))
            return MemoryValidationReport(is_valid=False, diagnostics=tuple(diagnostics))

        # Basic check: transformed IR should have at least the nodes from the original IR
        if len(transformed_ir.nodes) < len(original_ir.nodes):
            diagnostics.append(MemoryRealizationDiagnostic(
                severity="ERROR",
                message="Transformed IR has fewer nodes than original IR."
            ))
            return MemoryValidationReport(is_valid=False, diagnostics=tuple(diagnostics))

        return MemoryValidationReport(
            is_valid=len(diagnostics) == 0,
            diagnostics=tuple(diagnostics)
        )
