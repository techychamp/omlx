# SPDX-License-Identifier: Apache-2.0
"""
Scoring framework for backend intelligence.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from omlx.planner.compiler.backend.descriptor import BackendDescriptor
from omlx.planner.ir.physical.graph import PhysicalIR
from .constraints import ExecutionConstraints

@dataclass(frozen=True)
class BackendScore:
    total_score: float
    latency_score: float
    memory_score: float
    throughput_score: float
    compatibility_score: float
    reasons: tuple[str, ...] = tuple()
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

class BackendScoringFramework:
    """
    A stateless scoring framework that computes comparative scores for backends
    given a specific execution context and physical IR.
    """

    def __init__(self):
        pass

    def compute_score(self, descriptor: BackendDescriptor, physical_ir: PhysicalIR, constraints: ExecutionConstraints) -> BackendScore:
        """
        Compute a comparative score for the backend. Does not perform actual selection.
        """
        # This is a stub implementation. In reality, it would evaluate the descriptor's
        # cost models and capabilities against the physical IR and constraints.

        # A basic check just to generate some score components
        compatibility_score = 100.0
        memory_score = 50.0
        latency_score = 50.0
        throughput_score = 50.0

        # We can simulate evaluating capability matches
        reasons = []
        if constraints.preferred_execution_family in descriptor.supported_execution_families:
            compatibility_score += 10.0
            reasons.append("Matches preferred execution family.")

        total_score = (compatibility_score + memory_score + latency_score + throughput_score) / 4.0

        return BackendScore(
            total_score=total_score,
            latency_score=latency_score,
            memory_score=memory_score,
            throughput_score=throughput_score,
            compatibility_score=compatibility_score,
            reasons=tuple(reasons)
        )
