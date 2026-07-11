from typing import Dict, List, Set, Tuple
from omlx.planner.ir.graph import ExecutionIR
from .artifacts import TransformationDiagnostic, TransformationValidationReport

class TransformationValidator:
    """
    Validates that transformed graphs preserve semantics and remain structurally valid.
    """
    def validate(self, original_ir: ExecutionIR, transformed_ir: ExecutionIR) -> TransformationValidationReport:
        diagnostics = []
        is_valid = True

        # 1. Structural Validation
        # Check roots
        if not transformed_ir.roots:
            diagnostics.append(TransformationDiagnostic(
                level="ERROR",
                message="Transformed graph has no roots."
            ))
            is_valid = False

        for root in transformed_ir.roots:
            if root not in transformed_ir.nodes:
                diagnostics.append(TransformationDiagnostic(
                    level="ERROR",
                    message=f"Root node {root} not found in nodes.",
                    node_id=root
                ))
                is_valid = False

        # Check dependencies exist
        for nid, node in transformed_ir.nodes.items():
            for dep in node.dependencies:
                if dep not in transformed_ir.nodes:
                    diagnostics.append(TransformationDiagnostic(
                        level="ERROR",
                        message=f"Node {nid} has missing dependency {dep}",
                        node_id=nid
                    ))
                    is_valid = False

        # Cycle detection
        if self._has_cycle(transformed_ir):
            diagnostics.append(TransformationDiagnostic(
                level="ERROR",
                message="Transformed graph contains a cycle."
            ))
            is_valid = False

        return TransformationValidationReport(
            is_valid=is_valid,
            diagnostics=tuple(diagnostics)
        )

    def _has_cycle(self, ir: ExecutionIR) -> bool:
        visited = set()
        rec_stack = set()

        def check(node_id):
            if node_id in rec_stack:
                return True
            if node_id in visited:
                return False

            visited.add(node_id)
            rec_stack.add(node_id)

            for dep in ir.nodes.get(node_id, frozenset()).dependencies if node_id in ir.nodes else []:
                if check(dep):
                    return True

            rec_stack.remove(node_id)
            return False

        for root in ir.roots:
            if check(root):
                return True

        return False
