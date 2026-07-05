# SPDX-License-Identifier: Apache-2.0
import pytest
from typing import Tuple, Any
from omlx.optimization.manager import PassManager
from omlx.optimization.passes import OptimizationPass, PassCategory, CompilerStage, OptimizationContext
from omlx.optimization.pipeline import OptimizationPipeline
from omlx.optimization.validation import PassValidationError
from omlx.optimization.diagnostics import DiagnosticsTracker
from omlx.optimization.statistics import StatisticsCollector

class DummyOptPass(OptimizationPass):
    def __init__(self, name: str, reqs: Tuple[str, ...] = None, conflicts: Tuple[str, ...] = None):
        self._name = name
        self._reqs = reqs or ()
        self._conflicts = conflicts or ()

    @property
    def name(self) -> str: return self._name

    @property
    def category(self) -> PassCategory: return PassCategory.OPTIMIZATION

    @property
    def supported_stages(self) -> Tuple[CompilerStage, ...]:
        return (CompilerStage.LOGICAL_IR,)

    @property
    def required_passes(self) -> Tuple[str, ...]: return self._reqs

    @property
    def conflicting_passes(self) -> Tuple[str, ...]: return self._conflicts

    def apply(self, artifact: Any, context: OptimizationContext) -> Any:
        return artifact + [self._name]

def test_pass_manager_ordering():
    pm = PassManager()
    pm.register(DummyOptPass("A"))
    pm.register(DummyOptPass("B", reqs=("A",)))
    pm.register(DummyOptPass("C", reqs=("B",)))

    order = [p.name for p in pm.get_execution_order(CompilerStage.LOGICAL_IR)]
    assert order.index("A") < order.index("B")
    assert order.index("B") < order.index("C")

def test_pass_manager_execution():
    pm = PassManager()
    pm.register(DummyOptPass("A"))
    pm.register(DummyOptPass("B", reqs=("A",)))

    pipeline = OptimizationPipeline(CompilerStage.LOGICAL_IR, pm)
    tracker = DiagnosticsTracker()
    stats = StatisticsCollector()
    context = OptimizationContext(tracker=tracker, stats=stats)

    result = pipeline.execute([], context)
    assert result == ["A", "B"]

    summary = stats.get_summary()
    assert summary["total_passes_run"] == 2
    assert summary["successful_passes"] == 2
    assert len(tracker.get_all()) == 2

def test_pass_manager_missing_dep():
    pm = PassManager()
    pm.register(DummyOptPass("A", reqs=("X",)))
    with pytest.raises(PassValidationError):
        pm.get_execution_order(CompilerStage.LOGICAL_IR)

def test_pass_manager_conflict():
    pm = PassManager()
    pm.register(DummyOptPass("A", conflicts=("B",)))
    pm.register(DummyOptPass("B"))
    with pytest.raises(PassValidationError):
        pm.get_execution_order(CompilerStage.LOGICAL_IR)

def test_pass_manager_circular_dep():
    pm = PassManager()
    pm.register(DummyOptPass("A", reqs=("B",)))
    pm.register(DummyOptPass("B", reqs=("A",)))
    with pytest.raises(PassValidationError):
        pm.get_execution_order(CompilerStage.LOGICAL_IR)
