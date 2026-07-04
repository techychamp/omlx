# SPDX-License-Identifier: Apache-2.0
"""
Event system for OMLX inference runtime.
"""

from __future__ import annotations

import enum
import time
import uuid
import threading
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


__all__ = [
    "LifecycleEvent",
    "ExecutionEvent",
    "Event",
    "EventBus",
    "EventCategory",
    "EventContext",
    "RuntimeLifecycleEvent",
    "EventDispatchError"
]


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
    LOGICAL_IR_BUILT = "logical_ir_built"
    LOGICAL_IR_OPTIMIZED = "logical_ir_optimized"
    LOWERING_STARTED = "lowering_started"
    LOWERING_COMPLETED = "lowering_completed"
    PHYSICAL_IR_BUILT = "physical_ir_built"
    COMPILER_PASS_COMPLETED = "compiler_pass_completed"
    COMPILATION_FAILED = "compilation_failed"



class EventDispatchError(Exception):
    """Raised when an event handler throws an exception."""
    pass

logger = logging.getLogger("omlx.runtime.events")

class EventCategory(enum.Enum):
    """Categories of runtime events."""
    RUNTIME = "runtime"
    LIFECYCLE = "lifecycle"
    CONFIGURATION = "configuration"
    PLUGIN = "plugin"
    VERIFICATION = "verification"
    METRICS = "metrics"
    TRACING = "tracing"
    ENGINE = "engine"
    SCHEDULER = "scheduler"
    EXECUTION = "execution"
    MODEL = "model"
    BACKEND = "backend"
    ADAPTER = "adapter"
    CAPABILITY = "capability"
    REGISTRY = "registry"
    ADMIN = "admin"
    API = "api"
    HEALTH = "health"
    CUSTOM = "custom"


class RuntimeLifecycleEvent(enum.Enum):
    """Specific lifecycle events for the Runtime itself."""
    RUNTIME_STARTING = "runtime_starting"
    RUNTIME_STARTED = "runtime_started"
    RUNTIME_READY = "runtime_ready"
    RUNTIME_STOPPING = "runtime_stopping"
    RUNTIME_STOPPED = "runtime_stopped"
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_FAILED = "plugin_failed"
    REGISTRY_LOCKED = "registry_locked"
    ENGINE_CREATED = "engine_created"
    ENGINE_DESTROYED = "engine_destroyed"
    MODEL_LOADED = "model_loaded"
    MODEL_EVICTED = "model_evicted"
    VERIFICATION_STARTED = "verification_started"
    VERIFICATION_COMPLETED = "verification_completed"
    CONFIGURATION_RELOADED = "configuration_reloaded"
    HEALTH_CHANGED = "health_changed"


@dataclass
class EventContext:
    """Context in which an event executes."""
    runtime_context: Any
    execution_context: Optional[Any] = None
    logger: Optional[Any] = None
    cancellation_token: Optional[Any] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    tracing_context: Optional[Any] = None


@dataclass
class Event:
    """An event emitted during the request lifecycle or execution pipeline."""
    type: LifecycleEvent | ExecutionEvent | RuntimeLifecycleEvent | str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.monotonic)
    source: str = "system"
    category: EventCategory = EventCategory.CUSTOM
    priority: int = 0
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    request_id: Optional[str] = None
    engine_id: Optional[str] = None
    model_id: Optional[str] = None
    version: str = "1.0"

    # Legacy fields for backward compatibility
    @property
    def data(self) -> dict[str, Any]:
        return self.payload

    @data.setter
    def data(self, value: dict[str, Any]) -> None:
        self.payload = value





