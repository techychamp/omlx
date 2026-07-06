from dataclasses import dataclass, field
from typing import Optional, Any, Dict, List
import uuid

from omlx.planner.domains.bundle import PlanningBundle
# For typing without circular import during initialization
# The actual integration is loosely coupled, QueueSession is passed at handoff.
try:
    from omlx.framework.queue.artifacts import QueueSession
except ImportError:
    QueueSession = Any

@dataclass(frozen=True)
class SessionDescriptor:
    """Immutable definition of the session request."""
    session_id: str
    client_id: Optional[str] = None
    priority: int = 0

@dataclass(frozen=True)
class SessionMetadata:
    """Immutable key-value pairs associated with the session."""
    created_at: float
    tags: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class SessionStatistics:
    """Immutable summary of execution statistics."""
    total_duration: float = 0.0
    tokens_generated: int = 0
    memory_peak: int = 0

@dataclass(frozen=True)
class SessionValidationReport:
    """Immutable diagnostic report of the session parameters."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

@dataclass
class RuntimeSession:
    """
    Coordinates the execution lifecycle for a single generation/execution request.
    Owns the PlanningBundle but does not perform planning itself.
    Takes ownership from a queue session if one is provided.
    Owns the execution context but does not perform execution itself.
    """
    session_id: str
    state: str = "created"
    queue_session: Optional[QueueSession] = None

    # Owned immutable artifacts
    descriptor: Optional[SessionDescriptor] = None
    metadata: Optional[SessionMetadata] = None
    statistics: Optional[SessionStatistics] = None
    validation_report: Optional[SessionValidationReport] = None

    # Attached execution resources
    planning_bundle: Optional[PlanningBundle] = None
    execution_context: Optional[Any] = None # Will be ExecutionContext
    device_context: Optional[Any] = None # Will be DeviceContext
    memory_context: Optional[Any] = None # Will be MemoryContext
    cache_session: Optional[Any] = None
    observation_session: Optional[Any] = None
    generation_strategy: Optional[Any] = None

    # Speculative Execution additions
    speculative_context: Optional[Any] = None
    verification_context: Optional[Any] = None
    speculative_statistics: Optional[Any] = None
    speculative_reports: List[Any] = field(default_factory=list)

    @classmethod
    def create(cls) -> "RuntimeSession":
        """Creates a default RuntimeSession without a preceding QueueSession."""
        return cls(session_id=str(uuid.uuid4()))

    @classmethod
    def from_queue_session(cls, queue_session: QueueSession, planning_bundle: Optional[PlanningBundle] = None) -> "RuntimeSession":
        """
        Creates a RuntimeSession by taking ownership from an admitted QueueSession.
        The queue session represents the pre-execution lifecycle, while this represents the execution lifecycle.
        """
        return cls(
            session_id=str(uuid.uuid4()),
            planning_bundle=planning_bundle,
            state="created",
            queue_session=queue_session
        )
