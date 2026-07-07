# SPDX-License-Identifier: Apache-2.0
"""
Artifacts for OMLX Execution Engine.
"""

from typing import Any, Optional
from dataclasses import dataclass, field
from omlx.framework.graph.descriptor import GraphDescriptor
from typing import List, Optional
from omlx.planner.domains.speculation.artifacts import SpeculativeExecutionGraph

BackendOperationGraph = Any

@dataclass(frozen=True)
class ExecutionGraph(GraphDescriptor):
    """Base canonical execution graph."""
    pass

@dataclass(frozen=True)
class CacheExecutionGraph(ExecutionGraph):
    """Execution graph specialized for caching operations."""
    pass

@dataclass(frozen=True)
class MemoryExecutionGraph(ExecutionGraph):
    """Execution graph specialized for memory allocation and movement."""
    pass

@dataclass(frozen=True)
class BatchExecutionGraph(ExecutionGraph):
    """Execution graph specialized for batched execution."""
    pass


@dataclass(frozen=True)
class ExpertExecutionGraph(ExecutionGraph):
    """Execution graph specialized for Mixture of Experts (MoE) execution."""
    pass

@dataclass(frozen=True)
class DiffusionExecutionGraph(ExecutionGraph):
    """Execution graph specialized for diffusion modeling."""
    pass



@dataclass(frozen=True)
class VerificationResult:
    """Strongly typed outcome from VerificationExecutionGraph."""
    accepted: bool
    accepted_tokens: tuple[int, ...] = tuple()
    rejected_tokens: tuple[int, ...] = tuple()

@dataclass(frozen=True)
class VerificationExecutionReport:
    """Report detailing verification outcome and latency."""
    accepted: bool = False
    accepted_tokens_count: int = 0
    rejected_tokens_count: int = 0
    latency_ms: float = 0.0

@dataclass(frozen=True)
class AcceptanceExecutionReport:
    """Report detailing acceptance evaluation."""
    accepted_tokens: tuple[int, ...] = tuple()
    latency_ms: float = 0.0

@dataclass(frozen=True)
class RollbackExecutionReport:
    """Report detailing rollback operation due to rejection."""
    rejected_tokens: tuple[int, ...] = tuple()
    latency_ms: float = 0.0

@dataclass(frozen=True)
class SpeculativeExecutionReport:
    """Report detailing speculative generation details."""
    attempts: int = 0
    accepted_tokens: int = 0
    rejected_tokens: int = 0
    latency_ms: float = 0.0

@dataclass(frozen=True)
class VerificationWindow:
    """Window of generated tokens to be verified."""
    draft_tokens: tuple[int, ...] = tuple()
    start_index: int = 0

@dataclass(frozen=True)
class AcceptanceWindow:
    """Window of accepted tokens after verification."""
    accepted_tokens: tuple[int, ...] = tuple()
    rejected_tokens: tuple[int, ...] = tuple()

@dataclass(frozen=True)
class AcceptanceStatistics:
    """Statistics about acceptance rates."""
    total_verified: int = 0
    total_accepted: int = 0
    acceptance_rate: float = 0.0

@dataclass(frozen=True)
class VerificationStatistics:
    """Statistics about verification latency and overhead."""
    verification_count: int = 0
    total_latency_ms: float = 0.0
    average_latency_ms: float = 0.0

@dataclass(frozen=True)
class CommitReport:
    """Report detailing committed tokens and state updates."""
    committed_tokens: tuple[int, ...] = tuple()
    commit_latency_ms: float = 0.0


@dataclass(frozen=True)
class RuntimeSpeculativeState:
    """Runtime state wrapper for speculative execution."""
    speculative_graph: Optional[SpeculativeExecutionGraph] = None
    reports: tuple[Any, ...] = field(default_factory=tuple)
