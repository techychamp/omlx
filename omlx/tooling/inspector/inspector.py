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
        res = {}
        for k, v in d.items():
            if hasattr(v, "value"): # Enum
                res[k] = v.value
            elif isinstance(v, (dict, list, tuple, set, frozenset)):
                # basic stringification or json conversion could happen here, keeping simple for now
                try:
                    json.dumps(v)
                    res[k] = v
                except TypeError:
                    res[k] = str(v)
            else:
                res[k] = v
        return res

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
