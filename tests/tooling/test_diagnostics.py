import pytest
from types import MappingProxyType
from omlx.tooling.session import ReplaySession, CompilerSession
from omlx.tooling.trace.tracer import InteractiveTrace
from omlx.tooling.introspection.diagnostics import DiagnosticsEngine

def test_diagnostics_engine():
    replay = ReplaySession(
        compiler_version="1.0",
        planner_version="1.0",
        feature_flags=MappingProxyType({}),
        backend="mlx",
        optimization_pipeline=(),
        timestamps=MappingProxyType({})
    )

    session = CompilerSession(
        replay_session=replay,
        artifacts=MappingProxyType({"Plan": {}})
    )

    engine = DiagnosticsEngine()
    summary = engine.generate_compiler_summary(session)
    assert summary["artifact_count"] == 1
    assert summary["backend"] == "mlx"

    trace = InteractiveTrace()
    trace.record_event("pass_start_opt1")
    trace.timings["opt1"] = 0.5

    opt_summary = engine.generate_optimization_summary(trace)
    assert opt_summary["passes_run"] == 1
    assert opt_summary["total_time"] == 0.5
