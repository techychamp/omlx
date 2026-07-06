from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Tuple

@dataclass(frozen=True)
class DeviceDescriptor:
    device_id: str
    device_type: str
    capabilities: Tuple[str, ...]
    total_memory: int

@dataclass(frozen=True)
class DeviceRequirement:
    required_device_type: str
    minimum_memory: int
    required_capabilities: Tuple[str, ...]

@dataclass(frozen=True)
class ExecutionPlacement:
    device_id: str
    strategy: str

@dataclass(frozen=True)
class ExecutionAffinity:
    affinity_group: str
    priority: int

@dataclass(frozen=True)
class DevicePlan:
    placement: ExecutionPlacement
    affinity: ExecutionAffinity
    requirements: DeviceRequirement
    planner_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class DeviceCompatibilityReport:
    is_compatible: bool
    missing_capabilities: Tuple[str, ...]
    memory_deficit: int

@dataclass(frozen=True)
class DeviceStatistics:
    device_id: str
    utilization_percentage: float
    memory_used: int

@dataclass(frozen=True)
class DeviceValidationReport:
    is_valid: bool
    errors: Tuple[str, ...]
    warnings: Tuple[str, ...]
