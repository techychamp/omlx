import pytest
from unittest.mock import MagicMock

from omlx.runtime.builder import RuntimeBuilder
from omlx.api.v1.runtime import RuntimeService
from omlx.tooling.framework.unified import get_tooling
from omlx.tooling.inspector.queue_inspector import QueueInspector
from omlx.runtime.events import EventCategory, RuntimeLifecycleEvent

def test_runtime_owns_queue_manager():
    builder = RuntimeBuilder()
    runtime = builder.build()

    assert runtime.queue_manager is not None
    assert runtime.context.queue_manager is not None

    # Test enqueue/dequeue via runtime delegates to queue_manager
    session = runtime.enqueue_request("test_req", priority=5)
    assert session.entry.request == "test_req"
    assert session.entry.priority == 5

    dequeued = runtime.dequeue_request()
    assert dequeued.session_id == session.session_id
    assert dequeued.status == "ready_for_execution"

def test_runtime_service_exposes_queue_diagnostics():
    builder = RuntimeBuilder()
    runtime = builder.build()

    # Put one request to test stats
    runtime.enqueue_request("test_req", priority=5)

    service = RuntimeService(runtime)

    stats = service.get_queue_statistics()
    assert "queue_id" in stats
    assert stats["current_depth"] == 1

    diagnostics = service.get_queue_diagnostics()
    assert "is_healthy" in diagnostics
    assert diagnostics["is_healthy"] is True

def test_queue_inspector():
    tooling = get_tooling()
    inspector = tooling.get_inspector("queue")

    assert isinstance(inspector, QueueInspector)

    builder = RuntimeBuilder()
    runtime = builder.build()

    runtime.enqueue_request("test_req")
    runtime.enqueue_request("test_req2")

    depth = inspector.inspect_queue_depth(runtime.queue_manager)
    assert depth == 2

    stats = inspector.inspect_queue_statistics(runtime.queue_manager)
    assert stats is not None
    assert stats.current_depth == 2

    diag = inspector.inspect_queue_diagnostics(runtime.queue_manager)
    assert diag is not None
    assert diag.is_healthy is True
