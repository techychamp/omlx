# SPDX-License-Identifier: Apache-2.0

import pytest
from typing import Tuple, Any

from omlx.optimization.passes import (
    CompilerStage, PassCategory, OptimizationContext, OptimizationPass, AnalysisPass
)
from omlx.optimization.diagnostics import DiagnosticsTracker, DiagnosticLevel
from omlx.optimization.statistics import StatisticsCollector
from omlx.optimization.manager import PassManager
from omlx.optimization.pipeline import OptimizationPipeline
from omlx.optimization.validation import PassValidationError
from omlx.optimization.reference_passes import (
    DependencyAnalysisPass, MemoryAnalysisPass, CanonicalizationPass, DeadNodeEliminationPass
)

class DummyArtifact:
    def __init__(self, value=0):
        self.value = value

class PassA(OptimizationPass):
    @property
    def name(self): return "A"
    @property
    def category(self): return PassCategory.OPTIMIZATION
    @property
    def supported_stages(self): return (CompilerStage.LOGICAL_IR,)

    def apply(self, artifact, context):
        return DummyArtifact(artifact.value + 1)

class PassB(OptimizationPass):
    @property
    def name(self): return "B"
    @property
    def category(self): return PassCategory.OPTIMIZATION
    @property
    def supported_stages(self): return (CompilerStage.LOGICAL_IR,)
    @property
    def required_passes(self): return ("A",)

    def apply(self, artifact, context):
        return DummyArtifact(artifact.value * 2)

class PassC(OptimizationPass):
    @property
    def name(self): return "C"
    @property
    def category(self): return PassCategory.OPTIMIZATION
    @property
    def supported_stages(self): return (CompilerStage.LOGICAL_IR,)
    @property
    def required_passes(self): return ("B",)

    def apply(self, artifact, context):
        return DummyArtifact(artifact.value - 1)


class PassConflict1(OptimizationPass):
    @property
    def name(self): return "conflict1"
    @property
    def category(self): return PassCategory.OPTIMIZATION
    @property
    def supported_stages(self): return (CompilerStage.LOGICAL_IR,)
    def apply(self, artifact, context): return artifact

class PassConflict2(OptimizationPass):
    @property
    def name(self): return "conflict2"
    @property
    def category(self): return PassCategory.OPTIMIZATION
    @property
    def supported_stages(self): return (CompilerStage.LOGICAL_IR,)
    @property
    def conflicting_passes(self): return ("conflict1",)
    def apply(self, artifact, context): return artifact


class PassCycle1(OptimizationPass):
    @property
    def name(self): return "cycle1"
    @property
    def category(self): return PassCategory.OPTIMIZATION
    @property
    def supported_stages(self): return (CompilerStage.LOGICAL_IR,)
    @property
    def required_passes(self): return ("cycle2",)
    def apply(self, artifact, context): return artifact

class PassCycle2(OptimizationPass):
    @property
    def name(self): return "cycle2"
    @property
    def category(self): return PassCategory.OPTIMIZATION
    @property
    def supported_stages(self): return (CompilerStage.LOGICAL_IR,)
    @property
    def required_passes(self): return ("cycle1",)
    def apply(self, artifact, context): return artifact


def test_pass_registration():
    manager = PassManager()
    manager.register(PassA())
    assert len(manager.get_registered_passes()) == 1

    with pytest.raises(ValueError):
        manager.register(PassA())

def test_dependency_resolution():
    manager = PassManager()
    # Register out of order
    manager.register(PassC())
    manager.register(PassA())
    manager.register(PassB())

    order = manager.get_execution_order()
    names = [p.name for p in order]
    assert names == ["A", "B", "C"]

def test_circular_dependency_detection():
    manager = PassManager()
    manager.register(PassCycle1())
    manager.register(PassCycle2())

    with pytest.raises(PassValidationError):
        manager.get_execution_order()

def test_conflicting_passes():
    manager = PassManager()
    manager.register(PassConflict1())
    manager.register(PassConflict2())

    with pytest.raises(PassValidationError):
        manager.get_execution_order()

def test_pipeline_execution():
    manager = PassManager()
    manager.register(PassA())
    manager.register(PassC())
    manager.register(PassB())

    pipeline = OptimizationPipeline(CompilerStage.LOGICAL_IR, manager)
    context = OptimizationContext(tracker=DiagnosticsTracker(), stats=StatisticsCollector())

    initial_artifact = DummyArtifact(2)
    # Execution should be A, B, C
    # A: 2 + 1 = 3
    # B: 3 * 2 = 6
    # C: 6 - 1 = 5
    final_artifact = pipeline.execute(initial_artifact, context)

    assert final_artifact.value == 5

def test_statistics_collection():
    manager = PassManager()
    manager.register(PassA())
    manager.register(PassB())

    pipeline = OptimizationPipeline(CompilerStage.LOGICAL_IR, manager)
    stats = StatisticsCollector()
    context = OptimizationContext(stats=stats)

    pipeline.execute(DummyArtifact(0), context)

    summary = stats.get_summary()
    assert summary["total_passes_run"] == 2
    assert summary["successful_passes"] == 2
    assert summary["failed_passes"] == 0

def test_diagnostics_tracking():
    manager = PassManager()
    manager.register(DependencyAnalysisPass())

    pipeline = OptimizationPipeline(CompilerStage.LOGICAL_IR, manager)
    tracker = DiagnosticsTracker()
    context = OptimizationContext(tracker=tracker)

    pipeline.execute(DummyArtifact(0), context)

    diags = tracker.get_all()
    assert len(diags) > 0
    assert any("Executing pass" in d.message for d in diags)
    assert any("Dependency analysis complete" in d.message for d in diags)
