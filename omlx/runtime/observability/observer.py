# SPDX-License-Identifier: Apache-2.0
"""
Passive Observability API for OMLX.
"""
from contextlib import contextmanager
from typing import Any, Dict, Optional, List
from types import MappingProxyType
import time

import uuid
import threading
import logging

from .trace import TraceBuilder, ExecutionTrace
from .artifacts import ArtifactTracker, ArtifactBundle
from .telemetry import TelemetryCollector, TelemetrySnapshot
from .timeline import TimelineBuilder, Timeline
from .session import ObservationSession

logger = logging.getLogger("omlx.observability")

class Observer:
    """Thread-safe context-aware observer."""
    def __init__(self, run_id: Optional[str] = None):
        self.run_id = run_id or str(uuid.uuid4())
        self.trace_builder = TraceBuilder()
        self.artifact_tracker = ArtifactTracker()
        self.telemetry = TelemetryCollector()
        self.timeline_builder = TimelineBuilder()
        self.start_time = time.time()
        self.diagnostics: List[str] = []
        self._lock = threading.Lock()

    @contextmanager
    def observe_phase(self, phase: str, component: str, operation: str, metadata: Dict[str, Any] = None):
        start = time.time()
        thread_id = threading.get_ident()
        try:
            yield
            status = "success"
        except Exception as e:
            status = f"error: {str(e)}"
            self.add_diagnostic(f"[{phase}:{component}:{operation}] Error: {str(e)}")
            raise
        finally:
            duration = time.time() - start
            event_id = self.trace_builder.record(
                phase=phase,
                component=component,
                operation=operation,
                duration_sec=duration,
                status=status,
                metadata=metadata
            )
            self.timeline_builder.record(
                event_id=event_id,
                timestamp=start,
                phase=phase,
                duration_sec=duration,
                thread_id=thread_id,
                session_id=self.run_id,
                metadata={"component": component, "operation": operation, "status": status}
            )

            self.telemetry.measure(f"{phase}.{operation}.duration", duration)
            self.telemetry.increment(f"{phase}.{operation}.count")

    def track_artifact(self, name: str, artifact: Any):
        self.artifact_tracker.track(name, artifact)

    def observe_speculation(self, attempt_info: Dict[str, Any]) -> None:
        """Track a speculative execution attempt."""
        self.track_artifact("SpeculativeAttempt", attempt_info)
        self.telemetry.increment("speculation.attempts")
        if "accepted" in attempt_info:
            self.telemetry.measure("speculation.accepted_tokens", attempt_info["accepted"])

    def observe_verification(self, verification_info: Dict[str, Any]) -> None:
        """Track a speculative execution verification result."""
        self.track_artifact("SpeculativeVerification", verification_info)
        self.telemetry.increment("speculation.verifications")


    def record_graph_metrics(self, stats):
        """Records graph statistics from the Graph Analysis Framework into telemetry."""
        self.telemetry.measure("graph.node_count", stats.node_count)
        self.telemetry.measure("graph.edge_count", stats.edge_count)
        self.telemetry.measure("graph.root_count", stats.root_count)
        self.telemetry.measure("graph.leaf_count", stats.leaf_count)
        self.telemetry.measure("graph.max_depth", stats.max_depth)
        self.telemetry.measure("graph.average_branching_factor", stats.average_branching_factor)
        self.track_artifact("GraphStatistics", stats)

    def add_diagnostic(self, message: str):
        with self._lock:
            self.diagnostics.append(message)

    def get_trace(self) -> ExecutionTrace:
        return self.trace_builder.build()

    def get_artifacts(self) -> ArtifactBundle:
        return self.artifact_tracker.build()

    def get_telemetry(self) -> TelemetrySnapshot:
        return self.telemetry.build()

    def get_timeline(self) -> Timeline:
        return self.timeline_builder.build()

    def build_session(self, end_time: float, status: str, generated_tokens: List[int], statistics: Dict[str, Any]) -> ObservationSession:
        return ObservationSession(
            run_id=self.run_id,
            start_time=self.start_time,
            end_time=end_time,
            status=status,
            timeline=self.get_timeline(),
            trace=self.get_trace(),
            artifacts=self.get_artifacts(),
            telemetry=self.get_telemetry(),
            diagnostics=tuple(self.diagnostics),
            statistics=MappingProxyType(statistics),
            metadata=MappingProxyType({}),
            generated_tokens=tuple(generated_tokens)
        )
