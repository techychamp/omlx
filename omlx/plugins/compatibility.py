from typing import Dict, List, Optional, Any
import logging
from .descriptor import PluginDescriptor
from .registry import PluginRegistry

logger = logging.getLogger(__name__)

class CompatibilityNegotiator:
    """
    Handles compatibility checking for compiler, framework, plugin versions,
    backend compatibility, feature flags, and dependency compatibility.
    """
    def __init__(self, registry: PluginRegistry, current_compiler_version: str, current_runtime_version: str):
        self._registry = registry
        self._current_compiler_version = current_compiler_version
        self._current_runtime_version = current_runtime_version

    def check_compatibility(self, descriptors: List[PluginDescriptor]) -> Dict[str, Any]:
        """
        Validates compatibility across all plugins.
        """
        diagnostics: Dict[str, Any] = {
            "version_conflicts": [],
            "dependency_conflicts": [],
            "competing_implementations": []
        }

        seen_plugins = set()

        for desc in descriptors:
            # Check for duplicate plugins
            if desc.plugin_id in seen_plugins:
                diagnostics["version_conflicts"].append(f"Duplicate plugin ID: {desc.plugin_id}")
            seen_plugins.add(desc.plugin_id)

            # Check compiler version compatibility
            if desc.supported_compiler_versions and self._current_compiler_version not in desc.supported_compiler_versions:
                 diagnostics["version_conflicts"].append(
                     f"Plugin {desc.plugin_id} does not support compiler version {self._current_compiler_version}"
                 )

            # Check runtime version compatibility
            if desc.supported_runtime_versions and self._current_runtime_version not in desc.supported_runtime_versions:
                 diagnostics["version_conflicts"].append(
                     f"Plugin {desc.plugin_id} does not support runtime version {self._current_runtime_version}"
                 )

            # Check dependency compatibility
            for req_plugin_id, req_version in desc.dependencies.items():
                 req_desc = self._registry.get_descriptor(req_plugin_id)
                 if req_desc:
                     if req_desc.version != req_version: # Simplified version check
                         diagnostics["dependency_conflicts"].append(
                             f"Plugin {desc.plugin_id} requires {req_plugin_id} v{req_version}, but v{req_desc.version} is installed"
                         )

        return diagnostics
