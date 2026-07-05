import pytest
from types import MappingProxyType
from omlx.tooling.session.compiler_session import CompilerSession
from omlx.tooling.session.replay_session import ReplaySession
from omlx.tooling.session.browser import CompilerSessionBrowser
from omlx.planner.plan import ExecutionPlan
from omlx.capabilities.descriptor import ExecutionFamily, CacheLayoutType

def test_session_browser():
    replay = ReplaySession(
        compiler_version="2.0",
        planner_version="1.0",
        feature_flags=MappingProxyType({}),
        backend="mlx",
        optimization_pipeline=(),
        timestamps=MappingProxyType({})
    )

    plan = ExecutionPlan(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        execution_backend="mlx",
        execution_mode="streaming",
        execution_topology="single_device",
        cache_strategy=CacheLayoutType.PAGED,
        scheduler_strategy="continuous_batching",
        verification_stages=("verify_graph",),
        optimization_passes=("pass1",)
    )

    session = CompilerSession(
        replay_session=replay,
        artifacts=MappingProxyType({
            "ExecutionPlan": plan,
            "LogicalIR": {"id": "logical_ir_mock"}
        }),
        diagnostics=("warn: test",),
        statistics=MappingProxyType({"time": 1.0})
    )

    browser = CompilerSessionBrowser(session)
    summary = browser.summary
    assert summary["version"] == "2.0"
    assert "ExecutionPlan" in summary["artifacts_available"]

    assert browser.get_artifact("ExecutionPlan") == plan

    pipeline = list(browser.walk_pipeline())
    assert len(pipeline) == 2
    assert pipeline[0][0] == "ExecutionPlan"
    assert pipeline[1][0] == "LogicalIR"

    assert browser.get_verification_stages() == ["verify_graph"]
