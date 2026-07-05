import re

with open("omlx/plugins/manager.py", "r") as f:
    content = f.read()

content = content.replace("from .descriptor import PluginDescriptor, PluginLifecycleState", "from .descriptor import PluginDescriptor, PluginLifecycleState\nfrom .compatibility import CompatibilityNegotiator")

validation_mod = """    def validate_and_seal(self) -> None:
        \"\"\"
        Phase 4: Validate dependency graph, compatibility, and seal registry.
        \"\"\"
        self._registry.validate_dependencies()

        # Compatibility check
        negotiator = CompatibilityNegotiator(
            self._registry,
            current_compiler_version="1.0.0", # TODO: Get from context
            current_runtime_version="1.0.0"
        )

        descriptors = list(self._registry._descriptors.values())
        compatibility_diagnostics = negotiator.check_compatibility(descriptors)

        # Merge diagnostics
        self._registry._diagnostics["compatibility"] = compatibility_diagnostics

        # If conflicts exist, transition to failed
        for pid in compatibility_diagnostics["version_conflicts"]:
             if pid in self._registry._descriptors:
                 self._registry.transition_state(pid, PluginLifecycleState.FAILED)"""

content = content.replace("""    def validate_and_seal(self) -> None:
        \"\"\"
        Phase 4: Validate dependency graph and seal registry.
        \"\"\"
        self._registry.validate_dependencies()""", validation_mod)


with open("omlx/plugins/manager.py", "w") as f:
    f.write(content)
