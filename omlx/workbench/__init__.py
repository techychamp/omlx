"""
Developer Workbench Foundation.
"""
from .navigation import ModuleInfo, WorkbenchModule, NavigationManager
from .modules import (
    DashboardModule,
    RuntimeExplorerModule,
    CompilerExplorerModule,
    PlanningExplorerModule,
    ModelExplorerModule,
    DiagnosticsExplorerModule,
    PluginExplorerModule,
    SessionExplorerModule
)
from .app import DeveloperWorkbench

__all__ = [
    "ModuleInfo",
    "WorkbenchModule",
    "NavigationManager",
    "DashboardModule",
    "RuntimeExplorerModule",
    "CompilerExplorerModule",
    "PlanningExplorerModule",
    "ModelExplorerModule",
    "DiagnosticsExplorerModule",
    "PluginExplorerModule",
    "SessionExplorerModule",
    "DeveloperWorkbench"
]
