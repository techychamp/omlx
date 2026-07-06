# SPDX-License-Identifier: Apache-2.0
"""
Immutable artifacts for compiler-native fusion planning.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Optional

@dataclass(frozen=True)
class FusionGroup:
    """An immutable grouping of nodes identified for fusion."""
    id: str
    node_ids: tuple[str, ...]
    fusion_type: str  # e.g., "ATTENTION_QKV", "MLP_ACT"
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class FusionOpportunity:
    """An immutable descriptor for a detected fusion opportunity."""
    id: str
    target_nodes: tuple[str, ...]
    potential_group_type: str
    estimated_benefit: float = 0.0
    constraints: tuple[str, ...] = field(default_factory=tuple)
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class FusionDiagnostic:
    """An immutable diagnostic message related to fusion."""
    severity: str  # "INFO", "WARNING", "ERROR"
    message: str
    node_ids: tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class FusionCompatibilityReport:
    """An immutable report on fusion compatibility."""
    is_compatible: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)
    diagnostics: tuple[FusionDiagnostic, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class FusionStatistics:
    """Immutable statistics describing the outcome of a fusion planning pass."""
    total_opportunities_found: int = 0
    total_groups_formed: int = 0
    nodes_fused: int = 0
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class FusionPlan:
    """The immutable artifact emitted by the Fusion Planning domain."""
    groups: tuple[FusionGroup, ...] = field(default_factory=tuple)
    statistics: Optional[FusionStatistics] = None
    diagnostics: tuple[FusionDiagnostic, ...] = field(default_factory=tuple)
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
