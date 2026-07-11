# SPDX-License-Identifier: Apache-2.0
"""
Immutable Execution Traces.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from types import MappingProxyType
import time
import uuid

@dataclass(frozen=True)
class TraceEvent:
    id: str
    timestamp: float
    phase: str
    component: str
    operation: str
    duration_sec: Optional[float] = None
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    status: str = "success"
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class ExecutionTrace:
    events: tuple[TraceEvent, ...] = field(default_factory=tuple)

    def with_event(self, event: TraceEvent) -> "ExecutionTrace":
        return ExecutionTrace(events=self.events + (event,))

class TraceBuilder:
    def __init__(self):
        self._events: List[TraceEvent] = []

    def record(self, phase: str, component: str, operation: str, duration_sec: Optional[float] = None,
               parent_id: Optional[str] = None, status: str = "success", metadata: Dict[str, Any] = None) -> str:
        event_id = str(uuid.uuid4())
        event = TraceEvent(
            id=event_id,
            timestamp=time.time(),
            phase=phase,
            component=component,
            operation=operation,
            duration_sec=duration_sec,
            parent_id=parent_id,
            status=status,
            metadata=MappingProxyType(metadata or {})
        )
        self._events.append(event)
        return event_id

    def build(self) -> ExecutionTrace:
        return ExecutionTrace(events=tuple(self._events))
