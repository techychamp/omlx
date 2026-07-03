# SPDX-License-Identifier: Apache-2.0
"""
Execution graph definition for generation strategies.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any


__all__ = [
    "GraphNodeType",
    "GraphNode",
    "ExecutionGraph",
    "build_autoregressive_graph",
    "build_diffusion_graph",
    "build_linear_speculation_graph",
]


class GraphNodeType(enum.Enum):
    """Types of nodes in an execution graph."""
    PREFILL = "prefill"
    FORWARD = "forward"
    SAMPLE = "sample"
    VERIFY = "verify"
    DENOISE = "denoise"
    DRAFT = "draft"
    ACCEPT = "accept"
    EMIT = "emit"
    INITIALIZE_BLOCK = "initialize_block"


@dataclass
class GraphNode:
    """A node in an execution graph."""
    node_type: GraphNodeType
    next_nodes: list[GraphNode] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionGraph:
    """Defines the execution flow for a generation strategy.
    
    Phase 1: linear traversal only. Future: DAG execution.
    """
    root: GraphNode
    name: str

    def linear_order(self) -> list[GraphNode]:
        """Return nodes in linear traversal order (follows first next_node)."""
        nodes = []
        current = self.root
        while current is not None:
            nodes.append(current)
            if current.next_nodes:
                current = current.next_nodes[0]
            else:
                break
        return nodes


def build_autoregressive_graph() -> ExecutionGraph:
    """Prefill → Forward → Sample → Emit"""
    emit_node = GraphNode(node_type=GraphNodeType.EMIT)
    sample_node = GraphNode(node_type=GraphNodeType.SAMPLE, next_nodes=[emit_node])
    forward_node = GraphNode(node_type=GraphNodeType.FORWARD, next_nodes=[sample_node])
    prefill_node = GraphNode(node_type=GraphNodeType.PREFILL, next_nodes=[forward_node])
    return ExecutionGraph(root=prefill_node, name="autoregressive")


def build_diffusion_graph() -> ExecutionGraph:
    """Prefill → Initialize Block → Forward → Denoise → Forward → Emit"""
    emit_node = GraphNode(node_type=GraphNodeType.EMIT)
    forward_2_node = GraphNode(node_type=GraphNodeType.FORWARD, next_nodes=[emit_node])
    denoise_node = GraphNode(node_type=GraphNodeType.DENOISE, next_nodes=[forward_2_node])
    forward_1_node = GraphNode(node_type=GraphNodeType.FORWARD, next_nodes=[denoise_node])
    init_node = GraphNode(node_type=GraphNodeType.INITIALIZE_BLOCK, next_nodes=[forward_1_node])
    prefill_node = GraphNode(node_type=GraphNodeType.PREFILL, next_nodes=[init_node])
    return ExecutionGraph(root=prefill_node, name="diffusion")


def build_linear_speculation_graph() -> ExecutionGraph:
    """Prefill → Draft → Verify → Accept → Emit"""
    emit_node = GraphNode(node_type=GraphNodeType.EMIT)
    accept_node = GraphNode(node_type=GraphNodeType.ACCEPT, next_nodes=[emit_node])
    verify_node = GraphNode(node_type=GraphNodeType.VERIFY, next_nodes=[accept_node])
    draft_node = GraphNode(node_type=GraphNodeType.DRAFT, next_nodes=[verify_node])
    prefill_node = GraphNode(node_type=GraphNodeType.PREFILL, next_nodes=[draft_node])
    return ExecutionGraph(root=prefill_node, name="linear_speculation")
