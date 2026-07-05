# SPDX-License-Identifier: Apache-2.0
"""
Thread-safe tracker for optimization intelligence statistics.
"""
import threading
from typing import Dict, Any, List
from .telemetry import OptimizationTelemetry

class IntelligenceStatisticsTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self._total_estimated_gain_ms = 0.0
        self._total_estimated_cost_ms = 0.0
        self._applied_passes = 0
        self._skipped_passes = 0
        self._analysis_reuses = 0
        self._cache_reuses = 0
        self._phase_timings_ms: Dict[str, float] = {}
        self._telemetry_history: List[OptimizationTelemetry] = []

    def record_telemetry(self, telemetry: OptimizationTelemetry):
        with self._lock:
            self._telemetry_history.append(telemetry)
            if telemetry.applied:
                self._applied_passes += 1
            else:
                self._skipped_passes += 1

            if telemetry.analysis_reused:
                self._analysis_reuses += 1
            if telemetry.cache_reused:
                self._cache_reuses += 1

            if telemetry.estimated_improvement:
                self._total_estimated_cost_ms += telemetry.estimated_improvement.optimization.application_time_ms

    def record_phase_timing(self, phase_name: str, duration_ms: float):
        with self._lock:
            self._phase_timings_ms[phase_name] = self._phase_timings_ms.get(phase_name, 0.0) + duration_ms

    def get_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "total_estimated_gain_ms": self._total_estimated_gain_ms,
                "total_estimated_cost_ms": self._total_estimated_cost_ms,
                "applied_passes": self._applied_passes,
                "skipped_passes": self._skipped_passes,
                "analysis_reuses": self._analysis_reuses,
                "cache_reuses": self._cache_reuses,
                "phase_timings_ms": self._phase_timings_ms.copy(),
                "telemetry_count": len(self._telemetry_history)
            }
