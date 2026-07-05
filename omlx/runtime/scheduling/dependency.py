# SPDX-License-Identifier: Apache-2.0
"""
Dependency Analyzer for OMLX Scheduling subsystem.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
from .types import BackendOperationGraph

@dataclass(frozen=True)
class DependencyAnalysisResult:
    """Immutable results of dependency analysis."""
    is_cyclic: bool
    roots: List[str]
    leaves: List[str]
    graph_depth: int
    avg_fan_in: float
    avg_fan_out: float
    in_degrees: Dict[str, int]
    out_degrees: Dict[str, int]
    levels: Dict[str, int]
    valid: bool

class DependencyAnalyzer:
    """Analyzes BackendOperationGraph dependencies without executing them."""

    def analyze(self, graph: BackendOperationGraph) -> DependencyAnalysisResult:
        if not graph or not hasattr(graph, 'operations'):
            return DependencyAnalysisResult(
                is_cyclic=False, roots=[], leaves=[], graph_depth=0,
                avg_fan_in=0.0, avg_fan_out=0.0, in_degrees={}, out_degrees={}, levels={}, valid=False
            )

        operations = graph.operations
        in_degrees: Dict[str, int] = {op_id: 0 for op_id in operations}
        out_degrees: Dict[str, int] = {op_id: 0 for op_id in operations}
        adj_list: Dict[str, List[str]] = {op_id: [] for op_id in operations}

        for op_id, op in operations.items():
            for dep_id in op.dependencies:
                if dep_id in adj_list:
                    adj_list[dep_id].append(op_id)
                    in_degrees[op_id] += 1
                    out_degrees[dep_id] += 1

        roots = [op_id for op_id, deg in in_degrees.items() if deg == 0]
        leaves = [op_id for op_id, deg in out_degrees.items() if deg == 0]

        # Topological sort for cycle detection and leveling
        levels: Dict[str, int] = {}
        queue = [(root, 0) for root in roots]
        visited_count = 0

        while queue:
            current, level = queue.pop(0)
            visited_count += 1
            levels[current] = max(levels.get(current, 0), level)

            for neighbor in adj_list.get(current, []):
                in_degrees[neighbor] -= 1
                if in_degrees[neighbor] == 0:
                    queue.append((neighbor, levels[current] + 1))

        # Restore in_degrees for the result
        for op_id, op in operations.items():
             for dep_id in op.dependencies:
                  if dep_id in in_degrees:
                       in_degrees[op_id] += 1

        is_cyclic = visited_count != len(operations)
        graph_depth = max(levels.values()) + 1 if levels else 0

        total_nodes = len(operations)
        avg_fan_in = sum(in_degrees.values()) / total_nodes if total_nodes > 0 else 0.0
        avg_fan_out = sum(out_degrees.values()) / total_nodes if total_nodes > 0 else 0.0

        return DependencyAnalysisResult(
            is_cyclic=is_cyclic,
            roots=sorted(roots),
            leaves=sorted(leaves),
            graph_depth=graph_depth,
            avg_fan_in=avg_fan_in,
            avg_fan_out=avg_fan_out,
            in_degrees=in_degrees,
            out_degrees=out_degrees,
            levels=levels,
            valid=not is_cyclic
        )
