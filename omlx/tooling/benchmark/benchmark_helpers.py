# SPDX-License-Identifier: Apache-2.0
"""
Benchmark Helpers
Reusable benchmark utilities.
"""
from typing import Any, Dict
from omlx.runtime.observability.global_observer import get_observer
from omlx.tooling.session.compiler_session import CompilerSession

class BenchmarkReport:
    """Deterministic report of benchmark results."""
    def __init__(self, metrics: Dict[str, Any]):
        self.metrics = metrics

    def to_dict(self) -> Dict[str, Any]:
        return {"metrics": self.metrics}

class BenchmarkHelper:
    """Helper to run non-mutating benchmarks (if supported) or analyze prior benchmark runs."""

    def analyze_compiler_performance(self, session: CompilerSession = None) -> BenchmarkReport:
        """Analyzes compiler performance based on existing observation data or provided session."""
        observer = get_observer()
        metrics = {}

        # If we have real telemetry data, extract compiler performance metrics.
        if session and session.statistics:
             metrics["compile_time_ms"] = session.statistics.get("total_time_ms", 0.0)

        # Optional: query global observer for historical events
        # metrics["historical_compile_avg"] = ...

        return BenchmarkReport(metrics)

    def analyze_backend_comparison(self, backend_a: str, backend_b: str, cost_models: Dict[str, Any] = None) -> BenchmarkReport:
        """Compares backend performance based on cost models or existing data.
        Does NOT actively benchmark or execute code.
        """
        metrics = {
             "comparison": f"{backend_a} vs {backend_b}"
        }

        if cost_models and backend_a in cost_models and backend_b in cost_models:
             cost_a = cost_models[backend_a].get("estimated_latency", float('inf'))
             cost_b = cost_models[backend_b].get("estimated_latency", float('inf'))
             if cost_b > 0 and cost_a != float('inf') and cost_b != float('inf'):
                  metrics["estimated_speedup"] = cost_b / cost_a

        return BenchmarkReport(metrics)
