from typing import List, Dict, Any
from pydantic import BaseModel, Field

class ObservationSummary(BaseModel, frozen=True):
    session_id: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    status: str

class ObservationQueryBuilder:
    def __init__(self):
        self._session_id = None

    def with_session(self, session_id: str) -> 'ObservationQueryBuilder':
        self._session_id = session_id
        return self

    def build(self) -> dict:
        return {"session_id": self._session_id}

class ObservationService:
    def sessions(self) -> List[ObservationSummary]:
        return []

    def timeline(self, session_id: str) -> List[dict]:
        return []

    def statistics(self, session_id: str) -> dict:
        return {}

    def diagnostics(self, session_id: str) -> dict:
        return {}
