# SPDX-License-Identifier: Apache-2.0
"""
Compiler Diff Tool
Compares two compiler artifacts to identify structural and metadata changes.
"""
from typing import Any, Dict
from omlx.verify.structural_compare import StructuralComparator

class CompilerDiffer:
    """Highlights added, removed, and changed elements between two artifacts."""

    def __init__(self):
        self.comparator = StructuralComparator()

    def diff_dicts(self, old_data: dict[str, Any], new_data: dict[str, Any]) -> dict[str, Any]:
        """Generic recursive dictionary differ."""
        return self.comparator.diff_dicts(old_data, new_data)

    def diff_graphs(self, old_graph: dict[str, Any], new_graph: dict[str, Any]) -> dict[str, Any]:
        """Specialized diff for exported graph dicts (nodes/edges)."""
        old_nodes = old_graph.get("nodes", {})
        new_nodes = new_graph.get("nodes", {})

        node_diff = self.diff_dicts(old_nodes, new_nodes)

        # Simple edge comparison by serializing them
        old_edges = {str(e) for e in old_graph.get("edges", [])}
        new_edges = {str(e) for e in new_graph.get("edges", [])}

        edge_diff = {
            "added": list(new_edges - old_edges),
            "removed": list(old_edges - new_edges)
        }

        return {"nodes": node_diff, "edges": edge_diff}

    def diff_semantic(self, old_plan: Any, new_plan: Any) -> dict[str, Any]:
        """Provides a semantic diff of two ExecutionPlans."""
        diff_msgs = []

        if old_plan.execution_backend != new_plan.execution_backend:
            diff_msgs.append(f"Execution backend changed from {old_plan.execution_backend} to {new_plan.execution_backend}")

        old_mode = getattr(old_plan, "execution_mode", "standard")
        new_mode = getattr(new_plan, "execution_mode", "standard")

        if old_mode != new_mode:
            if old_mode == "streaming" and new_mode != "streaming":
                diff_msgs.append("Streaming was disabled")
            elif old_mode != "streaming" and new_mode == "streaming":
                diff_msgs.append("Streaming was enabled")
            else:
                diff_msgs.append(f"Execution mode changed from {old_mode} to {new_mode}")

        old_cache = old_plan.cache_strategy.value if hasattr(old_plan.cache_strategy, "value") else str(old_plan.cache_strategy)
        new_cache = new_plan.cache_strategy.value if hasattr(new_plan.cache_strategy, "value") else str(new_plan.cache_strategy)
        if old_cache != new_cache:
            diff_msgs.append(f"Cache strategy changed from {old_cache} to {new_cache}")

        # Simplified optimization pass checking
        old_passes = set(old_plan.optimization_passes)
        new_passes = set(new_plan.optimization_passes)

        for p in new_passes - old_passes:
            diff_msgs.append(f"Optimization pass added: {p}")
        for p in old_passes - new_passes:
            diff_msgs.append(f"Optimization pass removed: {p}")

        return {
            "has_semantic_changes": len(diff_msgs) > 0,
            "semantic_changes": diff_msgs
        }
