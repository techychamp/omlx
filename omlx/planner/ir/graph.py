# SPDX-License-Identifier: Apache-2.0
"""
Execution IR Graph.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from types import MappingProxyType
import json
from .nodes import IRNode, IRNodeType

@dataclass(frozen=True)
class ExecutionIR:
    """An immutable, backend-independent representation of an execution plan."""
    nodes: MappingProxyType[str, IRNode]
    roots: tuple[str, ...]
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def get_node(self, node_id: str) -> IRNode:
        """Returns the node with the given ID."""
        if node_id not in self.nodes:
            raise KeyError(f"Node {node_id} not found in ExecutionIR")
        return self.nodes[node_id]

    def to_dict(self) -> dict[str, Any]:
        """Serializes the IR graph to a dictionary."""
        return {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "roots": list(self.roots),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExecutionIR:
        """Deserializes the IR graph from a dictionary."""
        return cls(
            nodes=MappingProxyType({k: IRNode.from_dict(v) for k, v in data.get("nodes", {}).items()}),
            roots=tuple(data.get("roots", [])),
            metadata=MappingProxyType(data.get("metadata", {})),
        )

    def to_json(self) -> str:
        """Serializes the IR graph to JSON."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> ExecutionIR:
        """Deserializes the IR graph from JSON."""
        return cls.from_dict(json.loads(json_str))
