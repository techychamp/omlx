# SPDX-License-Identifier: Apache-2.0
"""
Physical IR Validation.
"""
from typing import List, Set
from .graph import PhysicalIR

class PhysicalIRValidationError(Exception):
    def __init__(self, errors: List[str]):
        super().__init__("\n".join(errors))
        self.errors = errors

def validate_physical_ir(ir: PhysicalIR) -> None:
    errors: List[str] = []

    if not ir.roots:
        errors.append("PhysicalIR has no roots defined.")
    for root_id in ir.roots:
        if root_id not in ir.operations:
            errors.append(f"Root operation '{root_id}' is not in operations.")

    for op_id, op in ir.operations.items():
        for dep_id in op.dependencies:
            if dep_id not in ir.operations:
                errors.append(f"Operation '{op_id}' depends on missing operation '{dep_id}'.")

    visited: Set[str] = set()
    rec_stack: Set[str] = set()

    def check_cycles(op_id: str) -> bool:
        if op_id in rec_stack:
            return True
        if op_id in visited:
            return False

        visited.add(op_id)
        rec_stack.add(op_id)

        if op_id in ir.operations:
            for dep_id in ir.operations[op_id].dependencies:
                if check_cycles(dep_id):
                    errors.append(f"Cycle detected involving operation '{op_id}' and '{dep_id}'.")
                    return True

        rec_stack.remove(op_id)
        return False

    for root_id in ir.roots:
        check_cycles(root_id)

    for op_id in ir.operations:
        if op_id not in visited:
            check_cycles(op_id)

    if errors:
        raise PhysicalIRValidationError(errors)
