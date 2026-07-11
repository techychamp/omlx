# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
from typing import Any, List
import logging

class PlatformContext:
    """Every PlatformService receives this context during initialization."""
    def __init__(
        self,
        config: Any,
        event_bus: Any,
        registry: Any = None,
        auth: Any = None,
        state: Any = None,
        logger: Any = None,
        metrics: Any = None,
        process_manager: Any = None
    ) -> None:
        self.config = config
        self.event_bus = event_bus
        self.registry = registry
        self.auth = auth
        self.state = state
        self.logger = logger
        self.metrics = metrics
        self.process_manager = process_manager

class PlatformService:
    """Peer plugin interface for Control Plane operations."""
    name: str = "base_service"
    version: str = "1.0.0"
    enabled: bool = True
    tags: List[str] = []

    def dependencies(self) -> List[str]:
        """Return list of service class names required to be initialized beforehand."""
        return []

    def initialize(self, context: PlatformContext) -> None:
        """Perform initial dependency setup, config loading, and registration."""
        pass

    def start(self) -> None:
        """Start the service execution, spawn background workers or threads if needed."""
        pass

    def healthy(self) -> None:
        """Called when all services have been started and the platform is healthy."""
        pass

    def stop(self) -> None:
        """Gracefully instruct the service to stop accepting work."""
        pass

    def shutdown(self) -> None:
        """Gracefully shut down the service and clean up resources completely."""
        pass

    def health(self) -> dict:
        """Return diagnostic health checks for the service."""
        return {"status": "healthy"}

    def publish_state(self) -> dict:
        """Publish the immutable local state dictionary to be aggregated."""
        return {}

    def subscribe_events(self, event_bus: Any) -> None:
        """Register listeners for platform messages."""
        pass
