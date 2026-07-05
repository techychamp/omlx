import pytest
import time
import threading
from typing import Any
from dataclasses import dataclass

from omlx.runtime.events import (
    EventBus,
    Event,
    EventCategory,
    LifecycleEvent,
    ExecutionEvent,
    RuntimeLifecycleEvent,
    EventDispatchError
)

def test_basic_pub_sub():
    bus = EventBus()
    received_events = []

    def handler(event: Event):
        received_events.append(event)

    bus.subscribe(LifecycleEvent.REQUEST_ADDED, handler)

    event = Event(type=LifecycleEvent.REQUEST_ADDED, source="test")
    bus.publish(event)

    assert len(received_events) == 1
    assert received_events[0].type == LifecycleEvent.REQUEST_ADDED
    assert received_events[0].source == "test"

    # Publish different event type
    event2 = Event(type=LifecycleEvent.REQUEST_FINISHED)
    bus.publish(event2)
    assert len(received_events) == 1  # Should not receive it

def test_unsubscribe():
    bus = EventBus()
    received_events = []

    def handler(event: Event):
        received_events.append(event)

    bus.subscribe(LifecycleEvent.REQUEST_ADDED, handler)
    bus.unsubscribe(LifecycleEvent.REQUEST_ADDED, handler)

    event = Event(type=LifecycleEvent.REQUEST_ADDED)
    bus.publish(event)

    assert len(received_events) == 0

def test_async_dispatch():
    bus = EventBus()
    received_events = []
    event_done = threading.Event()

    def handler(event: Event):
        received_events.append(event)
        event_done.set()

    bus.subscribe("test_event", handler)
    bus.publish_async(Event(type="test_event"))

    # Wait for the async thread to execute the callback
    event_done.wait(timeout=1.0)

    assert len(received_events) == 1
    assert received_events[0].type == "test_event"

def test_priority_ordering():
    bus = EventBus()
    execution_order = []

    def handler_low(event: Event):
        execution_order.append("low")

    def handler_high(event: Event):
        execution_order.append("high")

    def handler_med(event: Event):
        execution_order.append("med")

    bus.subscribe("test_event", handler_low, priority=10)
    bus.subscribe("test_event", handler_high, priority=100)
    bus.subscribe("test_event", handler_med, priority=50)

    bus.publish(Event(type="test_event"))

    assert execution_order == ["high", "med", "low"]

def test_error_isolation():
    bus = EventBus()
    execution_order = []

    def handler_fail(event: Event):
        execution_order.append("fail")
        raise RuntimeError("Handler failed!")

    def handler_success(event: Event):
        execution_order.append("success")

    # High priority fails, low priority should still run
    bus.subscribe("test_event", handler_fail, priority=100)
    bus.subscribe("test_event", handler_success, priority=10)

    # Should not raise exception to the caller
    bus.publish(Event(type="test_event"))

    assert execution_order == ["fail", "success"]

    metrics = bus.get_metrics()
    assert metrics["handler_errors"] == 1
    assert metrics["events_published"] == 1

def test_wildcard_subscriptions():
    bus = EventBus()
    received = []

    def handler(event: Event):
        received.append(event.type)

    bus.subscribe("*", handler)

    bus.publish(Event(type="event1"))
    bus.publish(Event(type="event2"))

    assert len(received) == 2
    assert "event1" in received
    assert "event2" in received

def test_filtered_subscriptions():
    bus = EventBus()
    received = []

    def handler(event: Event):
        received.append(event.payload.get("val"))

    # Only process events where payload.val > 10
    def filter_fn(event: Event) -> bool:
        return event.payload.get("val", 0) > 10

    bus.subscribe("data_event", handler, filter_fn=filter_fn)

    bus.publish(Event(type="data_event", payload={"val": 5}))
    bus.publish(Event(type="data_event", payload={"val": 15}))
    bus.publish(Event(type="data_event", payload={"val": 8}))
    bus.publish(Event(type="data_event", payload={"val": 20}))

    assert received == [15, 20]

def test_thread_safety():
    bus = EventBus()

    # Run multiple threads that subscribe, publish, and unsubscribe simultaneously
    def worker():
        for i in range(100):
            def handler(e): pass
            bus.subscribe("event", handler)
            bus.publish(Event(type="event"))
            bus.unsubscribe("event", handler)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Should complete without deadlock or crashes
    assert True

def test_metrics():
    bus = EventBus()

    def handler(event: Event):
        pass

    bus.subscribe("test_event", handler)

    for _ in range(5):
        bus.publish(Event(type="test_event"))

    metrics = bus.get_metrics()
    assert metrics["events_published"] == 5
    assert metrics["events_dispatched"] == 5
    assert metrics["handler_errors"] == 0
    assert metrics["total_dispatch_time_ms"] >= 0.0
