import pytest
import time
from unittest.mock import MagicMock

from omlx.framework.queue.artifacts import QueueDescriptor, QueueEntry, QueueSession, QueueStatistics
from omlx.framework.queue.admission import QueueAdmissionController
from omlx.framework.queue.manager import QueueManager
from omlx.framework.queue.observability import capture_queue_metrics, record_queue_latency
from omlx.framework.queue.api import QueueAPI
from omlx.runtime.session import RuntimeSession

def test_queue_artifacts():
    # Test immutability and creation
    entry = QueueEntry(entry_id="1", request="mock_request", priority=1)

    with pytest.raises(Exception): # FrozenInstanceError or similar
        entry.priority = 2

    assert entry.priority == 1
    assert entry.request == "mock_request"
    assert entry.metadata == {}

def test_queue_admission():
    controller = QueueAdmissionController()
    entry = controller.admit_request("mock_request", priority=5, metadata={"test": "data"})

    assert isinstance(entry, QueueEntry)
    assert entry.request == "mock_request"
    assert entry.priority == 5
    assert entry.metadata == {"test": "data"}
    assert entry.admitted_at > 0

def test_queue_manager_lifecycle():
    manager = QueueManager(max_capacity=2)

    # Enqueue
    session1 = manager.enqueue("req1", priority=1)
    session2 = manager.enqueue("req2", priority=10) # Higher priority

    assert manager.current_depth == 2
    assert manager.descriptor.max_capacity == 2

    # Capacity limit
    with pytest.raises(RuntimeError):
        manager.enqueue("req3")

    # Dequeue (should be req2 due to priority)
    dequeued1 = manager.dequeue()
    assert dequeued1 is not None
    assert dequeued1.entry.request == "req2"
    assert dequeued1.status == "ready_for_execution"

    dequeued2 = manager.dequeue()
    assert dequeued2 is not None
    assert dequeued2.entry.request == "req1"

    # Empty
    assert manager.dequeue() is None

    # Remove
    assert manager.remove_session(session1.session_id) is True
    assert manager.get_session(session1.session_id) is None

def test_runtime_session_handoff():
    manager = QueueManager()
    manager.enqueue("req1")
    queue_session = manager.dequeue()

    assert queue_session is not None

    # Handoff to runtime
    runtime_session = RuntimeSession.from_queue_session(queue_session)

    assert isinstance(runtime_session, RuntimeSession)
    assert runtime_session.state == "created"
    assert runtime_session.queue_session == queue_session

def test_queue_observability_and_api():
    manager = QueueManager()

    session = manager.enqueue("req1")
    time.sleep(0.01) # Small wait

    api = QueueAPI(manager)

    # Check stats before dequeue
    stats = api.get_statistics()
    assert stats.current_depth == 1
    assert stats.total_admitted == 1
    assert stats.total_dequeued == 0

    manager.dequeue()

    # Check stats after dequeue
    stats_after = api.get_statistics()
    assert stats_after.current_depth == 0
    assert stats_after.total_dequeued == 1
    assert stats_after.average_wait_time > 0

    latency = record_queue_latency(session.entry)
    assert latency > 0

    # Diagnostics
    diag = api.get_diagnostics()
    assert diag.is_healthy is True
    assert diag.validation_report is not None
    assert diag.validation_report.is_valid is True
