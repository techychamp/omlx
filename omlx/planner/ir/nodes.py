# SPDX-License-Identifier: Apache-2.0
"""
Execution IR Nodes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import enum
from typing import Any
from types import MappingProxyType

class IRNodeType(str, enum.Enum):
    """Logical execution steps for an IR graph."""
    PREFILL = "prefill"
    FORWARD = "forward"
    SAMPLE = "sample"
    VERIFY = "verify"
    EMIT = "emit"
    CACHE_READ = "cache_read"
    CACHE_WRITE = "cache_write"
    ATTENTION = "attention"
    ROUTING = "routing"
    SYNCHRONIZATION = "synchronization"
    BARRIER = "barrier"
    ALLOCATION = "allocation"
    RELEASE = "release"
    ROOT = "root"

@dataclass(frozen=True)
class IRNode:
    """An immutable node in the Execution IR DAG."""
    id: str
    node_type: IRNodeType
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "node_type": self.node_type.value,
            "dependencies": list(self.dependencies),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IRNode:
        return cls(
            id=data["id"],
            node_type=IRNodeType(data["node_type"]),
            dependencies=tuple(data.get("dependencies", [])),
            metadata=MappingProxyType(data.get("metadata", {})),
        )
