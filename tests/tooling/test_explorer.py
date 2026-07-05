import pytest
from types import MappingProxyType
from omlx.tooling.session import ReplaySession, CompilerSession
from omlx.tooling.explorer.explorer import ArtifactExplorer

def test_artifact_explorer():
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
        artifacts=MappingProxyType({
            "CapabilityDescriptor": {"id": 1},
            "ExecutionPlan": {"id": 2},
            "LogicalIR": {"id": 3}
        })
    )

    explorer = ArtifactExplorer(session)
    path = explorer.navigate("CapabilityDescriptor")

    assert "CapabilityDescriptor" in path
    assert "ExecutionPlan" in path
    assert "LogicalIR" in path
    assert "PhysicalIR" not in path
