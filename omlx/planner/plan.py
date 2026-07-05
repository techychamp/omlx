from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from omlx.capabilities.descriptor import (
    ExecutionFamily, AttentionType, CacheLayoutType
)

@dataclass(frozen=True)
class ExecutionPlan:
    """Immutable execution plan produced by the ExecutionPlanner."""
    execution_family: ExecutionFamily
    execution_backend: str
    execution_mode: str
    execution_topology: str
    cache_strategy: CacheLayoutType
    scheduler_strategy: str
    verification_stages: tuple[str, ...]
    optimization_passes: tuple[str, ...]

    execution_hints: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    hardware_requirements: tuple[str, ...] = tuple()
    planner_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