class EventBus:
    """Per-engine event bus for pub/sub communication."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        # subscribers maps event type to list of (callback, priority, filter_fn) tuples
        self._subscribers: dict[Any, list[tuple[Callable[[Event], None], int, Optional[Callable[[Event], bool]]]]] = defaultdict(list)
        self._wildcard_subscribers: list[tuple[Callable[[Event], None], int, Optional[Callable[[Event], bool]]]] = []

        # Metrics
        self._metrics = {
            "events_published": 0,
            "events_dispatched": 0,
            "handler_errors": 0,
            "total_dispatch_time_ms": 0.0
        }

    def subscribe(self, event_type: Any, callback: Callable[[Event], None], priority: int = 0, filter_fn: Optional[Callable[[Event], bool]] = None) -> None:
        """Subscribe a callback to an event type."""
        self.register_handler(event_type, callback, priority, filter_fn)

    def register_handler(self, event_type: Any, callback: Callable[[Event], None], priority: int = 0, filter_fn: Optional[Callable[[Event], bool]] = None) -> None:
        """Register a handler for an event type. Use '*' for wildcard (all events)."""
        with self._lock:
            if event_type == "*":
                # Check if already registered
                if not any(cb == callback for cb, _, _ in self._wildcard_subscribers):
                    self._wildcard_subscribers.append((callback, priority, filter_fn))
                    # Sort by priority descending
                    self._wildcard_subscribers.sort(key=lambda x: x[1], reverse=True)
            else:
                # Check if already registered
                if not any(cb == callback for cb, _, _ in self._subscribers[event_type]):
                    self._subscribers[event_type].append((callback, priority, filter_fn))
                    # Sort by priority descending
                    self._subscribers[event_type].sort(key=lambda x: x[1], reverse=True)

    def unsubscribe(self, event_type: Any, callback: Callable[[Event], None]) -> None:
        """Unsubscribe a callback from an event type."""
        self.remove_handler(event_type, callback)

    def remove_handler(self, event_type: Any, callback: Callable[[Event], None]) -> None:
        """Remove a handler from an event type."""
        with self._lock:
            if event_type == "*":
                self._wildcard_subscribers = [
                    (cb, p, f) for cb, p, f in self._wildcard_subscribers if cb != callback
                ]
            else:
                if event_type in self._subscribers:
                    self._subscribers[event_type] = [
                        (cb, p, f) for cb, p, f in self._subscribers[event_type] if cb != callback
                    ]

    def _get_handlers_for_event(self, event: Event) -> list[Callable[[Event], None]]:
        """Get all handlers for an event, properly sorted by priority."""
        handlers_to_run = []

        with self._lock:
            # Get typed subscribers
            typed_subs = self._subscribers.get(event.type, [])

            # Combine all applicable subscribers (typed + wildcard)
            # Both lists are already sorted by priority internally, but we need to merge them
            all_applicable = []

            for cb, priority, filter_fn in typed_subs:
                if filter_fn is None or filter_fn(event):
                    all_applicable.append((cb, priority))

            for cb, priority, filter_fn in self._wildcard_subscribers:
                if filter_fn is None or filter_fn(event):
                    all_applicable.append((cb, priority))

            # Sort combined list by priority (descending)
            all_applicable.sort(key=lambda x: x[1], reverse=True)

            handlers_to_run = [cb for cb, _ in all_applicable]

        return handlers_to_run

    def publish(self, event: Event) -> None:
        """Publish an event synchronously to all subscribers."""
        start_time = time.time()

        with self._lock:
            self._metrics["events_published"] += 1

        handlers = self._get_handlers_for_event(event)

        # Execute outside lock to avoid deadlocks
        for callback in handlers:
            try:
                callback(event)
                with self._lock:
                    self._metrics["events_dispatched"] += 1
            except Exception as e:
                logger.error(f"Error dispatching event {event.type} to {callback}: {e}")
                with self._lock:
                    self._metrics["handler_errors"] += 1
                # Continue remaining handlers; error isolation

        dispatch_time_ms = (time.time() - start_time) * 1000
        with self._lock:
            self._metrics["total_dispatch_time_ms"] += dispatch_time_ms

    def publish_async(self, event: Event) -> None:
        """Publish an event asynchronously."""
        def _dispatch():
            self.publish(event)

        t = threading.Thread(target=_dispatch, daemon=True)
        t.start()

    def get_metrics(self) -> dict[str, Any]:
        """Get a copy of the current metrics."""
        with self._lock:
            return dict(self._metrics)

    def clear(self) -> None:
        """Clear all subscribers and reset metrics."""
        with self._lock:
            self._subscribers.clear()
            self._wildcard_subscribers.clear()
            self._metrics = {
                "events_published": 0,
                "events_dispatched": 0,
                "handler_errors": 0,
                "total_dispatch_time_ms": 0.0
            }
