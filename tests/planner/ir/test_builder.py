# SPDX-License-Identifier: Apache-2.0

from types import MappingProxyType
from omlx.planner.ir.builder import IRBuilder
from omlx.planner.plan import ExecutionPlan

def test_ir_builder_autoregressive():
    plan = ExecutionPlan(
        execution_family="llm",
        execution_backend="autoregressive_backend",
        execution_mode="autoregressive",
        execution_topology="single_node",
        cache_strategy="paged",
        scheduler_strategy="continuous_batching",
        verification_stages=tuple(),
        optimization_passes=tuple(),
        execution_hints=MappingProxyType({}),
        hardware_requirements=tuple(),
        planner_metadata=MappingProxyType({})
    )

    builder = IRBuilder()
    ir = builder.build(plan)

    assert "node_prefill" in ir.nodes
    assert "node_forward" in ir.nodes
    assert "node_sample" in ir.nodes
    assert "node_verify" in ir.nodes
    assert "node_emit" in ir.nodes

    assert ir.get_node("node_sample").dependencies == ("node_prefill",)
    assert ir.get_node("node_forward").dependencies == ("node_sample",)
    assert ir.get_node("node_emit").dependencies == ("node_verify",)

    assert "node_emit" in ir.roots
