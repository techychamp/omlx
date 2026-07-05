from typing import Dict, List, Optional
from .registry import PluginRegistry
from .descriptor import PluginDescriptor, PluginCapability, PluginPermission, PluginTrustLevel

class PluginRegistryExtensions:
    def __init__(self, registry: PluginRegistry):
        self._registry = registry

    def get_by_capability(self, capability: PluginCapability) -> List[PluginDescriptor]:
        return self._registry.get_by_capability(capability)

    def get_by_permission(self, permission: PluginPermission) -> List[PluginDescriptor]:
        return self._registry.get_by_permission(permission)

    def get_by_trust_level(self, trust_level: PluginTrustLevel) -> List[PluginDescriptor]:
        return self._registry.get_by_trust_level(trust_level)

    def get_by_compiler_stage(self, stage: str) -> List[PluginDescriptor]:
        return self._registry.get_by_compiler_stage(stage)

    def get_by_backend_family(self, family: str) -> List[PluginDescriptor]:
        return self._registry.get_by_backend_family(family)

    def get_by_execution_family(self, family: str) -> List[PluginDescriptor]:
        return self._registry.get_by_execution_family(family)

    def get_by_dependency(self, plugin_id: str) -> List[PluginDescriptor]:
        return self._registry.get_by_dependency(plugin_id)
