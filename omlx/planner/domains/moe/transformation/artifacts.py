# SPDX-License-Identifier: Apache-2.0
"""
Immutable artifacts for compiler-native MoE realization.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Tuple, Optional
from omlx.planner.ir.nodes import IRNode

@dataclass(frozen=True)
class RealizedExpertGraph:
    """An immutable realized expert execution graph."""
    expert_id: str
    expert_nodes: Tuple[IRNode, ...]
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class ExpertRoutingGraph:
    """An immutable realized routing graph."""
    routing_id: str
    routing_node: IRNode
    expert_graphs: Tuple[RealizedExpertGraph, ...]
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class ExpertExecutionGraph:
    """An immutable realized complete MoE execution graph for a group."""
    group_id: str
    routing_graph: ExpertRoutingGraph
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class ExpertRealizationDiagnostic:
    """Diagnostic information from MoE realization."""
    level: str  # "INFO", "WARNING", "ERROR"
    message: str
    node_id: str = ""
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class ExpertRealizationStatistics:
    """Statistics about MoE graph realization."""
    original_node_count: int
    transformed_node_count: int
    experts_realized: int
    groups_realized: int
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class ExpertValidationReport:
    """Report on the validity of a realized MoE graph."""
    is_valid: bool
    diagnostics: Tuple[ExpertRealizationDiagnostic, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class ExpertRealizationReport:
    """Overall report containing all MoE realization information."""
    statistics: ExpertRealizationStatistics
    validation_report: ExpertValidationReport
    realized_groups: Tuple[ExpertExecutionGraph, ...] = field(default_factory=tuple)
