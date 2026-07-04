# SPDX-License-Identifier: Apache-2.0
"""
Diagnostics Engine
Generates human-readable summaries and developer hints for compiler execution.
"""
from typing import Any
from omlx.tooling.session.compiler_session import CompilerSession
from omlx.tooling.trace.tracer import InteractiveTrace

class DiagnosticsEngine:
    """Provides semantic diagnostics and summaries."""

    def generate_compiler_summary(self, session: CompilerSession) -> dict[str, Any]:
        """Summarizes a compiler session."""

        has_artifacts = bool(session.artifacts)
        artifact_count = len(session.artifacts) if has_artifacts else 0

        hints = []
        if not has_artifacts:
            hints.append("Session contains no artifacts. Did the compiler run?")

        return {
            "version": session.replay_session.compiler_version,
            "backend": session.replay_session.backend,
            "artifact_count": artifact_count,
            "diagnostics_count": len(session.diagnostics),
            "hints": hints
        }

    def generate_optimization_summary(self, trace: InteractiveTrace) -> dict[str, Any]:
        """Summarizes optimization passes from a trace."""
        passes = [e["event"] for e in trace.events if e["event"].startswith("pass_start")]

        hints = []
        if not passes:
            hints.append("No optimization passes were recorded.")

        return {
            "passes_run": len(passes),
            "pass_list": passes,
            "total_time": sum(trace.timings.values()) if trace.timings else 0.0,
            "hints": hints
        }
