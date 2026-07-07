from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
from types import MappingProxyType

from .descriptor import DiffusionDescriptor, TimestepDescriptor
from .requirement import DiffusionRequirement
from .report import DiffusionValidationReport

@dataclass(frozen=True)
class DiffusionPlan:
    """Immutable plan for diffusion execution."""
    descriptor: DiffusionDescriptor
    requirement: DiffusionRequirement
    timestep_schedule: Tuple[Any, ...] = tuple()
    denoising_plan: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    validation: Optional[DiffusionValidationReport] = None
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
@dataclass(frozen=True)
class DiffusionPlan:
    """Immutable plan for diffusion execution."""
    descriptor: DiffusionDescriptor
    requirement: DiffusionRequirement
    timestep_schedule: List[Any] = field(default_factory=list)
    denoising_plan: Dict[str, Any] = field(default_factory=dict)
    validation: Optional[DiffusionValidationReport] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
