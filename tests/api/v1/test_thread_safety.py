import asyncio
import pytest
from omlx.api.v1 import (
    CompilerRequestBuilder,
    PlanningRequestBuilder,
    BackendRequestBuilder
)

@pytest.mark.asyncio
async def test_parallel_sdk_usage():
    """
    Tests parallel SDK usage to ensure thread safety without mutable global state.
    """
    async def run_compiler():
        builder = CompilerRequestBuilder()
        request = builder.with_model("model-1").build_request()
        compiler = builder.build()
        result = await compiler.compile_async(request)
        return result.success

    async def run_planner():
        builder = PlanningRequestBuilder()
        request = builder.require_capability("attention").build_request()
        planner = builder.build()
        result = await planner.plan_async(request)
        return result.success

    async def run_backend():
        builder = BackendRequestBuilder()
        request = builder.with_model_family("llama").build_request()
        manager = builder.build()
        result = await manager.select_backend_async(request)
        return result.selected_backend

    # Run many requests in parallel
    tasks = [run_compiler() for _ in range(20)] + \
            [run_planner() for _ in range(20)] + \
            [run_backend() for _ in range(20)]

    results = await asyncio.gather(*tasks)

    # Assert all operations succeeded and returned expected results
    assert all(r is True or r == "mlx" for r in results)
