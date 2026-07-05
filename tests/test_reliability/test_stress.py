import pytest
import time
import asyncio
from omlx.capabilities.resolver import CapabilityResolver
from omlx.capabilities.sources import RuntimeOverrideSource
from omlx.planner.planner import ExecutionPlanner
from omlx.capabilities.descriptor import ExecutionFamily, AttentionType, CacheLayoutType

def test_capability_resolver_stress():
    resolver = CapabilityResolver()

    start_time = time.time()
    for i in range(5000):
        # Provide real capability definitions
        source = RuntimeOverrideSource({
            "execution_family": ExecutionFamily.AUTOREGRESSIVE,
            "attention_types": [AttentionType.CAUSAL],
            "cache_layout": CacheLayoutType.PAGED,
            "supports_streaming": True,
            "execution_hints": {"iteration": str(i)}
        })
        desc = resolver.resolve(additional_sources=[source])
        assert desc.execution_family == ExecutionFamily.AUTOREGRESSIVE

    elapsed = time.time() - start_time
    assert elapsed < 10.0, f"CapabilityResolver stress test failed, took {elapsed}s"

def test_planner_stress():
    resolver = CapabilityResolver()
    planner = ExecutionPlanner()

    source = RuntimeOverrideSource({
        "execution_family": ExecutionFamily.AUTOREGRESSIVE,
        "attention_types": [AttentionType.CAUSAL],
        "cache_layout": CacheLayoutType.PAGED,
        "supports_streaming": True
    })
    desc = resolver.resolve(additional_sources=[source])

    start_time = time.time()
    for _ in range(5000):
        plan = planner.plan(desc)
        assert plan.execution_family == ExecutionFamily.AUTOREGRESSIVE
    elapsed = time.time() - start_time
    assert elapsed < 10.0, f"ExecutionPlanner stress test failed, took {elapsed}s"
