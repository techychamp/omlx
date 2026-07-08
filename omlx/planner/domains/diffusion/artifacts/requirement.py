from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from .descriptor import TimestepDescriptor, ConditioningDescriptor

@dataclass(frozen=True)
class DiffusionRequirement:
    """Requirements for diffusion execution."""
    timestep_descriptor: TimestepDescriptor
    conditioning_descriptor: ConditioningDescriptor
    batch_size: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
