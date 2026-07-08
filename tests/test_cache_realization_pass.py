import pytest
from types import MappingProxyType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.framework.cache.plan import CachePlan
from omlx.planner.domains.cache.transformation.pass_ import CacheRealizationPass
from omlx.planner.domains.cache.transformation.realizer import CacheRealizer
from omlx.planner.domains.cache.transformation.validator import CacheTransformationValidator

def create_mock_ir():
    node1 = IRNode(id="prefill_1", node_type=IRNodeType.PREFILL)
    node2 = IRNode(id="forward_1", node_type=IRNodeType.FORWARD, dependencies=("prefill_1",))
    return ExecutionIR(
        nodes=MappingProxyType({"prefill_1": node1, "forward_1": node2}),
        roots=("forward_1",),
        metadata=MappingProxyType({})
    )

def test_cache_realizer():
    ir = create_mock_ir()
    plan = CachePlan(
        plan_id="test_plan",
        allocation_strategy="contiguous",
        eviction_policy="lru",
        cache_layout="standard",
        max_capacity=1024
    )

    realizer = CacheRealizer()
    new_ir, report = realizer.realize(ir, plan)

    assert report.is_successful is True
    assert report.statistics.metadata["plan_id"] == "test_plan"

    # Pre-fill should generate 1 WRITE, Forward should generate 1 READ and 1 WRITE
    assert report.statistics.nodes_added == 3
    assert report.statistics.cache_read_ops == 1
    assert report.statistics.cache_write_ops == 2

    cache_reads = [n for n in new_ir.nodes.values() if n.node_type == IRNodeType.CACHE_READ]
    cache_writes = [n for n in new_ir.nodes.values() if n.node_type == IRNodeType.CACHE_WRITE]

    assert len(cache_reads) == 1
    assert len(cache_writes) == 2

def test_cache_validator():
    ir = create_mock_ir()
    validator = CacheTransformationValidator()
    report = validator.validate(ir, ir)
    assert report.is_valid is True

    # Test failure case
    bad_ir = ExecutionIR(
        nodes=MappingProxyType({"cw": IRNode(id="cw", node_type=IRNodeType.CACHE_WRITE)}),
        roots=("cw",)
    )
    report2 = validator.validate(ir, bad_ir)
    assert report2.is_valid is False

def test_cache_realization_pass():
    ir = create_mock_ir()
    plan = CachePlan(
        plan_id="test_plan_2",
        allocation_strategy="contiguous",
        eviction_policy="lru",
        cache_layout="standard",
        max_capacity=1024
    )

    cache_pass = CacheRealizationPass(plan)
    new_ir = cache_pass.apply(ir)

    assert new_ir is not None
    assert cache_pass.report.is_successful is True
    assert cache_pass.report.statistics.nodes_added == 3

def test_cache_realization_pass_no_plan():
    ir = create_mock_ir()
    cache_pass = CacheRealizationPass(None)
    new_ir = cache_pass.apply(ir)

    assert new_ir is ir
