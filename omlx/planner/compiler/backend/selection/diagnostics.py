# SPDX-License-Identifier: Apache-2.0
"""
Backend Selection Diagnostics.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Optional

from .evaluation import BackendEvaluationReport
from .compatibility import CompatibilityReport
from .negotiation import NegotiationDiagnostics
from .fallback import FallbackPlan
from ..evaluation.reports import BackendEvaluationReport as DetailedBackendEvaluationReport, BackendSelectionReport
from ..evaluation.telemetry import BackendTelemetrySummary

@dataclass(frozen=True)
class BackendSelectionDiagnostics:
    timestamp: float
    candidate_backends: tuple[str, ...]
    evaluations: MappingProxyType[str, BackendEvaluationReport]
    compatibility_reports: MappingProxyType[str, CompatibilityReport]
    negotiations: MappingProxyType[str, NegotiationDiagnostics]
    fallback_plan: FallbackPlan
    selected_backend: str
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    detailed_evaluations: Optional[MappingProxyType[str, DetailedBackendEvaluationReport]] = field(default_factory=lambda: MappingProxyType({}))
    telemetry_summary: Optional[BackendTelemetrySummary] = field(default=None)
    selection_report: Optional[BackendSelectionReport] = field(default=None)
