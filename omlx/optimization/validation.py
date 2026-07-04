# SPDX-License-Identifier: Apache-2.0
"""
Compiler Optimization Framework - Validation
"""
from typing import List, Dict, Set
from .passes import BasePass

class PassValidationError(Exception):
    pass

def validate_pass_dependencies(passes: List[BasePass]) -> None:
    """
    Validates that all required dependencies are present in the list of passes
    and that there are no circular dependencies.
    """
    pass_names = {p.name for p in passes}
    pass_map = {p.name: p for p in passes}

    # Check for missing required dependencies
    for p in passes:
        for req in p.required_passes:
            if req not in pass_names:
                raise PassValidationError(f"Pass '{p.name}' requires '{req}', which is not registered.")

    # Check for circular dependencies using DFS
    visited = set()
    rec_stack = set()

    def is_cyclic(pass_name: str) -> bool:
        visited.add(pass_name)
        rec_stack.add(pass_name)

        p = pass_map[pass_name]

        # We need to check both required and optional (if present) for cycles
        deps_to_check = list(p.required_passes)
        for opt in p.optional_passes:
            if opt in pass_names:
                deps_to_check.append(opt)

        for dep in deps_to_check:
            if dep not in visited:
                if is_cyclic(dep):
                    return True
            elif dep in rec_stack:
                return True

        rec_stack.remove(pass_name)
        return False

    for pass_name in pass_names:
        if pass_name not in visited:
            if is_cyclic(pass_name):
                raise PassValidationError("Circular dependency detected among passes.")

def validate_pass_compatibility(passes: List[BasePass]) -> None:
    """
    Validates that no conflicting passes are registered together.
    """
    pass_names = {p.name for p in passes}

    for p in passes:
        for conflict in p.conflicting_passes:
            if conflict in pass_names:
                raise PassValidationError(f"Pass '{p.name}' conflicts with registered pass '{conflict}'.")
