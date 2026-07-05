import re

with open('omlx/plugins/contracts.py', 'r') as f:
    content = f.read()

content = content.replace("from typing import Protocol, Any, Dict, runtime_checkable", "from typing import Protocol, Any, Dict, List, Tuple, runtime_checkable\nfrom .descriptor import PluginCapability")

ext_point_mod = """@runtime_checkable
class ExtensionPoint(Protocol):
    @property
    def extension_id(self) -> str:
        ...

    @property
    def display_name(self) -> str:
        return self.extension_id

    @property
    def description(self) -> str:
        return ""

    @property
    def plugin_owner(self) -> str:
        return ""

    @property
    def supported_compiler_stages(self) -> Tuple[str, ...]:
        return ()

    @property
    def supported_backend_families(self) -> Tuple[str, ...]:
        return ()

    @property
    def supported_execution_families(self) -> Tuple[str, ...]:
        return ()

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def capabilities(self) -> Tuple[PluginCapability, ...]:
        return ()

    @property
    def diagnostics(self) -> Dict[str, Any]:
        return {}"""

content = content.replace("""@runtime_checkable
class ExtensionPoint(Protocol):
    @property
    def extension_id(self) -> str:
        ...""", ext_point_mod)

with open('omlx/plugins/contracts.py', 'w') as f:
    f.write(content)
