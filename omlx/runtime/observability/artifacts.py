# SPDX-License-Identifier: Apache-2.0
"""
Artifact Tracking for compiler phases.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class ArtifactBundle:
    """Immutable collection of serialized artifacts."""
    artifacts: Dict[str, Any] = field(default_factory=dict)

class ArtifactTracker:
    def __init__(self):
        self._artifacts: Dict[str, Any] = {}

    def track(self, name: str, artifact: Any):
        """Track an artifact."""
        self._artifacts[name] = artifact

    def get(self, name: str) -> Optional[Any]:
        return self._artifacts.get(name)

    def build(self) -> ArtifactBundle:
        return ArtifactBundle(artifacts=self._artifacts.copy())
