# SPDX-License-Identifier: Apache-2.0
"""
Compiler Diff Tool
Compares two compiler artifacts to identify structural and metadata changes.
"""
from typing import Any, Dict

class CompilerDiffer:
    """Highlights added, removed, and changed elements between two artifacts."""

    def diff_dicts(self, old_data: dict[str, Any], new_data: dict[str, Any]) -> dict[str, Any]:
        """Generic recursive dictionary differ."""
        diff = {"added": {}, "removed": {}, "changed": {}}

        old_keys = set(old_data.keys())
        new_keys = set(new_data.keys())

        for k in new_keys - old_keys:
            diff["added"][k] = new_data[k]

        for k in old_keys - new_keys:
            diff["removed"][k] = old_data[k]

        for k in old_keys & new_keys:
            v_old = old_data[k]
            v_new = new_data[k]

            if isinstance(v_old, dict) and isinstance(v_new, dict):
                sub_diff = self.diff_dicts(v_old, v_new)
                if any(sub_diff.values()):
                    diff["changed"][k] = sub_diff
            elif v_old != v_new:
                 diff["changed"][k] = {"from": v_old, "to": v_new}

        return diff

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
