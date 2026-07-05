# SPDX-License-Identifier: Apache-2.0
"""
Compiler Optimization Framework - Pass Manager
"""
from typing import List, Dict, Set, Optional
from collections import deque
from .passes import BasePass, CompilerStage
from .validation import validate_pass_dependencies, validate_pass_compatibility, PassValidationError

class PassManager:
    def __init__(self):
        self._passes: Dict[str, BasePass] = {}

    def register(self, pass_: BasePass) -> None:
        if pass_.name in self._passes:
            raise ValueError(f"Pass with name '{pass_.name}' is already registered.")
        self._passes[pass_.name] = pass_

    def get_registered_passes(self) -> List[BasePass]:
        return list(self._passes.values())

    def get_execution_order(self, stage: Optional[CompilerStage] = None) -> List[BasePass]:
        passes = self.get_registered_passes()

        if stage is not None:
            passes = [p for p in passes if stage in p.supported_stages]

        # Validation
        validate_pass_dependencies(passes)
        validate_pass_compatibility(passes)

        # Topological Sort
        # We need a graph where an edge A -> B means B must run BEFORE A.
        # So we process dependencies. If A depends on B, B must be before A.

        # Build adjacency list: node -> list of nodes that depend on it
        adj: Dict[str, List[str]] = {p.name: [] for p in passes}
        in_degree: Dict[str, int] = {p.name: 0 for p in passes}

        pass_names = set(self._passes.keys())

        for p in passes:
            # required
            for req in p.required_passes:
                adj[req].append(p.name)
                in_degree[p.name] += 1

            # optional
            for opt in p.optional_passes:
                if opt in pass_names:
                    adj[opt].append(p.name)
                    in_degree[p.name] += 1

        queue = deque([name for name, deg in in_degree.items() if deg == 0])
        order = []

        while queue:
            curr = queue.popleft()
            order.append(self._passes[curr])

            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(passes):
             raise PassValidationError("Could not resolve execution order (likely a cycle, though validation should have caught it).")

        return order
