# SPDX-License-Identifier: Apache-2.0
"""
SchedulingDiagnostics for OMLX Scheduling subsystem.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass(frozen=True)
class SchedulingDiagnostics:
    """Immutable snapshot of scheduling diagnostics."""
    scheduling_report: Dict[str, Any] = field(default_factory=dict)
    dependency_report: Dict[str, Any] = field(default_factory=dict)
    critical_path_report: Dict[str, Any] = field(default_factory=dict)
    execution_group_report: Dict[str, Any] = field(default_factory=dict)
    parallelism_report: Dict[str, Any] = field(default_factory=dict)
    policy_report: Dict[str, Any] = field(default_factory=dict)
    execution_ordering_report: Dict[str, Any] = field(default_factory=dict)
