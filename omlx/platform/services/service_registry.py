# SPDX-License-Identifier: Apache-2.0
from ..base import PlatformService, PlatformContext
from ..event_bus import PlatformEvent
from typing import Dict

class ServiceRegistry(PlatformService):
    name = "registry"
    version = "1.0.0"

    def __init__(self):
        self.services: Dict[str, dict] = {}

    def initialize(self, context: PlatformContext) -> None:
        context.registry = self

    def subscribe_events(self, event_bus) -> None:
        event_bus.subscribe("RuntimeReady", self.handle_registration)

    def handle_registration(self, event: PlatformEvent) -> None:
        service_name = event.data.get("service_name", "unknown")
        self.services[service_name] = {
            "endpoint": event.data.get("endpoint"),
            "capabilities": event.data.get("capabilities", {}),
            "pid": event.data.get("pid"),
            "health": event.data.get("health", "healthy")
        }

    def get_service(self, service_name: str) -> dict | None:
        return self.services.get(service_name)

    def publish_state(self) -> dict:
        return {"services": self.services}
