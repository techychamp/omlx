from typing import Dict, List, Any
from .descriptor import PluginDescriptor, PluginTrustLevel
from .registry import PluginRegistry

class PluginValidationFramework:
    """
    Validates plugin descriptors, permissions, trust policies, and isolation policies
    against stated constraints.
    """
    def __init__(self, registry: PluginRegistry):
        self._registry = registry

    def validate_plugin(self, descriptor: PluginDescriptor) -> Dict[str, Any]:
        """
        Validates a single plugin descriptor.
        Returns a dictionary of validation results.
        """
        results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        # Validate isolation policy conflicts
        if descriptor.trust_level in (PluginTrustLevel.UNTRUSTED, PluginTrustLevel.EXPERIMENTAL):
            if descriptor.isolation_policy.shared_state_allowed:
                results["errors"].append("Untrusted/Experimental plugins cannot allow shared state")
                results["is_valid"] = False

            if not descriptor.isolation_policy.read_only_context:
                 results["errors"].append("Untrusted/Experimental plugins must have a read-only context")
                 results["is_valid"] = False

        # Validate capabilities vs required stages
        if "backend_extension" in [c.value for c in descriptor.capabilities]:
            if not descriptor.supported_backend_families:
                 results["warnings"].append("Backend extension plugin does not declare supported backend families")

        # Additional custom validation logic would go here

        return results

    def validate_all(self, descriptors: List[PluginDescriptor]) -> Dict[str, Any]:
        """
        Validates a list of plugin descriptors.
        """
        global_results = {}
        for desc in descriptors:
             global_results[desc.plugin_id] = self.validate_plugin(desc)
        return global_results
