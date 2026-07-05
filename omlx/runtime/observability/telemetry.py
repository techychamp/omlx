# SPDX-License-Identifier: Apache-2.0
"""
Telemetry tracking.
"""
from dataclasses import dataclass, field
from typing import Dict, Any
from types import MappingProxyType

@dataclass(frozen=True)
class TelemetrySnapshot:
    """Immutable snapshot of telemetry data."""
    measurements: MappingProxyType[str, float] = field(default_factory=lambda: MappingProxyType({}))
    counters: MappingProxyType[str, int] = field(default_factory=lambda: MappingProxyType({}))

class TelemetryCollector:
    def __init__(self):
        self._measurements: Dict[str, float] = {}
        self._counters: Dict[str, int] = {}

    def measure(self, key: str, value: float):
        self._measurements[key] = value

    def increment(self, key: str, amount: int = 1):
        self._counters[key] = self._counters.get(key, 0) + amount

    def build(self) -> TelemetrySnapshot:
        return TelemetrySnapshot(
            measurements=MappingProxyType(self._measurements.copy()),
            counters=MappingProxyType(self._counters.copy())
        )
