# SPDX-License-Identifier: Apache-2.0
"""
Passive Observability API for OMLX.
"""
from contextlib import contextmanager
from typing import Any, Dict, Optional
import time

from .trace import TraceBuilder, ExecutionTrace
from .artifacts import ArtifactTracker, ArtifactBundle
from .telemetry import TelemetryCollector, TelemetrySnapshot

class Observer:
    """Thread-safe context-aware observer."""
    def __init__(self):
        self.trace_builder = TraceBuilder()
        self.artifact_tracker = ArtifactTracker()
        self.telemetry = TelemetryCollector()

    @contextmanager
    def observe_phase(self, phase: str, component: str, operation: str, metadata: Dict[str, Any] = None):
        start = time.time()
        try:
            yield
            status = "success"
        except Exception as e:
            status = f"error: {str(e)}"
            raise
        finally:
            duration = time.time() - start
            self.trace_builder.record(
                phase=phase,
                component=component,
                operation=operation,
                duration_sec=duration,
                status=status,
                metadata=metadata
            )
            self.telemetry.measure(f"{phase}.{operation}.duration", duration)
            self.telemetry.increment(f"{phase}.{operation}.count")

    def track_artifact(self, name: str, artifact: Any):
        self.artifact_tracker.track(name, artifact)

    def get_trace(self) -> ExecutionTrace:
        return self.trace_builder.build()

    def get_artifacts(self) -> ArtifactBundle:
        return self.artifact_tracker.build()

    def get_telemetry(self) -> TelemetrySnapshot:
        return self.telemetry.build()
