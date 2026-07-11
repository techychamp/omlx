# SPDX-License-Identifier: Apache-2.0
"""
Compiler-native cache realizer.
"""

from typing import Tuple, Any, Dict
from types import MappingProxyType


from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.framework.cache.plan import CachePlan
from omlx.planner.domains.cache.artifacts import CacheRealizationReport, CacheRealizationStatistics, CacheRealizationDiagnostic, CacheExecutionGraph
from omlx.framework.graph.descriptor import GraphDescriptor
from omlx.framework.graph.artifacts import GraphNode, GraphEdge
from omlx.framework.graph.transformation import GraphRewriter, TransformationStatistics

class CacheRealizer:
    """Realizes a CachePlan into an ExecutionIR graph."""

    def realize(self, ir: ExecutionIR, plan: CachePlan) -> Tuple[ExecutionIR, CacheRealizationReport]:
        """
        Transforms the given ExecutionIR by inserting appropriate cache read/write operations
        based on the provided CachePlan.
        """
        if not plan:
            return ir, CacheRealizationReport(is_successful=True)

        nodes_added = 0
        edges_added = 0
        cache_read_ops = 0
        cache_write_ops = 0

        # Convert ExecutionIR to GraphDescriptor
        # Note: This is currently scaffolding for future integration with GraphRewriter.
        # While the current pass manipulates nodes directly, future iterations of cache
        # realization will leverage GraphRewriter for complex topology changes.
        graph_nodes = {}
        graph_edges = []
        for node_id, node in ir.nodes.items():
            graph_nodes[node_id] = GraphNode(id=node_id, metadata=MappingProxyType(node.to_dict()))
            for dep in node.dependencies:
                graph_edges.append(GraphEdge(source_id=dep, target_id=node_id))

        graph = GraphDescriptor(id="cache_realization", nodes=MappingProxyType(graph_nodes), edges=tuple(graph_edges))

        # We will iterate over nodes.
        # For FORWARD nodes, we want a CACHE_READ before, and CACHE_WRITE after.
        # For PREFILL nodes, we want a CACHE_WRITE after.

        new_nodes = dict(ir.nodes)

        for node_id, node in list(ir.nodes.items()):
            if node.node_type == IRNodeType.FORWARD:
                # Add CACHE_READ before FORWARD
                read_id = f"{node.id}_cache_read"
                read_node = IRNode(
                    id=read_id,
                    node_type=IRNodeType.CACHE_READ,
                    dependencies=node.dependencies, # Preserve original dependencies for the read
                    metadata=MappingProxyType({"plan_id": plan.plan_id})
                )
                new_nodes[read_id] = read_node

                # Update FORWARD dependencies to point exclusively to the new read node.
                # This explicitly preserves the semantic dependency chain: original_deps -> read -> forward
                updated_node = IRNode(
                    id=node.id,
                    node_type=node.node_type,
                    dependencies=(read_id,),
                    metadata=node.metadata
                )
                new_nodes[node.id] = updated_node

                nodes_added += 1
                edges_added += 1
                cache_read_ops += 1

                # Add CACHE_WRITE after FORWARD
                write_id = f"{node.id}_cache_write"
                write_node = IRNode(
                    id=write_id,
                    node_type=IRNodeType.CACHE_WRITE,
                    dependencies=(node.id,),
                    metadata=MappingProxyType({"plan_id": plan.plan_id})
                )
                new_nodes[write_id] = write_node

                nodes_added += 1
                edges_added += 1
                cache_write_ops += 1

            elif node.node_type == IRNodeType.PREFILL:
                # Add CACHE_WRITE after PREFILL
                write_id = f"{node.id}_cache_write"
                write_node = IRNode(
                    id=write_id,
                    node_type=IRNodeType.CACHE_WRITE,
                    dependencies=(node.id,),
                    metadata=MappingProxyType({"plan_id": plan.plan_id})
                )
                new_nodes[write_id] = write_node

                nodes_added += 1
                edges_added += 1
                cache_write_ops += 1

        # CACHE_WRITE nodes are sinks. We must add them to roots so they are reachable during execution traversal.
        new_roots = list(ir.roots)
        for node_id, node in new_nodes.items():
            if node.node_type == IRNodeType.CACHE_WRITE:
                if node_id not in new_roots:
                    new_roots.append(node_id)

        new_ir = ExecutionIR(
            nodes=MappingProxyType(new_nodes),
            roots=tuple(new_roots),
            metadata=ir.metadata
        )

        stats = CacheRealizationStatistics(
            nodes_added=nodes_added,
            edges_added=edges_added,
            cache_read_ops=cache_read_ops,
            cache_write_ops=cache_write_ops,
            metadata=MappingProxyType({"plan_id": plan.plan_id})
        )

        # Build the final GraphDescriptor for CacheExecutionGraph
        final_graph_nodes = {}
        final_graph_edges = []
        for node_id, node in new_nodes.items():
            final_graph_nodes[node_id] = GraphNode(id=node_id, metadata=MappingProxyType(node.to_dict()))
            for dep in node.dependencies:
                final_graph_edges.append(GraphEdge(source_id=dep, target_id=node_id))

        final_graph = GraphDescriptor(id="cache_realization", nodes=MappingProxyType(final_graph_nodes), edges=tuple(final_graph_edges))
        cache_execution_graph = CacheExecutionGraph(graph=final_graph)

        report = CacheRealizationReport(
            is_successful=True,
            statistics=stats,
            diagnostics=tuple(),
            execution_graph=cache_execution_graph
        )

        return new_ir, report
