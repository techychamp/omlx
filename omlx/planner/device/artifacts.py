from dataclasses import dataclass, field
from typing import Dict, Any

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
    metadata: Dict[str, Any] = field(default_factory=dict)
