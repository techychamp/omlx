# SPDX-License-Identifier: Apache-2.0
"""
Physical Operations.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import enum
from types import MappingProxyType
from typing import Any

class PhysicalOperationType(str, enum.Enum):
    """Types of physical operations."""
    FORWARD = "forward"
    SAMPLING = "sampling"
    CACHE_LOOKUP = "cache_lookup"
    CACHE_UPDATE = "cache_update"
    SYNCHRONIZATION = "synchronization"
    NOOP = "noop"

@dataclass(frozen=True)
class PhysicalOperation:
    """An immutable physical operation to be executed."""
    id: str
    operation_type: PhysicalOperationType
    inputs: tuple[str, ...] = tuple()
    outputs: tuple[str, ...] = tuple()
    dependencies: tuple[str, ...] = tuple()
    execution_family: str | None = None
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "operation_type": self.operation_type.value,
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "dependencies": list(self.dependencies),
            "execution_family": self.execution_family,
            "metadata": dict(self.metadata)
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PhysicalOperation:
        return cls(
            id=data["id"],
            operation_type=PhysicalOperationType(data["operation_type"]),
            inputs=tuple(data.get("inputs", [])),
            outputs=tuple(data.get("outputs", [])),
            dependencies=tuple(data.get("dependencies", [])),
            execution_family=data.get("execution_family"),
            metadata=MappingProxyType(data.get("metadata", {}))
        )
