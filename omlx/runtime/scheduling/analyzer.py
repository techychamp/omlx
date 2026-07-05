# SPDX-License-Identifier: Apache-2.0
"""
Analyzer tools for OMLX Scheduling subsystem.
"""
# This file can re-export or serve as a unified facade if needed
from .dependency import DependencyAnalyzer, DependencyAnalysisResult
from .critical_path import CriticalPathAnalyzer, CriticalPathResult

class GraphAnalyzer:
    """Unified analyzer for scheduling."""
    def __init__(self):
        self.dep_analyzer = DependencyAnalyzer()
        self.cp_analyzer = CriticalPathAnalyzer()

    def analyze(self, graph):
        dep_result = self.dep_analyzer.analyze(graph)
        cp_result = self.cp_analyzer.analyze(graph, dep_result)
        return dep_result, cp_result
