# SPDX-License-Identifier: Apache-2.0
import pytest
from omlx.api.v1 import RuntimeBuilder
from omlx.tooling.framework.unified import get_tooling
from omlx.tooling.inspector.execution_inspector import ExecutionInspector
from omlx.tooling.inspector.backend_inspector import BackendInspector
from types import MappingProxyType

def test_execution_inspector():
    inspector = ExecutionInspector()

    class DummySchedule:
        execution_groups = [1, 2]

    schedule = DummySchedule()
    res = inspector.inspect_schedule(schedule)
    assert res["num_groups"] == 2

    res = inspector.inspect_context("dummy_context")
    assert res["type"] == "<class 'str'>"

def test_backend_inspector():
    inspector = BackendInspector()

    class DummyBackend:
        def get_capabilities(self):
            return {"cap": "value"}
        def get_diagnostics(self):
            return {"diag": "value"}

    backend = DummyBackend()
    assert inspector.inspect_capabilities(backend) == {"cap": "value"}
    assert inspector.inspect_diagnostics(backend) == {"diag": "value"}

def test_profiler():
    tooling = get_tooling()
    profiler = tooling.get_profiler("default")
    assert profiler is not None
    assert "stub" in profiler.get_compile_time_profile()
    assert "stub" in profiler.get_execution_time_profile()

def test_benchmark():
    tooling = get_tooling()
    benchmark = tooling.get_benchmark("default")
    assert benchmark is not None

    # Test real implementation
    report = benchmark.analyze_backend_comparison("a", "b", {"a": {"estimated_latency": 10}, "b": {"estimated_latency": 5}})
    assert "estimated_speedup" in report.metrics
    assert report.metrics["estimated_speedup"] == 0.5

def test_artifact_explorer():
    from omlx.tooling.explorer.explorer import ArtifactExplorer
    from omlx.tooling.session.compiler_session import CompilerSession
    from omlx.tooling.session.replay_session import ReplaySession

    replay = ReplaySession("test", "1.0", {}, "mock", [], {})
    session = CompilerSession(
        replay_session=replay,
        artifacts=MappingProxyType({"CapabilityDescriptor": None, "ExecutionPlan": None, "LogicalIR": None, "PhysicalIR": None, "BackendGraph": None})
    )

    explorer = ArtifactExplorer(session)
    path = explorer.navigate("CapabilityDescriptor")

    assert path == ["CapabilityDescriptor", "ExecutionPlan", "LogicalIR", "PhysicalIR", "BackendGraph"]
