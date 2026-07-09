# SPDX-License-Identifier: Apache-2.0
from ..base import PlatformService, PlatformContext
from ..event_bus import PlatformEvent
import time
from typing import Dict, List, Tuple

class MetricsService(PlatformService):
    name = "metrics"
    version = "1.0.0"

    def __init__(self) -> None:
        self.context: PlatformContext | None = None
        self.start_time = time.time()
        self.restarts: Dict[str, int] = {}
        self.launch_durations: Dict[str, float] = {}
        self.health_transitions: List[Tuple[str, str, str, float]] = []
        self.recovery_count = 0

    def initialize(self, context: PlatformContext) -> None:
        self.context = context
        context.metrics = self

    def subscribe_events(self, event_bus) -> None:
        event_bus.subscribe("ProcessStateChanged", self.handle_state_change)
        event_bus.subscribe("ProcessCrashed", self.handle_crash)

    def handle_state_change(self, event: PlatformEvent) -> None:
        proc_name = event.data.get("process_name")
        from_state = event.data.get("from_state")
        to_state = event.data.get("to_state")
        
        self.health_transitions.append((proc_name, from_state, to_state, time.time()))
        
        if to_state == "Running":
            self.restarts[proc_name] = self.restarts.get(proc_name, 0) + 1

    def handle_crash(self, event: PlatformEvent) -> None:
        self.recovery_count += 1

    def record_launch_duration(self, proc_name: str, duration: float) -> None:
        self.launch_durations[proc_name] = duration

    def publish_state(self) -> dict:
        return {
            "uptime": time.time() - self.start_time,
            "restarts": self.restarts,
            "launch_durations": self.launch_durations,
            "health_transitions_count": len(self.health_transitions),
            "recovery_count": self.recovery_count
        }
