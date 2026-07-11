from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class BatchRequirement:
    max_batch_size: int
    max_tokens: int

@dataclass(frozen=True)
class BatchDescriptor:
    batch_id: str
    request_ids: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class BatchCompatibilityReport:
    is_compatible: bool
    reason: Optional[str] = None

@dataclass(frozen=True)
class BatchPlan:
    batch_descriptor: BatchDescriptor
    requirements: BatchRequirement
    compatibility_report: BatchCompatibilityReport

@dataclass(frozen=True)
class BatchStatistics:
    total_batches: int = 0
    average_batch_size: float = 0.0

@dataclass(frozen=True)
class BatchValidationReport:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
