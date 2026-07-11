import pytest
from types import MappingProxyType
from omlx.tooling.session import ReplaySession, CompilerSession
from omlx.tooling.replay import CompilerReplay

def test_replay_session_creation():
    session = ReplaySession(
        compiler_version="1.0",
        planner_version="1.0",
        feature_flags=MappingProxyType({"flag1": True}),
        backend="mlx",
        optimization_pipeline=("pass1",),
        timestamps=MappingProxyType({"start": 0.0}),
    )
    assert session.compiler_version == "1.0"

def test_compiler_session_creation():
    replay_session = ReplaySession(
        compiler_version="1.0",
        planner_version="1.0",
        feature_flags=MappingProxyType({}),
        backend="mlx",
        optimization_pipeline=(),
        timestamps=MappingProxyType({}),
    )
    session = CompilerSession(
        replay_session=replay_session,
    )
    assert session.replay_session == replay_session

def test_compiler_replay():
    session = ReplaySession(
        compiler_version="1.0",
        planner_version="1.0",
        feature_flags=MappingProxyType({}),
        backend="mlx",
        optimization_pipeline=(),
        timestamps=MappingProxyType({}),
    )
    replay = CompilerReplay(session)
    res = replay.replay()
    assert res["status"] == "success"

from omlx.tooling.trace.tracer import InteractiveTrace

def test_interactive_trace():
    trace = InteractiveTrace()
    trace.record_event("start", {"info": "init"})
    trace.record_event("end", {"info": "done"})
    trace.add_diagnostic("warning")

    md = trace.export_markdown()
    assert "Compiler Trace Timeline" in md
    assert "start" in md
    assert "warning" in md

    mmd = trace.export_mermaid()
    assert "gantt" in mmd
    assert "start" in mmd
