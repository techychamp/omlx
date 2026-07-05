# SPDX-License-Identifier: Apache-2.0
"""
Optimization telemetry for the compiler.
"""
from dataclasses import dataclass, field
from typing import Dict, Any
from .cost_models import CostEstimate

@dataclass(frozen=True)
class OptimizationTelemetry:
    pass_name: str
    applied: bool
    reason_skipped: str = ""
    estimated_improvement: CostEstimate = field(default_factory=CostEstimate)
    actual_compiler_statistics: Dict[str, Any] = field(default_factory=dict)
    analysis_reused: bool = False
    cache_reused: bool = False
    pipeline_timing_ms: float = 0.0
