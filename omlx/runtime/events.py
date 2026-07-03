# SPDX-License-Identifier: Apache-2.0
"""
Event system for OMLX inference runtime.
"""

from __future__ import annotations

import enum
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable


__all__ = ["LifecycleEvent", "ExecutionEvent", "Event", "EventBus"]


class LifecycleEvent(enum.Enum):
    """Lifecycle events for requests."""
    REQUEST_ADDED = "request_added"
    REQUEST_FINISHED = "request_finished"
    REQUEST_CANCELLED = "request_cancelled"


class ExecutionEvent(enum.Enum):
    """Execution events within the generation pipeline."""
    BEFORE_PREFILL = "before_prefill"
    AFTER_PREFILL = "after_prefill"
    BEFORE_FORWARD = "before_forward"
    AFTER_FORWARD = "after_forward"
    BEFORE_SAMPLE = "before_sample"
    AFTER_SAMPLE = "after_sample"
    BEFORE_EMIT = "before_emit"
    AFTER_EMIT = "after_emit"


@dataclass
class Event:
    """An event emitted during the request lifecycle or execution pipeline."""
    type: LifecycleEvent | ExecutionEvent
    request_id: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.monotonic)


class EventBus:
    """Per-engine event bus for pub/sub communication.
    
    Strategies subscribe to events; the scheduler publishes them.
    """
    def __init__(self) -> None:
        self._subscribers: dict[LifecycleEvent | ExecutionEvent, list[Callable[[Event], None]]] = defaultdict(list)

    def subscribe(self, event_type: LifecycleEvent | ExecutionEvent, callback: Callable[[Event], None]) -> None:
        """Subscribe a callback to an event type."""
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: LifecycleEvent | ExecutionEvent, callback: Callable[[Event], None]) -> None:
        """Unsubscribe a callback from an event type."""
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        for callback in self._subscribers[event.type]:
            callback(event)

    def clear(self) -> None:
        """Clear all subscribers."""
        self._subscribers.clear()
