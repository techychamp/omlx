from typing import Dict, Any, List
from omlx.framework.graph import (
    GraphDescriptor,
    GraphNode,
    GraphEdge,
    GraphStatistics,
    GraphValidationReport
)

class GraphInspector:
    """Tooling inspector for canonical Graph Framework artifacts."""

    def inspect_descriptor(self, descriptor: GraphDescriptor) -> Dict[str, Any]:
        """Inspects a GraphDescriptor and returns a detailed read-only dictionary."""
        return {
            "id": descriptor.id,
            "nodes": [self.inspect_node(n) for n in descriptor.nodes.values()],
            "edges": [self.inspect_edge(e) for e in descriptor.edges],
            "metadata": dict(descriptor.metadata.attributes)
        }

    def inspect_node(self, node: GraphNode) -> Dict[str, Any]:
        """Inspects a GraphNode."""
        return {
            "id": node.id,
            "metadata": dict(node.metadata)
        }

    def inspect_edge(self, edge: GraphEdge) -> Dict[str, Any]:
        """Inspects a GraphEdge."""
        return {
            "source_id": edge.source_id,
            "target_id": edge.target_id,
            "metadata": dict(edge.metadata)
        }

    def inspect_statistics(self, stats: GraphStatistics) -> Dict[str, Any]:
        """Inspects a GraphStatistics object."""
        return {
            "node_count": stats.node_count,
            "edge_count": stats.edge_count,
            "metadata": dict(stats.metadata)
        }

    def inspect_validation_report(self, report: GraphValidationReport) -> Dict[str, Any]:
        """Inspects a GraphValidationReport object."""
        return {
            "is_valid": report.is_valid,
            "diagnostics": [
                {
                    "level": d.level,
                    "message": d.message,
                    "metadata": dict(d.metadata)
                } for d in report.diagnostics
            ]
        }
