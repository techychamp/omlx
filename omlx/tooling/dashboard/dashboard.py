# SPDX-License-Identifier: Apache-2.0
"""
Diagnostics Dashboard
Generates machine-readable statistics reports for compiler performance.
"""
from typing import Any
from omlx.tooling.trace.tracer import CompilerTrace

class DiagnosticsDashboard:
    """Generates structured diagnostic reports."""

    def generate_report(self, trace: CompilerTrace) -> dict[str, Any]:
        """Consumes a CompilerTrace and produces a machine-readable report."""
        report = {
            "compiler_statistics": {
                "total_passes_run": len(trace.timings),
                "total_duration_sec": sum(trace.timings.values()) if trace.timings else 0.0,
            },
            "pass_timings": trace.timings,
            "diagnostics_count": len(trace.diagnostics)
        }
        return report
