# SPDX-License-Identifier: Apache-2.0
"""
Diagnostics for OMLX Execution Engine.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass(frozen=True)
class ExecutionTimeline:
    """Immutable snapshot of the execution timeline."""
    events: List[Dict[str, Any]] = field(default_factory=list)

@dataclass(frozen=True)
class BackendInvocationReport:
    """Immutable snapshot of backend invocations."""
    invocations: List[Dict[str, Any]] = field(default_factory=list)

@dataclass(frozen=True)
class ExecutionReport:
    """Immutable snapshot of the execution report."""
    timeline: ExecutionTimeline = field(default_factory=ExecutionTimeline)
    backend_invocations: BackendInvocationReport = field(default_factory=BackendInvocationReport)
    fallback_report: Optional[Dict[str, Any]] = None
    compiler_execution_report: Optional[Dict[str, Any]] = None
    compatibility_report: Optional[Dict[str, Any]] = None
    summary: str = ""
    trace: List[str] = field(default_factory=list)

from typing import Optional

@dataclass(frozen=True)
class SpeculativeDiagnostics:
    """Diagnostic information for speculative execution."""
    verification_windows: List[Dict[str, Any]] = field(default_factory=list)
    rejection_reasons: List[Dict[str, Any]] = field(default_factory=list)
    speedup_estimate: float = 0.0
