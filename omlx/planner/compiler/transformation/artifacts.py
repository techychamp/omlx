from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Tuple

from omlx.planner.ir.nodes import IRNode

@dataclass(frozen=True)
class RealizedFusionGroup:
    """An immutable realized fusion group containing the fused node."""
    id: str
    original_node_ids: tuple[str, ...]
    fused_node: IRNode
    fusion_type: str
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class TransformationDiagnostic:
    """Diagnostic information from graph transformation."""
    level: str  # "INFO", "WARNING", "ERROR"
    message: str
    node_id: str = ""
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class TransformationStatistics:
    """Statistics about a graph transformation."""
    original_node_count: int
    transformed_node_count: int
    nodes_fused: int
    groups_realized: int
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class TransformationValidationReport:
    """Report on the validity of a transformed graph."""
    is_valid: bool
    diagnostics: tuple[TransformationDiagnostic, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class TransformationReport:
    """Overall report containing all transformation information."""
    statistics: TransformationStatistics
    validation_report: TransformationValidationReport
    realized_groups: tuple[RealizedFusionGroup, ...] = field(default_factory=tuple)
