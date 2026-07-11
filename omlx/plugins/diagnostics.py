from typing import Dict, Any, List
from .registry import PluginRegistry

class DiagnosticsGenerator:
    """
    Generates various diagnostic reports for the plugin ecosystem.
    """
    def __init__(self, registry: PluginRegistry):
        self._registry = registry

    def generate_composition_report(self) -> Dict[str, Any]:
        report = {"composition": {}}
        for ext_type, exts in self._registry._extensions_by_type.items():
             report["composition"][str(ext_type)] = [ext.extension_id for ext in exts]
        return report

    def generate_configuration_report(self) -> Dict[str, Any]:
        report = {"configurations": {}}
        for pid, desc in self._registry._descriptors.items():
            report["configurations"][pid] = {
                 "enabled": desc.configuration.enabled,
                 "priority": desc.configuration.priority.name,
                 "feature_flags": list(desc.configuration.feature_flags)
            }
        return report

    def generate_priority_report(self) -> Dict[str, Any]:
        report = {"priorities": {}}
        for pid, desc in self._registry._descriptors.items():
             report["priorities"][pid] = desc.configuration.priority.name
        return report

    def generate_extension_report(self) -> Dict[str, Any]:
        report = {"extensions": {}}
        for pid, exts in self._registry._extensions_by_plugin.items():
             report["extensions"][pid] = [ext.extension_id for ext in exts]
        return report

    def generate_full_report(self) -> Dict[str, Any]:
        report = {}
        report.update(self.generate_composition_report())
        report.update(self.generate_configuration_report())
        report.update(self.generate_priority_report())
        report.update(self.generate_extension_report())
        report.update(self._registry.generate_diagnostics_report())
        return report
from typing import Dict, Any
from .registry import PluginRegistry
from .graph import PluginDependencyGraph
from .lifecycle import PluginLifecycleMonitor

class PluginDiagnosticsGenerator:
    def __init__(self, registry: PluginRegistry, graph: PluginDependencyGraph, monitor: PluginLifecycleMonitor):
        self._registry = registry
        self._graph = graph
        self._monitor = monitor

    def generate(self) -> Dict[str, Any]:
        return {
            "dependency_graph_report": self._generate_graph_report(),
            "trust_report": self._generate_trust_report(),
            "permission_report": self._generate_permission_report(),
            "lifecycle_report": self._monitor.generate_report(),
            "registry_report": self._registry.generate_diagnostics_report(),
            "sandbox_report": self._generate_sandbox_report(),
        }

    def _generate_graph_report(self) -> Dict[str, Any]:
        report = {
            "nodes": {},
            "roots": list(self._graph.roots),
            "metadata": self._graph.metadata
        }
        for pid, node in self._graph.nodes.items():
            report["nodes"][pid] = {
                "depends_on": list(node.depends_on),
                "required_by": list(node.required_by),
                "optional_dependencies": list(node.optional_dependencies)
            }
        return report

    def _generate_trust_report(self) -> Dict[str, Any]:
        report = {}
        for pid, desc in self._registry._descriptors.items():
            report[pid] = desc.trust_level.value
        return report

    def _generate_permission_report(self) -> Dict[str, Any]:
        report = {}
        for pid, desc in self._registry._descriptors.items():
            report[pid] = [p.value for p in desc.permissions]
        return report

    def _generate_sandbox_report(self) -> Dict[str, Any]:
        # Architecture placeholder
        return {"policy": "Not implemented"}
