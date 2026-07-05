# SPDX-License-Identifier: Apache-2.0
"""
Optimization Planner to select and order optimization passes, skip unprofitable ones,
and generate a deterministic execution plan.
"""
import time
from typing import List, Dict, Any, Tuple
from omlx.optimization.passes import BasePass, OptimizationPass, AnalysisPass
from omlx.compiler_perf.keys import CacheKey
from .policies import AdaptiveOptimizationPolicy, OptimizationStrategy
from .profitability import OptimizationProfitabilityAnalysis
from .telemetry import OptimizationTelemetry
from .statistics import IntelligenceStatisticsTracker
from .cost_cache import CostCache

class OptimizationPlanner:
    def __init__(self, policy: AdaptiveOptimizationPolicy, cache: CostCache, tracker: IntelligenceStatisticsTracker):
        self.policy = policy
        self.cache = cache
        self.tracker = tracker

    def analyze_profitability(self, pass_name: str, artifact: Any, cost_estimate: Any) -> OptimizationProfitabilityAnalysis:
        # Note: Placeholder profitability heuristics are temporary until richer cost models arrive.
        if "Unprofitable" in pass_name:
            return OptimizationProfitabilityAnalysis(is_profitable=False, reason="Mocked unprofitable")
        return OptimizationProfitabilityAnalysis(
            is_profitable=True,
            expected_gain_ms=10.0,
            expected_memory_reduction_bytes=1024,
            reason="Mocked profitable"
        )

    def select_passes(self, passes: List[BasePass], artifact: Any) -> Tuple[List[BasePass], Dict[str, Any]]:
        selected_passes = []
        analysis_results = {}

        start_time = time.time()

        for p in passes:
            # Check cache first if applicable
            ckey = CacheKey(pass_name=p.name, artifact_state=str(artifact)).compute_hash() # Use CacheKey with artifact representation
            cache_key = f"pass_result:{ckey}"
            cached_result = self.cache.get(cache_key)

            if isinstance(p, AnalysisPass):
                if cached_result and self.policy.require_cache_reuse:
                    analysis_results[p.name] = cached_result
                    self.tracker.record_telemetry(OptimizationTelemetry(
                        pass_name=p.name, applied=True, analysis_reused=True, cache_reused=True
                    ))
                else:
                    selected_passes.append(p)
            elif isinstance(p, OptimizationPass):
                profitability = self.analyze_profitability(p.name, artifact, None)
                if profitability.is_profitable:
                    selected_passes.append(p)
                else:
                    self.tracker.record_telemetry(OptimizationTelemetry(
                        pass_name=p.name, applied=False, reason_skipped=profitability.reason
                    ))
            else:
                selected_passes.append(p)

        duration = (time.time() - start_time) * 1000
        self.tracker.record_phase_timing("select_passes", duration)

        return selected_passes, analysis_results
