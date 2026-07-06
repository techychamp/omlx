from types import MappingProxyType
from typing import Sequence

from omlx.framework.graph import GraphDescriptor, GraphNode, GraphEdge
from omlx.framework.graph.transformation import (
    TransformationPass,
    TransformationDescriptor,
    TransformationContext,
    TransformationStatistics,
    GraphRewriter
)
from .artifacts import FusionPlan, FusionGroup

class FusionRealizationPass(TransformationPass):
    """
    Consumes a FusionPlan and performs the actual graph transformation
    using the Graph Transformation Framework.
    """

    def __init__(self, plan: FusionPlan):
        self.plan = plan

    @property
    def descriptor(self) -> TransformationDescriptor:
        return TransformationDescriptor(
            id="fusion_realization_pass",
            description="Realizes fusion groups by rewriting the graph"
        )

    def apply(self, graph: GraphDescriptor, context: TransformationContext) -> tuple[GraphDescriptor, TransformationStatistics]:
        current_graph = graph
        total_stats = TransformationStatistics()

        for group in self.plan.groups:
            # Skip invalid or empty groups
            if not group.node_ids:
                continue

            # Create a fused node
            fused_node_id = f"fused_{'_'.join(group.node_ids)}"

            # Extract metadata from source nodes (simple merge for now)
            merged_metadata = {"fused_from": group.node_ids}
            for node_id in group.node_ids:
                if node_id in current_graph.nodes:
                    node = current_graph.nodes[node_id]
                    for k, v in node.metadata.items():
                        if k not in merged_metadata:
                            merged_metadata[k] = v

            fused_node = GraphNode(
                id=fused_node_id,
                metadata=MappingProxyType(merged_metadata)
            )

            # Insert fused node
            current_graph, pass_stats = GraphRewriter.insert_node(current_graph, fused_node)
            total_stats = self._merge_stats(total_stats, pass_stats)

            # Find edges connecting to outside of the fusion group
            new_edges = []
            edges_to_remove = []
            for edge in current_graph.edges:
                is_source_internal = edge.source_id in group.node_ids
                is_target_internal = edge.target_id in group.node_ids

                if is_source_internal and is_target_internal:
                    # Internal edge, should be removed
                    edges_to_remove.append(edge)
                elif is_source_internal:
                    # Outgoing edge from group
                    new_edges.append(GraphEdge(source_id=fused_node_id, target_id=edge.target_id, metadata=edge.metadata))
                    edges_to_remove.append(edge)
                elif is_target_internal:
                    # Incoming edge to group
                    new_edges.append(GraphEdge(source_id=edge.source_id, target_id=fused_node_id, metadata=edge.metadata))
                    edges_to_remove.append(edge)

            # Rewire edges
            edges = list(current_graph.edges)
            for e in edges_to_remove:
                if e in edges:
                    edges.remove(e)
            for e in new_edges:
                edges.append(e)

            current_graph = GraphDescriptor(
                id=current_graph.id,
                nodes=current_graph.nodes,
                edges=tuple(edges),
                metadata=current_graph.metadata
            )

            total_stats = TransformationStatistics(
                nodes_added=total_stats.nodes_added,
                nodes_removed=total_stats.nodes_removed,
                nodes_replaced=total_stats.nodes_replaced,
                edges_added=total_stats.edges_added + len(new_edges),
                edges_removed=total_stats.edges_removed + len(edges_to_remove),
                metadata=total_stats.metadata
            )

            # Remove original nodes
            for node_id in group.node_ids:
                current_graph, pass_stats = GraphRewriter.remove_node(current_graph, node_id)
                total_stats = self._merge_stats(total_stats, pass_stats)

        return current_graph, total_stats

    def _merge_stats(self, s1: TransformationStatistics, s2: TransformationStatistics) -> TransformationStatistics:
        return TransformationStatistics(
            nodes_added=s1.nodes_added + s2.nodes_added,
            nodes_removed=s1.nodes_removed + s2.nodes_removed,
            nodes_replaced=s1.nodes_replaced + s2.nodes_replaced,
            edges_added=s1.edges_added + s2.edges_added,
            edges_removed=s1.edges_removed + s2.edges_removed,
            metadata=MappingProxyType({**s1.metadata, **s2.metadata})
        )
