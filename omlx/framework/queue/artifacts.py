from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import time

@dataclass(frozen=True)
class QueueDescriptor:
    """Describes the configuration and characteristics of a queue."""
    queue_id: str
    max_capacity: int
    prioritization_supported: bool = False
    distributed: bool = False

@dataclass(frozen=True)
class QueueEntry:
    """Represents an admitted request in the queue."""
    entry_id: str
    request: Any  # The original request object (GenerationRequest, etc.)
    admitted_at: float = field(default_factory=time.time)
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class QueueSession:
    """Represents the pre-execution lifecycle of a request in the queue."""
    session_id: str
    entry: QueueEntry
    descriptor: QueueDescriptor
    status: str = "queued"

@dataclass(frozen=True)
class QueueStatistics:
    """Immutable snapshot of queue statistics."""
    queue_id: str
    current_depth: int
    total_admitted: int
    total_dequeued: int
    average_wait_time: float
    timestamp: float = field(default_factory=time.time)

@dataclass(frozen=True)
class QueueValidationReport:
    """Diagnostic report on queue validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class QueueDiagnostics:
    """Immutable snapshot of queue diagnostics and health."""
    queue_id: str
    is_healthy: bool
    last_error: Optional[str] = None
    validation_report: Optional[QueueValidationReport] = None
    timestamp: float = field(default_factory=time.time)
