import pytest
import threading
import time
from unittest.mock import MagicMock, patch

from omlx.runtime.observability import (
    get_observer, set_observer, reset_observer, Observer,
    ExecutionTrace, ArtifactBundle, TelemetrySnapshot, ObservationSession, Timeline
)
from omlx.runtime.streaming.controller import StreamingController
from omlx.runtime.streaming.events import StreamingEvent, StreamingEventType
from omlx.runtime.streaming.types import StreamCompletion

def test_observer_lifecycle():
    reset_observer()

    obs1 = get_observer()
    assert obs1 is not None

    obs2 = get_observer()
    assert obs1 is obs2

    reset_observer()
    obs3 = get_observer()
    assert obs1 is not obs3

def test_observe_phase():
    obs = Observer()
    set_observer(obs)

    with obs.observe_phase("Phase1", "Comp1", "Op1", {"key": "val"}):
        time.sleep(0.01)

    trace = obs.get_trace()
    assert len(trace.events) == 1
    event = trace.events[0]
    assert event.phase == "Phase1"
    assert event.component == "Comp1"
    assert event.operation == "Op1"
    assert event.status == "success"
    assert "key" in event.metadata

    timeline = obs.get_timeline()
    assert len(timeline.events) == 1
    t_event = timeline.events[0]
    assert t_event.phase == "Phase1"

    telemetry = obs.get_telemetry()
    assert "Phase1.Op1.count" in telemetry.counters
    assert telemetry.counters["Phase1.Op1.count"] == 1

    reset_observer()

def test_observe_phase_error():
    obs = Observer()
    set_observer(obs)

    with pytest.raises(ValueError):
        with obs.observe_phase("Phase2", "Comp2", "Op2"):
            raise ValueError("test error")

    trace = obs.get_trace()
    assert len(trace.events) == 1
    event = trace.events[0]
    assert event.status == "error: test error"

    assert len(obs.diagnostics) == 1
    assert "test error" in obs.diagnostics[0]

    reset_observer()

def test_streaming_integration():
    obs = Observer()
    set_observer(obs)

    controller = StreamingController()
    session = controller.create_session()

    event = StreamingEvent(
        event_type=StreamingEventType.TOKEN_GENERATED,
        timestamp=time.time(),
        payload={"token": "test"}
    )
    controller.publish_event(session.session_id, event)

    trace = obs.get_trace()
    # SESSION_STARTED + TOKEN_GENERATED
    assert len(trace.events) == 2
    assert any(e.phase == "Streaming" and "TOKEN" in str(e.operation).upper() for e in trace.events)

    timeline = obs.get_timeline()
    assert len(timeline.events) == 2

    reset_observer()

def test_build_session():
    obs = Observer()
    obs.track_artifact("test_artifact", {"data": 123})
    obs.add_diagnostic("test diag")

    session = obs.build_session(
        end_time=time.time(),
        status="success",
        generated_tokens=[1, 2, 3],
        statistics={"stat1": 10}
    )

    assert isinstance(session, ObservationSession)
    assert session.status == "success"
    assert list(session.generated_tokens) == [1, 2, 3]
    assert "test_artifact" in session.artifacts.artifacts
    assert session.diagnostics == ("test diag",)
    assert dict(session.statistics) == {"stat1": 10}
