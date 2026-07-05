# SPDX-License-Identifier: Apache-2.0
from typing import Dict, Any
from omlx.optimization.passes import BasePass, AnalysisPass, OptimizationPass, PassCategory
from omlx.optimization.intelligence.planner import OptimizationPlanner
from omlx.optimization.intelligence.policies import AdaptiveOptimizationPolicy
from omlx.optimization.intelligence.cost_cache import CostCache
from omlx.optimization.intelligence.statistics import IntelligenceStatisticsTracker
from omlx.compiler_perf.keys import CacheKey

class MockAnalysisPass(AnalysisPass):
    @property
    def supported_stages(self): return {'all'}
    @property
    def name(self) -> str: return "MockAnalysis"
    @property
    def category(self) -> PassCategory: return PassCategory.ANALYSIS
    def analyze(self, artifact: Any) -> Dict[str, Any]: return {"res": 1}

class MockOptPassProfitable(OptimizationPass):
    @property
    def supported_stages(self): return {'all'}
    @property
    def name(self) -> str: return "MockOptProfitable"
    @property
    def category(self) -> PassCategory: return PassCategory.OPTIMIZATION
    def apply(self, artifact: Any) -> Any: return artifact

class MockOptPassUnprofitable(OptimizationPass):
    @property
    def supported_stages(self): return {'all'}
    @property
    def name(self) -> str: return "MockOptUnprofitable"
    @property
    def category(self) -> PassCategory: return PassCategory.OPTIMIZATION
    def apply(self, artifact: Any) -> Any: return artifact

def test_planner_selection_and_caching():
    policy = AdaptiveOptimizationPolicy(require_cache_reuse=True)
    cache = CostCache()
    tracker = IntelligenceStatisticsTracker()
    planner = OptimizationPlanner(policy, cache, tracker)

    passes = [MockAnalysisPass(), MockOptPassProfitable(), MockOptPassUnprofitable()]
    artifact = "test_artifact"

    selected, analysis = planner.select_passes(passes, artifact)

    assert len(selected) == 2
    assert isinstance(selected[0], MockAnalysisPass)
    assert isinstance(selected[1], MockOptPassProfitable)
    assert len(analysis) == 0

    snap = tracker.get_snapshot()
    assert snap["skipped_passes"] == 1

    ckey = CacheKey(pass_name="MockAnalysis", artifact_state=str(artifact)).compute_hash()
    cache_key = f"pass_result:{ckey}"
    cache.put(cache_key, {"res": "cached"})

    selected2, analysis2 = planner.select_passes(passes, artifact)

    assert len(selected2) == 1
    assert isinstance(selected2[0], MockOptPassProfitable)
    assert analysis2["MockAnalysis"] == {"res": "cached"}

    snap2 = tracker.get_snapshot()
    assert snap2["skipped_passes"] == 2
    assert snap2["analysis_reuses"] == 1
    assert snap2["cache_reuses"] == 1
