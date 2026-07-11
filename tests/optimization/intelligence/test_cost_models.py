# SPDX-License-Identifier: Apache-2.0
import pytest
from omlx.optimization.intelligence.cost_models import (
    ExecutionCost, MemoryCost, CompilationCost, CacheCost,
    OptimizationCost, GraphComplexityCost, BackendCompatibilityCost, CostEstimate
)

def test_cost_models_immutability():
    ec = ExecutionCost(flops=100)
    with pytest.raises(Exception):
        ec.flops = 200

def test_cost_estimate_defaults():
    ce = CostEstimate()
    assert ce.execution.flops == 0
    assert ce.memory.peak_memory_bytes == 0
    assert ce.compilation.compile_time_ms == 0.0

def test_cost_estimate_custom():
    ce = CostEstimate(
        execution=ExecutionCost(flops=500, memory_bytes=1024, latency_ms=1.5),
        cache=CacheCost(hit_ratio_estimate=0.95)
    )
    assert ce.execution.flops == 500
    assert ce.cache.hit_ratio_estimate == 0.95
