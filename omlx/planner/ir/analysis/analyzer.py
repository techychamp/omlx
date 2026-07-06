# SPDX-License-Identifier: Apache-2.0
"""
Graph Analyzer implementation.
Provides stateless, read-only analysis of ExecutionIR graphs.
"""

from typing import Dict, List, Set, Tuple, Any, Optional
from types import MappingProxyType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from .artifacts import (
    GraphValidationReport,
    GraphDiagnostic,
    DiagnosticLevel,
    GraphStatistics,
    DependencyAnalysis,
    CriticalPathReport,
    TraversalResult,
    GraphAnalysisReport,
)

class GraphAnalyzer:
    """
    Stateless, read-only analyzer for ExecutionIR graphs.
    Never modifies graphs. Produces immutable artifacts.
    """

    def analyze(self, ir: ExecutionIR) -> GraphAnalysisReport:
        """Runs comprehensive analysis on an ExecutionIR graph."""
        validation_report = self.validate(ir)
        dependency_analysis = self.analyze_dependencies(ir)
        stats = self.compute_statistics(ir, dependency_analysis)
        critical_path = self.analyze_critical_path(ir, dependency_analysis)

        return GraphAnalysisReport(
            validation=validation_report,
            statistics=stats,
            dependencies=dependency_analysis,
            critical_path=critical_path,
        )

    def validate(self, ir: ExecutionIR) -> GraphValidationReport:
        """Validates the structure and consistency of the ExecutionIR graph."""
        diagnostics: List[GraphDiagnostic] = []
        is_valid = True

        # 1. Check Roots
        if not ir.roots:
            diagnostics.append(GraphDiagnostic(
                level=DiagnosticLevel.ERROR,
                message="ExecutionIR has no roots defined."
            ))
            is_valid = False

        for root_id in ir.roots:
            if root_id not in ir.nodes:
                diagnostics.append(GraphDiagnostic(
                    level=DiagnosticLevel.ERROR,
                    message=f"Root node '{root_id}' is not in nodes.",
                    node_id=root_id
                ))
                is_valid = False

        # 2. Missing Dependencies
        for node_id, node in ir.nodes.items():
            for dep_id in node.dependencies:
                if dep_id not in ir.nodes:
                    diagnostics.append(GraphDiagnostic(
                        level=DiagnosticLevel.ERROR,
                        message=f"Node '{node_id}' depends on missing node '{dep_id}'.",
                        node_id=node_id,
                        context=MappingProxyType({"missing_dependency": dep_id})
                    ))
                    is_valid = False

        # 3. Reachability and Cycle Detection
        deps_analysis = self.analyze_dependencies(ir)
        if deps_analysis.has_cycles:
            diagnostics.append(GraphDiagnostic(
                level=DiagnosticLevel.ERROR,
                message="Cycle detected in graph dependencies."
            ))
            is_valid = False

        traversal = self.traverse(ir)
        if traversal.unreachable_nodes:
            diagnostics.append(GraphDiagnostic(
                level=DiagnosticLevel.ERROR,
                message=f"Unreachable nodes detected: {', '.join(traversal.unreachable_nodes)}",
                context=MappingProxyType({"unreachable_nodes": tuple(traversal.unreachable_nodes)})
            ))
            is_valid = False

        return GraphValidationReport(
            is_valid=is_valid,
            diagnostics=tuple(diagnostics)
        )

    def analyze_dependencies(self, ir: ExecutionIR) -> DependencyAnalysis:
        """Analyzes dependencies and computes reverse dependencies (dependents)."""
        dependents: Dict[str, List[str]] = {node_id: [] for node_id in ir.nodes}
        dependencies: Dict[str, Tuple[str, ...]] = {}

        has_cycles = False
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
                        return True

            rec_stack.remove(node_id)
            return False

        for node_id, node in ir.nodes.items():
            dependencies[node_id] = node.dependencies
            for dep_id in node.dependencies:
                if dep_id in dependents:
                    dependents[dep_id].append(node_id)

            if node_id not in visited:
                if check_cycles(node_id):
                    has_cycles = True

        frozen_dependents = {k: tuple(v) for k, v in dependents.items()}

        return DependencyAnalysis(
            dependencies=MappingProxyType(dependencies),
            dependents=MappingProxyType(frozen_dependents),
            has_cycles=has_cycles
        )

    def compute_statistics(self, ir: ExecutionIR, deps: Optional[DependencyAnalysis] = None) -> GraphStatistics:
        """Computes structural statistics of the graph."""
        if deps is None:
            deps = self.analyze_dependencies(ir)

        node_count = len(ir.nodes)
        edge_count = sum(len(n.dependencies) for n in ir.nodes.values())
        root_count = len(ir.roots)

        leaf_count = 0
        for node_id in ir.nodes:
            if len(deps.dependencies.get(node_id, ())) == 0:
                leaf_count += 1

        depths: Dict[str, int] = {}
        visited: Set[str] = set()

        def get_depth(node_id: str) -> int:
            if node_id in depths:
                return depths[node_id]

            if node_id not in ir.nodes or node_id in visited:
                return 0

            visited.add(node_id)
            deps_list = ir.nodes[node_id].dependencies
            if not deps_list:
                depths[node_id] = 1
                visited.remove(node_id)
                return 1

            max_dep_depth = max((get_depth(d) for d in deps_list), default=0)
            depths[node_id] = max_dep_depth + 1
            visited.remove(node_id)
            return depths[node_id]

        max_depth = 0
        if not deps.has_cycles:
            max_depth = max((get_depth(r) for r in ir.roots), default=0)
        else:
            max_depth = -1 # Indicate invalid depth due to cycles

        avg_branching = edge_count / node_count if node_count > 0 else 0.0

        return GraphStatistics(
            node_count=node_count,
            edge_count=edge_count,
            root_count=root_count,
            leaf_count=leaf_count,
            max_depth=max_depth,
            average_branching_factor=avg_branching
        )

    def analyze_critical_path(self, ir: ExecutionIR, deps: Optional[DependencyAnalysis] = None) -> Optional[CriticalPathReport]:
        """Identifies the longest path through the graph. Returns None if cycle detected."""
        if deps is None:
            deps = self.analyze_dependencies(ir)

        if deps.has_cycles:
            return None

        memo: Dict[str, Tuple[float, List[str]]] = {}

        def get_longest_path(node_id: str) -> Tuple[float, List[str]]:
            if node_id in memo:
                return memo[node_id]

            if node_id not in ir.nodes:
                return (0.0, [])

            node = ir.nodes[node_id]
            cost = 1.0

            if not node.dependencies:
                res = (cost, [node_id])
                memo[node_id] = res
                return res

            max_dep_cost = -1.0
            best_path: List[str] = []

            for dep_id in node.dependencies:
                dep_cost, dep_path = get_longest_path(dep_id)
                if dep_cost > max_dep_cost:
                    max_dep_cost = dep_cost
                    best_path = dep_path

            res = (cost + max_dep_cost, [node_id] + best_path)
            memo[node_id] = res
            return res

        best_overall_cost = -1.0
        best_overall_path: List[str] = []

        for root_id in ir.roots:
            cost, path = get_longest_path(root_id)
            if cost > best_overall_cost:
                best_overall_cost = cost
                best_overall_path = path

        if best_overall_cost == -1.0:
             return None

        return CriticalPathReport(
            path_nodes=tuple(best_overall_path),
            estimated_cost=best_overall_cost
        )

    def traverse(self, ir: ExecutionIR) -> TraversalResult:
        """Traverses the graph and returns visit order and reachability."""
        visited: Set[str] = set()
        order: List[str] = []
        rec_stack: Set[str] = set()

        def dfs(node_id: str):
            if node_id in visited:
                return
            if node_id in rec_stack:
                return # Avoid infinite loop on cycles

            rec_stack.add(node_id)

            if node_id in ir.nodes:
                for dep_id in ir.nodes[node_id].dependencies:
                    dfs(dep_id)

            rec_stack.remove(node_id)
            visited.add(node_id)
            order.append(node_id)

        for root_id in ir.roots:
            dfs(root_id)

        unreachable = set(ir.nodes.keys()) - visited

        return TraversalResult(
            visited_nodes=tuple(visited),
            traversal_order=tuple(order), # Post-order traversal (dependencies first)
            unreachable_nodes=tuple(unreachable)
        )
