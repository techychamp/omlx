from dataclasses import dataclass, field
import threading
from typing import Mapping, Sequence

@dataclass(frozen=True)
class BackendTelemetrySummary:
    """Telemetry summary."""
    selection_reason: str
    policy_applied: str
    estimated_latency_ms: float
    estimated_peak_memory_mb: float
    estimated_throughput_tokens_per_sec: float
    capability_usage: tuple[str, ...]
    fallback_usage: tuple[str, ...]

class BackendTelemetry:
    """Collects and provides backend telemetry."""
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._summaries: list[BackendTelemetrySummary] = []
        self._selection_frequency: dict[str, int] = {}
        self._policy_usage: dict[str, int] = {}
        self._fallback_frequency: dict[str, int] = {}
        self._capability_utilization: dict[str, int] = {}
        self._evaluation_times: list[float] = []

    def record_selection(self, backend_id: str, summary: BackendTelemetrySummary, evaluation_time_ms: float) -> None:
        with self._lock:
            self._summaries.append(summary)
            self._selection_frequency[backend_id] = self._selection_frequency.get(backend_id, 0) + 1
            self._policy_usage[summary.policy_applied] = self._policy_usage.get(summary.policy_applied, 0) + 1
            for cap in summary.capability_usage:
                self._capability_utilization[cap] = self._capability_utilization.get(cap, 0) + 1
            if summary.fallback_usage:
                for fallback in summary.fallback_usage:
                    self._fallback_frequency[fallback] = self._fallback_frequency.get(fallback, 0) + 1
            self._evaluation_times.append(evaluation_time_ms)

    def get_selection_frequency(self) -> Mapping[str, int]:
        with self._lock:
            return dict(self._selection_frequency)

    def get_policy_usage(self) -> Mapping[str, int]:
        with self._lock:
            return dict(self._policy_usage)

    def get_fallback_frequency(self) -> Mapping[str, int]:
        with self._lock:
            return dict(self._fallback_frequency)

    def get_capability_utilization(self) -> Mapping[str, int]:
        with self._lock:
            return dict(self._capability_utilization)

    def get_average_evaluation_time_ms(self) -> float:
        with self._lock:
            if not self._evaluation_times:
                return 0.0
            return sum(self._evaluation_times) / len(self._evaluation_times)

    def get_summaries(self) -> Sequence[BackendTelemetrySummary]:
        with self._lock:
            return tuple(self._summaries)
