# SPDX-License-Identifier: Apache-2.0
"""
Immutable cache planning artifacts.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Tuple

@dataclass(frozen=True)
class CachePlan:
    """
    Immutable plan for cache execution.
    Produced by the Compiler, consumed by ExecutionEngine.
    """
    plan_id: str
    allocation_strategy: str
    eviction_policy: str
    cache_layout: str
    max_capacity: int
    dependencies: Tuple[str, ...] = tuple()
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
