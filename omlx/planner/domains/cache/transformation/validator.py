# SPDX-License-Identifier: Apache-2.0
"""
Transformation validator for cache realization.
"""

from typing import Tuple
from dataclasses import dataclass, field
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNodeType
from omlx.planner.domains.cache.artifacts import CacheRealizationDiagnostic

@dataclass(frozen=True)
class CacheValidationReport:
    """Immutable report resulting from validation of cache realization."""
    is_valid: bool
    diagnostics: Tuple[CacheRealizationDiagnostic, ...] = field(default_factory=tuple)

class CacheTransformationValidator:
    """Validates that a transformed ExecutionIR contains valid cache operations."""

    def validate(self, original_ir: ExecutionIR, transformed_ir: ExecutionIR) -> CacheValidationReport:
        """
        Validates the transformed ExecutionIR to ensure cache constraints are met.

        Currently, this validator is intentionally lightweight and only checks for basic
        connectivity properties (e.g., that CACHE_WRITE nodes have dependencies).

        TODO: CACHE-003 will perform deeper validation, including:
        - read/write ordering correctness
        - dependency validation across complex control flow
        - cache lifetime consistency checks
        - cache coherence verification across multiple streams/requests
        """
        diagnostics = []
        is_valid = True

        for node_id, node in transformed_ir.nodes.items():
            if node.node_type == IRNodeType.CACHE_READ:
                # Cache read should ideally have some dependency if not root
                pass
            elif node.node_type == IRNodeType.CACHE_WRITE:
                if not node.dependencies:
                    is_valid = False
                    diagnostics.append(CacheRealizationDiagnostic(
                        severity="ERROR",
                        message=f"CACHE_WRITE node {node_id} has no dependencies.",
                        node_ids=(node_id,)
                    ))

        return CacheValidationReport(
            is_valid=is_valid,
            diagnostics=tuple(diagnostics)
        )
