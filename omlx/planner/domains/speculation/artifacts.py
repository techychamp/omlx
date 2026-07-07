# SPDX-License-Identifier: Apache-2.0
"""
Speculative Execution Graph Framework Artifacts.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Optional, Tuple, Sequence

from omlx.framework.graph.descriptor import GraphDescriptor
from omlx.planner.ir.physical.graph import PhysicalIR


@dataclass(frozen=True)
class SpeculativeExecutionDescriptor:
    """Immutable descriptor defining a speculative plan."""
    draft_model_id: str
    target_model_id: str
    draft_length: int
    draft_nodes: Tuple[str, ...] = field(default_factory=tuple)
    verification_nodes: Tuple[str, ...] = field(default_factory=tuple)
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class DraftExecutionGraph:
    """Immutable realization of draft token generation graph."""
    id: str
    graph: GraphDescriptor
    physical_graph: Optional[PhysicalIR] = None
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class VerificationExecutionGraph:
    """Immutable realization of target verification graph."""
    id: str
    graph: GraphDescriptor
    physical_graph: Optional[PhysicalIR] = None
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class AcceptanceExecutionGraph:
    """Immutable realization of token acceptance evaluation graph."""
    id: str
    graph: GraphDescriptor
    physical_graph: Optional[PhysicalIR] = None
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class SpeculativeExecutionGraph:
    """
    Immutable realization of a complete speculative execution step.
    Wraps draft, verification, and acceptance subgraphs.
    """
    id: str
    draft_graph: DraftExecutionGraph
    verification_graph: VerificationExecutionGraph
    acceptance_graph: AcceptanceExecutionGraph
    descriptor: SpeculativeExecutionDescriptor
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class SpeculativeRealizationDiagnostic:
    """Immutable diagnostic information for speculative realization."""
    level: str
    message: str
    node_id: Optional[str] = None
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class SpeculativeRealizationStatistics:
    """Immutable statistics for speculative realization."""
    draft_node_count: int = 0
    verification_node_count: int = 0
    acceptance_node_count: int = 0
    realization_latency_ms: float = 0.0
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class SpeculativeRealizationReport:
    """Immutable report for the speculative realization process."""
    success: bool
    speculative_graph: Optional[SpeculativeExecutionGraph] = None
    diagnostics: Tuple[SpeculativeRealizationDiagnostic, ...] = field(default_factory=tuple)
    statistics: SpeculativeRealizationStatistics = field(default_factory=SpeculativeRealizationStatistics)


@dataclass(frozen=True)
class SpeculativeValidationReport:
    """Immutable report detailing speculative graph validation results."""
    is_valid: bool
    diagnostics: Tuple[SpeculativeRealizationDiagnostic, ...] = field(default_factory=tuple)
