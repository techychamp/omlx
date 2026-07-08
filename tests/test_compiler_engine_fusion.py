import pytest
from types import MappingProxyType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.domains.fusion.artifacts import FusionPlan, FusionGroup
from omlx.planner.domains.bundle import PlanningBundle
from omlx.planner.compiler.engine import CompilerEngine
from omlx.planner.plan import ExecutionPlan
from omlx.capabilities.descriptor import ExecutionFamily, CacheLayoutType

def test_compiler_engine_with_fusion():
    node_c = IRNode(id="node_c", node_type=IRNodeType.FORWARD, dependencies=("node_b",))
    node_b = IRNode(id="node_b", node_type=IRNodeType.FORWARD, dependencies=("node_a",))
    node_a = IRNode(id="node_a", node_type=IRNodeType.FORWARD, dependencies=())

    nodes = {
        "node_a": node_a,
        "node_b": node_b,
        "node_c": node_c
    }

    ir = ExecutionIR(
        nodes=MappingProxyType(nodes),
        roots=("node_c",),
        metadata=MappingProxyType({})
    )

    fusion_plan = FusionPlan(
        groups=(
            FusionGroup(
                id="group_1",
                node_ids=("node_a", "node_b"),
                fusion_type="test_fusion"
            ),
        )
    )

    bundle = PlanningBundle(
        execution_plan=ExecutionPlan(
            execution_family=ExecutionFamily.AUTOREGRESSIVE,
            execution_backend="mlx",
            execution_mode="standard",
            execution_topology="single",
            cache_strategy=CacheLayoutType.PAGED,
            scheduler_strategy="default",
            verification_stages=tuple(),
            optimization_passes=tuple()
        ),
        fusion_plan=fusion_plan
    )

    engine = CompilerEngine()
    physical_ir = engine.compile(ir, planning_bundle=bundle)

    assert len(physical_ir.operations) == 2
