# SPDX-License-Identifier: Apache-2.0
"""
Critical Path Analyzer for OMLX Scheduling subsystem.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set
from .types import BackendOperationGraph
from .dependency import DependencyAnalysisResult

@dataclass(frozen=True)
class CriticalPathResult:
    """Immutable results of critical path analysis."""
    path: List[str]
    length: int
    estimated_latency: float

class CriticalPathAnalyzer:
    """Analyzes critical path in BackendOperationGraph structurally without executing."""

    def analyze(self, graph: BackendOperationGraph, dependency_result: DependencyAnalysisResult) -> CriticalPathResult:
        if not graph or not hasattr(graph, 'operations') or not dependency_result.valid:
            return CriticalPathResult(path=[], length=0, estimated_latency=0.0)

        operations = graph.operations
        # We need a reversed adjacency list to build paths from leaves up, or we can use dynamic programming from roots down.
        # Let's do longest path in DAG (since it's acyclic)

        # topological order
        in_degrees = {op_id: 0 for op_id in operations}
        adj_list = {op_id: [] for op_id in operations}

        for op_id, op in operations.items():
            for dep_id in op.dependencies:
                if dep_id in adj_list:
                    adj_list[dep_id].append(op_id)
                    in_degrees[op_id] += 1

        queue = [op_id for op_id, deg in in_degrees.items() if deg == 0]
        topo_order = []
        while queue:
             curr = queue.pop(0)
             topo_order.append(curr)
             for nxt in adj_list.get(curr, []):
                 in_degrees[nxt] -= 1
                 if in_degrees[nxt] == 0:
                     queue.append(nxt)

        # compute longest path
        dist: Dict[str, int] = {op_id: 1 for op_id in operations} # length in nodes
        parent: Dict[str, str] = {op_id: None for op_id in operations}

        for u in topo_order:
            for v in adj_list.get(u, []):
                if dist[v] < dist[u] + 1:
                    dist[v] = dist[u] + 1
                    parent[v] = u

        if not dist:
            return CriticalPathResult(path=[], length=0, estimated_latency=0.0)

        max_node = max(dist, key=dist.get)
        path = []
        curr = max_node
        while curr is not None:
             path.append(curr)
             curr = parent[curr]

        path.reverse()

        # structural latency estimate: simple proxy (1 per node)
        estimated_latency = float(len(path))

        return CriticalPathResult(
            path=path,
            length=len(path),
            estimated_latency=estimated_latency
        )
