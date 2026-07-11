# SPDX-License-Identifier: Apache-2.0
"""
Replay Session
Immutable dataclass representing a snapshot of a compiler state.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from omlx.capabilities.descriptor import CapabilityDescriptor
from omlx.planner.plan import ExecutionPlan
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.physical.graph import PhysicalIR

@dataclass(frozen=True)
class ReplaySession:
    """Immutable representation of a compiler replay session."""
    compiler_version: str
    planner_version: str
    feature_flags: MappingProxyType[str, Any]
    backend: str
    optimization_pipeline: tuple[str, ...]
    timestamps: MappingProxyType[str, float]

    # Artifacts captured
    capability_descriptor: CapabilityDescriptor | None = None
    execution_plan: ExecutionPlan | None = None
    logical_ir: ExecutionIR | None = None
    physical_ir: PhysicalIR | None = None
    backend_graph: Any | None = None
    translation_result: Any | None = None

    diagnostics: tuple[str, ...] = tuple()
    compiler_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
