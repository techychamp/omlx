import pytest
from omlx.planner.compiler.optimization_pipeline import OptimizationPipeline
from omlx.planner.compiler.passes import LogicalPassRegistry, PhysicalPassRegistry, LogicalPass
from omlx.planner.ir.graph import ExecutionIR
from types import MappingProxyType

class DummyLogicalPass(LogicalPass):
    @property
    def name(self) -> str:
        return "dummy_logical_pass"

    def apply(self, ir: ExecutionIR) -> ExecutionIR:
        new_metadata = dict(ir.metadata)
        new_metadata["optimized"] = True
        return ExecutionIR(
            nodes=ir.nodes,
            roots=ir.roots,
            metadata=MappingProxyType(new_metadata)
        )

def test_optimization_pipeline():
    logical_registry = LogicalPassRegistry()
    logical_registry.register(DummyLogicalPass())
    physical_registry = PhysicalPassRegistry()

    pipeline = OptimizationPipeline(logical_registry, physical_registry)

    initial_ir = ExecutionIR(
        nodes=MappingProxyType({}),
        roots=tuple()
    )

    optimized_ir = pipeline.optimize_logical(initial_ir)
    assert optimized_ir.metadata.get("optimized") is True
