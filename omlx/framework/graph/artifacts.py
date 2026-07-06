from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

@dataclass(frozen=True)
class GraphDescriptor:
    id: str
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class GraphAnalysisReport:
    """Immutable report resulting from graph analysis."""
    node_properties: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    metrics: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
