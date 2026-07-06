# SPDX-License-Identifier: Apache-2.0
"""
Artifacts for OMLX Execution Engine.
"""

from typing import Any
BackendOperationGraph = Any
from dataclasses import dataclass, field
from typing import List, Optional

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
    draft_tokens: List[int] = field(default_factory=list)
    start_index: int = 0

@dataclass(frozen=True)
class AcceptanceWindow:
    """Window of accepted tokens after verification."""
    accepted_tokens: List[int] = field(default_factory=list)
    rejected_tokens: List[int] = field(default_factory=list)

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
    committed_tokens: List[int] = field(default_factory=list)
    commit_latency_ms: float = 0.0
