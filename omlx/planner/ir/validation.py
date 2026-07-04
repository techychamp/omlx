# SPDX-License-Identifier: Apache-2.0
"""
Execution IR Validation.
"""

from typing import List, Set
from .graph import ExecutionIR

class IRValidationError(Exception):
    """Exception raised for errors in the Execution IR validation."""
    def __init__(self, errors: List[str]):
        super().__init__("\n".join(errors))
        self.errors = errors

def validate_ir(ir: ExecutionIR) -> None:
    """
    Validates an Execution IR graph.
    Checks for:
    - Invalid roots
    - Missing dependencies
    - Cyclic dependencies
    - Unreachable nodes
    """
    errors: List[str] = []

    # 1. Check Roots
    if not ir.roots:
        errors.append("ExecutionIR has no roots defined.")
    for root_id in ir.roots:
        if root_id not in ir.nodes:
            errors.append(f"Root node '{root_id}' is not in nodes.")

    # 2. Missing Dependencies
    for node_id, node in ir.nodes.items():
        for dep_id in node.dependencies:
            if dep_id not in ir.nodes:
                errors.append(f"Node '{node_id}' depends on missing node '{dep_id}'.")

    # 3. Cycle Detection
    visited: Set[str] = set()
    rec_stack: Set[str] = set()

    def check_cycles(node_id: str) -> bool:
        if node_id in rec_stack:
            return True
        if node_id in visited:
            return False

        visited.add(node_id)
        rec_stack.add(node_id)

        if node_id in ir.nodes:
            for dep_id in ir.nodes[node_id].dependencies:
                if check_cycles(dep_id):
                    errors.append(f"Cycle detected involving node '{node_id}' and '{dep_id}'.")
                    return True

        rec_stack.remove(node_id)
        return False

    # Check cycles from roots (dependencies form a directed graph)
    # The edges in our dependency array point from a node TO its dependencies.
    for root_id in ir.roots:
        check_cycles(root_id)

    # Check for cycles in any unconnected subgraphs
    for node_id in ir.nodes:
        if node_id not in visited:
            check_cycles(node_id)

    # 4. Unreachable nodes from roots
    # A node is reachable if there is a path from a root to the node.
    # Since edges point to dependencies: root -> dependency
    reachable: Set[str] = set()

    def dfs_reachable(node_id: str):
        if node_id in reachable:
            return
        reachable.add(node_id)
        if node_id in ir.nodes:
            for dep_id in ir.nodes[node_id].dependencies:
                dfs_reachable(dep_id)

    for root_id in ir.roots:
        dfs_reachable(root_id)

    unreachable = set(ir.nodes.keys()) - reachable
    if unreachable:
        errors.append(f"Unreachable nodes detected: {', '.join(unreachable)}")

    if errors:
        raise IRValidationError(errors)
