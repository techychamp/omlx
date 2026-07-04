# SPDX-License-Identifier: Apache-2.0
"""
Immutable Value types for semantic data flow in Execution IR.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import enum
from types import MappingProxyType
from typing import Any

class ValueType(str, enum.Enum):
    """Types of values that flow between logical nodes."""
    TOKEN_STREAM = "token_stream"
    HIDDEN_STATES = "hidden_states"
    ATTENTION_MASK = "attention_mask"
    KV_CACHE = "kv_cache"
    VERIFICATION_RESULT = "verification_result"
    EXPERT_ROUTING = "expert_routing"
    LATENT_REPRESENTATION = "latent_representation"
    LOGITS = "logits"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class Value:
    """An immutable value representing data produced or consumed by a node."""
    id: str
    value_type: ValueType
    producer_id: str | None = None
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "value_type": self.value_type.value,
            "producer_id": self.producer_id,
            "metadata": dict(self.metadata)
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Value:
        return cls(
            id=data["id"],
            value_type=ValueType(data.get("value_type", "unknown")),
            producer_id=data.get("producer_id"),
            metadata=MappingProxyType(data.get("metadata", {}))
        )
