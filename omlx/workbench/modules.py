from typing import Any, Dict, Optional, List
from omlx.api.v1.client import OMLXClient
from omlx.workbench.navigation import WorkbenchModule, ModuleInfo

class DashboardModule(WorkbenchModule):
    def __init__(self, client: OMLXClient):
        super().__init__(ModuleInfo(
            id="dashboard",
            name="Dashboard",
            description="Unified view of Runtime status, active sessions, and loaded models.",
            route="/dashboard"
        ))
        self.client = client

    def get_summary(self) -> Dict[str, Any]:
        return {
            "active_sessions": len(self.client._sessions) if hasattr(self.client, "_sessions") else 0,
            "models_loaded": 0, # Placeholder
            "status": "Online"
        }

class RuntimeExplorerModule(WorkbenchModule):
    def __init__(self, client: OMLXClient):
        super().__init__(ModuleInfo(
            id="runtime_explorer",
            name="Runtime Explorer",
            description="Visualize RuntimeSessions and execution state.",
            route="/runtime"
        ))
        self.client = client

    def list_sessions(self) -> List[Dict[str, Any]]:
        return [{"session_id": sid, "active": sess.active} for sid, sess in self.client._sessions.items()]

class CompilerExplorerModule(WorkbenchModule):
    def __init__(self, client: OMLXClient):
        super().__init__(ModuleInfo(
            id="compiler_explorer",
            name="Compiler Explorer",
            description="Visualize PlanningBundle and compiler passes.",
            route="/compiler"
        ))
        self.client = client

    def get_compiler_info(self) -> Dict[str, Any]:
        return {"status": "available" if hasattr(self.client._runtime, "compiler") else "unavailable"}

class PlanningExplorerModule(WorkbenchModule):
    def __init__(self, client: OMLXClient):
        super().__init__(ModuleInfo(
            id="planning_explorer",
            name="Planning Explorer",
            description="Visualize Planning domains.",
            route="/planning"
        ))
        self.client = client

    def get_planning_domains(self) -> List[str]:
        return ["CachePlan", "MemoryPlan", "DevicePlan", "BatchPlan", "MoEPlan"]

class ModelExplorerModule(WorkbenchModule):
    def __init__(self, client: OMLXClient):
        super().__init__(ModuleInfo(
            id="model_explorer",
            name="Model Explorer",
            description="Visualize discovered models and metadata.",
            route="/models"
        ))
        self.client = client

    def get_model_intelligence(self) -> Dict[str, Any]:
         try:
              return self.client.get_model_info()
         except Exception:
              return {"status": "unavailable"}

class DiagnosticsExplorerModule(WorkbenchModule):
    def __init__(self, client: OMLXClient):
        super().__init__(ModuleInfo(
            id="diagnostics_explorer",
            name="Diagnostics Explorer",
            description="Visualize validation reports and diagnostics.",
            route="/diagnostics"
        ))
        self.client = client

class PluginExplorerModule(WorkbenchModule):
    def __init__(self, client: OMLXClient):
        super().__init__(ModuleInfo(
            id="plugin_explorer",
            name="Plugin Explorer",
            description="Visualize installed plugins and capabilities.",
            route="/plugins"
        ))
        self.client = client

class SessionExplorerModule(WorkbenchModule):
    def __init__(self, client: OMLXClient):
        super().__init__(ModuleInfo(
            id="session_explorer",
            name="Session Explorer",
            description="Detailed visualization of RuntimeSessions.",
            route="/sessions"
        ))
        self.client = client
