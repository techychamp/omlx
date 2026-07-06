from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any
from .artifacts import GraphNode, GraphEdge, GraphMetadata

@dataclass(frozen=True)
class GraphDescriptor:
    """Immutable canonical descriptor for all graph structures."""
    id: str
    nodes: MappingProxyType[str, GraphNode]
    edges: tuple[GraphEdge, ...]
    metadata: GraphMetadata = field(default_factory=lambda: GraphMetadata())
