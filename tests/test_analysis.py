import pytest
from typing import Set, Any
from omlx.compiler.framework.manager import PassManager
from omlx.compiler.framework.passes import AnalysisPass, PassCategory
from omlx.compiler.passes.analysis import DependencyAnalysisPass, GraphComplexityAnalysisPass

def test_analysis_execution():
    pm = PassManager("LogicalIR")
    pm.register(DependencyAnalysisPass())
    pm.register(GraphComplexityAnalysisPass())

    artifact = ["test_artifact"]
    result, analysis = pm.execute(artifact)

    # Assert artifact remains immutable
    assert result == ["test_artifact"]

    # Assert analysis dicts are populated
    assert "DependencyAnalysisPass" in analysis
    assert analysis["DependencyAnalysisPass"]["dependencies_count"] == 0
    assert "GraphComplexityAnalysisPass" in analysis
    assert analysis["GraphComplexityAnalysisPass"]["node_count"] == 0
