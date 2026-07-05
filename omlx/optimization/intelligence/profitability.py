# SPDX-License-Identifier: Apache-2.0
"""
Optimization profitability analysis for the compiler.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class OptimizationProfitabilityAnalysis:
    is_profitable: bool
    expected_gain_ms: float = 0.0
    expected_memory_reduction_bytes: int = 0
    expected_graph_simplification_nodes: int = 0
    expected_cache_improvement_ratio: float = 0.0
    expected_backend_improvement_ms: float = 0.0
    expected_compilation_overhead_ms: float = 0.0
    reason: str = ""
