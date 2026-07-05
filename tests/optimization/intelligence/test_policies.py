# SPDX-License-Identifier: Apache-2.0
from omlx.optimization.intelligence.policies import AdaptiveOptimizationPolicy, OptimizationStrategy

def test_adaptive_policy_defaults():
    policy = AdaptiveOptimizationPolicy()
    assert policy.strategy == OptimizationStrategy.BALANCED
    assert policy.max_compilation_time_ms is None
    assert policy.min_profitability_gain_ms == 0.0

def test_adaptive_policy_custom():
    policy = AdaptiveOptimizationPolicy(
        strategy=OptimizationStrategy.LATENCY_OPTIMIZED,
        require_cache_reuse=True
    )
    assert policy.strategy == OptimizationStrategy.LATENCY_OPTIMIZED
    assert policy.require_cache_reuse is True
