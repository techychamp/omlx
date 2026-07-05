# SPDX-License-Identifier: Apache-2.0
"""
Adaptive optimization policies for the compiler.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class OptimizationStrategy(Enum):
    COMPILATION_OPTIMIZED = "compilation_optimized"
    EXECUTION_OPTIMIZED = "execution_optimized"
    MEMORY_OPTIMIZED = "memory_optimized"
    LATENCY_OPTIMIZED = "latency_optimized"
    BALANCED = "balanced"
    DEBUG = "debug"
    RESEARCH = "research"

@dataclass(frozen=True)
class AdaptiveOptimizationPolicy:
    strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    max_compilation_time_ms: Optional[float] = None
    min_profitability_gain_ms: float = 0.0
    require_cache_reuse: bool = False
    allow_experimental_passes: bool = False
