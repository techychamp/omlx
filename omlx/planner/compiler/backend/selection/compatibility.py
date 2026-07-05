# SPDX-License-Identifier: Apache-2.0
"""
Backend Compatibility Framework.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any
from typing import Any
from ..descriptor import BackendDescriptor
from omlx.capabilities.descriptor import CapabilityDescriptor
from .policy import ExecutionPolicy

@dataclass(frozen=True)
class CompatibilityReport:
    is_compatible: bool
    reasons: tuple[str, ...] = tuple()
    warnings: tuple[str, ...] = tuple()
    diagnostics: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

class CompatibilityChecker:
    @staticmethod
    def check_compatibility(
        plan: Any,
        backend_desc: BackendDescriptor,
        cap_desc: CapabilityDescriptor,
        policy: ExecutionPolicy
    ) -> CompatibilityReport:
        # Check basic execution constraints
        reasons = []
        warnings = []
        is_compatible = True

        # We would typically check if backend_desc.supported_execution_semantics covers plan's requirements.
        # This is a stub for the generic logic.
        if backend_desc.backend_family not in policy.fallback_chain and policy.selected_backend != backend_desc.backend_id and policy.selected_backend != "":
             warnings.append(f"Backend {backend_desc.backend_id} is not the primary selected backend and not in fallback chain.")

        # Just a basic validation for now.
        if backend_desc.memory_model == "":
            is_compatible = False
            reasons.append("Backend descriptor has no memory model defined.")

        diagnostics = {
            "hardware_metadata": backend_desc.hardware_metadata,
            "policy": policy.selection_policy
        }

        return CompatibilityReport(
            is_compatible=is_compatible,
            reasons=tuple(reasons),
            warnings=tuple(warnings),
            diagnostics=MappingProxyType(diagnostics)
        )
