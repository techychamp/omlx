# SPDX-License-Identifier: Apache-2.0
"""
Graph View Helpers
Maps compiler objects into standardized graph dictionaries suitable for exporters.
"""
from typing import Any
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.physical.graph import PhysicalIR

def to_value_graph(ir: ExecutionIR) -> dict[str, Any]:
    """Extracts a Value Graph from a Logical IR."""
    # Maps semantic values flowing between nodes. (Simplified implementation)
    nodes = {}
    edges = []

    for node_id, node in ir.nodes.items():
        is_streaming = "is_streaming: True" if getattr(node, "is_streaming", False) else ""
        cache_type = f"cache: {node.cache_strategy}" if getattr(node, "cache_strategy", None) else ""
        semantic_labels = [l for l in [is_streaming, cache_type] if l]
        label = f"{node.node_type.value}\\n{node_id}"
        if semantic_labels:
            label += "\\n" + "\\n".join(semantic_labels)
        nodes[node_id] = {"label": label}
        for dep in node.dependencies:
            edges.append({"source": dep, "target": node_id, "label": "value"})

    return {"nodes": nodes, "edges": edges}

def to_operation_graph(ir: PhysicalIR) -> dict[str, Any]:
    """Extracts an Operation Graph from a Physical IR."""
    nodes = {}
    edges = []

    for op_id, op in ir.operations.items():
        nodes[op_id] = {"label": f"{op.op_type}\\n{op_id}"}
        for dep in op.dependencies:
            edges.append({"source": dep, "target": op_id, "label": "dep"})

    return {"nodes": nodes, "edges": edges}

def to_dependency_graph(plan_or_ir: Any) -> dict[str, Any]:
    """Extracts a generic dependency graph."""
    if hasattr(plan_or_ir, "nodes"):
        return to_value_graph(plan_or_ir)
    if hasattr(plan_or_ir, "operations"):
        return to_operation_graph(plan_or_ir)
    return {"nodes": {"root": {"label": "Unknown Object"}}, "edges": []}

def to_control_flow_graph(ir: PhysicalIR) -> dict[str, Any]:
    """Extracts Control Flow Graph. Simplistic mapping for now."""
    return to_operation_graph(ir)

def to_data_flow_graph(ir: ExecutionIR) -> dict[str, Any]:
    """Extracts Data Flow Graph. Simplistic mapping for now."""
    return to_value_graph(ir)
