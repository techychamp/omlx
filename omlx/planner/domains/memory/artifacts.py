from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass(frozen=True)
class TensorLifetime:
    tensor_id: str
    creation_step: int
    last_use_step: int
    size_bytes: int
    can_be_reused: bool = False

@dataclass(frozen=True)
class MemoryDescriptor:
    total_estimated_memory: int
    peak_memory: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class MemoryRequirement:
    minimum_required: int
    recommended: int

@dataclass(frozen=True)
class AllocationGraph:
    allocations: List[Any] = field(default_factory=list)

@dataclass(frozen=True)
class LifetimeGraph:
    lifetimes: List[TensorLifetime] = field(default_factory=list)

@dataclass(frozen=True)
class MemoryCompatibilityReport:
    is_compatible: bool
    reasons: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class MemoryValidationReport:
    is_valid: bool
    errors: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class MemoryStatistics:
    peak_allocated: int
    reuse_amount: int

@dataclass(frozen=True)
class MemoryPlan:
    """
    Immutable composition of all memory planning decisions.
    Consumed by ExecutionEngine.
    """
    descriptor: MemoryDescriptor
    requirement: MemoryRequirement
    allocation_graph: AllocationGraph = field(default_factory=AllocationGraph)
    lifetime_graph: LifetimeGraph = field(default_factory=LifetimeGraph)
    strategy_intent: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)
