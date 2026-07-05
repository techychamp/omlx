# SPDX-License-Identifier: Apache-2.0
from omlx.optimization.intelligence.cost_cache import CostCache
from omlx.optimization.intelligence.cost_models import CostEstimate, ExecutionCost
from omlx.optimization.intelligence.profitability import OptimizationProfitabilityAnalysis

def test_cost_cache_operations():
    cache = CostCache()

    est = CostEstimate(execution=ExecutionCost(latency_ms=10.0))
    cache.put_estimate("artifact_1", est)
    cached_est = cache.get_estimate("artifact_1")
    assert cached_est is not None
    assert cached_est.execution.latency_ms == 10.0

    analysis_res = {"nodes": 5}
    cache.put_analysis("pass_1", analysis_res)
    assert cache.get_analysis("pass_1") == {"nodes": 5}

    prof = OptimizationProfitabilityAnalysis(is_profitable=True)
    cache.put_profitability("opt_1", prof)
    assert cache.get_profitability("opt_1").is_profitable is True
