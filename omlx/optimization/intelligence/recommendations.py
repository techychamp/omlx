# SPDX-License-Identifier: Apache-2.0
"""
Structured recommendations from the optimization planner.
"""
from enum import Enum
from dataclasses import dataclass

class RecommendationType(Enum):
    PASS_SKIPPED = "pass_skipped"
    PASS_UNNECESSARY = "pass_unnecessary"
    ANALYSIS_REUSABLE = "analysis_reusable"
    CACHE_REUSABLE = "cache_reusable"
    PIPELINE_SIMPLIFICATION = "pipeline_simplification"
    BACKEND_OPTIMIZATION_OPPORTUNITY = "backend_optimization_opportunity"

@dataclass(frozen=True)
class OptimizationRecommendation:
    type: RecommendationType
    message: str
    target_pass: str = ""
    suggested_action: str = ""
