from typing import Dict, Any, List
import threading
from omlx.api.v1.client import OMLXClient
from omlx.workbench.navigation import NavigationManager
from omlx.workbench.modules import (
    DashboardModule,
    RuntimeExplorerModule,
    CompilerExplorerModule,
    PlanningExplorerModule,
    ModelExplorerModule,
    DiagnosticsExplorerModule,
    PluginExplorerModule,
    SessionExplorerModule
)

class DeveloperWorkbench:
    """
    Developer Workbench Foundation.
    A read-only API client for inspecting the OMLX platform.
    """
    def __init__(self, client: OMLXClient):
        self.client = client
        self.navigation = NavigationManager()
        self._lock = threading.Lock()
        self._initialize_modules()

    def _initialize_modules(self) -> None:
        with self._lock:
            self.navigation.register_module(DashboardModule(self.client))
            self.navigation.register_module(RuntimeExplorerModule(self.client))
            self.navigation.register_module(CompilerExplorerModule(self.client))
            self.navigation.register_module(PlanningExplorerModule(self.client))
            self.navigation.register_module(ModelExplorerModule(self.client))
            self.navigation.register_module(DiagnosticsExplorerModule(self.client))
            self.navigation.register_module(PluginExplorerModule(self.client))
            self.navigation.register_module(SessionExplorerModule(self.client))

    def get_module_data(self, module_id: str) -> Dict[str, Any]:
        """Provides read-only access to a specific module's data."""
        module = self.navigation.get_module(module_id)
        if not module:
            raise ValueError(f"Module {module_id} not found.")

        # Simple dispatch for presentation
        if module_id == "dashboard":
            return getattr(module, "get_summary")()
        elif module_id == "runtime_explorer":
            return {"sessions": getattr(module, "list_sessions")()}
        elif module_id == "compiler_explorer":
             return getattr(module, "get_compiler_info")()
        elif module_id == "planning_explorer":
             return {"domains": getattr(module, "get_planning_domains")()}
        elif module_id == "model_explorer":
             return getattr(module, "get_model_intelligence")()

        return {"status": "ok", "module": module.info.name}
