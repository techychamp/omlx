# SPDX-License-Identifier: Apache-2.0
"""
Compiler Optimization Framework - Diagnostics
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional

class DiagnosticLevel(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    DEBUG = auto()

@dataclass
class OptimizationDiagnostic:
    level: DiagnosticLevel
    message: str
    pass_name: Optional[str] = None
    artifact_id: Optional[str] = None

class DiagnosticsTracker:
    def __init__(self):
        self._diagnostics: List[OptimizationDiagnostic] = []

    def add_diagnostic(self, level: DiagnosticLevel, message: str, pass_name: Optional[str] = None, artifact_id: Optional[str] = None):
        diag = OptimizationDiagnostic(level=level, message=message, pass_name=pass_name, artifact_id=artifact_id)
        self._diagnostics.append(diag)

    def get_all(self) -> List[OptimizationDiagnostic]:
        return list(self._diagnostics)

    def get_errors(self) -> List[OptimizationDiagnostic]:
        return [d for d in self._diagnostics if d.level == DiagnosticLevel.ERROR]

    def clear(self):
        self._diagnostics.clear()
