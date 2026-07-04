# SPDX-License-Identifier: Apache-2.0
"""
Immutable cost models for backend intelligence framework.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class MemoryCostModel:
    base_memory_bytes: int = 0
    per_token_memory_bytes: int = 0
    peak_memory_bytes: int = 0
    kv_cache_memory_bytes: int = 0

@dataclass(frozen=True)
class LatencyCostModel:
    base_latency_ms: float = 0.0
    per_token_latency_ms: float = 0.0
    time_to_first_token_ms: float = 0.0

@dataclass(frozen=True)
class SynchronizationCostModel:
    barrier_cost_ms: float = 0.0
    stream_sync_cost_ms: float = 0.0

@dataclass(frozen=True)
class TransferCostModel:
    host_to_device_bw_bytes_per_sec: float = 0.0
    device_to_host_bw_bytes_per_sec: float = 0.0
    device_to_device_bw_bytes_per_sec: float = 0.0

@dataclass(frozen=True)
class CompilationCostModel:
    estimated_compile_time_ms: float = 0.0
    cache_hit_ratio: float = 0.0

@dataclass(frozen=True)
class ExecutionCostModel:
    flops_per_token: float = 0.0
    compute_efficiency: float = 0.0
    memory_bandwidth_efficiency: float = 0.0

@dataclass(frozen=True)
class CacheCostModel:
    cache_lookup_cost_ms: float = 0.0
    cache_update_cost_ms: float = 0.0
    eviction_cost_ms: float = 0.0

@dataclass(frozen=True)
class RoutingCostModel:
    expert_routing_cost_ms: float = 0.0
    triage_routing_cost_ms: float = 0.0
