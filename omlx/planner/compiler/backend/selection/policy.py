# SPDX-License-Identifier: Apache-2.0
"""
Backend Selection and Execution Policies.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Optional, Dict
import enum
from abc import ABC, abstractmethod

class BackendSelectionPolicy(str, enum.Enum):
    LATENCY_OPTIMIZED = "LATENCY_OPTIMIZED"
    MEMORY_OPTIMIZED = "MEMORY_OPTIMIZED"
    BALANCED = "BALANCED"
    ENERGY_EFFICIENT = "ENERGY_EFFICIENT"
    MAXIMUM_THROUGHPUT = "MAXIMUM_THROUGHPUT"
    DEVELOPER_OVERRIDE = "DEVELOPER_OVERRIDE"
    CUSTOM = "CUSTOM"

class PolicyStrategy(ABC):
    """Base strategy for calculating a score from an evaluation report."""
    @abstractmethod
    def score(self, evaluation: Any) -> float:
        pass

class LatencyPolicyStrategy(PolicyStrategy):
    def score(self, evaluation: Any) -> float:
        if hasattr(evaluation, 'is_compatible') and not evaluation.is_compatible: return 0.0

        if hasattr(evaluation, 'estimated_latency_ms'):
            latency = evaluation.estimated_latency_ms
        else:
            latency = evaluation.cost_report.estimated_latency_ms

        # High score for low latency
        return 10000.0 / (latency + 1e-9)

class MemoryPolicyStrategy(PolicyStrategy):
    def score(self, evaluation: Any) -> float:
        if hasattr(evaluation, 'is_compatible') and not evaluation.is_compatible: return 0.0

        if hasattr(evaluation, 'estimated_memory_mb'):
            memory = evaluation.estimated_memory_mb
        else:
            memory = evaluation.cost_report.estimated_peak_memory_mb

        # High score for low memory
        return 10000.0 / (memory + 1e-9)

class BalancedPolicyStrategy(PolicyStrategy):
    def score(self, evaluation: Any) -> float:
        if hasattr(evaluation, 'is_compatible') and not evaluation.is_compatible: return 0.0
        return getattr(evaluation, 'score', getattr(evaluation, 'suitability_score', 0.0))

class MaximumThroughputPolicyStrategy(PolicyStrategy):
    def score(self, evaluation: Any) -> float:
        if hasattr(evaluation, 'is_compatible') and not evaluation.is_compatible: return 0.0

        if hasattr(evaluation, 'estimated_throughput_tps'):
            throughput = evaluation.estimated_throughput_tps
        else:
            throughput = evaluation.cost_report.estimated_throughput_tokens_per_sec

        return throughput

class EnergyEfficientPolicyStrategy(PolicyStrategy):
    def score(self, evaluation: Any) -> float:
        if hasattr(evaluation, 'is_compatible') and not evaluation.is_compatible: return 0.0
        return getattr(evaluation, 'score', getattr(evaluation, 'suitability_score', 0.0))

class DeveloperOverridePolicyStrategy(PolicyStrategy):
    def score(self, evaluation: Any) -> float:
        if hasattr(evaluation, 'is_compatible') and not evaluation.is_compatible: return 0.0
        return getattr(evaluation, 'score', getattr(evaluation, 'suitability_score', 0.0))

_STRATEGIES: Dict[BackendSelectionPolicy, PolicyStrategy] = {
    BackendSelectionPolicy.LATENCY_OPTIMIZED: LatencyPolicyStrategy(),
    BackendSelectionPolicy.MEMORY_OPTIMIZED: MemoryPolicyStrategy(),
    BackendSelectionPolicy.BALANCED: BalancedPolicyStrategy(),
    BackendSelectionPolicy.MAXIMUM_THROUGHPUT: MaximumThroughputPolicyStrategy(),
    BackendSelectionPolicy.ENERGY_EFFICIENT: EnergyEfficientPolicyStrategy(),
    BackendSelectionPolicy.DEVELOPER_OVERRIDE: DeveloperOverridePolicyStrategy(),
}

def get_policy_strategy(policy_enum: BackendSelectionPolicy) -> PolicyStrategy:
    return _STRATEGIES.get(policy_enum, BalancedPolicyStrategy())

@dataclass(frozen=True)
class ExecutionPolicy:
    selected_backend: str
    selection_reason: str
    selection_policy: BackendSelectionPolicy
    selection_constraints: tuple[str, ...] = tuple()
    fallback_chain: tuple[str, ...] = tuple()
    optimization_preference: str = "balanced"
    resource_limits: MappingProxyType[str, float] = field(default_factory=lambda: MappingProxyType({}))
    diagnostics: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
