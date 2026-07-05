import re

with open("omlx/plugins/registry.py", "r") as f:
    content = f.read()

registry_methods = """
    def get_by_capability(self, capability) -> List[PluginDescriptor]:
        with self._lock:
            return [desc for desc in self._descriptors.values() if capability.value in desc.capabilities]

    def get_by_priority(self, priority) -> List[PluginDescriptor]:
        with self._lock:
            return [desc for desc in self._descriptors.values() if desc.priority == priority]

    def get_extensions_by_capability(self, capability) -> List[ExtensionPoint]:
        with self._lock:
            extensions = []
            for exts in self._extensions_by_plugin.values():
                for ext in exts:
                    if capability in ext.capabilities:
                        extensions.append(ext)
            return extensions
"""

# Insert methods before generate_diagnostics_report
content = content.replace("    def generate_diagnostics_report(self) -> Dict[str, Any]:", registry_methods + "\n    def generate_diagnostics_report(self) -> Dict[str, Any]:")

with open("omlx/plugins/registry.py", "w") as f:
    f.write(content)
