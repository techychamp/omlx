# SPDX-License-Identifier: Apache-2.0
"""
Compiler-Native Graph Analysis & Intelligence Framework.
Provides stateless, immutable analysis of execution graphs.
"""

from .artifacts import (
    GraphDiagnostic,
    DiagnosticLevel,
    GraphValidationReport,
    GraphStatistics,
    DependencyAnalysis,
    CriticalPathReport,
    GraphCompatibilityReport,
    TraversalResult,
    GraphAnalysisReport,
)
from .analyzer import GraphAnalyzer

__all__ = [
    "GraphDiagnostic",
    "DiagnosticLevel",
    "GraphValidationReport",
    "GraphStatistics",
    "DependencyAnalysis",
    "CriticalPathReport",
    "GraphCompatibilityReport",
    "TraversalResult",
    "GraphAnalysisReport",
    "GraphAnalyzer",
]
