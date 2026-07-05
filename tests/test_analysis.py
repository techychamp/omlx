# SPDX-License-Identifier: Apache-2.0
import pytest
from omlx.optimization.manager import PassManager
from omlx.optimization.passes import OptimizationContext, CompilerStage
from omlx.optimization.pipeline import OptimizationPipeline
from omlx.optimization.reference_passes import DependencyAnalysisPass, MemoryAnalysisPass

def test_analysis_execution():
    pm = PassManager()
    pm.register(DependencyAnalysisPass())
    pm.register(MemoryAnalysisPass())

    pipeline = OptimizationPipeline(CompilerStage.LOGICAL_IR, pm)
    analysis_cache = {}
    context = OptimizationContext(analysis_cache=analysis_cache)

    artifact = ["test_artifact"]
    result = pipeline.execute(artifact, context)

    # Assert artifact remains immutable
    assert result == ["test_artifact"]

    # Assert analysis dicts/cache are populated
    assert "dependency_analysis" in analysis_cache
    assert "memory_analysis" in analysis_cache
