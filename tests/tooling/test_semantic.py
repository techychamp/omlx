import pytest
from omlx.planner.plan import ExecutionPlan
from omlx.capabilities.descriptor import ExecutionFamily, CacheLayoutType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.tooling.inspector.inspector import CompilerInspector

def test_semantic_inspection_plan():
    plan = ExecutionPlan(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        execution_backend="mlx",
        execution_mode="streaming",
        execution_topology="single_device",
        cache_strategy=CacheLayoutType.PAGED,
        scheduler_strategy="continuous_batching",
        verification_stages=(),
        optimization_passes=("pass1",)
    )

    inspector = CompilerInspector()
    res = inspector.inspect_semantic_plan(plan)

    assert res["is_streaming"] is True
    assert res["execution_backend"] == "mlx"
    assert "streaming" in res["human_readable"]

def test_semantic_inspection_ir():
    ir = ExecutionIR(
        nodes={
            "n1": IRNode(id="n1", node_type=IRNodeType.FORWARD, dependencies=()),
            "n2": IRNode(id="n1", node_type=IRNodeType.ATTENTION, dependencies=("n1",))
        },
        roots=("n2",)
    )

    inspector = CompilerInspector()
    res = inspector.inspect_semantic_ir(ir)

    assert res["total_nodes"] == 2
    assert res["has_attention"] is True
    assert res["has_forward"] is True
    assert res["node_types"]["forward"] == 1
    assert res["node_types"]["attention"] == 1

from omlx.tooling.diff.differ import CompilerDiffer

def test_semantic_diff():
    plan1 = ExecutionPlan(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        execution_backend="mlx",
        execution_mode="streaming",
        execution_topology="single_device",
        cache_strategy=CacheLayoutType.PAGED,
        scheduler_strategy="continuous_batching",
        verification_stages=(),
        optimization_passes=("pass1",)
    )

    plan2 = ExecutionPlan(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        execution_backend="cuda",
        execution_mode="standard",
        execution_topology="single_device",
        cache_strategy=CacheLayoutType.CONTINUOUS,
        scheduler_strategy="continuous_batching",
        verification_stages=(),
        optimization_passes=("pass1", "pass2")
    )

    differ = CompilerDiffer()
    diff = differ.diff_semantic(plan1, plan2)

    assert diff["has_semantic_changes"] is True
    changes = diff["semantic_changes"]
    assert "Execution backend changed from mlx to cuda" in changes
    assert "Streaming was disabled" in changes
    assert "Optimization pass added: pass2" in changes
    assert any("Cache strategy changed" in c for c in changes)
