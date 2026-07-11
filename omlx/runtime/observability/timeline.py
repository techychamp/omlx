# SPDX-License-Identifier: Apache-2.0
"""
Immutable Timeline for ObservationSession.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from types import MappingProxyType

@dataclass(frozen=True)
class TimelineEvent:
    id: str
    timestamp: float
    phase: str
    duration_sec: Optional[float] = None
    thread_id: Optional[int] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class Timeline:
    events: tuple[TimelineEvent, ...] = field(default_factory=tuple)

    def with_event(self, event: TimelineEvent) -> "Timeline":
        return Timeline(events=self.events + (event,))

class TimelineBuilder:
    def __init__(self):
        self._events: List[TimelineEvent] = []

    def record(self, event_id: str, timestamp: float, phase: str, duration_sec: Optional[float] = None,
               thread_id: Optional[int] = None, session_id: Optional[str] = None,
               correlation_id: Optional[str] = None, metadata: Dict[str, Any] = None) -> None:

        event = TimelineEvent(
            id=event_id,
            timestamp=timestamp,
            phase=phase,
            duration_sec=duration_sec,
            thread_id=thread_id,
            session_id=session_id,
            correlation_id=correlation_id,
            metadata=MappingProxyType(metadata or {})
        )
        self._events.append(event)

    def build(self) -> Timeline:
        return Timeline(events=tuple(self._events))
