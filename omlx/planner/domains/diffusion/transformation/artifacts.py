# SPDX-License-Identifier: Apache-2.0
"""
Immutable artifacts for compiler-native Diffusion realization.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Tuple

from omlx.planner.ir.nodes import IRNode

@dataclass(frozen=True)
class LatentExecutionGraph:
    """An immutable realized latent execution graph."""
    nodes: Tuple[IRNode, ...]
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class ConditioningExecutionGraph:
    """An immutable realized conditioning execution graph."""
    nodes: Tuple[IRNode, ...]
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class RealizedTimestepGraph:
    """An immutable realized timestep execution graph."""
    timestep: int
    nodes: Tuple[IRNode, ...]
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class DiffusionRealizationDiagnostic:
    """Diagnostic information from diffusion realization."""
    level: str  # "INFO", "WARNING", "ERROR"
    message: str
    node_id: str = ""
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class DiffusionRealizationStatistics:
    """Statistics about diffusion graph realization."""
    original_node_count: int
    transformed_node_count: int
    timesteps_realized: int
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class DiffusionValidationReport:
    """Report on the validity of a realized diffusion graph."""
    is_valid: bool
    diagnostics: Tuple[DiffusionRealizationDiagnostic, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class DiffusionExecutionGraph:
    """An immutable realized complete diffusion execution graph."""
    latent_graph: LatentExecutionGraph
    conditioning_graph: ConditioningExecutionGraph
    timesteps: Tuple[RealizedTimestepGraph, ...]
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class DiffusionRealizationReport:
    """Overall report containing all diffusion realization information."""
    statistics: DiffusionRealizationStatistics
    validation_report: DiffusionValidationReport
    execution_graph: DiffusionExecutionGraph
