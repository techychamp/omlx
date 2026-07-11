# SPDX-License-Identifier: Apache-2.0
"""
Debug Views
Generates different structural representations of compiler artifacts.
"""
from typing import Any

def to_summary_view(data: dict[str, Any]) -> dict[str, Any]:
    """Returns a high-level summary of the artifact."""
    summary = {}
    if "nodes" in data:
        summary["node_count"] = len(data["nodes"])
    if "operations" in data:
        summary["operation_count"] = len(data["operations"])
    if "roots" in data:
        summary["roots"] = data["roots"]
    return summary

def to_detailed_view(data: dict[str, Any]) -> dict[str, Any]:
    """Returns the full data dictionary (identity function for now)."""
    return data

def to_tree_view(data: dict[str, Any]) -> dict[str, Any]:
    """Attempts to construct a hierarchical tree from a flat node/edge graph."""
    # Simplified tree generation
    return {"tree": data.get("roots", []), "nodes": data.get("nodes", {})}

def to_statistics_view(data: dict[str, Any]) -> dict[str, Any]:
    """Returns statistical metrics about the graph/artifact."""
    stats = {}
    if "nodes" in data:
        stats["total_nodes"] = len(data["nodes"])
        # Could count by type here if we inspected the nodes deeply
    return stats
