# SPDX-License-Identifier: Apache-2.0
"""
Compiler Session Browser
Provides interactive, read-only browsing of a CompilerSession.
"""
from typing import Any, Iterator
from omlx.tooling.session.compiler_session import CompilerSession
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.plan import ExecutionPlan
from omlx.planner.ir.physical.graph import PhysicalIR

class CompilerSessionBrowser:
    """Provides a read-only interface for deeply navigating session data."""
    def __init__(self, session: CompilerSession):
        self._session = session

    @property
    def summary(self) -> dict[str, Any]:
        """Returns a high-level summary of the session."""
        return {
            "version": self._session.replay_session.compiler_version,
            "backend": self._session.replay_session.backend,
            "artifacts_available": list(self._session.artifacts.keys()),
            "diagnostics_count": len(self._session.diagnostics),
            "statistics_keys": list(self._session.statistics.keys())
        }

    def get_artifact(self, name: str) -> Any:
        """Retrieves an artifact by name, returning None if not found."""
        return self._session.artifacts.get(name)

    def walk_pipeline(self) -> Iterator[tuple[str, Any]]:
        """Walks the standard compiler pipeline if artifacts are available."""
        pipeline_order = [
            "CapabilityDescriptor",
            "ExecutionPlan",
            "LogicalIR",
            "PhysicalIR",
            "BackendGraph"
        ]

        for artifact_name in pipeline_order:
            artifact = self.get_artifact(artifact_name)
            if artifact:
                yield artifact_name, artifact

    def get_statistics(self) -> dict[str, Any]:
        """Returns the session statistics."""
        return dict(self._session.statistics)

    def get_diagnostics(self) -> list[str]:
        """Returns the session diagnostics."""
        return list(self._session.diagnostics)

    def get_verification_stages(self) -> list[str]:
        """Extracts verification stages from the ExecutionPlan if available."""
        plan = self.get_artifact("ExecutionPlan")
        if plan and hasattr(plan, "verification_stages"):
            return list(plan.verification_stages)
        return []
