# SPDX-License-Identifier: Apache-2.0
"""
Observation Session
Immutable dataclass representing a full observation run.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
from types import MappingProxyType
import uuid
import time
from .timeline import Timeline
from .trace import ExecutionTrace
from .artifacts import ArtifactBundle
from .telemetry import TelemetrySnapshot

@dataclass(frozen=True)
class ObservationSession:
    """Immutable representation of a complete execution run."""
    run_id: str
    start_time: float
    end_time: Optional[float] = None
    status: str = "running"

    timeline: Timeline = field(default_factory=Timeline)
    trace: ExecutionTrace = field(default_factory=ExecutionTrace)
    artifacts: ArtifactBundle = field(default_factory=ArtifactBundle)
    telemetry: TelemetrySnapshot = field(default_factory=TelemetrySnapshot)

    diagnostics: tuple[str, ...] = tuple()
    statistics: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    generated_tokens: tuple[int, ...] = tuple()

    def complete(self, end_time: float, status: str, generated_tokens: List[int],
                 diagnostics: List[str], statistics: Dict[str, Any]) -> "ObservationSession":
        return ObservationSession(
            run_id=self.run_id,
            start_time=self.start_time,
            end_time=end_time,
            status=status,
            timeline=self.timeline,
            trace=self.trace,
            artifacts=self.artifacts,
            telemetry=self.telemetry,
            diagnostics=tuple(diagnostics),
            statistics=MappingProxyType(statistics),
            metadata=self.metadata,
            generated_tokens=tuple(generated_tokens)
        )
