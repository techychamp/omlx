# SPDX-License-Identifier: Apache-2.0
"""
Physical Execution IR Graph.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any
import json
from .operations import PhysicalOperation

@dataclass(frozen=True)
class PhysicalIR:
    """An immutable, backend-aware representation of an execution plan."""
    operations: MappingProxyType[str, PhysicalOperation]
    roots: tuple[str, ...]
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def get_operation(self, op_id: str) -> PhysicalOperation:
        if op_id not in self.operations:
            raise KeyError(f"Operation {op_id} not found in PhysicalIR")
        return self.operations[op_id]

    def to_dict(self) -> dict[str, Any]:
        return {
            "operations": {k: v.to_dict() for k, v in self.operations.items()},
            "roots": list(self.roots),
            "metadata": dict(self.metadata)
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PhysicalIR:
        return cls(
            operations=MappingProxyType({k: PhysicalOperation.from_dict(v) for k, v in data.get("operations", {}).items()}),
            roots=tuple(data.get("roots", [])),
            metadata=MappingProxyType(data.get("metadata", {}))
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> PhysicalIR:
        return cls.from_dict(json.loads(json_str))
