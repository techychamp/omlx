from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

@dataclass(frozen=True)
class GraphDescriptor:
    id: str = "planning_graph"
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class GraphNode:
    """Canonical representation of a graph node."""
    id: str
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class GraphAnalysisReport:
    """Immutable report resulting from graph analysis."""
    node_properties: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    metrics: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class GraphEdge:
    """Canonical representation of a directed graph edge."""
    source_id: str
    target_id: str
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class GraphMetadata:
    """Metadata for a graph."""
    attributes: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class GraphStatistics:
    """Statistics for a graph."""
    node_count: int
    edge_count: int
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class GraphDiagnostic:
    """Diagnostic information about a graph."""
    level: str
    message: str
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class GraphValidationReport:
    """Validation report for a graph."""
    is_valid: bool
    diagnostics: tuple[GraphDiagnostic, ...] = tuple()
