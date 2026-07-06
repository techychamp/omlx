from dataclasses import dataclass
from typing import Optional, Any
import uuid

from omlx.planner.domains.bundle import PlanningBundle

@dataclass
class RuntimeSession:
    """
    Coordinates the execution lifecycle for a single generation/execution request.
    Owns the PlanningBundle but does not perform planning itself.
    """
    session_id: str
    planning_bundle: Optional[PlanningBundle] = None
    state: str = "created"

    @classmethod
    def create(cls) -> "RuntimeSession":
        return cls(session_id=str(uuid.uuid4()))
