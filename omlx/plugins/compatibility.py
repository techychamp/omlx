from typing import Dict, List, Optional, Any
import logging
from .descriptor import PluginDescriptor
from .registry import PluginRegistry
from .versioning import SemanticVersion

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
            "competing_implementations": [],
            "capability_conflicts": [],
            "permission_conflicts": [],
            "trust_conflicts": []
        }

        seen_plugins = set()

        for desc in descriptors:
            # Check for duplicate plugins
            if desc.plugin_id in seen_plugins:
                diagnostics["version_conflicts"].append(f"Duplicate plugin ID: {desc.plugin_id}")
            seen_plugins.add(desc.plugin_id)

            # Check compiler version compatibility
            if desc.supported_compiler_versions:
                is_compat = False
                for supported_ver in desc.supported_compiler_versions:
                    if SemanticVersion.is_compatible(self._current_compiler_version, supported_ver):
                        is_compat = True
                        break
                if not is_compat:
                    diagnostics["version_conflicts"].append(
                        f"Plugin {desc.plugin_id} does not support compiler version {self._current_compiler_version}"
                    )

            # Check runtime version compatibility
            if desc.supported_runtime_versions:
                is_compat = False
                for supported_ver in desc.supported_runtime_versions:
                    if SemanticVersion.is_compatible(self._current_runtime_version, supported_ver):
                        is_compat = True
                        break
                if not is_compat:
                    diagnostics["version_conflicts"].append(
                        f"Plugin {desc.plugin_id} does not support runtime version {self._current_runtime_version}"
                    )

            # Check dependency compatibility
            for req_plugin_id, req_version in desc.dependencies.items():
                 req_desc = self._registry.get_descriptor(req_plugin_id)
                 if req_desc:
                     if not SemanticVersion.is_compatible(req_desc.version, req_version):
                         diagnostics["dependency_conflicts"].append(
                             f"Plugin {desc.plugin_id} requires {req_plugin_id} {req_version}, but v{req_desc.version} is installed"
                         )


        # Additional Conflict Checks
        # Detect duplicate providers for exclusive extension points
        provided_extensions = {}
        for desc in descriptors:
            for ext in desc.provided_extension_points:
                if ext in provided_extensions:
                    diagnostics["competing_implementations"].append(
                        f"Extension {ext} provided by both {provided_extensions[ext]} and {desc.plugin_id}"
                    )
                provided_extensions[ext] = desc.plugin_id

        # Trust conflicts: A Core/Built-in plugin cannot depend on an Untrusted plugin
        from .descriptor import PluginTrustLevel
        for desc in descriptors:
            if desc.trust_level in (PluginTrustLevel.CORE, PluginTrustLevel.BUILT_IN, PluginTrustLevel.VERIFIED):
                for req_plugin_id in desc.dependencies:
                    req_desc = self._registry.get_descriptor(req_plugin_id)
                    if req_desc and req_desc.trust_level in (PluginTrustLevel.UNTRUSTED, PluginTrustLevel.EXPERIMENTAL):
                         diagnostics["trust_conflicts"].append(
                             f"Trusted plugin {desc.plugin_id} depends on untrusted plugin {req_plugin_id}"
                         )

        # We can add more generic conflicts (capability and permission conflicts) here if needed
        # based on specific runtime policies.
        return diagnostics
