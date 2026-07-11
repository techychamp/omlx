import pytest
import asyncio
from omlx.capabilities.resolver import CapabilityResolver
from omlx.capabilities.sources import RuntimeOverrideSource
from omlx.planner.planner import ExecutionPlanner
from omlx.capabilities.descriptor import ExecutionFamily, AttentionType, CacheLayoutType

@pytest.mark.asyncio
async def test_capability_resolver_concurrency():
    resolver = CapabilityResolver()

    async def resolve_task(i):
        # We need this to yield control
        await asyncio.sleep(0)
        source = RuntimeOverrideSource({
            "execution_family": ExecutionFamily.AUTOREGRESSIVE,
            "execution_hints": {"task_id": i}
        })
        desc = resolver.resolve(additional_sources=[source])
        assert desc.execution_hints["task_id"] == i

    tasks = [resolve_task(i) for i in range(1000)]
    await asyncio.gather(*tasks)

@pytest.mark.asyncio
async def test_planner_concurrency():
    resolver = CapabilityResolver()
    planner = ExecutionPlanner()

    source = RuntimeOverrideSource({
        "execution_family": ExecutionFamily.AUTOREGRESSIVE,
        "attention_types": [AttentionType.CAUSAL],
        "cache_layout": CacheLayoutType.PAGED,
        "supports_streaming": True
    })
    desc = resolver.resolve(additional_sources=[source])

    async def plan_task():
        await asyncio.sleep(0)
        plan = planner.plan(desc).execution_plan
        assert plan.execution_family == ExecutionFamily.AUTOREGRESSIVE

    tasks = [plan_task() for _ in range(1000)]
    await asyncio.gather(*tasks)
