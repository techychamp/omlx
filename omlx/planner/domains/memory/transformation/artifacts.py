# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from types import MappingProxyType
from omlx.planner.ir.nodes import IRNode

@dataclass(frozen=True)
class RealizedAllocationGraph:
    allocation_id: str
    allocation_node: IRNode

@dataclass(frozen=True)
class RealizedLifetimeGraph:
    lifetime_id: str
    lifetime_nodes: Tuple[IRNode, ...]

@dataclass(frozen=True)
class MemoryExecutionGraph:
    allocations: Tuple[RealizedAllocationGraph, ...]
    lifetimes: Tuple[RealizedLifetimeGraph, ...]

@dataclass(frozen=True)
class MemoryRealizationDiagnostic:
    severity: str
    message: str

@dataclass(frozen=True)
class MemoryRealizationStatistics:
    original_node_count: int
    transformed_node_count: int
    allocations_realized: int
    lifetimes_realized: int

@dataclass(frozen=True)
class MemoryValidationReport:
    is_valid: bool
    diagnostics: Tuple[MemoryRealizationDiagnostic, ...]

@dataclass(frozen=True)
class MemoryRealizationReport:
    statistics: MemoryRealizationStatistics
    validation_report: MemoryValidationReport
    execution_graph: MemoryExecutionGraph
