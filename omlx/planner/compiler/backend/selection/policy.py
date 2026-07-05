# SPDX-License-Identifier: Apache-2.0
"""
Backend Selection and Execution Policies.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Optional, Dict
import enum
from abc import ABC, abstractmethod
from .evaluation import BackendEvaluationReport

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
    def score(self, evaluation: BackendEvaluationReport) -> float:
        pass

class LatencyPolicyStrategy(PolicyStrategy):
    def score(self, evaluation: BackendEvaluationReport) -> float:
        if not evaluation.is_compatible: return 0.0
        return evaluation.score + (1000 / (evaluation.estimated_latency_ms + 1e-9)) * 10

class MemoryPolicyStrategy(PolicyStrategy):
    def score(self, evaluation: BackendEvaluationReport) -> float:
        if not evaluation.is_compatible: return 0.0
        return evaluation.score + (10000 / (evaluation.estimated_memory_mb + 1e-9))

class BalancedPolicyStrategy(PolicyStrategy):
    def score(self, evaluation: BackendEvaluationReport) -> float:
        if not evaluation.is_compatible: return 0.0
        return evaluation.score

class MaximumThroughputPolicyStrategy(PolicyStrategy):
    def score(self, evaluation: BackendEvaluationReport) -> float:
        if not evaluation.is_compatible: return 0.0
        return evaluation.score + (evaluation.estimated_throughput_tps * 20)

class EnergyEfficientPolicyStrategy(PolicyStrategy):
    def score(self, evaluation: BackendEvaluationReport) -> float:
        if not evaluation.is_compatible: return 0.0
        return evaluation.score # Stub for now

class DeveloperOverridePolicyStrategy(PolicyStrategy):
    def score(self, evaluation: BackendEvaluationReport) -> float:
        if not evaluation.is_compatible: return 0.0
        return evaluation.score

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
