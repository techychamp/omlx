import pytest
from omlx.tooling.replay.timeline import CompilerTimeline, TimelineEvent

def test_compiler_timeline():
    trace_events = [
        {"event": "session_start", "timestamp": 100.0, "data": {}},
        {"event": "pass_start_opt1", "timestamp": 101.0, "data": {}},
        {"event": "pass_end_opt1", "timestamp": 102.0, "data": {"duration_sec": 1.0}},
    ]

    timeline = CompilerTimeline.from_trace(trace_events)
    assert len(timeline.events) == 3
    assert timeline.events[2].duration_sec == 1.0
