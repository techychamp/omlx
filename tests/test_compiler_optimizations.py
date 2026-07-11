import pytest
from omlx.optimization.pipeline import OptimizationPipeline
from omlx.optimization.passes import CompilerStage, OptimizationContext, OptimizationPass
from omlx.optimization.manager import PassManager
from omlx.planner.ir.graph import ExecutionIR
from types import MappingProxyType

class DummyLogicalPass(OptimizationPass):
    @property
    def name(self) -> str:
        return "dummy_logical_pass"

    @property
    def category(self):
        from omlx.optimization.passes import PassCategory
        return PassCategory.OPTIMIZATION

    @property
    def supported_stages(self):
        return (CompilerStage.LOGICAL_IR,)

    def apply(self, ir: ExecutionIR, ctx=None) -> ExecutionIR:
        new_metadata = dict(ir.metadata)
        new_metadata["optimized"] = True
        return ExecutionIR(
            nodes=ir.nodes,
            roots=ir.roots,
            metadata=MappingProxyType(new_metadata)
        )

def test_optimization_pipeline():
    pm = PassManager()
    pm.register(DummyLogicalPass())
    pipeline = OptimizationPipeline(CompilerStage.LOGICAL_IR, pm)

    initial_ir = ExecutionIR(
        nodes=MappingProxyType({}),
        roots=tuple()
    )

    ctx = OptimizationContext(tracker=None, stats=None, analysis_cache=None)
    optimized_ir = pipeline.execute(initial_ir, ctx)
    assert optimized_ir.metadata.get("optimized") is True

def test_apple_optimization_integration():
    from omlx.planner.compiler.engine import CompilerEngine
    engine = CompilerEngine()
    from omlx.planner.domains.bundle import PlanningBundle
    bundle = PlanningBundle()

    # Try to compile with a planning bundle to ensure apple optimization doesn't crash
    ir = ExecutionIR(nodes=MappingProxyType({}), roots=tuple())
    engine.compile(ir, planning_bundle=bundle)

def test_exception_handling():
    class FailingPass(OptimizationPass):
        @property
        def name(self) -> str:
            return "failing_pass"
        @property
        def category(self):
            from omlx.optimization.passes import PassCategory
            return PassCategory.OPTIMIZATION
        @property
        def supported_stages(self):
            return (CompilerStage.LOGICAL_IR,)
        def apply(self, ir, ctx=None):
            raise ValueError("Test error")

    pm = PassManager()
    pm.register(FailingPass())
    pipeline = OptimizationPipeline(CompilerStage.LOGICAL_IR, pm)

    initial_ir = ExecutionIR(nodes=MappingProxyType({}), roots=tuple())
    ctx = OptimizationContext(tracker=None, stats=None, analysis_cache=None)

    from omlx.api.v1.exceptions import CompilerError
    with pytest.raises(CompilerError):
        pipeline.execute(initial_ir, ctx)
