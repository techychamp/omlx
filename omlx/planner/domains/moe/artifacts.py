from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from types import MappingProxyType

@dataclass(frozen=True)
class ExpertDescriptor:
    id: str
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class RoutingDescriptor:
    id: str
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class ExpertGroup:
    id: str
    experts: Tuple[ExpertDescriptor, ...]

@dataclass(frozen=True)
class RoutingRequirement:
    requirement_type: str
    details: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class RoutingStatistics:
    expert_usage: MappingProxyType[str, int] = field(default_factory=lambda: MappingProxyType({}))
    total_routings: int = 0

@dataclass(frozen=True)
class RoutingCompatibilityReport:
    is_compatible: bool
    reasons: Tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class RoutingValidationReport:
    is_valid: bool
    errors: Tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class MoEPlan:
    experts: Tuple[ExpertDescriptor, ...] = field(default_factory=tuple)
    routing: Optional[RoutingDescriptor] = None
    groups: Tuple[ExpertGroup, ...] = field(default_factory=tuple)
    requirements: Tuple[RoutingRequirement, ...] = field(default_factory=tuple)
    statistics: Optional[RoutingStatistics] = None
    compatibility: Optional[RoutingCompatibilityReport] = None
    validation: Optional[RoutingValidationReport] = None
