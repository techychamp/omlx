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
