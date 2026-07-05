# SPDX-License-Identifier: Apache-2.0
"""
Compiler Timeline
Provides an immutable representation of a compiler's execution timeline.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

@dataclass(frozen=True)
class TimelineEvent:
    event_name: str
    timestamp: float
    duration_sec: float | None = None
    data: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class CompilerTimeline:
    """Immutable timeline of compiler phases and optimizations."""
    events: tuple[TimelineEvent, ...]

    @classmethod
    def from_trace(cls, trace_events: list[dict[str, Any]]) -> "CompilerTimeline":
        """Builds an immutable timeline from a trace's raw event list."""
        timeline_events = []
        for e in trace_events:
            data_dict = e.get("data", {})
            timeline_events.append(TimelineEvent(
                event_name=e["event"],
                timestamp=e["timestamp"],
                duration_sec=data_dict.get("duration_sec"),
                data=MappingProxyType(data_dict)
            ))
        return cls(events=tuple(timeline_events))
