# SPDX-License-Identifier: Apache-2.0
"""
Compiler Inspector
Provides read-only methods for inspecting various compiler artifacts.
"""
from typing import Any
import json

from omlx.capabilities.descriptor import CapabilityDescriptor
from omlx.planner.plan import ExecutionPlan
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.physical.graph import PhysicalIR

class CompilerInspector:
    """
    Generic Compiler Inspector.
    Provides read-only inspection methods for compiler objects.
    Must never mutate compiler objects.
    """

    def __init__(self):
        pass

    def _freeze_dict(self, d: dict) -> dict:
        """Helper to recursively ensure nested structures are safe for export (e.g. enum strings)."""
        from omlx.utils.serialization import serialize_artifact
        return serialize_artifact(d)

    def inspect_capability_descriptor(self, descriptor: CapabilityDescriptor) -> dict[str, Any]:
        """Inspects a CapabilityDescriptor and returns a dict representation."""
        res = {}
        for field_name in descriptor.__dataclass_fields__:
            if field_name == "_diagnostics":
                # include diagnostics in inspection
                res[field_name] = getattr(descriptor, field_name)
            else:
                res[field_name] = getattr(descriptor, field_name)
        return self._freeze_dict(res)

    def inspect_execution_plan(self, plan: ExecutionPlan) -> dict[str, Any]:
        """Inspects an ExecutionPlan and returns a dict representation."""
        res = {}
        for field_name in plan.__dataclass_fields__:
            res[field_name] = getattr(plan, field_name)
        return self._freeze_dict(res)

    def inspect_logical_ir(self, ir: ExecutionIR) -> dict[str, Any]:
        """Inspects a Logical IR and returns its dictionary representation."""
        # ExecutionIR already has to_dict
        return ir.to_dict()

    def inspect_physical_ir(self, ir: PhysicalIR) -> dict[str, Any]:
        """Inspects a Physical IR and returns its dictionary representation."""
        # PhysicalIR already has to_dict
        return ir.to_dict()

    def inspect_backend_graph(self, graph: Any) -> dict[str, Any]:
        """Inspects a Backend Operation Graph."""
        # Placeholder for backend graph representation
        if hasattr(graph, "to_dict"):
            return graph.to_dict()
        return {"type": str(type(graph)), "repr": repr(graph)}

    def inspect_semantic_plan(self, plan: ExecutionPlan) -> dict[str, Any]:
        """Provides a semantic, human-readable summary of the ExecutionPlan."""
        # Note: the fields are extracted based on the attributes available on ExecutionPlan

        is_streaming = plan.execution_mode == "streaming"

        summary = {
            "execution_family": plan.execution_family.value if hasattr(plan.execution_family, "value") else str(plan.execution_family),
            "execution_backend": plan.execution_backend,
            "execution_mode": plan.execution_mode,
            "cache_strategy": plan.cache_strategy.value if hasattr(plan.cache_strategy, "value") else str(plan.cache_strategy),
            "is_streaming": is_streaming,
            "human_readable": (
                f"Executes {plan.execution_family} model on {plan.execution_backend} "
                f"using {plan.cache_strategy} cache in {'streaming' if is_streaming else 'standard'} mode."
            ),
            "optimizations": list(plan.optimization_passes),
            "verifications": list(plan.verification_stages)
        }
        return summary

    def inspect_semantic_ir(self, ir: ExecutionIR) -> dict[str, Any]:
        """Provides a semantic summary of the Logical IR nodes."""
        node_counts = {}
        for node in ir.nodes.values():
            node_type = node.node_type.value if hasattr(node.node_type, "value") else str(node.node_type)
            node_counts[node_type] = node_counts.get(node_type, 0) + 1

        summary = {
            "total_nodes": len(ir.nodes),
            "node_types": node_counts,
            "has_attention": "attention" in node_counts,
            "has_forward": "forward" in node_counts,
            "roots": list(ir.roots)
        }
        return summary
