# SPDX-License-Identifier: Apache-2.0
"""
Immutable artifacts for compiler-native cache realization.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Tuple
from omlx.framework.graph.descriptor import GraphDescriptor

@dataclass(frozen=True)
class CacheRealizationDiagnostic:
    """An immutable diagnostic message related to cache realization."""
    severity: str  # "INFO", "WARNING", "ERROR"
    message: str
    node_ids: Tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class CacheRealizationStatistics:
    """Immutable statistics describing the outcome of cache realization."""
    nodes_added: int = 0
    edges_added: int = 0
    cache_read_ops: int = 0
    cache_write_ops: int = 0
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class CacheExecutionGraph:
    """Immutable realization of cache execution operations."""
    graph: GraphDescriptor = field(default_factory=lambda: GraphDescriptor(id="default", nodes=MappingProxyType({}), edges=tuple()))

@dataclass(frozen=True)
class CacheRealizationReport:
    """Immutable report resulting from cache realization."""
    is_successful: bool
    statistics: CacheRealizationStatistics = field(default_factory=CacheRealizationStatistics)
    diagnostics: Tuple[CacheRealizationDiagnostic, ...] = field(default_factory=tuple)
    execution_graph: CacheExecutionGraph = field(default_factory=lambda: CacheExecutionGraph())
