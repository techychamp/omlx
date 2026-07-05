# SPDX-License-Identifier: Apache-2.0
"""
Immutable cost models for compiler optimization intelligence.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ExecutionCost:
    flops: int = 0
    memory_bytes: int = 0
    latency_ms: float = 0.0

@dataclass(frozen=True)
class MemoryCost:
    peak_memory_bytes: int = 0
    allocation_count: int = 0
    fragmentation_ratio: float = 0.0

@dataclass(frozen=True)
class CompilationCost:
    compile_time_ms: float = 0.0
    memory_overhead_bytes: int = 0

@dataclass(frozen=True)
class CacheCost:
    lookup_cost_ms: float = 0.0
    insert_cost_ms: float = 0.0
    miss_penalty_ms: float = 0.0
    hit_ratio_estimate: float = 0.0

@dataclass(frozen=True)
class OptimizationCost:
    analysis_time_ms: float = 0.0
    application_time_ms: float = 0.0
    memory_overhead_bytes: int = 0

@dataclass(frozen=True)
class GraphComplexityCost:
    node_count: int = 0
    edge_count: int = 0
    max_depth: int = 0
    cyclomatic_complexity: int = 0

@dataclass(frozen=True)
class BackendCompatibilityCost:
    fallback_penalty_ms: float = 0.0
    conversion_overhead_ms: float = 0.0
    unsupported_ops_count: int = 0

@dataclass(frozen=True)
class CostEstimate:
    execution: ExecutionCost = ExecutionCost()
    memory: MemoryCost = MemoryCost()
    compilation: CompilationCost = CompilationCost()
    cache: CacheCost = CacheCost()
    optimization: OptimizationCost = OptimizationCost()
    graph_complexity: GraphComplexityCost = GraphComplexityCost()
    backend_compatibility: BackendCompatibilityCost = BackendCompatibilityCost()
