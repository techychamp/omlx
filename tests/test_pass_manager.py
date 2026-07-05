import pytest
from typing import Set, Any
from omlx.compiler.framework.manager import PassManager, PassDependencyError
from omlx.compiler.framework.passes import OptimizationPass, PassCategory, AnalysisPass

class DummyOptPass(OptimizationPass[Any]):
    def __init__(self, name: str, reqs: Set[str] = None, conflicts: Set[str] = None):
        self._name = name
        self._reqs = reqs or set()
        self._conflicts = conflicts or set()

    @property
    def name(self) -> str: return self._name

    @property
    def category(self) -> PassCategory: return PassCategory.OPTIMIZATION

    @property
    def required_passes(self) -> Set[str]: return self._reqs

    @property
    def conflicting_passes(self) -> Set[str]: return self._conflicts

    def apply(self, artifact: Any) -> Any:
        return artifact + [self._name]

def test_pass_manager_ordering():
    pm = PassManager("LogicalIR")
    pm.register(DummyOptPass("A"))
    pm.register(DummyOptPass("B", reqs={"A"}))
    pm.register(DummyOptPass("C", reqs={"B"}))

    order = [p.name for p in pm.schedule()]
    assert order.index("A") < order.index("B")
    assert order.index("B") < order.index("C")

def test_pass_manager_execution():
    pm = PassManager("LogicalIR")
    pm.register(DummyOptPass("A"))
    pm.register(DummyOptPass("B", reqs={"A"}))

    result, analysis = pm.execute([])
    assert result == ["A", "B"]

    assert pm.stats.executed_passes == 2
    assert pm.stats.failed_passes == 0
    assert len(pm.stats.execution_order) == 2
    assert len(pm.stats.diagnostics) == 2

def test_pass_manager_missing_dep():
    pm = PassManager("LogicalIR")
    pm.register(DummyOptPass("A", reqs={"X"}))
    with pytest.raises(PassDependencyError):
        pm.schedule()

def test_pass_manager_conflict():
    pm = PassManager("LogicalIR")
    pm.register(DummyOptPass("A", conflicts={"B"}))
    pm.register(DummyOptPass("B"))
    with pytest.raises(PassDependencyError):
        pm.schedule()

def test_pass_manager_circular_dep():
    pm = PassManager("LogicalIR")
    pm.register(DummyOptPass("A", reqs={"B"}))
    pm.register(DummyOptPass("B", reqs={"A"}))
    with pytest.raises(PassDependencyError):
        pm.schedule()
