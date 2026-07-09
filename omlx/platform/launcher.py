# SPDX-License-Identifier: Apache-2.0
import logging
import time
import json
from pathlib import Path
from typing import List, Dict, Any

from .base import PlatformContext, PlatformService
from .event_bus import PlatformEventBus, PlatformEvent
from ..settings import GlobalSettings

logger = logging.getLogger("omlx.platform.launcher")

class Launcher:
    def __init__(self, base_path: Path | None = None, cli_args: Any = None) -> None:
        self.base_path = base_path
        self.cli_args = cli_args
        self.event_bus = PlatformEventBus()
        self.services: List[PlatformService] = []
        self.context: PlatformContext | None = None
        self.running = False

    def bootstrap(self) -> None:
        logger.info("Starting Platform Control Plane Bootstrap...")
        self.event_bus.publish(PlatformEvent("BootstrapStarted", data={}))

        # Load GlobalSettings
        settings = GlobalSettings.load(base_path=self.base_path, cli_args=self.cli_args)
        import sys
        errors = settings.validate()
        if errors:
            for error in errors:
                print(f"Configuration error: {error}")
            sys.exit(1)
        settings.ensure_directories()
        self.base_path = settings.base_path

        # Initialize placeholders for context
        registry = None
        auth = None
        state = None

        self.context = PlatformContext(
            config=settings,
            event_bus=self.event_bus,
            registry=registry,
            auth=auth,
            state=state,
            logger=logger
        )
        self.context.launcher = self

        # Dynamic service discovery
        import importlib
        import pkgutil
        from . import base
        from . import services

        for _, module_name, _ in pkgutil.walk_packages(services.__path__, services.__name__ + "."):
            try:
                importlib.import_module(module_name)
            except Exception as e:
                logger.error(f"Failed to import platform service {module_name}: {e}")

        try:
            importlib.import_module("omlx.platform.api")
        except Exception as e:
            logger.error(f"Failed to import platform UDS API: {e}")

        def find_subclasses(cls):
            subs = cls.__subclasses__()
            result = []
            for sub in subs:
                if getattr(sub, "name", None) and sub.name != "base_service":
                    result.append(sub)
                result.extend(find_subclasses(sub))
            return result

        service_classes = find_subclasses(base.PlatformService)
        raw_services = []
        for cls in service_classes:
            if getattr(cls, "enabled", True):
                raw_services.append(cls())

        # Topological sort
        self.services = self._topological_sort(raw_services)
        logger.info("Resolved service dependency order: %s", [s.__class__.__name__ for s in self.services])

        # Initialize
        for s in self.services:
            logger.info("Initializing service: %s", s.__class__.__name__)
            s.initialize(self.context)
            s.subscribe_events(self.event_bus)

        # Start
        for s in self.services:
            logger.info("Starting service: %s", s.__class__.__name__)
            s.start()

        # Healthy
        for s in self.services:
            logger.info("Service healthy check-in: %s", s.__class__.__name__)
            s.healthy()

        self.running = True
        self.event_bus.publish(PlatformEvent("BootstrapCompleted", data={}))
        logger.info("Platform Control Plane successfully bootstrapped.")

    def shutdown(self) -> None:
        if not self.running:
            return
        logger.info("Shutting down Platform Control Plane...")
        
        # Stop in reverse topological order
        for s in reversed(self.services):
            logger.info("Stopping service: %s", s.__class__.__name__)
            try:
                s.stop()
            except Exception as e:
                logger.error("Error stopping service %s: %s", s.__class__.__name__, e)
                
        # Shutdown in reverse topological order
        for s in reversed(self.services):
            logger.info("Shutting down service: %s", s.__class__.__name__)
            try:
                s.shutdown()
            except Exception as e:
                logger.error("Error shutting down service %s: %s", s.__class__.__name__, e)
                
        self.running = False
        logger.info("Platform Control Plane shut down complete.")

    def _topological_sort(self, services: List[PlatformService]) -> List[PlatformService]:
        service_map = {s.__class__.__name__: s for s in services}
        visited = {name: 0 for name in service_map} # 0=unvisited, 1=visiting, 2=visited
        order = []

        def dfs(name: str):
            if visited.get(name) == 1:
                raise ValueError(f"Circular dependency detected in platform services: {name}")
            if visited.get(name) == 2:
                return
            visited[name] = 1
            service = service_map.get(name)
            if service:
                for dep in service.dependencies():
                    if dep in service_map:
                        dfs(dep)
            visited[name] = 2
            order.append(name)

        for name in service_map:
            if visited[name] == 0:
                dfs(name)

        return [service_map[name] for name in order]

def main() -> None:
    import sys
    launcher = Launcher()
    try:
        launcher.bootstrap()
        while launcher.running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nShutting down One platform...")
        launcher.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()
