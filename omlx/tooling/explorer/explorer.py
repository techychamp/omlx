# SPDX-License-Identifier: Apache-2.0
"""
Artifact Explorer
Provides read-only navigation through compiler artifact graphs.
"""
from typing import Any
from omlx.tooling.session.compiler_session import CompilerSession

class ArtifactExplorer:
    """Allows navigation through compiler artifacts via simulated links."""

    def __init__(self, session: CompilerSession):
        self.session = session

    def navigate(self, start_artifact: str) -> list[str]:
        """
        Simulates navigation through the artifact graph.
        Returns a list of connected artifact identifiers.
        """
        artifacts = self.session.artifacts
        if not artifacts:
            return []

        path = []
        if start_artifact == "CapabilityDescriptor":
            path.append("CapabilityDescriptor")
            if "ExecutionPlan" in artifacts:
                path.append("ExecutionPlan")
                if "LogicalIR" in artifacts:
                    path.append("LogicalIR")
                    if "PhysicalIR" in artifacts:
                        path.append("PhysicalIR")
                        if "BackendGraph" in artifacts:
                            path.append("BackendGraph")
        elif start_artifact == "ExecutionPlan":
             if "ExecutionPlan" in artifacts:
                path.append("ExecutionPlan")
                if "LogicalIR" in artifacts:
                    path.append("LogicalIR")
        return path
