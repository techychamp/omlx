from dataclasses import dataclass
from typing import Optional, Any
import uuid

from omlx.planner.domains.bundle import PlanningBundle
# For typing without circular import during initialization
# The actual integration is loosely coupled, QueueSession is passed at handoff.
try:
    from omlx.framework.queue.artifacts import QueueSession
except ImportError:
    QueueSession = Any

@dataclass
class RuntimeSession:
    """
    Coordinates the execution lifecycle for a single generation/execution request.
    Owns the PlanningBundle but does not perform planning itself.
    Takes ownership from a queue session if one is provided.
    """
    session_id: str
    planning_bundle: Optional[PlanningBundle] = None
    state: str = "created"
    queue_session: Optional[QueueSession] = None

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
