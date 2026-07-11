# SPDX-License-Identifier: Apache-2.0
"""
Immutable artifacts for Graph Analysis Framework.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Tuple, Optional
import enum

class DiagnosticLevel(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

@dataclass(frozen=True)
class GraphDiagnostic:
    """A diagnostic message about a graph."""
    level: DiagnosticLevel
    message: str
    node_id: Optional[str] = None
    context: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class GraphValidationReport:
    """Report generated after validating a graph."""
    is_valid: bool
    diagnostics: Tuple[GraphDiagnostic, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class GraphStatistics:
    """Basic statistics of a graph."""
    node_count: int
    edge_count: int
    root_count: int
    leaf_count: int
    max_depth: int
    average_branching_factor: float

@dataclass(frozen=True)
class DependencyAnalysis:
    """Analysis of node dependencies."""
    # Maps node id to its direct dependencies
    dependencies: MappingProxyType[str, Tuple[str, ...]]
    # Maps node id to its direct dependents (nodes that depend on it)
    dependents: MappingProxyType[str, Tuple[str, ...]]
    # Indicates if any cycles were found
    has_cycles: bool

@dataclass(frozen=True)
class CriticalPathReport:
    """Report detailing the critical path through the graph."""
    path_nodes: Tuple[str, ...]
    estimated_cost: float

@dataclass(frozen=True)
class GraphCompatibilityReport:
    """Compatibility analysis result for a graph against specific constraints."""
    is_compatible: bool
    diagnostics: Tuple[GraphDiagnostic, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class TraversalResult:
    """Result of traversing a graph."""
    visited_nodes: Tuple[str, ...]
    traversal_order: Tuple[str, ...]
    unreachable_nodes: Tuple[str, ...]

@dataclass(frozen=True)
class GraphAnalysisReport:
    """A comprehensive report covering all analyses of a graph."""
    validation: GraphValidationReport
    statistics: GraphStatistics
    dependencies: DependencyAnalysis
    critical_path: Optional[CriticalPathReport] = None
    diagnostics: Tuple[GraphDiagnostic, ...] = field(default_factory=tuple)
